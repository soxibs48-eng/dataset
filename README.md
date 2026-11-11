# Mobile Price Classification Dataset (O'zbek / Русский / English)

> **Kutubxonalar:** `Scikit-learn`, `Pandas`, `kagglehub`  
> **Dataset manbasi:** [Kaggle - Mobile Price Classification Dataset](https://www.kaggle.com/datasets/iabhishekofficial/mobile-price-classification) (`iabhishekofficial/mobile-price-classification`)

Ushbu loyiha Kaggle'dagi mashhur **"Mobile Price Classification"** ma'lumotlar to'plamini yuklab olib, **Pandas** va **Scikit-learn** kutubxonalari yordamida qayta ishlaydi, 3 ta tilda (**O'zbek**, **Rus**, **Ingliz**) tayyorlaydi hamda telefonlarning texnik parametrlari (RAM, batareya, kamera) asosida narx toifasini **96.5% aniqlikda** tasniflovchi Machine Learning modelini taqdim etadi.

---

## ⚡ Bitta Buyruq Bilan Butun Loyihani Ishga Tushirish

```bash
python main.py
```
*(Ushbu buyruq datasetni yuklaydi, Pandas orqali tahlil qiladi, Scikit-learn orqali modellarni o'qitadi, yangi telefonlarni 3 tilda tasniflaydi va test to'plami bashoratlarini saqlaydi).*


---

## 📁 Loyiha Strukturasi (Project Structure)

```text
dataset/
│
├── original/                   # Kaggle'dan olingan asl fayllar
│   ├── train.csv
│   └── test.csv
│
├── uz/                         # O'zbek tili (Uzbek language)
│   ├── train_uz.csv            # ML uchun tayyor (raqamli ustunlar)
│   ├── test_uz.csv
│   ├── train_uz_tavsifli.csv   # EDA va vizualizatsiya uchun tavsifli
│   └── README_UZ.md            # O'zbekcha to'liq qo'llanma
│
├── ru/                         # Rus tili (Русский язык)
│   ├── train_ru.csv            # Готов для ML (числовые значения)
│   ├── test_ru.csv
│   ├── train_ru_opisanie.csv   # С текстовыми описаниями для EDA
│   └── README_RU.md            # Подробная документация на русском
│
├── en/                         # Ingliz tili (English language)
│   ├── train_en.csv            # Numerical format for ML models
│   ├── test_en.csv
│   ├── train_en_labeled.csv    # Labeled format for EDA
│   └── README_EN.md            # English documentation
│
├── metadata_features.json      # Barcha ustunlarning 3 tildagi lug'ati (JSON formatda)
├── prepare_dataset.py          # Datasetni yuklab oluvchi va qayta ishlovchi script
└── README.md                   # Asosiy ma'lumotnoma
```

---

## 📊 Ustunlar Taqqoslash Jadvali (Column Comparison Table)

| Asl nomi (EN) | O'zbekcha (UZ) | Русский (RU) | Qiymatlar / Birlik |
| :--- | :--- | :--- | :--- |
| `battery_power` | `akkumulyator_quvvati` | `emkost_batarei_mach` | mAh (Akkumulyator quvvati) |
| `blue` | `bluetooth` | `bluetooth` | 0 = Yo'q / Нет / No, 1 = Bor / Есть / Yes |
| `clock_speed` | `protsessor_tezligi` | `taktovaya_chastota_ggts` | GHz (Chastota) |
| `dual_sim` | `ikkita_sim` | `dve_sim_karty` | 0 = Yo'q / Нет / No, 1 = Bor / Есть / Yes |
| `fc` | `old_kamera_mp` | `front_kamera_mp` | MP (Old kamera megapikseli) |
| `four_g` | `tort_g` | `four_g` | 0 = Yo'q / Нет / No, 1 = Bor / Есть / Yes |
| `int_memory` | `ichki_xotira_gb` | `vstroennaya_pamyat_gb` | GB (Ichki xotira) |
| `m_dep` | `qalinligi_sm` | `tolschina_sm` | sm (Telefon qalinligi) |
| `mobile_wt` | `telefon_vazni_gr` | `ves_telefona_gr` | g (Telefon og'irligi) |
| `n_cores` | `yadro_soni` | `kolichestvo_yader` | CPU yadrolar soni |
| `pc` | `asosiy_kamera_mp` | `osnovnaya_kamera_mp` | MP (Asosiy kamera) |
| `px_height` | `piksel_balandligi` | `vysota_razresheniya_px` | px (Ekran balandligi pikselda) |
| `px_width` | `piksel_kengligi` | `shirina_razresheniya_px` | px (Ekran kengligi pikselda) |
| `ram` | `ram_mb` | `ram_mb` | MB (Operativ xotira) |
| `sc_h` | `ekran_balandligi_sm` | `vysota_ekrana_sm` | sm (Ekran balandligi) |
| `sc_w` | `ekran_kengligi_sm` | `shirina_ekrana_sm` | sm (Ekran kengligi) |
| `talk_time` | `gaplashish_vaqti_soat` | `vremya_razgovora_ch` | Soat (So'zlashuv vaqti) |
| `three_g` | `uch_g` | `three_g` | 0 = Yo'q / Нет / No, 1 = Bor / Есть / Yes |
| `touch_screen` | `sensorli_ekran` | `sensornyy_ekran` | 0 = Yo'q / Нет / No, 1 = Bor / Есть / Yes |
| `wifi` | `wifi` | `wifi` | 0 = Yo'q / Нет / No, 1 = Bor / Есть / Yes |
| **`price_range`** | **`narx_toifasi`** | **`diapazon_cen`** | **0: Arzon, 1: O'rtacha, 2: Qimmat, 3: Juda qimmat** |

---

## 🚀 Foydalanish (Qo'llanma)

### 1. Parametrlarga qarab narx toifasini aniqlash (CLI):
Terminal orqali telefon parametrlarini kiritib narx toifasini bilish:

```bash
# O'zbek tilida:
python predict.py --lang uz --ram 3800 --battery 4000 --camera 20 --storage 64

# Rus tilida:
python predict.py --lang ru --ram 1800 --battery 1500 --camera 12 --storage 32

# Ingliz tilida:
python predict.py --lang en --ram 800 --battery 1000 --camera 5 --storage 16

# Interaktiv rejimda ishga tushirish (savol-javob orqali):
python predict.py --lang uz
```

### 2. Veb-interfeys orqali vizual tahlil (Web UI):
Brauzeringizda [`index.html`](file:///c:/Users/HP%20PC/21/21.10/dataset/index.html) faylini oching. Slayderlar (RAM, Akkumulyator, Kamera va h.k.) yordamida qiymatlarni o'zgartirishingiz bilan AI modeli real vaqtda narx toifasi va ehtimolliklarini ko'rsatadi.

### 3. Modelni qayta o'qitish:
```bash
python train_model.py
```
Model natijasi: **96.50% aniqlik** (Logistic Regression / Scaler).


