import os
import unittest
import pandas as pd
import joblib

class TestMobilePriceClassification(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base_dir = os.path.dirname(os.path.abspath(__file__))
        cls.model_path = os.path.join(cls.base_dir, 'models', 'mobile_price_model.joblib')

    def test_01_datasets_exist(self):
        """1. Barcha tillardagi dataset fayllari mavjudligini tekshirish"""
        required_files = [
            os.path.join(self.base_dir, 'uz', 'train_uz.csv'),
            os.path.join(self.base_dir, 'uz', 'test_uz.csv'),
            os.path.join(self.base_dir, 'ru', 'train_ru.csv'),
            os.path.join(self.base_dir, 'en', 'train_en.csv'),
            os.path.join(self.base_dir, 'original', 'train.csv')
        ]
        for f in required_files:
            self.assertTrue(os.path.exists(f), f"Fayl topilmadi: {f}")

    def test_02_dataset_shape_and_no_missing(self):
        """2. Dataset o'lchami va null qiymatlar yo'qligini tekshirish"""
        df_train = pd.read_csv(os.path.join(self.base_dir, 'uz', 'train_uz.csv'))
        self.assertEqual(df_train.shape, (2000, 21), "Train dataset 2000 qator va 21 ustundan iborat bo'lishi kerak")
        self.assertEqual(df_train.isnull().sum().sum(), 0, "Datasatda bo'sh (null) qiymatlar bo'lmasligi kerak")

    def test_03_model_accuracy_threshold(self):
        """3. O'qitilgan ML modeli aniqligi kamida 90% dan yuqori ekanligini tekshirish"""
        self.assertTrue(os.path.exists(self.model_path), "Model fayli mavjud emas")
        data = joblib.load(self.model_path)
        acc = data.get('accuracy', 0.0)
        self.assertGreaterEqual(acc, 0.90, f"Model aniqligi {acc} 90% dan kam!")

    def test_04_prediction_sanity_check(self):
        """4. Flagman va arzon telefonlar to'g'ri toifaga ajratilishini tekshirish"""
        from predict import predict_price, load_trained_model
        model_data = load_trained_model()

        # Flagman telefon (RAM 3900 MB, Batareya 4000 mAh) -> Class 3
        flagship_pred, _, _ = predict_price({'ram_mb': 3900, 'akkumulyator_quvvati': 4000}, model_data)
        self.assertEqual(flagship_pred, 3, "Yuqori parametrli telefon 3-toifa (Flagman) bo'lishi kerak")

        # Hamyonbop telefon (RAM 700 MB, Batareya 800 mAh) -> Class 0
        budget_pred, _, _ = predict_price({'ram_mb': 700, 'akkumulyator_quvvati': 800}, model_data)
        self.assertEqual(budget_pred, 0, "Past parametrli telefon 0-toifa (Arzon) bo'lishi kerak")

    def test_05_kaggle_submission_format(self):
        """5. Kaggle submission fayli formati to'g'riligini tekshirish"""
        sub_path = os.path.join(self.base_dir, 'predictions', 'submission_kaggle.csv')
        self.assertTrue(os.path.exists(sub_path), "submission_kaggle.csv mavjud emas")
        df_sub = pd.read_csv(sub_path)
        self.assertEqual(len(df_sub), 1000, "Submission aynan 1000 ta qator bo'lishi kerak")
        self.assertListEqual(list(df_sub.columns), ['id', 'price_range'], "Ustunlar ['id', 'price_range'] bo'lishi kerak")

    def test_06_web_files_exist(self):
        """6. Veb-sayt fayllari mavjudligini tekshirish"""
        html_path = os.path.join(self.base_dir, 'index.html')
        self.assertTrue(os.path.exists(html_path), "index.html mavjud emas")

if __name__ == '__main__':
    unittest.main()

