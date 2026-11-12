# 📱 SmartPrice AI — Mobil Telefonlar Narxini Aniqlash Tizimi

> **Kutubxonalar:** `Scikit-learn`, `Pandas`, `kagglehub`, `joblib`  
> **Dataset manbasi:** [Kaggle - Mobile Price Classification](https://www.kaggle.com/datasets/iabhishekofficial/mobile-price-classification) (`iabhishekofficial/mobile-price-classification`)  
> **Tillar:** 🇺🇿 O'zbekcha, 🇷🇺 Русский, 🇬🇧 English  
> **AI Modeli Aniqligi:** **$96.50\%$** (Logistic Regression + StandardScaler)  
> **Jonli Valyuta Kursi:** O'zbekiston Respublikasi Markaziy Banki (**CBU API**) bilan integratsiya qilingan

---

## 🌟 Asosiy Imkoniyatlar

1. **Aniq Narx Hisoblash:** Har bir telefonning texnik parametrlariga qarab bozor narxini so'mda va dollarda aniq hisoblaydi.
2. **Jonli Dollar Kursi (API):** Markaziy Bankning rasmiy API'sidan real-vaqtda kursni oladi va telefon narxlarini doimiy yangilab turadi.
3. **Mashhur Telefon Modellari Katalogi:** iPhone 15 Pro Max, Galaxy S24 Ultra, Redmi Note 13, Galaxy A15 kabi 15+ mashhur model parametrlari tayyor kiritilgan.
4. **Nasiya / Muddatli To'lov Kalkulyatori:** 3, 6 va 12 oylik bo'lib to'lash rejasi va oylik summalarni ko'rsatadi.
5. **Afzallik va Kamchiliklar Tahlili (Pros & Cons):** Batareya chidamliligi, RAM tezligi va xotira yetarliligi bo'yicha sun'iy intellekt xulosasi.
6. **Oddiy va Pro Rejim:** Oddiy odamlar uchun 4 ta oson savol, mutaxassislar uchun to'liq texnik mikrosxema slayderlari.
7. **3 Tilda Ishlash:** O'zbekcha, Ruscha va Inglizcha to'liq lokalizatsiya.

---

## 📁 Loyiha Tuzilishi

```text
dataset/
│
├── index.html                   # Interaktiv zamonaviy AI veb-sayti (Jonli kurs + Model katalogi)
├── server.py                    # Mahalliy veb-server (http://localhost:8000)
├── main.py                      # Butun loyihani ishga tushiruvchi yagona Python pipeline
├── predict.py                   # Jonli CBU kursi va model katalogiga ega CLI dastur
├── predict_test.py              # 1000 ta test telefoni narxini bashorat qiluvchi skript
├── train_model.py               # Scikit-learn ML modellarini o'qitish va baholash
├── test_suite.py                # 6 ta avtomatlashtirilgan unit testlar
├── push_to_github.bat           # 1-klikda GitHub'ga yuklash (Windows script)
│
├── uz/                          # O'zbekcha datasetlar (train_uz.csv, test_uz.csv, tavsifli.csv, README_UZ.md)
├── ru/                          # Ruscha datasetlar (train_ru.csv, test_ru.csv, opisanie.csv, README_RU.md)
├── en/                          # Inglizcha datasetlar (train_en.csv, test_en.csv, labeled.csv, README_EN.md)
├── original/                    # Kaggle'dagi asl fayllar (train.csv, test.csv)
├── models/                      # Saqlangan model (mobile_price_model.joblib, model_metrics.json, model_web.json)
├── predictions/                 # Kaggle submission va 1000 ta test natijalari
└── .github/workflows/ci.yml     # GitHub Actions avtomatik CI/CD testlari
```

---

## ⚡ Qanday Ishga Tushirish Mumkin?

### 1. Veb-saytni ochish:
- Brauzerda ochish: 👉 [**http://localhost:8000**](http://localhost:8000)
- Yoki [`index.html`](index.html) faylini to'g'ridan-to'g'ri brauzerda oching.
- Veb-serverni ishga tushirish uchun:
  ```bash
  python server.py
  ```

### 2. Terminal (CLI) orqali telefon narxini bilish:
```bash
# Samsung Galaxy A15 narxi:
python predict.py --model "galaxy a15"

# iPhone 15 Pro Max narxi:
python predict.py --model "iphone 15 pro max"

# O'z parametrlaringiz bo'yicha:
python predict.py --ram 3800 --battery 5000 --camera 50 --storage 128
```

### 3. Butun loyihani qayta o'qitish:
```bash
python main.py
```

### 4. Testlarni tekshirish:
```bash
python test_suite.py
```

---

## 🚀 GitHub'ga Yuklash (Push):

1. **Avtomatik (Windows):** [`push_to_github.bat`](push_to_github.bat) faylini oching va GitHub havolangizni kiriting.
2. **Qo'lda buyruq orqali:**
   ```bash
   git remote add origin https://github.com/<USERNAME>/<REPO_NOMI>.git
   git branch -M main
   git push -u origin main
   ```

---

## 🌐 Bepul Internetga Joylash (GitHub Pages):
Loyiha hech qanday murakkab server talab qilmaydi. GitHub repozitoriyangizdagi:
`Settings -> Pages -> Branch: main -> Save` qilsangiz, loyiha internetda hamma uchun bepul va doimiy ishlab turadi!

---

## 📞 Bog'lanish va Muallif:
- **Telegram Bot:** [@telefonnarxx_bot](https://t.me/telefonnarxx_bot)
- **Telegram Profil:** [@Sbrjonv](https://t.me/Sbrjonv)
- **Telefon:** `+998 94 215 01 21`
- **GitHub:** [https://github.com/soxibs48-eng/dataset](https://github.com/soxibs48-eng/dataset)
