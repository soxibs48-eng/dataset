import os
import joblib
import pandas as pd

def main():
    print("==================================================")
    print(" Test To'plami Uchun Bashoratlarni Yaratish ")
    print("==================================================")

    base_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(base_dir, 'models', 'mobile_price_model.joblib')
    
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model topilmadi: {model_path}. Avval train_model.py ni ishga tushiring.")

    model_data = joblib.load(model_path)
    pipeline = model_data['model']
    features = model_data['features']

    # 1. O'zbekcha test to'plamini o'qish
    test_uz_path = os.path.join(base_dir, 'uz', 'test_uz.csv')
    df_test_uz = pd.read_csv(test_uz_path)
    
    X_test_uz = df_test_uz[features]
    predictions = pipeline.predict(X_test_uz)

    # Chiqish papkasi
    preds_dir = os.path.join(base_dir, 'predictions')
    os.makedirs(preds_dir, exist_ok=True)

    # A) Kaggle submission formati (id, price_range)
    df_submission = pd.DataFrame({
        'id': df_test_uz['id'],
        'price_range': predictions
    })
    sub_path = os.path.join(preds_dir, 'submission_kaggle.csv')
    df_submission.to_csv(sub_path, index=False)
    print(f"✓ Kaggle submission fayli yaratildi: {sub_path}")

    # B) O'zbekcha to'liq bashorat fayli
    cat_names_uz = {
        0: "0 - Hamyonbop / Arzon narx",
        1: "1 - O'rta-quyi toifa",
        2: "2 - O'rta-yuqori toifa",
        3: "3 - Flagman / Juda qimmat"
    }
    df_pred_uz = df_test_uz.copy()
    df_pred_uz['bashorat_qilingan_narx_toifasi'] = predictions
    df_pred_uz['narx_toifasi_tavsifi'] = df_pred_uz['bashorat_qilingan_narx_toifasi'].map(cat_names_uz)
    uz_sub_path = os.path.join(preds_dir, 'test_predictions_uz.csv')
    df_pred_uz.to_csv(uz_sub_path, index=False)
    print(f"✓ O'zbekcha bashoratlar yaratildi: {uz_sub_path}")

    # C) Ruscha to'liq bashorat fayli
    cat_names_ru = {
        0: "0 - Бюджетный класс (Низкая цена)",
        1: "1 - Средне-бюджетный класс (Средняя цена)",
        2: "2 - Средне-высокий класс (Высокая цена)",
        3: "3 - Флагманский класс (Очень высокая цена)"
    }
    test_ru_path = os.path.join(base_dir, 'ru', 'test_ru.csv')
    df_test_ru = pd.read_csv(test_ru_path)
    df_pred_ru = df_test_ru.copy()
    df_pred_ru['prognoziruemyy_diapazon_cen'] = predictions
    df_pred_ru['opisanie_cenovoy_kategorii'] = df_pred_ru['prognoziruemyy_diapazon_cen'].map(cat_names_ru)
    ru_sub_path = os.path.join(preds_dir, 'test_predictions_ru.csv')
    df_pred_ru.to_csv(ru_sub_path, index=False)
    print(f"✓ Ruscha bashoratlar yaratildi: {ru_sub_path}")

    # D) Inglizcha to'liq bashorat fayli
    cat_names_en = {
        0: "0 - Low Cost (Budget tier)",
        1: "1 - Medium Cost (Mid-tier)",
        2: "2 - High Cost (Upper mid-tier)",
        3: "3 - Very High Cost (Flagship tier)"
    }
    test_en_path = os.path.join(base_dir, 'en', 'test_en.csv')
    df_test_en = pd.read_csv(test_en_path)
    df_pred_en = df_test_en.copy()
    df_pred_en['predicted_price_range'] = predictions
    df_pred_en['price_range_label'] = df_pred_en['predicted_price_range'].map(cat_names_en)
    en_sub_path = os.path.join(preds_dir, 'test_predictions_en.csv')
    df_pred_en.to_csv(en_sub_path, index=False)
    print(f"✓ Inglizcha bashoratlar yaratildi: {en_sub_path}")

    # Statistika chiqarish
    counts = pd.Series(predictions).value_counts().sort_index()
    print("\n📊 Test to'plamidagi 1000 ta telefonning narx toifalari taqsimoti:")
    for cat_id, cnt in counts.items():
        pct = (cnt / len(predictions)) * 100
        print(f"  {cat_names_uz[cat_id]}: {cnt} ta ({pct:.1f}%)")

if __name__ == "__main__":
    main()

