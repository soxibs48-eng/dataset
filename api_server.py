"""
SmartPrice AI - REST API Serveri
Ushbu server tashqi ilovalar (Telegram bot, mobil ilovalar, veb saytlar) uchun
mobil telefon narx toifasini aniqlash API xizmatini taqdim etadi.

Endpoints:
  GET  /api/info    - Model haqida ma'lumot va metrikalar
  POST /api/predict - Parametrlar asosida narx toifasini aniqlash
"""

import os
import json
import joblib
import pandas as pd
import numpy as np
from http.server import HTTPServer, BaseHTTPRequestHandler

PORT = 5000
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Modelni xotiraga yuklash
MODEL_PATH = os.path.join(BASE_DIR, 'models', 'mobile_price_model.joblib')
if os.path.exists(MODEL_PATH):
    MODEL_DATA = joblib.load(MODEL_PATH)
else:
    MODEL_DATA = None

DEFAULT_VALUES = {
    'akkumulyator_quvvati': 1226.0,
    'bluetooth': 1.0,
    'protsessor_tezligi': 1.5,
    'ikkita_sim': 1.0,
    'old_kamera_mp': 4.0,
    'tort_g': 1.0,
    'ichki_xotira_gb': 32.0,
    'qalinligi_sm': 0.5,
    'telefon_vazni_gr': 141.0,
    'yadro_soni': 4.0,
    'asosiy_kamera_mp': 10.0,
    'piksel_balandligi': 564.0,
    'piksel_kengligi': 1247.0,
    'ram_mb': 2146.0,
    'ekran_balandligi_sm': 12.0,
    'ekran_kengligi_sm': 5.0,
    'gaplashish_vaqti_soat': 11.0,
    'uch_g': 1.0,
    'sensorli_ekran': 1.0,
    'wifi': 1.0
}

LABELS = {
    'uz': {
        0: "0 - Hamyonbop / Arzon narx (Low Cost)",
        1: "1 - O'rta-quyi toifa (Medium Cost)",
        2: "2 - O'rta-yuqori toifa (High Cost)",
        3: "3 - Flagman / Juda qimmat (Very High Cost)"
    },
    'ru': {
        0: "0 - Бюджетный класс (Низкая цена)",
        1: "1 - Средне-бюджетный класс (Средняя цена)",
        2: "2 - Средне-высокий класс (Высокая цена)",
        3: "3 - Флагманский класс (Очень высокая цена)"
    },
    'en': {
        0: "0 - Low Cost (Budget tier)",
        1: "1 - Medium Cost (Mid-tier)",
        2: "2 - High Cost (Upper mid-tier)",
        3: "3 - Very High Cost (Flagship tier)"
    }
}

class APIHandler(BaseHTTPRequestHandler):
    def _send_json(self, status_code, data):
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False, indent=2).encode('utf-8'))

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        if self.path in ['/api/info', '/']:
            info = {
                "name": "SmartPrice AI - Mobile Price Classification API",
                "version": "1.0.0",
                "model_name": MODEL_DATA['model_name'] if MODEL_DATA else "N/A",
                "accuracy": f"{MODEL_DATA['accuracy']*100:.2f}%" if MODEL_DATA else "N/A",
                "endpoints": {
                    "GET /api/info": "Model haqida umumiy ma'lumot",
                    "POST /api/predict": "Telefon parametrlari bo'yicha narxni bashorat qilish"
                },
                "supported_languages": ["uz", "ru", "en"]
            }
            self._send_json(200, info)
        else:
            self._send_json(404, {"error": "Endpoint topilmadi"})

    def do_POST(self):
        if self.path == '/api/predict':
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            try:
                payload = json.loads(body) if body else {}
            except json.JSONDecodeError:
                self._send_json(400, {"error": "Noto'g'ri JSON formati"})
                return

            if not MODEL_DATA:
                self._send_json(500, {"error": "Model yuklanmagan"})
                return

            lang = payload.get('lang', 'uz')
            if lang not in LABELS:
                lang = 'uz'

            # Kiruvchi parametrlarni moslash
            user_features = DEFAULT_VALUES.copy()

            # Kalitlarni o'zbekcha / inglizcha nomlar bilan qabul qilish
            key_aliases = {
                'ram': 'ram_mb',
                'ram_mb': 'ram_mb',
                'battery': 'akkumulyator_quvvati',
                'battery_power': 'akkumulyator_quvvati',
                'akkumulyator_quvvati': 'akkumulyator_quvvati',
                'camera': 'asosiy_kamera_mp',
                'pc': 'asosiy_kamera_mp',
                'asosiy_kamera_mp': 'asosiy_kamera_mp',
                'front_camera': 'old_kamera_mp',
                'fc': 'old_kamera_mp',
                'old_kamera_mp': 'old_kamera_mp',
                'storage': 'ichki_xotira_gb',
                'int_memory': 'ichki_xotira_gb',
                'ichki_xotira_gb': 'ichki_xotira_gb',
                'clock_speed': 'protsessor_tezligi',
                'protsessor_tezligi': 'protsessor_tezligi',
                'px_height': 'piksel_balandligi',
                'piksel_balandligi': 'piksel_balandligi'
            }

            for k, v in payload.items():
                if k in key_aliases:
                    user_features[key_aliases[k]] = float(v)
                elif k in user_features:
                    user_features[k] = float(v)

            pipeline = MODEL_DATA['model']
            features = MODEL_DATA['features']
            df_in = pd.DataFrame([user_features])[features]

            pred_class = int(pipeline.predict(df_in)[0])

            probs_dict = {}
            if hasattr(pipeline.named_steps['clf'], 'predict_proba'):
                probs = pipeline.predict_proba(df_in)[0]
                for c_idx, p_val in enumerate(probs):
                    probs_dict[f"category_{c_idx}"] = round(float(p_val), 4)

            response = {
                "status": "success",
                "predicted_category": pred_class,
                "label": LABELS[lang][pred_class],
                "probabilities": probs_dict,
                "input_specs": {
                    "ram_mb": int(user_features['ram_mb']),
                    "battery_mah": int(user_features['akkumulyator_quvvati']),
                    "camera_mp": int(user_features['asosiy_kamera_mp']),
                    "storage_gb": int(user_features['ichki_xotira_gb'])
                }
            }
            self._send_json(200, response)
        else:
            self._send_json(404, {"error": "Endpoint topilmadi"})

def run_server():
    server_address = ('', PORT)
    httpd = HTTPServer(server_address, APIHandler)
    print(f"🚀 SmartPrice REST API serveri ishga tushdi: http://localhost:{PORT}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nAPI server to'xtatildi.")

if __name__ == '__main__':
    run_server()

