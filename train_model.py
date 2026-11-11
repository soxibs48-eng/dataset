import os
import json
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

def main():
    print("==================================================")
    print(" Mobil Telefonlar Narx Kategoriyasini O'qitish ")
    print("==================================================")

    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(base_dir, 'uz', 'train_uz.csv')

    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Ma'lumotlar to'plami topilmadi: {data_path}")

    df = pd.read_csv(data_path)
    X = df.drop('narx_toifasi', axis=1)
    y = df['narx_toifasi']

    # 80% train, 20% validation
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

    results = {}
    best_acc = 0.0
    best_model_name = ""
    best_model_pipeline = None

    for name, model in models.items():
        print(f"\nModel o'qitilmoqda: {name}...")
        model.fit(X_train, y_train)
        y_pred = model.predict(X_val)
        acc = accuracy_score(y_val, y_pred)
        results[name] = {
            "accuracy": round(float(acc), 4),
            "report": classification_report(y_val, y_pred, output_dict=True)
        }
        print(f"-> Aniqlik (Accuracy): {acc * 100:.2f}%")

        if acc > best_acc:
            best_acc = acc
            best_model_name = name
            best_model_pipeline = model

    print(f"\n Eng yaxshi model: {best_model_name} (Aniqlik: {best_acc * 100:.2f}%)")

    # Modellar uchun katalog
    models_dir = os.path.join(base_dir, 'models')
    os.makedirs(models_dir, exist_ok=True)

    # Eng yaxshi modelni saqlash
    model_file = os.path.join(models_dir, 'mobile_price_model.joblib')
    joblib.dump({
        'model': best_model_pipeline,
        'model_name': best_model_name,
        'accuracy': best_acc,
        'features': list(X.columns)
    }, model_file)
    print(f"✓ Model saqlandi: {model_file}")

    # Metrikani saqlash
    metrics_file = os.path.join(models_dir, 'model_metrics.json')
    with open(metrics_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"✓ Baholash natijalari saqlandi: {metrics_file}")

if __name__ == "__main__":
    main()

