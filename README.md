# MiniMed Bot - PythonAnywhere Deployment Guide

## 📦 Fayllar (6 ta fayl)

```
minimed/
├── minimed_bot.py              ✅ ASOSIY BOT
├── minimed_settings.py         ✅ Sozlamalar
├── minimed_ai_service.py       ✅ AI Service
├── minimed_prompts.py          ✅ Prompts
├── minimed_diseases_db.py      ✅ Kasalliklar bazasi
├── requirements.txt            ✅ Dependencies
└── .env                        ✅ Konfiguratsiya
```

## 🚀 PythonAnywhere'da O'rnatish

### 1. Virtual Environment
```bash
mkvirtualenv minimed-bot --python=3.10
workon minimed-bot
```

### 2. Dependencies
```bash
pip install -r requirements.txt
```

### 3. .env Fayli
```env
TELEGRAM_BOT_TOKEN=sizning_token
GROQ_API_KEY=sizning_groq_key
ADMIN_USERNAMES=Rakh_matova19,CEO_Bekhruz
APP_ENV=production
APP_DEBUG=False
FORCE_SUBSCRIBE_CHANNELS=https://t.me/+YVKl_R-uUSwxNGIy,https://t.me/+6CYVuWlbS803Y2Vi
```

### 4. Ishga Tushirish
```bash
cd /home/yourusername/minimed
python minimed_bot.py
```

### 5. Always-On Task (Pullik)
Dashboard → Always-on tasks → Add task:
```
/home/yourusername/.virtualenvs/minimed-bot/bin/python /home/yourusername/minimed/minimed_bot.py
```

## ✅ Test

Telegram: @Mini_Med_bot
```
/start
🩺 Tekshirish
💬 Doktor Rayhona
📚 Ma'lumotlar
🚨 Shoshilinch
```

## 📊 Loglar

```bash
tail -f /home/yourusername/minimed/logs/bot.log
```

## 🎯 Xususiyatlar

✅ Majburiy obuna tizimi
✅ Alomatlarni raqam bilan tanlash (1-8)
✅ "Tanlashni tugatish" tugmasi
✅ AI tashxis (Groq API)
✅ 1000+ kasallik bazasi
✅ Chat Doktor Rayhona bilan
✅ Shoshilinch yordam
