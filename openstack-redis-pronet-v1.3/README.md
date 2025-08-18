# ☁️ CloudLab - OpenStack Cloud Management Dashboard

A modern, modular Flask web application for managing OpenStack cloud resources with Google & Email authentication, automated project provisioning, email confirmation, password reset, and Redis-backed session management.

## 🎯 উদ্দেশ্য

এই প্রজেক্টটি এমন একটি প্ল্যাটফর্ম তৈরি করে যেখানে ব্যবহারকারীরা সহজেই একটি OpenStack ক্লাউড একাউন্ট তৈরি করতে পারে, এবং তাদের জন্য স্বয়ংক্রিয়ভাবে একটি আইসোলেটেড প্রজেক্ট, নেটওয়ার্ক, রাউটার এবং সাবনেট তৈরি করা হয়। ভবিষ্যতে ক্রেডিট সিস্টেম, বিলিং, কোয়োটা ম্যানেজমেন্ট এবং এডমিন প্যানেল যোগ করা হবে।

---

## 🧱 প্রজেক্ট কাঠামো (Project Structure)

```
openstack-flask-gmsso-redis-v2/
├── config/               # কনফিগারেশন ফাইল
│   ├── settings.py       # Flask, Mail, Redis, OpenStack
│   └── constants.py      # ক্রেডিট, কোয়োটা ডিফল্ট
├── models/               # ডাটাবেজ মডেল
│   └── user.py           # User, OAuth, Credits, Quota
├── auth/                 # অথেনটিকেশন সিস্টেম
│   ├── routes.py         # /signup, /login, /reset
│   ├── forms.py          # Flask-WTF ফর্ম
│   └── utils.py          # মেইল, টোকেন, ভেরিফিকেশন
├── openstack/            # OpenStack ইন্টিগ্রেশন
│   ├── provision.py      # অটো-প্রভিশন
│   ├── client.py         # OpenStack কানেকশন
│   └── operations.py     # ভবিষ্যত VM/Network ম্যানেজমেন্ট
├── billing/              # ক্রেডিট সিস্টেম
│   └── credit.py         # ফ্রি ক্রেডিট, ডেডাকশন
├── dashboard/            # লগইন-প্রটেক্টেড পেজ
│   └── routes.py         # /dashboard, /profile
├── templates/            # HTML টেমপ্লেট (Jinja2)
├── static/               # CSS, JS, Images
├── clouds.yaml           # OpenStack ক্রেডেনশিয়াল
├── .env.example          # কনফিগ টেমপ্লেট
├── requirements.txt      # প্যাকেজ
├── wsgi.py               # এন্ট্রি পয়েন্ট
├── config.py             # ডাটাবেজ সেটআপ
└── README.md
```

---

## 🚀 স্থাপন নির্দেশনা (Setup Guide)

### 🔧 প্রয়োজনীয়তা
- Python 3.8+
- Redis Server
- Gmail অ্যাকাউন্ট (App Password)
- OpenStack এক্সেস
- `python-dotenv`, `openstacksdk`

---

### 🖥️ লোকাল হোস্টে রান করার ধাপ

#### 1. ভার্চুয়াল এনভায়রনমেন্ট তৈরি করুন

```bash
python -m venv venv
source venv/bin/activate
```

#### 2. ডিপেনডেন্সি ইনস্টল করুন

```bash
pip install -r requirements.txt
```

#### 3. Redis সার্ভার চালু করুন

```bash
# Ubuntu/Debian
sudo systemctl start redis

# macOS (Homebrew)
redis-server
```

#### 4. `.env` ফাইল তৈরি করুন

```bash
cp .env.example .env
```

`.env` ফাইল এডিট করুন এবং আপনার ক্রেডেনশিয়াল দিন।

#### 5. `clouds.yaml` ফাইল রাখুন

আপনার প্রজেক্ট রুটে `clouds.yaml` ফাইলটি রাখুন।

#### 6. ডাটাবেজ তৈরি করুন

```bash
python config.py
```

#### 7. সার্ভার রান করুন

```bash
python wsgi.py
```

> ব্রাউজারে যান: [http://localhost:5000](http://localhost:5000)

---

### 🐳 Docker ব্যবহার করে রান করুন

#### 1. ডকার কম্পোজ দিয়ে চালান

```bash
docker-compose up --build
```

#### 2. সার্ভিস
- Web App: `http://localhost:5000`
- Redis: `redis://localhost:6379`

> `.env` ফাইল আছে নিশ্চিত করুন।

---

## 🔐 কনফিগারেশন

| ভেরিয়েবল | বিবরণ |
|----------|--------|
| `SECRET_KEY` | Flask সিক্রেট কী |
| `GOOGLE_CLIENT_ID` | Google OAuth 2.0 Client ID |
| `GOOGLE_CLIENT_SECRET` | Google OAuth 2.0 Client Secret |
| `MAIL_USERNAME` | Gmail ইমেইল |
| `MAIL_PASSWORD` | Gmail App Password |
| `REDIS_HOST` | Redis সার্ভার IP (লোকালে `127.0.0.1`) |
| `DATABASE_URL` | SQLite বা PostgreSQL URI |

---

## 🌐 রুটস (Routes)

| রুট | বিবরণ |
|-----|--------|
| `/auth/signup` | নতুন ইউজার রেজিস্ট্রেশন |
| `/auth/login` | লগইন (ইমেইল বা Google) |
| `/auth/logout` | লগআউট |
| `/dashboard` | ড্যাশবোর্ড (লগইন প্রয়োজন) |
| `/profile` | প্রোফাইল পেজ |
| `/settings` | সেটিংস পেজ |

---

## 💡 ভবিষ্যত বৈশিষ্ট্য (Roadmap)

- ✅ অটো প্রভিশনিং (বর্তমানে আছে)
- 💰 ক্রেডিট সিস্টেম (ফ্রি ক্রেডিট, পেমেন্ট)
- 🔐 কোয়োটা ম্যানেজমেন্ট (VM, RAM, Disk)
- 📊 এডমিন ড্যাশবোর্ড
- 💳 Stripe/PayPal ইন্টিগ্রেশন
- 📱 API এন্ডপয়েন্ট (Flask-RESTful)
- 📅 বিলিং ও সাবস্ক্রিপশন

---

## 🤝 অবদান (Contributing)

আপনি চাইলে পুল রিকুয়েস্ট বা ইস্যু খুলতে পারেন। আমরা সব ধরনের অবদান স্বাগত জানাই।

---

## 📄 লাইসেন্স

MIT License - দেখুন `LICENSE` ফাইল।

---

## ✉️ যোগাযোগ

**Sumon Paul**  
Email: sumonpaul267@gmail.com  
Project: CloudLab - OpenStack Dashboard  
Version: v2.0 (Modular, Scalable, Future-Ready)
```

---
