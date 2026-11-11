import os
import argparse
import joblib
import json
import urllib.request
import pandas as pd
import numpy as np

# Real-time Dollar rate fetcher
def get_live_usd_rate():
    try:
        req = urllib.request.Request('https://cbu.uz/uz/arkhiv-kursov-valyut/json/', headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=3) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            for item in data:
                if item.get('Ccy') == 'USD':
                    return float(item.get('Rate', 11974.02))
    except Exception:
        pass
    try:
        req = urllib.request.Request('https://open.er-api.com/v6/latest/USD', headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=3) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            return float(data['rates']['UZS'])
    except Exception:
        return 11974.02

# Mashhur telefon modellari katalogi
PHONE_MODELS = {
    'iphone 15 pro max': {'name': 'Apple iPhone 15 Pro Max', 'ram_mb': 3950, 'akkumulyator_quvvati': 1950, 'asosiy_kamera_mp': 20, 'ichki_xotira_gb': 64, 'protsessor_tezligi': 3.2, 'usd_price': 1180},
    'iphone 15': {'name': 'Apple iPhone 15', 'ram_mb': 3700, 'akkumulyator_quvvati': 1850, 'asosiy_kamera_mp': 18, 'ichki_xotira_gb': 64, 'protsessor_tezligi': 3.0, 'usd_price': 840},
    'iphone 13': {'name': 'Apple iPhone 13', 'ram_mb': 3400, 'akkumulyator_quvvati': 1750, 'asosiy_kamera_mp': 16, 'ichki_xotira_gb': 48, 'protsessor_tezligi': 2.8, 'usd_price': 610},
    'galaxy s24 ultra': {'name': 'Samsung Galaxy S24 Ultra', 'ram_mb': 3990, 'akkumulyator_quvvati': 1980, 'asosiy_kamera_mp': 20, 'ichki_xotira_gb': 64, 'protsessor_tezligi': 3.3, 'usd_price': 1150},
    'galaxy s23 fe': {'name': 'Samsung Galaxy S23 FE', 'ram_mb': 3600, 'akkumulyator_quvvati': 1800, 'asosiy_kamera_mp': 18, 'ichki_xotira_gb': 64, 'protsessor_tezligi': 2.6, 'usd_price': 550},
    'galaxy a55': {'name': 'Samsung Galaxy A55 5G', 'ram_mb': 2900, 'akkumulyator_quvvati': 1700, 'asosiy_kamera_mp': 16, 'ichki_xotira_gb': 48, 'protsessor_tezligi': 2.4, 'usd_price': 380},
    'galaxy a35': {'name': 'Samsung Galaxy A35', 'ram_mb': 2400, 'akkumulyator_quvvati': 1600, 'asosiy_kamera_mp': 14, 'ichki_xotira_gb': 32, 'protsessor_tezligi': 2.2, 'usd_price': 310},
    'galaxy a15': {'name': 'Samsung Galaxy A15', 'ram_mb': 1750, 'akkumulyator_quvvati': 1500, 'asosiy_kamera_mp': 13, 'ichki_xotira_gb': 32, 'protsessor_tezligi': 2.0, 'usd_price': 185},
    'galaxy a05': {'name': 'Samsung Galaxy A05', 'ram_mb': 950, 'akkumulyator_quvvati': 1300, 'asosiy_kamera_mp': 10, 'ichki_xotira_gb': 16, 'protsessor_tezligi': 1.6, 'usd_price': 115},
    'redmi note 13 pro': {'name': 'Redmi Note 13 Pro+ 5G', 'ram_mb': 3300, 'akkumulyator_quvvati': 1800, 'asosiy_kamera_mp': 18, 'ichki_xotira_gb': 64, 'protsessor_tezligi': 2.6, 'usd_price': 410},
    'redmi note 13': {'name': 'Redmi Note 13', 'ram_mb': 2100, 'akkumulyator_quvvati': 1600, 'asosiy_kamera_mp': 14, 'ichki_xotira_gb': 32, 'protsessor_tezligi': 2.2, 'usd_price': 210},
    'poco x6 pro': {'name': 'POCO X6 Pro 5G', 'ram_mb': 3500, 'akkumulyator_quvvati': 1850, 'asosiy_kamera_mp': 16, 'ichki_xotira_gb': 64, 'protsessor_tezligi': 2.8, 'usd_price': 370},
    'redmi 13c': {'name': 'Redmi 13C', 'ram_mb': 1500, 'akkumulyator_quvvati': 1400, 'asosiy_kamera_mp': 12, 'ichki_xotira_gb': 32, 'protsessor_tezligi': 1.8, 'usd_price': 140},
    'redmi a3': {'name': 'Redmi A3', 'ram_mb': 750, 'akkumulyator_quvvati': 1100, 'asosiy_kamera_mp': 8, 'ichki_xotira_gb': 16, 'protsessor_tezligi': 1.4, 'usd_price': 90}
}

DEFAULT_FEATURE_VALUES = {
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

def load_trained_model():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(base_dir, 'models', 'mobile_price_model.joblib')
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model topilmadi: {model_path}.")
    return joblib.load(model_path)

def calculate_exact_price(ram, battery, cam, storage, probs, live_rate=None):
    if live_rate is None:
        live_rate = get_live_usd_rate()

    cont_score = sum(idx * p for idx, p in enumerate(probs))

    if cont_score <= 1.0:
        base_usd = 70 + cont_score * 120
    elif cont_score <= 2.0:
        base_usd = 190 + (cont_score - 1.0) * 230
    else:
        base_usd = 420 + (cont_score - 2.0) * 650

    ram_bonus = ((ram - 2000) / 1000) * 30
    storage_bonus = ((storage - 32) / 32) * 20

    total_usd = round(base_usd + ram_bonus + storage_bonus)
    total_usd = max(65, round(total_usd / 5) * 5)

    total_uzs = round((total_usd * live_rate) / 10000) * 10000
    low_range_uzs = round((total_uzs * 0.92) / 10000) * 10000
    high_range_uzs = round((total_uzs * 1.08) / 10000) * 10000
    inst_12 = round((total_uzs * 1.18) / 12 / 1000) * 1000

    return {
        'total_usd': total_usd,
        'total_uzs': total_uzs,
        'low_uzs': low_range_uzs,
        'high_uzs': high_range_uzs,
        'inst_12': inst_12,
        'live_rate': live_rate
    }

def predict_phone(params_dict, model_data=None):
    if model_data is None:
        model_data = load_trained_model()

    pipeline = model_data['model']
    features = model_data['features']

    input_row = DEFAULT_FEATURE_VALUES.copy()
    for k, v in params_dict.items():
        if k in input_row:
            input_row[k] = float(v)

    df_input = pd.DataFrame([input_row])[features]
    pred = int(pipeline.predict(df_input)[0])

    probs = None
    if hasattr(pipeline.named_steps['clf'], 'predict_proba'):
        probs = pipeline.predict_proba(df_input)[0]
    elif hasattr(pipeline.named_steps['clf'], 'decision_function'):
        dfn = pipeline.decision_function(df_input)[0]
        exp_dfn = np.exp(dfn - np.max(dfn))
        probs = exp_dfn / np.sum(exp_dfn)

    ram = input_row['ram_mb']
    bat = input_row['akkumulyator_quvvati']
    cam = input_row['asosiy_kamera_mp']
    storage = input_row['ichki_xotira_gb']

    price_info = calculate_exact_price(ram, bat, cam, storage, probs)
    return pred, probs, price_info, input_row

# Testlar uchun alias
predict_price = lambda p, m=None: (predict_phone(p, m)[0], predict_phone(p, m)[1], predict_phone(p, m)[3])

def format_num(n):
    return f"{n:,}".replace(",", " ")

def main():
    parser = argparse.ArgumentParser(description="Telefon narxini aniqlash")
    parser.add_argument('--model', type=str, help="Mashhur model nomi (masalan: 'iphone 15', 'galaxy a15', 'redmi note 13')")
    parser.add_argument('--ram', type=float, help="RAM hajmi MB (masalan 4000)")
    parser.add_argument('--battery', type=float, help="Batareya mAh (masalan 5000)")
    parser.add_argument('--camera', type=float, help="Kamera MP (masalan 50)")
    parser.add_argument('--storage', type=float, help="Ichki xotira GB (masalan 128)")
    parser.add_argument('--lang', choices=['uz', 'ru', 'en'], default='uz')
    args = parser.parse_args()

    live_rate = get_live_usd_rate()
    params = {}
    display_name = None

    if args.model:
        m_key = args.model.strip().lower()
        matched = None
        for k in PHONE_MODELS:
            if m_key in k or k in m_key:
                matched = k
                break
        if matched:
            display_name = PHONE_MODELS[matched]['name']
            params = PHONE_MODELS[matched].copy()
            print(f"✓ Model aniqlandi: {display_name}")
        else:
            print(f"⚠️ Model topilmadi: '{args.model}'. Kiritilgan parametrlar bo'yicha hisoblanadi.")

    if args.ram: params['ram_mb'] = args.ram
    if args.battery: params['akkumulyator_quvvati'] = min(2000, args.battery)
    if args.camera: params['asosiy_kamera_mp'] = min(20, args.camera)
    if args.storage: params['ichki_xotira_gb'] = min(64, args.storage)

    if not params:
        params = PHONE_MODELS['galaxy a15'].copy()
        display_name = PHONE_MODELS['galaxy a15']['name']

    pred, probs, price, full = predict_phone(params)

    tier_names = {
        0: "0 - Hamyonbop / Oddiy Sinf (Budget)",
        1: "1 - O'rta-Quyi Sinf (Mid-Range)",
        2: "2 - O'rta-Yuqori Sinf (Upper Mid-Range)",
        3: "3 - Flagman / Premium Sinf (Flagship)"
    }

    if 'usd_price' in params:
        final_usd = params['usd_price']
        final_uzs = round(final_usd * live_rate / 10000) * 10000
    else:
        final_usd = price['total_usd']
        final_uzs = price['total_uzs']

    low_uzs = round(final_uzs * 0.92 / 10000) * 10000
    high_uzs = round(final_uzs * 1.08 / 10000) * 10000
    inst_12 = round(final_uzs * 1.18 / 12 / 1000) * 1000

    print("\n" + "=" * 68)
    print(f"  🟢 JONLI VALYUTA KURSI (CBU API): 1 USD = {format_num(round(live_rate, 2))} UZS")
    if display_name:
        print(f"  📱 TELEFON MODELI: {display_name}")
    print(f"  ⚡ ASOSIY PARAMETRLAR: RAM {int(full['ram_mb'])} MB | Xotira {int(full['ichki_xotira_gb'])} GB")
    print("=" * 68)
    print(f"  🎯 Narx Toifasi: {tier_names[pred]}")
    print(f"  💰 ANIQ TAVSIYA BOZOR NARXI: {format_num(final_uzs)} SO'M (≈ ${final_usd})")
    print(f"  📊 Bozor oralig'i: {format_num(low_uzs)} — {format_num(high_uzs)} so'm")
    print(f"  💳 12 oyga bo'lib to'lash (Nasiya): oyiga ~{format_num(inst_12)} so'm")
    print("=" * 68)

if __name__ == '__main__':
    main()
