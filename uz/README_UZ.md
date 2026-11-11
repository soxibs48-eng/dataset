# Telefon Narxlarini Tasniflash (Mobile Price Classification) Ma'lumotlar To'plami

Ushbu to'plam mobil telefonlarning texnik xususiyatlariga qarab ularning narx toifasini aniqlash (Machine Learning / Data Science) uchun mo'ljallangan.

## Fayllar
- `train_uz.csv`: O'rgatish (train) to'plami (2000 ta qator). Barcha ustun nomlari o'zbek tiliga tarjima qilingan va qiymatlar raqamli ko'rinishda (ML modellari uchun tayyor).
- `test_uz.csv`: Test to'plami (1000 ta qator).
- `train_uz_tavsifli.csv`: Tushunish va tahlil (EDA) uchun qulaylashtirilgan to'plam (0 va 1 qiymatlar "Bor"/"Yo'q", narx toifalari "Arzon", "O'rtacha", "Qimmat", "Juda qimmat" deb yozilgan).

---

## Ustunlar Tavsifi (Lug'at)

| Ustun nomi (O'zbekcha) | Asl nomi (Inglizcha) | O'lchov birligi / Qiymatlar | Tavsif |
| :--- | :--- | :--- | :--- |
| `akkumulyator_quvvati` | `battery_power` | mAh | Akkumulyatorning bir marta to'liq quvvatlangandagi umumiy quvvati |
| `bluetooth` | `blue` | 0 = Yo'q, 1 = Bor | Bluetooth texnologiyasi mavjudligi |
| `protsessor_tezligi` | `clock_speed` | GHz | Mikroprotsessor chastotasi va ishlash tezligi |
| `ikkita_sim` | `dual_sim` | 0 = Yo'q, 1 = Bor | Ikkita SIM-karta qo'llab-quvvatlanishi |
| `old_kamera_mp` | `fc` | Megapiksel (MP) | Old (selfi) kamera ruxsati |
| `tort_g` | `four_g` | 0 = Yo'q, 1 = Bor | 4G aloqa tarmog'i mavjudligi |
| `ichki_xotira_gb` | `int_memory` | Gigabayt (GB) | Telefonning ichki doimiy xotira sig'imi |
| `qalinligi_sm` | `m_dep` | Santimetr (sm) | Telefon korpusining qalinligi |
| `telefon_vazni_gr` | `mobile_wt` | Gramm (g) | Telefonning umumiy og'irligi |
| `yadro_soni` | `n_cores` | Soni | Markaziy protsessor (CPU) yadrolari soni |
| `asosiy_kamera_mp` | `pc` | Megapiksel (MP) | Asosiy (orqa) kamera ruxsati |
| `piksel_balandligi` | `px_height` | Piksel (px) | Ekran o'lchami balandligi |
| `piksel_kengligi` | `px_width` | Piksel (px) | Ekran o'lchami kengligi |
| `ram_mb` | `ram` | Megabayt (MB) | Tezkor xotira (RAM) hajmi |
| `ekran_balandligi_sm` | `sc_h` | Santimetr (sm) | Telefon ekranining jismoniy balandligi |
| `ekran_kengligi_sm` | `sc_w` | Santimetr (sm) | Telefon ekranining jismoniy kengligi |
| `gaplashish_vaqti_soat` | `talk_time` | Soat | To'liq quvvat bilan to'xtovsiz gaplashish mumkin bo'lgan maksimal vaqt |
| `uch_g` | `three_g` | 0 = Yo'q, 1 = Bor | 3G aloqa tarmog'i mavjudligi |
| `sensorli_ekran` | `touch_screen` | 0 = Yo'q, 1 = Bor | Sensorli (touch screen) ekran mavjudligi |
| `wifi` | `wifi` | 0 = Yo'q, 1 = Bor | Wi-Fi simsiz aloqasi mavjudligi |
| `narx_toifasi` | `price_range` | 0, 1, 2, 3 | **Maqsadli o'zgaruvchi (Target):**<br>0: Arzon narx (Low cost)<br>1: O'rtacha narx (Medium cost)<br>2: Qimmat narx (High cost)<br>3: Juda qimmat / Premium (Very high cost) |

---

## Python orqali o'qish namunasi:
```python
import pandas as pd

df = pd.read_csv("uz/train_uz.csv")
print(df.head())
print(df.info())
```

