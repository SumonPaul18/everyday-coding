আপনি ছোট এবং ফ্রী ওপেন সোর্স LLM (Large Language Models) Docker Compose দিয়ে লোকাল বা সার্ভার এনভায়রনমেন্টে চালাতে চাইলে নিচে ধাপে ধাপে গাইডলাইন দেওয়া হলো। এতে কিছু ছোটমাপের জনপ্রিয় LLM মডেল এবং তাদের ডকার কম্পোজ সেটআপ উদাহরণ আছেঃ

## ১. ছোট ওপেন সোর্স LLM গুলোর Docker Compose সেটআপের সাধারণ গাইডলাইন

### প্রয়োজনীয়তা
- মেশিনে Docker এবং Docker Compose ইনস্টল থাকতে হবে।
- 16GB+ RAM এবং ভালো GPU থাকলে মডেল চালানো সুবিধাজনক হয়।
- ছোট মডেল যেমন 125M থেকে 7B প্যারামিটার মডেল আনতে রিসোর্স তুলনামূলক কম লাগে।

## ২. ছোট বা ফ্রী ওপেন-সোর্স LLM এবং Docker Compose উদাহরণ

### (ক) **smolLM2** (সর্বনিম্ন মেমোরি দরকার, আকার 135M)

```yaml
version: '3.8'
services:
  smollm2:
    image: smollm2/smollm2:latest
    container_name: smollm2_container
    ports:
      - "11434:11434"
    restart: unless-stopped
```

*ব্যবহার:*

- চালাতে: `docker-compose up -d`
- ভিজিট করুন: `http://localhost:11434` (API বা ভিজ্যুয়াল ইন্টারফেস থাকতে পারে)

### (খ) **StarCoder 1B এবং 3B মডেল** (কোডিং বিশেষায়িত)

```yaml
version: '3.8'
services:
  starcoder-llm:
    image: starcoder/llm:latest
    container_name: starcoder_llm
    ports:
      - "11434:11434"
    restart: unless-stopped
    volumes:
      - ./models:/models
```

*ব্যবহার:*

- আপনার লোকাল মডেল ফাইল `./models` ফোল্ডারে রাখুন।
- রান: `docker-compose up -d`
- পরবর্তীতে VS Code-এর AI এক্সটেনশনে এন্ডপয়েন্ট দিন: `http://localhost:11434`

### (গ) **Phi-3 (7B)** মডেল (দ্রুত চালানো যায়, ভালো পারফরম্যান্স)

```yaml
version: '3.8'
services:
  phi3:
    image: phi3/llm:latest
    container_name: phi3_llm
    ports:
      - "11435:11434"
    restart: unless-stopped
    volumes:
      - ./phi3-model:/models
```

*ব্যবহার:*

- মডেল লোকালি ডাউনলোড ও `./phi3-model` এখানে রাখুন।
- কমান্ড: `docker-compose up -d`
- আউটপুট পোর্ট: 11435 (Localhost)
- VS Code বা অন্য যেকোনো ক্লায়েন্টে কানেক্ট করুন।

### (ঘ) **Mistral 7B** (কম রিসোর্সে ভালো পারফরম্যান্স)

```yaml
version: '3.8'
services:
  mistral7b:
    image: mistral/mistral7b:latest
    container_name: mistral7b_llm
    ports:
      - "11436:11434"
    restart: unless-stopped
    volumes:
      - ./mistral7b-model:/models
```

*ব্যবহার:*

- লোকাল মডেল `./mistral7b-model` ডিরেক্টরিতে রাখুন।
- রান করুন `docker-compose up -d`
- পোর্ট নম্বর 11436 ও 11434 ম্যাপ করা হয়েছে।

### (ঙ) **Vicuna 7B** (চ্যাটবট ও কোড সহায়ক)

```yaml
version: '3.8'
services:
  vicuna:
    image: vicuna/llm:latest
    container_name: vicuna_llm
    ports:
      - "11437:11434"
    restart: unless-stopped
    volumes:
      - ./vicuna-model:/models
```

*ব্যবহার:*

- মডেল রাখুন `./vicuna-model`
- Run: `docker-compose up -d`
- 11437 পোর্টে API রয়েছে।

## ৩. Ollama + Open WebUI - Docker Compose দিয়ে খুব সহজ ও জনপ্রিয় লোকাল LLM ও UI সেটআপ

```yaml
version: "3"

services:

  ollama:
    image: ollama/ollama:latest
    container_name: ollama
    ports:
      - "11434:11434"
    volumes:
      - ollama-data:/root/.ollama
    restart: unless-stopped

  open-webui:
    image: ghcr.io/open-webui/open-webui:main
    container_name: open-webui
    depends_on:
      - ollama
    ports:
      - "3000:8080"
    volumes:
      - open-webui-data:/app/backend/data
    environment:
      - OLLAMA_BASE_URL=http://ollama:11434
      - WEBUI_SECRET_KEY=
    restart: unless-stopped

volumes:
  ollama-data: {}
  open-webui-data: {}
```

*ব্যবহার:*

- চালান: `docker-compose up -d`
- ব্রাউজারে গিয়ে `http://localhost:3000` ওপেন করুন
- Open WebUI ড্যাশবোর্ড থেকে ছোট মডেল (smollm2 ইত্যাদি) ডাউনলোড ও চালাতে পারবেন।

## ৪. সাধারণ Docker Compose রান কমান্ড:

```bash
docker-compose up -d
```

কন্টেইনার বন্ধ করার জন্য:

```bash
docker-compose down
```

## ৫. VS Code বা অন্য IDE-তে লোকাল মডেল সংযোগ

- Docker container যদি লোকাল হোস্টে 11434 পোর্টে চলে:
- এক্সটেনশন সেটিংসে মডেল এন্ডপয়েন্ট দিন:  
  `http://localhost:11434`
- কোড প্রম্পট দিন, কোড জেনারেট বা এআই সাহায্য নিন।

## অতিরিক্ত টিপস:

- মডেলের আকার এবং মেশিনের র‍্যাম দেখে মডেল নির্বাচন করুন।
- 7B বা ছোট মডেল 16GB র‍্যামেও ভালো চলে।
- বড় মডেলের জন্য GPU এবং বেশি RAM প্রয়োজন।
- মডেল quantization করে র‍্যাম কমানো যায়।
- Docker এর volumes ব্যবহার করে মডেল ডেটা সেভ করুন যাতে রি-ডাউনলোডের প্রয়োজন না হয়।

আপনি চাইলে নির্দিষ্ট মডেল এর জন্য আরও কাস্টমাইজড docker-compose.yml ও VS Code সেটআপ গাইড পেতে পারেন।  
এছাড়া Ollama + Open WebUI সেটআপ করলে খুব সহজেই ছোট মডেল চালানো যায় GUI সহ।  

প্রয়োজন হলে আমি ছোট মডেল smollm2 বা StarCoder দিয়ে সম্পূর্ণ ইনস্টলেশন ভিডিও বা টিউটোরিয়াল লিঙ্কসহ দিতে পারি।  

---

[1](https://langfuse.com/self-hosting/docker-compose)
[2](https://geshan.com.np/blog/2025/02/ollama-docker-compose/)
[3](https://www.docker.com/blog/llm-docker-for-local-and-hugging-face-hosting/)
[4](https://www.docker.com/blog/run-llms-locally/)
[5](https://www.datacamp.com/tutorial/deploy-llm-applications-using-docker)
[6](https://github.com/ivangabriele/docker-llm/blob/main/docker-compose.yml)
[7](https://collabnix.com/how-to-run-open-source-llms-locally-with-ollama-and-docker-llama3-1-phi3-mistral-gemma2/)
[8](https://www.youtube.com/watch?v=3p2uWjFyI1U)
[9](https://dev.to/docker/from-zero-to-local-llm-a-developers-guide-to-docker-model-runner-4oi2)
