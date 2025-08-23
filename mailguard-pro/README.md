# DNSight Pro: Comprehensive IP/Domain Health & Deliverability Toolkit

![DNSight Pro Screenshot](https://via.placeholder.com/800x400?text=DNSight+Pro+Screenshot)
*(**Action Required:** Please replace this placeholder image with an actual screenshot of your application's user interface for better visual appeal and clarity.)*

DNSight Pro is a robust, open-source web application designed to be your go-to solution for diagnosing and monitoring the health and deliverability aspects of IP addresses and domain names. Built with Python Flask, it streamlines the process of checking critical network and email configurations, providing a consolidated view of potential issues that could impact your online presence or email communication. From identifying blacklisting concerns to validating essential DNS records and SSL certificates, DNSight Pro equips system administrators, developers, and email marketers with the insights needed to maintain optimal server performance and email deliverability.

---

## Key Features

DNSight Pro offers a powerful suite of diagnostic tools, integrated into one intuitive interface:

* **Unified Query Interface:** Simply enter an IP address or domain name into a single input field to trigger a comprehensive suite of checks.
* **Real-time Blacklist Detection:** Instantly scan IP addresses against multiple popular Real-time Blackhole Lists (RBLs) to identify potential spam listings that can severely impact email deliverability.
* **Extensive DNS Record Analysis:** Gain deep insights into your domain's DNS setup by retrieving:
    * **MX Records:** Verify mail exchange server configurations and their priorities.
    * **NS Records:** Inspect name server entries and their corresponding IP addresses.
    * **A/AAAA Records:** Confirm IPv4 and IPv6 address mappings.
    * **CNAME Records:** Identify canonical name aliases.
    * **TXT Records:** Review generic text records, often used for verification purposes.
    * **SOA Records:** Examine Start of Authority records for domain administrative details.
* **Email Authentication Validation (SPF, DKIM, DMARC):** Critical for preventing email spoofing and ensuring deliverability, DNSight Pro meticulously checks for the correct implementation of:
    * **SPF (Sender Policy Framework):** Ensures authorized senders for your domain.
    * **DKIM (DomainKeys Identified Mail):** Verifies email authenticity using digital signatures, with automatic detection for common selectors.
    * **DMARC (Domain-based Message Authentication, Reporting, and Conformance):** Provides a policy for handling unauthorized email, offering robust protection.
* **Reverse DNS (PTR) Lookup:** For IP addresses, verify the existence and correctness of PTR records, a vital component for mail server reputation.
* **Essential Port Connectivity Scan:** Quickly determine the accessibility (Open, Closed, Filtered) of crucial ports, including:
    * **SMTP (Ports 25, 465, 587):** Essential for email sending and receiving.
    * **HTTP (Port 80):** Standard web traffic.
    * **HTTPS (Port 443):** Secure web traffic.
* **SSL/TLS Certificate Health Check:** For HTTPS-enabled domains, assess the validity, expiration date, common name, and issuing authority of your SSL/TLS certificates to ensure secure connections.
* **Overall Health Score & Issues Summary:** Receive an intuitive health score (out of 100) and a list of identified issues, offering a quick snapshot of the IP/domain's configuration and potential areas for improvement.
* **Downloadable Reports:** Generate and download a comprehensive PDF report of all scan results, ideal for documentation, client reporting, or troubleshooting records.
* **Guided Delisting Support:** While automated delisting is not feasible, the application provides clear guidance and direct links to major RBL providers to assist you in the manual delisting process if your IP/domain is blacklisted.
* **Robust Rate Limiting:** Built-in protection prevents service abuse by limiting the number of requests from a single source IP address, ensuring fair usage and system stability.

---

## Getting Started

Follow these instructions to set up and run DNSight Pro on your system.

### Prerequisites

Ensure you have the following installed:

* **Python 3.8+**
* **pip** (Python package installer)
* **Git** (for cloning the repository)
* **Docker** and **Docker Compose** (Highly recommended for simplified deployment)

### 1. Clone the Repository

Begin by cloning the DNSight Pro repository to your local machine:

```bash
git clone [https://github.com/YOUR_GITHUB_USERNAME/dnsight-pro.git](https://github.com/YOUR_GITHUB_USERNAME/dnsight-pro.git)
cd dnsight-pro
````

*(**Action Required:** Please replace `YOUR_GITHUB_USERNAME` with your actual GitHub username and `dnsight-pro.git` with your repository name after pushing your code.)*

### 2\. Project Structure

The project adheres to a clean and logical structure:

```
dnsight-pro/
├── app.py                  # Main Flask application logic
├── Dockerfile              # Docker build instructions for the app
├── docker-compose.yml      # Docker Compose configuration for container orchestration
├── requirements.txt        # Python package dependencies
├── .env.example            # Example environment variables file
└── templates/
    └── index.html          # HTML template for the web interface
```

### 3\. Environment Configuration (`.env` file)

To customize the application's behavior, create a `.env` file from the provided example:

```bash
cp .env.example .env
```

Now, open the `.env` file using a text editor (e.g., `nano .env` or `code .env`) and adjust the settings as needed. These variables control RBL servers, rate limits, and DKIM selector checks:

```dotenv
# .env file content
# Comma-separated list of RBL servers to check against. You can add or remove entries.
RBL_SERVERS=zen.spamhaus.org,bl.spamcop.net,cbl.abuseat.org,b.barracudacentral.org

# Rate Limiting Configuration:
# Maximum number of requests allowed from a single IP address within the defined time window.
RATE_LIMIT_COUNT=10
# The time window (in seconds) during which the RATE_LIMIT_COUNT applies (e.g., 60 for 1 minute).
RATE_LIMIT_WINDOW=60

# Common DKIM selectors to automatically check. Add popular selectors relevant to your needs.
COMMON_DKIM_SELECTORS=default,20200519,google,k1,selector1,mail,m1
```

-----

## Running the Application

DNSight Pro can be run using Docker Compose (recommended for ease of deployment and environment isolation) or directly with Python for local development.

### Option 1: Running with Docker Compose (Recommended)

Docker Compose provides a simple way to build and run the application within isolated containers, managing all dependencies automatically.

1.  **Build and Start Services:** Navigate to the `dnsight-pro` root directory in your terminal and execute:

    ```bash
    docker-compose up --build -d
    ```

      * `--build`: This ensures that the Docker image for the `web` service is built from scratch based on your `Dockerfile`.
      * `-d`: This runs the containers in detached mode (in the background).

    This command will:

      * Read the `docker-compose.yml` file.
      * Build the Docker image for your Flask application.
      * Start the `web` service container.

2.  **Access the Application:** Once the container is running, open your web browser and navigate to:
    `http://localhost:5000/`

3.  **View Logs (Optional):** To see the application's output and debug information:

    ```bash
    docker-compose logs -f web
    ```

4.  **Stop the Application:** To stop the running containers (and remove them by default), use:

    ```bash
    docker-compose down
    ```

### Option 2: Running Locally (Without Docker)

If you prefer to run the application directly on your host machine without Docker:

1.  **Create a Python Virtual Environment:** It's best practice to use a virtual environment to manage project dependencies and avoid conflicts with global Python packages.

    ```bash
    python -m venv venv
    ```

2.  **Activate the Virtual Environment:**

      * **On Windows (Command Prompt/PowerShell):**
        ```bash
        .\venv\Scripts\activate
        ```
      * **On macOS/Linux (Bash/Zsh):**
        ```bash
        source venv/bin/activate
        ```

3.  **Install Required Python Packages:** Install all dependencies listed in `requirements.txt`:

    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the Flask Application:** Ensure your virtual environment is active and then run the Flask app:

    ```bash
    python app.py
    ```

    The application will start, and you should see output indicating it's listening on `http://127.0.0.1:5000/`.

5.  **Access the Application:** Open your web browser and go to:
    `http://127.0.0.1:5000/`

6.  **Deactivate Virtual Environment:** When you're finished working with the application, you can deactivate the virtual environment:

    ```bash
    deactivate
    ```

-----

## Customization

DNSight Pro is designed for flexibility. You can easily customize its behavior and appearance:

  * **`app.py`:** Modify or extend the core logic, add new check functions, or integrate with other services.
  * **`templates/index.html`:** Adjust the front-end layout, styling, and interactivity using HTML, CSS, and JavaScript.
  * **`.env`:** Update the configuration for RBL servers, rate limiting thresholds, and DKIM selectors without touching the code.
  * **`Dockerfile`:** If your application requires additional system-level dependencies or a different base Python image, modify this file.
  * **`docker-compose.yml`:** Extend your Docker setup by adding more services, such as a reverse proxy (e.g., Nginx), a database for logging, or other monitoring tools.

-----

## Contributing

Contributions are highly valued\! If you encounter a bug, have a suggestion for a new feature, or wish to improve the existing codebase, please feel free to:

1.  Fork the repository.
2.  Create a new branch for your feature or bug fix.
3.  Commit your changes.
4.  Push your branch to your forked repository.
5.  Open a Pull Request with a clear description of your changes.

-----

## License

This project is open-source and distributed under the **MIT License**. For more details, see the [LICENSE](https://www.google.com/search?q=LICENSE) file in the repository.
*(**Action Required:** Ensure you have an actual `LICENSE` file in your repository. If not, create one with the MIT License text.)*

-----

## Contact

If you have any questions, feedback, or require further assistance, please open an issue on this GitHub repository. We appreciate your engagement\!

---

