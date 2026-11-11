"""
================================================================================
Loyiha: Mobile Price Classification (Telefon Narx Kategoriyasini Aniqlash)
Kutubxonalar: Scikit-learn, Pandas
Dataset manbasi: Kaggle - Mobile Price Classification Dataset
Muallif: Kagglehub orqali avtomatlashtirilgan
Tillar: O'zbekcha (UZ), Ruscha (RU), Inglizcha (EN)
================================================================================
"""

import os
import kagglehub
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

def main():
    print("=" * 75)
    print("  LOYIHA: Mobil Telefonlar Narx Kategoriyasini Aniqlash (Classification)")
    print("  Kutubxonalar: Scikit-learn, Pandas")
    print("  Dataset manbasi: Kaggle - Mobile Price Classification Dataset")
    print("=" * 75)

    # ---------------------------------------------------------
    # 1. DATASETNI YUKLASH (KAGGLEHUB & PANDAS)
    # ---------------------------------------------------------
    print("\n[1/5] Kaggle'dan ma'lumotlar to'plami yuklab olinmoqda...")
    raw_path = kagglehub.dataset_download("iabhishekofficial/mobile-price-classification")
    print(f"✓ Dataset saqlangan joy: {raw_path}")

    train_path = os.path.join(raw_path, "train.csv")
    test_path = os.path.join(raw_path, "test.csv")

    df_train = pd.read_csv(train_path)
    df_test = pd.read_csv(test_path)

    print(f"✓ Train to'plami o'lchami: {df_train.shape[0]} qator, {df_train.shape[1]} ustun")
    print(f"✓ Test to'plami o'lchami: {df_test.shape[0]} qator, {df_test.shape[1]} ustun")

    # ---------------------------------------------------------
    # 2. PANDAS ORQALI STATISTIK VA KORRELYATSIYA TAHLILI
    # ---------------------------------------------------------
    print("\n[2/5] Pandas yordamida ma'lumotlar tahlili (EDA):")
    missing_vals = df_train.isnull().sum().sum()
    print(f"• Yetishmayotgan (null) qiymatlar soni: {missing_vals}")
    print(f"• Sinf taqsimoti (price_range):\n{df_train['price_range'].value_counts().sort_index()}")

    # Narx toifasiga eng kuchli ta'sir qiluvchi xususiyatlar
    correlations = df_train.corr()['price_range'].sort_values(ascending=False)
    print("\n• Narx toifasi (price_range) bilan eng yuqori korrelyatsiyaga ega parametrlar:")
    print(correlations[['ram', 'battery_power', 'px_width', 'px_height', 'int_memory']].to_string())

    # ---------------------------------------------------------
    # 3. SCIKIT-LEARN: DATASETNI BO'LISH VA MODELNI O'QITISH
    # ---------------------------------------------------------
    print("\n[3/5] Scikit-learn orqali modellarni o'qitish va baholash:")
    X = df_train.drop('price_range', axis=1)
    y = df_train['price_range']

    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    models = {
        "Logistic Regression": Pipeline([
            ('scaler', StandardScaler()),
            ('clf', LogisticRegression(max_iter=1000, random_state=42))
        ]),
        "Support Vector Classifier (Linear)": Pipeline([
            ('scaler', StandardScaler()),
            ('clf', SVC(kernel='linear', random_state=42))
        ]),
        "Random Forest Classifier": RandomForestClassifier(
            n_estimators=150, max_depth=12, random_state=42
        )
    }

    best_model_name = ""
    best_acc = 0.0
    best_pipeline = None

    for name, model in models.items():
        model.fit(X_train, y_train)
        y_pred = model.predict(X_val)
        acc = accuracy_score(y_val, y_pred)
        print(f"  -> {name}: Aniqlik = {acc * 100:.2f}%")
        if acc > best_acc:
            best_acc = acc
            best_model_name = name
            best_pipeline = model

    print(f"\n✓ Eng yaxshi natija ko'rsatgan model: {best_model_name} ({best_acc * 100:.2f}%)")

    # Batafsil hisobot (Classification Report)
    y_pred_best = best_pipeline.predict(X_val)
    print("\n• Scikit-learn Classification Report:")
    print(classification_report(y_val, y_pred_best, target_names=[
        "0 (Arzon / Low)", "1 (O'rtacha / Mid)", "2 (Qimmat / High)", "3 (Flagman / Very High)"
    ]))

    # ---------------------------------------------------------
    # 4. KASTOM TELEFON PARAMETRLARI BO'YICHA BASHORAT (TEST)
    # ---------------------------------------------------------
    print("[4/5] Yangi telefon parametrlari asosida narx toifasini aniqlash:")
    sample_phones = pd.DataFrame([
        {
            'name_uz': "A-Model (Hamyonbop)",
            'name_ru': "A-Модель (Бюджетный)",
            'name_en': "A-Model (Budget)",
            'battery_power': 800, 'blue': 0, 'clock_speed': 1.0, 'dual_sim': 0,
            'fc': 2, 'four_g': 0, 'int_memory': 8, 'm_dep': 0.8, 'mobile_wt': 160,
            'n_cores': 2, 'pc': 5, 'px_height': 300, 'px_width': 600, 'ram': 700,
            'sc_h': 10, 'sc_w': 4, 'talk_time': 5, 'three_g': 0, 'touch_screen': 0, 'wifi': 0
        },
        {
            'name_uz': "B-Model (O'rta toifa)",
            'name_ru': "B-Модель (Средний класс)",
            'name_en': "B-Model (Mid-range)",
            'battery_power': 1400, 'blue': 1, 'clock_speed': 1.8, 'dual_sim': 1,
            'fc': 8, 'four_g': 1, 'int_memory': 32, 'm_dep': 0.5, 'mobile_wt': 145,
            'n_cores': 4, 'pc': 12, 'px_height': 720, 'px_width': 1280, 'ram': 2300,
            'sc_h': 12, 'sc_w': 5, 'talk_time': 12, 'three_g': 1, 'touch_screen': 1, 'wifi': 1
        },
        {
            'name_uz': "C-Model (Flagman)",
            'name_ru': "C-Модель (Флагман)",
            'name_en': "C-Model (Flagship)",
            'battery_power': 1950, 'blue': 1, 'clock_speed': 2.8, 'dual_sim': 1,
            'fc': 16, 'four_g': 1, 'int_memory': 64, 'm_dep': 0.3, 'mobile_wt': 130,
            'n_cores': 8, 'pc': 20, 'px_height': 1440, 'px_width': 2560, 'ram': 3900,
            'sc_h': 15, 'sc_w': 7, 'talk_time': 18, 'three_g': 1, 'touch_screen': 1, 'wifi': 1
        }
    ])

    feature_cols = list(X.columns)
    sample_preds = best_pipeline.predict(sample_phones[feature_cols])

    labels_uz = {0: "0 - Hamyonbop (Arzon)", 1: "1 - O'rta toifa", 2: "2 - Qimmat toifa", 3: "3 - Flagman (Juda qimmat)"}
    labels_ru = {0: "0 - Бюджетный класс", 1: "1 - Средний класс", 2: "2 - Высокий класс", 3: "3 - Флагман"}
    labels_en = {0: "0 - Low Cost (Budget)", 1: "1 - Medium Cost", 2: "2 - High Cost", 3: "3 - Very High Cost (Flagship)"}

    for i, p_class in enumerate(sample_preds):
        print(f"\n  📱 {sample_phones.loc[i, 'name_uz']} | RAM: {sample_phones.loc[i, 'ram']} MB | Batareya: {sample_phones.loc[i, 'battery_power']} mAh")
        print(f"     -> O'zbekcha: {labels_uz[p_class]}")
        print(f"     -> Русский:   {labels_ru[p_class]}")
        print(f"     -> English:   {labels_en[p_class]}")

    # ---------------------------------------------------------
    # 5. KAGGLE TEST.CSV TO'PLAMINI BASHORAT QILISH
    # ---------------------------------------------------------
    print("\n[5/5] Kaggle test.csv (1000 ta telefon) uchun bashoratlar hisoblanmoqda...")
    X_test_input = df_test.drop('id', axis=1)[feature_cols]
    test_preds = best_pipeline.predict(X_test_input)

    output_dir = "predictions"
    os.makedirs(output_dir, exist_ok=True)
    submission_file = os.path.join(output_dir, "submission_kaggle.csv")

    sub_df = pd.DataFrame({
        'id': df_test['id'],
        'price_range': test_preds
    })
    sub_df.to_csv(submission_file, index=False)
    print(f"✓ Kaggle submission tayyorlandi: {submission_file}")
    print(f"• Test to'plami taqsimoti:\n{sub_df['price_range'].value_counts().sort_index()}")

    print("\n" + "=" * 75)
    print("  Barcha bosqichlar muvaffaqiyatli yakunlandi!")
    print("=" * 75)

if __name__ == "__main__":
    main()

