# Mobile Price Classification Dataset

This dataset is designed to predict and classify mobile phone price ranges based on their technical hardware specifications.

## Files
- `train_en.csv`: Training dataset with 2000 records. Clean numerical format ready for machine learning algorithms.
- `test_en.csv`: Test dataset with 1000 records.
- `train_en_labeled.csv`: Human-readable version with binary values ("Yes"/"No") and descriptive price ranges ("0 - Low Cost", "1 - Medium Cost", etc.) for exploratory data analysis (EDA).

---

## Features Data Dictionary

| Column Name | Type / Values | Description |
| :--- | :--- | :--- |
| `battery_power` | mAh | Total energy a battery can store in one time measured in mAh |
| `blue` | 0 = No, 1 = Yes | Has Bluetooth support |
| `clock_speed` | GHz | Speed at which microprocessor executes instructions |
| `dual_sim` | 0 = No, 1 = Yes | Has dual sim support |
| `fc` | Megapixels | Front Camera megapixels |
| `four_g` | 0 = No, 1 = Yes | Has 4G network support |
| `int_memory` | Gigabytes (GB) | Internal Memory capacity in Gigabytes |
| `m_dep` | Centimeters (cm) | Mobile Depth / thickness in cm |
| `mobile_wt` | Grams (g) | Weight of mobile phone |
| `n_cores` | Integer | Number of processor cores |
| `pc` | Megapixels | Primary (rear) Camera megapixels |
| `px_height` | Pixels (px) | Pixel Resolution Height |
| `px_width` | Pixels (px) | Pixel Resolution Width |
| `ram` | Megabytes (MB) | Random Access Memory (RAM) in Mega Bytes |
| `sc_h` | Centimeters (cm) | Screen Height of mobile in cm |
| `sc_w` | Centimeters (cm) | Screen Width of mobile in cm |
| `talk_time` | Hours | Longest time that a single battery charge will last in call |
| `three_g` | 0 = No, 1 = Yes | Has 3G network support |
| `touch_screen` | 0 = No, 1 = Yes | Has touch screen display |
| `wifi` | 0 = No, 1 = Yes | Has Wi-Fi connectivity |
| `price_range` | 0, 1, 2, 3 | **Target Variable:**<br>0: Low Cost<br>1: Medium Cost<br>2: High Cost<br>3: Very High Cost |

---

## Python Quick Start:
```python
import pandas as pd

df = pd.read_csv("en/train_en.csv")
print(df.head())
print(df.info())
```

