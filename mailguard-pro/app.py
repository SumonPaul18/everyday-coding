import os
from flask import Flask, render_template, request, jsonify, send_file
import dns.resolver
import dns.reversename
import ipaddress
from dotenv import load_dotenv
import time
from collections import defaultdict
import socket
import ssl
from datetime import datetime
import io
from xhtml2pdf import pisa # For PDF generation

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# --- Configuration ---
RBL_SERVERS = os.getenv('RBL_SERVERS', "zen.spamhaus.org,bl.spamcop.net,cbl.abuseat.org,b.barracudacentral.org").split(',')
RBL_SERVERS = [rbl.strip() for rbl in RBL_SERVERS if rbl.strip()]

RATE_LIMIT_COUNT = int(os.getenv('RATE_LIMIT_COUNT', 10))
RATE_LIMIT_WINDOW = int(os.getenv('RATE_LIMIT_WINDOW', 60))
request_timestamps = defaultdict(list)

COMMON_DKIM_SELECTORS = os.getenv('COMMON_DKIM_SELECTORS', "default,20200519,google,k1,selector1,mail,m1").split(',')
COMMON_DKIM_SELECTORS = [s.strip() for s in COMMON_DKIM_SELECTORS if s.strip()]

# Common ports to scan
COMMON_PORTS = {
    "SMTP": 25,
    "SMTPS": 465, # Implicit TLS
    "Submission": 587, # Explicit TLS
    "HTTP": 80,
    "HTTPS": 443
}

# --- Rate Limiting ---
@app.before_request
def before_request():
    if request.path == '/check_all' and request.method == 'POST':
        client_ip = request.remote_addr
        current_time = time.time()

        request_timestamps[client_ip] = [
            ts for ts in request_timestamps[client_ip]
            if current_time - ts < RATE_LIMIT_WINDOW
        ]

        if len(request_timestamps[client_ip]) >= RATE_LIMIT_COUNT:
            time_since_first = current_time - request_timestamps[client_ip][0]
            time_to_wait = RATE_LIMIT_WINDOW - time_since_first
            if time_to_wait > 0:
                return jsonify({
                    "error": f"Too many requests from your IP. Please try again in {int(time_to_wait)} seconds."
                }), 429
        
        request_timestamps[client_ip].append(current_time)

# --- DNS Utility Functions ---
def resolve_dns_record(query_target, record_type, timeout=2):
    """Resolves a specific DNS record type."""
    try:
        answers = dns.resolver.resolve(query_target, record_type, lifetime=timeout)
        return [str(a) for a in answers]
    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.resolver.NoNameservers, dns.resolver.Timeout, Exception) as e:
        return [f"Error fetching {record_type} record for {query_target}: {e}"]

def check_ip_on_rbls(ip_address):
    """Checks if an IP address is listed on various RBLs."""
    results = {}
    for rbl in RBL_SERVERS:
        try:
            reversed_ip = ".".join(reversed(ip_address.split(".")))
            query = f"{reversed_ip}.{rbl}"
            answers = dns.resolver.resolve(query, 'A', lifetime=1) # Shorter timeout for RBLs
            results[rbl] = {"listed": True, "details": [str(a) for a in answers]}
        except dns.resolver.NXDOMAIN:
            results[rbl] = {"listed": False, "details": []}
        except (dns.resolver.Timeout, Exception) as e:
            results[rbl] = {"listed": "error", "details": [f"Query timed out or error: {e}"]}
    return results

def get_mx_records(domain):
    """Fetches and parses MX records."""
    mx_records_raw = resolve_dns_record(domain, 'MX')
    mx_records_parsed = []
    
    if "Error fetching MX record" in mx_records_raw[0] or "No MX record found" in mx_records_raw[0]:
        return [{"preference": "N/A", "exchange": mx_records_raw[0]}]

    for record in mx_records_raw:
        try:
            parts = record.split(' ')
            preference = int(parts[0])
            exchange = parts[1].strip('.')
            mx_records_parsed.append({"preference": preference, "exchange": exchange})
        except (ValueError, IndexError):
            mx_records_parsed.append({"preference": "Parse Error", "exchange": record})
    
    # Sort by preference if parsing was successful
    if mx_records_parsed and isinstance(mx_records_parsed[0]['preference'], int):
        mx_records_parsed.sort(key=lambda x: x['preference'])
    return mx_records_parsed

def get_all_dns_records(domain):
    """Fetches common DNS records for a domain (A, AAAA, CNAME, TXT, NS, SOA)."""
    all_records = {}
    record_types = ['A', 'AAAA', 'CNAME', 'TXT', 'NS', 'SOA']
    for rec_type in record_types:
        all_records[rec_type.lower()] = resolve_dns_record(domain, rec_type)
    return all_records

def get_ns_records_with_ips(domain):
    """Fetches NS records and resolves their corresponding IP addresses."""
    ns_records_data = []
    ns_servers = resolve_dns_record(domain, 'NS')

    for ns_server_name_raw in ns_servers:
        if "Error fetching NS record" in ns_server_name_raw or "No NS record found" in ns_server_name_raw:
            ns_records_data.append({"name": ns_server_name_raw, "ips": []})
            continue
        
        ns_server_clean = ns_server_name_raw.strip('.')
        ips = []
        try:
            a_records = resolve_dns_record(ns_server_clean, 'A')
            ips.extend([ip for ip in a_records if not ip.startswith("Error")])
        except Exception:
            pass
        try:
            aaaa_records = resolve_dns_record(ns_server_clean, 'AAAA')
            ips.extend([ip for ip in aaaa_records if not ip.startswith("Error")])
        except Exception:
            pass
        
        if not ips:
            ips = ["No IP found"]

        ns_records_data.append({"name": ns_server_clean, "ips": ips})
    return ns_records_data

def get_email_config_records(domain):
    """Fetches SPF, DKIM, and DMARC DNS records."""
    records = {}
    
    # SPF
    spf_results = resolve_dns_record(domain, 'TXT')
    records['spf'] = [r for r in spf_results if 'v=spf1' in r.lower()]
    if not records['spf'] and not ("No TXT record found" in spf_results[0] or "Error fetching TXT record" in spf_results[0]):
        records['spf'] = ["No SPF record found (v=spf1 not present in TXT records)."]
    elif not records['spf']:
        records['spf'] = spf_results

    # DKIM (try common selectors)
    found_dkim = False
    all_dkim_details = []
    for selector in COMMON_DKIM_SELECTORS:
        dkim_query_target = f"{selector}._domainkey.{domain}"
        dkim_results = resolve_dns_record(dkim_query_target, 'TXT')
        valid_dkim_records = [r for r in dkim_results if 'p=' in r.lower()]
        
        if valid_dkim_records:
            all_dkim_details.extend([f"Selector '{selector}': {rec}" for rec in valid_dkim_records])
            found_dkim = True
        elif not ("No TXT record found" in dkim_results[0] or "Error fetching TXT record" in dkim_results[0]):
             all_dkim_details.append(f"Selector '{selector}': {dkim_results[0]}")
        
    if found_dkim:
        records['dkim'] = all_dkim_details
    else:
        if not all_dkim_details: 
             records['dkim'] = ["No DKIM record found using common selectors."]
        else:
             records['dkim'] = all_dkim_details

    # DMARC
    dmarc_results = resolve_dns_record(f"_dmarc.{domain}", 'TXT')
    records['dmarc'] = [r for r in dmarc_results if 'v=DMARC1' in r.lower()]
    if not records['dmarc'] and not ("No TXT record found" in dmarc_results[0] or "Error fetching TXT record" in dmarc_results[0]):
        records['dmarc'] = ["No DMARC record found."]
    elif not records['dmarc']:
        records['dmarc'] = dmarc_results

    return records

def check_reverse_dns(ip_address):
    """Checks the PTR record for an IP address."""
    try:
        addr = dns.reversename.from_address(ip_address)
        ptr_records = dns.resolver.resolve(addr, 'PTR', lifetime=2)
        return [str(p).strip('.') for p in ptr_records] # Remove trailing dot
    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.resolver.Timeout, Exception) as e:
        return [f"Error fetching PTR record for {ip_address}: {e}"]

def perform_port_scan(target_host, port):
    """Attempts to connect to a specific port on a host."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1) # 1 second timeout for connection
        result = sock.connect_ex((target_host, port))
        sock.close()
        if result == 0:
            return "Open"
        elif result == 111: # Connection refused
            return "Closed"
        else:
            return f"Filtered (Error Code: {result})"
    except socket.gaierror:
        return "Hostname could not be resolved"
    except socket.error as e:
        return f"Socket error: {e}"
    except Exception as e:
        return f"Unknown error: {e}"

def check_ssl_certificate(host, port=443):
    """Checks SSL/TLS certificate details for a given host and port."""
    try:
        context = ssl.create_default_context()
        with socket.create_connection((host, port), timeout=2) as sock:
            with context.wrap_socket(sock, server_hostname=host) as ssock:
                cert = ssock.getpeercert()
                
                # Extract common name
                subject = dict(x[0] for x in cert['subject'])
                common_name = subject.get('commonName', 'N/A')

                # Extract issuer
                issuer = dict(x[0] for x in cert['issuer'])
                issuer_common_name = issuer.get('commonName', 'N/A')

                # Expiry date
                not_before = datetime.strptime(cert['notBefore'], '%b %d %H:%M:%S %Y %Z')
                not_after = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                
                expires_in_days = (not_after - datetime.now()).days

                status = "Valid"
                if datetime.now() < not_before:
                    status = "Not Yet Valid"
                elif datetime.now() > not_after:
                    status = "Expired"
                
                return {
                    "status": status,
                    "common_name": common_name,
                    "issuer": issuer_common_name,
                    "not_before": not_before.strftime("%Y-%m-%d %H:%M:%S"),
                    "not_after": not_after.strftime("%Y-%m-%d %H:%M:%S"),
                    "expires_in_days": expires_in_days,
                    "error": None
                }
    except ssl.SSLError as e:
        return {"status": "Error", "error": f"SSL Error: {e}"}
    except socket.timeout:
        return {"status": "Error", "error": "Connection timed out during SSL handshake."}
    except ConnectionRefusedError:
        return {"status": "Error", "error": "Connection refused. Port might be closed or service not running."}
    except socket.gaierror:
        return {"status": "Error", "error": "Hostname could not be resolved for SSL check."}
    except Exception as e:
        return {"status": "Error", "error": f"An unexpected error occurred during SSL check: {e}"}

def calculate_health_score(results):
    """
    Calculates a simple health score based on various checks.
    Higher score is better.
    """
    score = 100 # Max score
    issues = []

    # Blacklist Check (for IPs)
    if results.get("is_ip") and results.get("blacklist_results"):
        listed_count = sum(1 for rbl_data in results["blacklist_results"].values() if rbl_data.get("listed") is True)
        if listed_count > 0:
            score -= (listed_count * 10) # Deduct 10 points per listing
            issues.append(f"{listed_count} RBL listings found.")

    # Email Configuration Checks (for Domains)
    if not results.get("is_ip") and results.get("email_config"):
        email_cfg = results["email_config"]
        
        # SPF check
        if not email_cfg.get('spf') or "No SPF record found" in email_cfg['spf'][0]:
            score -= 15
            issues.append("Missing or invalid SPF record.")
        
        # DKIM check
        if not email_cfg.get('dkim') or "No DKIM record found" in email_cfg['dkim'][0]:
            score -= 15
            issues.append("Missing or invalid DKIM record.")

        # DMARC check
        if not email_cfg.get('dmarc') or "No DMARC record found" in email_cfg['dmarc'][0]:
            score -= 10
            issues.append("Missing or invalid DMARC record.")
        elif 'p=none' in email_cfg['dmarc'][0].lower(): # Weak DMARC policy
            score -= 5
            issues.append("DMARC policy is set to 'p=none', which is weak.")

    # Reverse DNS (PTR) check (for IPs)
    if results.get("is_ip") and results.get("ptr_records"):
        ptr_status = results['ptr_records'][0]
        if "Error fetching PTR record" in ptr_status or "No PTR record found" in ptr_status:
            score -= 10
            issues.append("Missing or invalid Reverse DNS (PTR) record.")
        elif results.get('query_host') and results.get('query_host') not in ptr_status: # PTR doesn't match host
             score -= 5
             issues.append(f"PTR record '{ptr_status}' does not directly match original host.")


    # Port scan check (for domains/IPs)
    if results.get("port_scan_results"):
        smtp_open = results["port_scan_results"].get("SMTP") == "Open" or results["port_scan_results"].get("Submission") == "Open"
        if not smtp_open:
            score -= 5
            issues.append("Common SMTP/Submission ports (25/587) are not open.")
        
        https_open = results["port_scan_results"].get("HTTPS") == "Open"
        if not https_open and not results.get("is_ip"): # Only for domains, or if IP is likely a web server
            score -= 3
            issues.append("HTTPS port (443) is not open for web services.")

    # SSL Certificate Check
    if results.get("ssl_cert_results") and results["ssl_cert_results"].get("status") == "Expired":
        score -= 10
        issues.append("SSL/TLS certificate is expired.")
    elif results.get("ssl_cert_results") and results["ssl_cert_results"].get("status") == "Error":
        score -= 5
        issues.append(f"SSL/TLS certificate check failed: {results['ssl_cert_results'].get('error', '')}")
    elif results.get("ssl_cert_results") and results["ssl_cert_results"].get("expires_in_days") is not None and results["ssl_cert_results"]["expires_in_days"] < 30:
        score -= 5
        issues.append(f"SSL/TLS certificate expires in less than 30 days ({results['ssl_cert_results']['expires_in_days']} days).")

    # Ensure score doesn't go below 0
    score = max(0, score)

    return {"score": score, "issues": issues}


# --- Flask Routes ---
@app.route('/')
def index():
    """Renders the main index page."""
    return render_template('index.html')

@app.route('/check_all', methods=['POST'])
def check_all_route():
    """
    Handles a single unified request to check IP/Domain blacklist, MX, NS,
    all DNS records, email configuration, PTR, Port Scan, and SSL.
    """
    query = request.form.get('query', '').strip()

    if not query:
        return jsonify({"error": "অনুগ্রহ করে একটি IP অ্যাড্রেস অথবা ডোমেইন দিন।"}), 400
    
    # Basic validation, can be enhanced with regex for strict domain/IP
    if not ('.' in query and query.count('.') >= 1) and not query.count('.') == 3: # min 1 dot for domain, exactly 3 for IPv4
        return jsonify({"error": "অনুগ্রহ করে একটি বৈধ IP অ্যাড্রেস অথবা ডোমেইন দিন।"}), 400

    results = {
        "query": query,
        "is_ip": False,
        "blacklist_results": {},
        "mx_records": [],
        "ns_records": [],
        "all_dns_records": {},
        "email_config": {},
        "ptr_records": [],
        "port_scan_results": {},
        "ssl_cert_results": {},
        "health_score": {"score": 0, "issues": []}, # Initialize
        "message": ""
    }

    target_host = query
    try:
        ip_obj = ipaddress.ip_address(query)
        results["is_ip"] = True
        # For IP, perform IP-specific checks
        results["blacklist_results"] = check_ip_on_rbls(query)
        results["ptr_records"] = check_reverse_dns(query)
        
        # Resolve hostname for IP if PTR exists and is single, to use for port scan if needed
        if results["ptr_records"] and len(results["ptr_records"]) == 1 and not results["ptr_records"][0].startswith("Error"):
            target_host = results["ptr_records"][0]
        
        results["message"] = f"'{query}' একটি IP অ্যাড্রেস। ব্ল্যাকলিস্ট, PTR এবং পোর্ট চেক করা হয়েছে।"

    except ValueError:
        # It's a domain, perform domain-specific checks
        results["is_ip"] = False
        results["mx_records"] = get_mx_records(query)
        results["ns_records"] = get_ns_records_with_ips(query)
        results["all_dns_records"] = get_all_dns_records(query)
        results["email_config"] = get_email_config_records(query)
        results["message"] = f"'{query}' একটি ডোমেইন। সকল প্রাসঙ্গিক রেকর্ড এবং সার্ভিস চেক করা হয়েছে।"
    
    # Common checks for both IP (if hostname resolved) and Domain
    # Use the resolved target_host for port scanning/SSL to ensure it's resolvable
    # or the original query if it's an IP
    host_for_network_checks = query if results["is_ip"] else query

    # Port Scanning
    port_scan_results = {}
    for service, port in COMMON_PORTS.items():
        scan_status = perform_port_scan(host_for_network_checks, port)
        port_scan_results[service] = scan_status
    results["port_scan_results"] = port_scan_results

    # SSL Certificate Check (only if HTTPS port is open and it's a domain or resolvable IP)
   # SSL Certificate Check (only if HTTPS port is open and it's a domain or resolvable IP)
    # Ensure ns_records has elements before trying to access index 0
    if port_scan_results.get("HTTPS") == "Open":
        if results["is_ip"]:
            # For IP, check if there's at least one NS record and it's not "No IP found"
            if results["ns_records"] and not results["ns_records"][0]["ips"][0] == "No IP found":
                results["ssl_cert_results"] = check_ssl_certificate(host_for_network_checks)
            else:
                results["ssl_cert_results"] = {"status": "Skipped", "error": "HTTPS port is open, but IP is not resolvable to a hostname for SSL check."}
        else: # It's a domain
            results["ssl_cert_results"] = check_ssl_certificate(host_for_network_checks)
    else:
        results["ssl_cert_results"] = {"status": "Skipped", "error": "HTTPS port not open or not applicable."}

    # Calculate overall health score
    results["health_score"] = calculate_health_score(results)

    return jsonify(results)

@app.route('/download_report', methods=['POST'])
def download_report():
    html_content = request.form.get('html_content', '')
    query = request.form.get('query', 'report')

    if not html_content:
        return "No content provided to generate report.", 400

    # Generate PDF from HTML
    pdf_buffer = io.BytesIO()
    pisa_status = pisa.CreatePDF(
        html_content,
        dest=pdf_buffer
    )

    if pisa_status.err:
        return "PDF generation error: %s" % pisa_status.err, 500
    
    pdf_buffer.seek(0)
    return send_file(pdf_buffer, download_name=f"mailguard_pro_report_{query}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf", as_attachment=True, mimetype='application/pdf')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)