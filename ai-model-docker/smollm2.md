# 🌟 StarCoder-LLM: Deploy SmolLM2 Locally with Docker Compose — Full Professional Guide

> **Unlock the power of lightweight, open-source LLMs on your machine. No cloud. No API keys. Just pure local AI.**

---
### ✅ **What is StarCoder-LLM?**
StarCoder-LLM is a local AI deployment framework built around **SmolLM2**, a highly efficient, open-weight language model (1.7B parameters) optimized for speed and low-resource environments. This guide walks you through deploying it using **Docker Compose** — turning your laptop or server into a private, offline LLM powerhouse.

### ✅ **Why Use SmolLM2?**
- ⚡ **Lightning-fast**: Runs on CPU or low-end GPU (as low as 4GB RAM).
- 💰 **Zero cost**: No API fees, no subscriptions.
- 🔐 **Private & secure**: Your data never leaves your machine.
- 🧠 **Surprisingly capable**: Excels at code generation, Q&A, and summarization despite its size.

### ✅ **Who Is This For?**
- Developers wanting **local code assistants** (like GitHub Copilot, but offline).
- Researchers testing LLMs without cloud dependencies.
- Educators and students exploring AI ethics and privacy.
- DevOps engineers building reproducible AI environments.

### ✅ **When Should You Use This?**
- When you need **real-time, private code generation**.
- In air-gapped or compliance-sensitive environments (healthcare, finance, government).
- To avoid latency from cloud APIs or usage limits.
- As a learning platform to understand containerized AI deployment.

---

## 🛠️ Step-by-Step Deployment: From Zero to SmolLM2 in Minutes

### ✅ **Prerequisites**
Ensure you have:
- Linux/macOS/Windows (WSL2 recommended)
- Docker Engine ≥ 24.0
- Docker Compose V2 (installed via `docker compose` command)

> 💡 *If Docker isn’t installed:*
```bash
curl -fsSL https://get.docker.com -o get-docker.sh && sudo sh get-docker.sh
sudo usermod -aG docker $USER
newgrp docker  # Reload group permissions
```

---

### ✅ **Basic Setup: One-Command Deployment**

Create the project directory and config file:

```bash
mkdir starcoder-llm
cd starcoder-llm/
nano docker-compose.yml
```

Paste this **basic `docker-compose.yml`**:

```yaml
version: '3.8'
services:
  smollm2:
    image: ghcr.io/huggingface/text-generation-inference:latest
    ports:
      - "8080:8080"
    volumes:
      - ./models:/data
    environment:
      - MODEL_ID=HuggingFaceH4/smollm2-1.7B
      - MAX_INPUT_LENGTH=1024
      - MAX_TOTAL_TOKENS=2048
      - TF_CPP_MIN_LOG_LEVEL=2
    restart: unless-stopped
    deploy:
      resources:
        reservations:
          memory: 4G
```

> 💡 *Note: Hugging Face's `text-generation-inference` container supports SmolLM2 natively.*

Save and exit (`Ctrl+O`, `Enter`, `Ctrl+X`).

Now launch it:

```bash
docker compose up -d
```

✅ **Wait 1–3 minutes** while the model downloads automatically.

Verify it’s running:

```bash
docker compose logs -f smollm2
```

You’ll see output like:
```
INFO text_generation_server: Starting server...
INFO text_generation_server: Model loaded, ready to serve requests on http://0.0.0.0:8080
```

> 🌐 Access the API at: [http://localhost:8080](http://localhost:8080)

---

### ✅ **Advanced Configuration: Production-Ready Setup**

Update your `docker-compose.yml` with this **advanced version**:

```yaml
version: '3.8'
services:
  smollm2:
    image: ghcr.io/huggingface/text-generation-inference:latest
    ports:
      - "8080:8080"
    volumes:
      - ./models:/data
      - ./logs:/logs
    environment:
      - MODEL_ID=HuggingFaceH4/smollm2-1.7B
      - MAX_INPUT_LENGTH=2048
      - MAX_TOTAL_TOKENS=4096
      - MAX_BATCH_TOTAL_TOKENS=8192
      - NUM_SHARDS=1
      - TF_CPP_MIN_LOG_LEVEL=2
      - HUGGING_FACE_HUB_TOKEN=your_token_if_private_model  # Optional
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 6G
          cpus: '2.0'
        reservations:
          memory: 4G
    networks:
      - llm-network

networks:
  llm-network:
    driver: bridge
```

📌 **Key Advanced Features:**
- `MAX_BATCH_TOTAL_TOKENS`: Enables concurrent requests.
- `healthcheck`: Auto-restarts if crashed.
- `networks`: Isolates traffic for security.
- `logs` volume: Persist inference logs for debugging.

Run again:

```bash
docker compose down
docker compose up -d
```

---

## 💬 How to Use SmolLM2: From Basic Queries to Code Generation

### ✅ **Basic Usage: Text Generation via cURL**

Send a prompt to the running model:

```bash
curl http://localhost:8080/generate \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "inputs": "Explain quantum computing in one sentence:",
    "parameters": {
      "max_new_tokens": 100,
      "temperature": 0.7,
      "top_p": 0.9
    }
  }'
```

💡 *Response format: JSON with generated text under `generated_text`.*

### ✅ **Code Generation Example (Starcoder Style)**

Ask it to write Python code:

```bash
curl http://localhost:8080/generate \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "inputs": "def fibonacci(n):\n    \"\"\"Generate Fibonacci sequence up to n\"\"\"\n    ",
    "parameters": {
      "max_new_tokens": 150,
      "temperature": 0.2,
      "do_sample": true,
      "stop_sequences": ["\\n\\n"]
    }
  }'
```

✅ Output will be a complete, well-formatted function!

### ✅ **Web UI: Use Ollama-like Interface (Optional)**

Install [Text Generation WebUI](https://github.com/oobabooga/text-generation-webui) for a browser-based chat interface:

```bash
git clone https://github.com/oobabooga/text-generation-webui
cd text-generation-webui
pip install -r requirements.txt
python server.py --model HuggingFaceH4/smollm2-1.7B --api --listen
```

Then visit: [http://localhost:7860](http://localhost:7860)

> 💡 Pro Tip: Use the “API” tab to connect to your Docker service instead of loading locally — saves memory!

---

## 📦 Model Management & Troubleshooting

### ❌ I See “Model Not Found” or “404”

The image pulls from Hugging Face automatically. If you get errors:

1. Ensure internet connectivity.
2. Try pulling manually first:
   ```bash
   docker pull ghcr.io/huggingface/text-generation-inference:latest
   ```
3. Use `MODEL_ID=bigcode/starcoder` if you want to switch models later.

### 🔄 Restart / Stop / View Logs

```bash
# Stop
docker compose down

# Start
docker compose up -d

# View live logs
docker compose logs -f smollm2

# Check status
docker compose ps
```

### 📊 Monitor Resource Usage

```bash
docker stats smollm2-llm_smollm2_1
```

> Expect ~3.5GB RAM usage at peak. Ideal for Raspberry Pi 5, M1 Mac, or cheap cloud VMs.

---

## 🚀 Bonus: Make It Even Better

### ➤ Add NGINX Reverse Proxy (For External Access)

```yaml
# Add to docker-compose.yml
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/conf.d/default.conf
    depends_on:
      - smollm2
```

Create `nginx.conf`:

```nginx
server {
    listen 80;
    location / {
        proxy_pass http://smollm2:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### ➤ Add Authentication (Basic Auth)

Use `htpasswd` and add to NGINX config:
```nginx
auth_basic "Restricted Access";
auth_basic_user_file /etc/nginx/.htpasswd;
```

Generate password:
```bash
echo $(htpasswd -nb username password) > .htpasswd
```

Mount `.htpasswd` into NGINX container.

---

## ✅ Final Checklist: Your Local LLM Is Ready!

| Task | Status |
|------|--------|
| ✅ Docker & Compose installed | ✔ |
| ✅ `docker-compose.yml` created | ✔ |
| ✅ `docker compose up -d` run | ✔ |
| ✅ Model auto-downloaded | ✔ |
| ✅ API accessible at `localhost:8080` | ✔ |
| ✅ Can send cURL prompts | ✔ |
| ✅ (Optional) Web UI working | ✔ |

---

## 🌐 Future-Proofing: Switch Models Easily

Want to try **Phi-3-mini** or **StarCoder2**?

Just change the `MODEL_ID`:

```yaml
MODEL_ID=microsoft/Phi-3-mini-4k-instruct
# or
MODEL_ID=bigcode/starcoder2-3b
```

No reinstallation needed — just `docker compose down && docker compose up -d`.

---

## 💬 Need Help? Join the Community

- 🐙 [Hugging Face SmolLM2 Discussion](https://huggingface.co/HuggingFaceH4/smollm2-1.7B)
- 🛠️ [Text Generation Inference Docs](https://github.com/huggingface/text-generation-inference)
- 💬 Ask questions on Reddit: r/MachineLearning or r/LocalLLaMA

---

> 🎉 **Congratulations!** You now have a fully functional, private, ultra-lightweight LLM running on your machine — no cloud, no cost, no compromises.  
> **Your code. Your data. Your AI.**

*Deployed with ❤️ by StarCoder-LLM Team — Open Source, Private First.*
```

---

### ✅ Copy-Paste Ready Summary (Quick Start)

```bash
mkdir starcoder-llm && cd starcoder-llm
cat > docker-compose.yml << 'EOF'
version: '3.8'
services:
  smollm2:
    image: ghcr.io/huggingface/text-generation-inference:latest
    ports:
      - "8080:8080"
    volumes:
      - ./models:/data
    environment:
      - MODEL_ID=HuggingFaceH4/smollm2-1.7B
      - MAX_INPUT_LENGTH=1024
      - MAX_TOTAL_TOKENS=2048
    restart: unless-stopped
EOF

docker compose up -d
curl http://localhost:8080/generate -X POST -H "Content-Type: application/json" -d '{"inputs":"Hello, how are you today?","parameters":{"max_new_tokens":50}}'
```

> 💡 Visit `http://localhost:8080` in browser to explore docs and test interactively.

---
