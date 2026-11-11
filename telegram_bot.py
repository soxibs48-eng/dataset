"""
====================================================================
SmartPrice AI - Telegram Bot (@telefonnarxx_bot)
Mobil telefonlar narxini aniqlash va baholash bo'yicha Telegram Bot.

Imkoniyatlar:
- Scikit-learn AI modeli orqali narx toifasini aniqlash (96.5% aniqlik)
- Real vaqtdagi Markaziy Bank (CBU) dollari kursi bilan UZS hisoblash
- Mashhur telefon modellari katalogi (iPhone, Galaxy, Redmi, POCO)
- 3, 6, 12 oylik nasiya to'lovlari hisob-kitobi
- Istalgan telefon parametrlarini kiritib narxini hisoblash
====================================================================
"""

import os
import re
import json
import urllib.request
import urllib.parse
import time
from predict import (
    PHONE_MODELS, 
    predict_phone, 
    get_live_usd_rate, 
    format_num,
    DEFAULT_FEATURE_VALUES,
    load_trained_model,
    calculate_exact_price
)

# Telegram Bot Token
BOT_TOKEN = os.environ.get("BOT_TOKEN", "9015385775:AAHcTWqdJI5iACrq8a4tcH9oJcRoNYUopGk")
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"
WEB_APP_URL = "https://soxibs48-eng.github.io/dataset/"

def telegram_api(method, payload=None):
    """Telegram Bot API bilan xavfsiz HTTP so'rov"""
    url = f"{API_URL}/{method}"
    headers = {'Content-Type': 'application/json'}
    data = json.dumps(payload).encode('utf-8') if payload else None
    req = urllib.request.Request(url, data=data, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=35) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except Exception as e:
        print(f"Telegram API xatoligi ({method}): {e}")
        return None

def send_message(chat_id, text, reply_markup=None):
    payload = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'HTML',
        'disable_web_page_preview': True
    }
    if reply_markup:
        payload['reply_markup'] = reply_markup
    return telegram_api('sendMessage', payload)

def send_chat_action(chat_id, action="typing"):
    telegram_api('sendChatAction', {'chat_id': chat_id, 'action': action})

def get_updates(offset=None):
    url = f"getUpdates?timeout=25"
    if offset:
        url += f"&offset={offset}"
    return telegram_api(url)

# Keyboards
def get_main_keyboard():
    return {
        'keyboard': [
            [{'text': '🍏 Apple iPhone'}, {'text': '🔷 Samsung Galaxy'}],
            [{'text': '🟠 Xiaomi & Redmi'}, {'text': '🚀 POCO & Boshqalar'}],
            [{'text': '⚙️ O\'z parametrlaringizni kiritish'}],
            [{'text': '💵 Jonli Dollar Kursi'}, {'text': '🌐 Web Saytni Ochish'}, {'text': 'ℹ️ Bot haqida'}]
        ],
        'resize_keyboard': True
    }

def get_apple_keyboard():
    return {
        'keyboard': [
            [{'text': '📱 iPhone 15 Pro Max'}, {'text': '📱 iPhone 15'}],
            [{'text': '📱 iPhone 13'}],
            [{'text': '🔙 Asosiy Menyu'}]
        ],
        'resize_keyboard': True
    }

def get_samsung_keyboard():
    return {
        'keyboard': [
            [{'text': '📱 Galaxy S24 Ultra'}, {'text': '📱 Galaxy S23 FE'}],
            [{'text': '📱 Galaxy A55'}, {'text': '📱 Galaxy A35'}],
            [{'text': '📱 Galaxy A15'}, {'text': '📱 Galaxy A05'}],
            [{'text': '🔙 Asosiy Menyu'}]
        ],
        'resize_keyboard': True
    }

def get_xiaomi_keyboard():
    return {
        'keyboard': [
            [{'text': '📱 Redmi Note 13 Pro'}, {'text': '📱 Redmi Note 13'}],
            [{'text': '📱 Redmi 13C'}, {'text': '📱 Redmi A3'}],
            [{'text': '🔙 Asosiy Menyu'}]
        ],
        'resize_keyboard': True
    }

def get_poco_keyboard():
    return {
        'keyboard': [
            [{'text': '📱 POCO X6 Pro'}],
            [{'text': '🔙 Asosiy Menyu'}]
        ],
        'resize_keyboard': True
    }

def get_phone_inline_buttons(model_key):
    return {
        'inline_keyboard': [
            [
                {'text': '🌐 Web saytda to\'liq ko\'rish', 'url': WEB_APP_URL}
            ],
            [
                {'text': '🔄 Boshqa model tanlash', 'callback_data': 'back_to_menu'}
            ]
        ]
    }

def generate_phone_quote(model_key, live_rate):
    """Telefon haqida to'liq hisob-kitob va chiroyli matn yaratish"""
    model = PHONE_MODELS.get(model_key)
    if not model:
        return "⚠️ Kechirasiz, ushbu model bazadan topilmadi."

    pred, probs, price, full = predict_phone(model)
    usd_price = model.get('usd_price', price['total_usd'])
    uzs_price = round(usd_price * live_rate / 10000) * 10000
    low_uzs = round(uzs_price * 0.92 / 10000) * 10000
    high_uzs = round(uzs_price * 1.08 / 10000) * 10000
    
    # Nasiya to'lovlari
    inst_3 = round(uzs_price * 1.06 / 3 / 1000) * 1000
    inst_6 = round(uzs_price * 1.10 / 6 / 1000) * 1000
    inst_12 = round(uzs_price * 1.18 / 12 / 1000) * 1000

    tiers = [
      "🟢 Hamyonbop (Byudjet sinf)",
      "🔵 O'rta-Quyi sinf smartfon",
      "🟣 O'rta-Yuqori sinf smartfon",
      "👑 Flagman / Premium smartfon"
    ]

    msg = f"📱 <b>{model['name']}</b>\n"
    msg += f"━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    msg += f"💰 <b>Bozor narxi:</b> <code>{format_num(uzs_price)} so'm</code> (≈ <b>${usd_price}</b>)\n"
    msg += f"📊 <b>Narx oralig'i:</b> {format_num(low_uzs)} — {format_num(high_uzs)} so'm\n"
    msg += f"🎯 <b>AI Toifasi:</b> {tiers[pred]}\n"
    msg += f"━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    msg += f"💳 <b>Nasiya to'lov rejalari (Muddatli to'lov):</b>\n"
    msg += f" • <b>3 oy:</b> oyiga <code>{format_num(inst_3)}</code> so'mdan\n"
    msg += f" • <b>6 oy:</b> oyiga <code>{format_num(inst_6)}</code> so'mdan\n"
    msg += f" • <b>12 oy:</b> oyiga <code>{format_num(inst_12)}</code> so'mdan\n"
    msg += f"━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    msg += f"⚡ <b>Texnik parametrlari:</b>\n"
    msg += f" • <b>Operativ xotira (RAM):</b> {model['ram_mb']} MB (~{(model['ram_mb']/1024):.1f} GB)\n"
    msg += f" • <b>Akkumulyator hajmi:</b> {model['akkumulyator_quvvati']} mAh\n"
    msg += f" • <b>Asosiy kamera:</b> {model['asosiy_kamera_mp']} MP\n"
    msg += f" • <b>Doimiy ichki xotira:</b> {model['ichki_xotira_gb']} GB\n"
    msg += f" • <b>Protsessor chastotasi:</b> {model['protsessor_tezligi']} GHz\n"
    msg += f"━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    msg += f"🏛️ <i>Markaziy Bank kursi: 1 USD = {format_num(round(live_rate, 2))} UZS</i>"
    return msg

def predict_custom_specs(ram_gb, battery_mah, cam_mp, storage_gb, live_rate):
    """Foydalanuvchi kiritgan parametrlar bo'yicha narxni hisoblash"""
    ram_mb = min(3990, max(512, int(ram_gb * 1024)))
    batt = min(1980, max(500, int(battery_mah * 0.40))) if battery_mah > 2200 else battery_mah
    cam = min(20, max(2, int(cam_mp * 0.40))) if cam_mp > 24 else cam_mp
    storage = min(64, max(8, int(storage_gb * 0.50))) if storage_gb > 64 else storage_gb

    input_specs = {
        'ram_mb': ram_mb,
        'akkumulyator_quvvati': batt,
        'asosiy_kamera_mp': cam,
        'ichki_xotira_gb': storage
    }
    pred, probs, price, full = predict_phone(input_specs)

    usd = price['total_usd']
    uzs = price['total_uzs']
    low_uzs = price['low_uzs']
    high_uzs = price['high_uzs']
    inst_12 = price['inst_12']

    tiers = [
      "🟢 Hamyonbop (0-toifa)",
      "🔵 O'rta-Quyi sinf (1-toifa)",
      "🟣 O'rta-Yuqori sinf (2-toifa)",
      "👑 Flagman / Premium (3-toifa)"
    ]

    msg = f"🔮 <b>Siz kiritgan parametrlar bo'yicha AI xulosasi:</b>\n"
    msg += f"━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    msg += f"• <b>RAM:</b> {ram_gb} GB\n"
    msg += f"• <b>Batareya:</b> {battery_mah} mAh\n"
    msg += f"• <b>Kamera:</b> {cam_mp} MP\n"
    msg += f"• <b>Xotira:</b> {storage_gb} GB\n"
    msg += f"━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    msg += f"💰 <b>Taxminiy bozor narxi:</b> <code>{format_num(uzs)} so'm</code> (≈ <b>${usd}</b>)\n"
    msg += f"📊 <b>Narx oralig'i:</b> {format_num(low_uzs)} — {format_num(high_uzs)} so'm\n"
    msg += f"🎯 <b>AI Toifasi:</b> {tiers[pred]}\n"
    msg += f"💳 <b>12 oylik nasiya:</b> oyiga ~{format_num(inst_12)} so'mdan\n"
    msg += f"━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    msg += f"🟢 <i>Markaziy Bank kursi: 1 USD = {format_num(round(live_rate, 2))} UZS</i>"
    return msg

def parse_specs_from_text(text):
    """Matndan RAM, Batareya, Kamera va Xotira raqamlarini ajratish"""
    # Masalan: 8 5000 50 128 yoki 8gb ram, 5000 batareya
    numbers = [int(n) for n in re.findall(r'\b\d+\b', text)]
    if len(numbers) >= 4:
        # Masalan: 8 5000 50 128
        ram = numbers[0] if numbers[0] < 32 else 8
        batt = numbers[1] if numbers[1] >= 1000 else 5000
        cam = numbers[2] if numbers[2] <= 200 else 50
        storage = numbers[3] if numbers[3] >= 16 else 128
        return ram, batt, cam, storage
    return None

def main():
    print("=" * 65)
    print("🚀 SmartPrice AI Telegram Bot ishga tushirilmoqda...")
    print(f"🤖 Bot Token: {BOT_TOKEN[:10]}...{BOT_TOKEN[-5:]}")
    print("=" * 65)

    # Bot ma'lumotlarini tekshirish
    me = telegram_api('getMe')
    if not me or not me.get('ok'):
        print(f"❌ Xatolik: Bot tokeni yaroqsiz yoki internet mavjud emas: {me}")
        return

    bot_info = me['result']
    print(f"✅ Bot muvaffaqiyatli ulandi!")
    print(f"• Nomi: {bot_info.get('first_name')}")
    print(f"• Username: @{bot_info.get('username')}")
    print(f"• ID: {bot_info.get('id')}")
    print("Xabarlar qabul qilinmoqda... (Polling faol)\n")

    offset = None
    live_rate = get_live_usd_rate()
    last_rate_time = time.time()

    model_keywords = {
        'iphone 15 pro max': 'iphone 15 pro max',
        '15 pro max': 'iphone 15 pro max',
        'iphone 15': 'iphone 15',
        'iphone 13': 'iphone 13',
        'galaxy s24 ultra': 'galaxy s24 ultra',
        's24 ultra': 'galaxy s24 ultra',
        'galaxy s23 fe': 'galaxy s23 fe',
        's23 fe': 'galaxy s23 fe',
        'galaxy a55': 'galaxy a55',
        'a55': 'galaxy a55',
        'galaxy a35': 'galaxy a35',
        'a35': 'galaxy a35',
        'galaxy a15': 'galaxy a15',
        'a15': 'galaxy a15',
        'galaxy a05': 'galaxy a05',
        'a05': 'galaxy a05',
        'redmi note 13 pro': 'redmi note 13 pro',
        'note 13 pro': 'redmi note 13 pro',
        'redmi note 13': 'redmi note 13',
        'note 13': 'redmi note 13',
        'poco x6 pro': 'poco x6 pro',
        'x6 pro': 'poco x6 pro',
        'redmi 13c': 'redmi 13c',
        '13c': 'redmi 13c',
        'redmi a3': 'redmi a3'
    }

    while True:
        try:
            # Har 5 daqiqada valyuta kursini yangilash
            if time.time() - last_rate_time > 300:
                live_rate = get_live_usd_rate()
                last_rate_time = time.time()

            updates = get_updates(offset)
            if updates and updates.get('ok'):
                for update in updates.get('result', []):
                    offset = update['update_id'] + 1
                    
                    # Callback query (tugma bosilishi)
                    if 'callback_data' in update:
                        cb = update['callback_data']
                        cb_id = cb.get('id')
                        chat_id = cb.get('message', {}).get('chat', {}).get('id')
                        telegram_api('answerCallbackQuery', {'callback_query_id': cb_id})
                        if chat_id:
                            send_message(chat_id, "Asosiy menyuga qaytdingiz. Telefonni tanlang:", get_main_keyboard())
                        continue

                    msg = update.get('message', {})
                    chat_id = msg.get('chat', {}).get('id')
                    text = (msg.get('text') or '').strip()
                    lower_text = text.lower()

                    if not chat_id:
                        continue

                    send_chat_action(chat_id, "typing")

                    # Buyruqlar va xabarlar
                    if lower_text in ['/start', 'start', 'salom', 'assalomu alaykum', '🔙 asosiy menyu']:
                        welcome = (
                            f"👋 Assalomu alaykum! <b>SmartPrice AI</b> rasmiy botiga xush kelibsiz! 📱\n\n"
                            f"Men sun'iy intellekt (Scikit-Learn) va real vaqtdagi Markaziy Bank kursi asosida "
                            f"har qanday telefonning <b>haqqoniy bozor narxi</b> va <b>nasiya to'lovlarini</b> hisoblab beraman.\n\n"
                            f"👇 <i>Kerakli brendni tanlang yoki telefon nomini yozing:</i>"
                        )
                        send_message(chat_id, welcome, get_main_keyboard())

                    elif 'apple' in lower_text or 'iphone' == lower_text:
                        send_message(chat_id, "🍏 <b>Apple iPhone</b> modellaridan birini tanlang:", get_apple_keyboard())

                    elif 'samsung' in lower_text or 'galaxy' == lower_text:
                        send_message(chat_id, "🔷 <b>Samsung Galaxy</b> modellaridan birini tanlang:", get_samsung_keyboard())

                    elif 'xiaomi' in lower_text or 'redmi' == lower_text:
                        send_message(chat_id, "🟠 <b>Xiaomi / Redmi</b> modellaridan birini tanlang:", get_xiaomi_keyboard())

                    elif 'poco' in lower_text:
                        send_message(chat_id, "🚀 <b>POCO</b> modellaridan birini tanlang:", get_poco_keyboard())

                    elif 'dollar' in lower_text or 'kurs' in lower_text or 'valyuta' in lower_text:
                        c_rate = get_live_usd_rate()
                        c_msg = (
                            f"🏛️ <b>O'zbekiston Respublikasi Markaziy Banki:</b>\n\n"
                            f"💵 <b>1 AQSH Dollari (USD):</b> <code>{format_num(round(c_rate, 2))} UZS</code>\n"
                            f"💶 <b>1 Yevro (EUR):</b> <code>{format_num(round(c_rate * 1.085, 2))} UZS</code>\n"
                            f"🇷🇺 <b>1 Rossiya Rubli (RUB):</b> <code>{format_num(round(c_rate / 92.5, 2))} UZS</code>\n\n"
                            f"⏱️ <i>Kurslar har soniyada API orqali yangilanib turadi.</i>"
                        )
                        send_message(chat_id, c_msg, get_main_keyboard())

                    elif 'web sayt' in lower_text or 'sayt' in lower_text or 'saytni ochish' in lower_text:
                        web_msg = (
                            f"🌐 <b>SmartPrice AI Veb-Platformasi:</b>\n\n"
                            f"Siz barcha parametrlarni interaktiv slayderlar orqali boshqarishingiz, "
                            f"grafik tahlillarni ko'rishingiz mumkin:\n\n"
                            f"🔗 <b>Jonli veb-sayt:</b> {WEB_APP_URL}\n"
                            f"💻 <b>Lokal server:</b> http://localhost:8000\n"
                            f"📂 <b>GitHub Repo:</b> https://github.com/soxibs48-eng/dataset"
                        )
                        markup = {
                            'inline_keyboard': [
                                [{'text': '🚀 Web Saytga O\'tish', 'url': WEB_APP_URL}]
                            ]
                        }
                        send_message(chat_id, web_msg, markup)

                    elif 'haqida' in lower_text or '/info' in lower_text:
                        about = (
                            "ℹ️ <b>SmartPrice AI Loyihasi haqida:</b>\n\n"
                            "• <b>ML Model:</b> Scikit-learn (Logistic Regression, 96.5% aniqlik)\n"
                            "• <b>Dataset:</b> Kaggle Mobile Price Classification (20 ta parametr)\n"
                            "• <b>Valyuta kursi:</b> O'zbekiston Markaziy Banki jonli API\n"
                            "• <b>Dasturchi:</b> Soxibjon (@soxibs48-eng)\n"
                            "• <b>Kod ombori:</b> https://github.com/soxibs48-eng/dataset"
                        )
                        send_message(chat_id, about, get_main_keyboard())

                    elif 'parametr' in lower_text or 'o\'z parametr' in lower_text:
                        param_msg = (
                            "⚙️ <b>O'zingiz xohlagan telefon parametrlarini yuboring!</b>\n\n"
                            "Format: <code>RAM Batareya Kamera Xotira</code>\n"
                            "Masalan: <code>8 5000 50 128</code>\n\n"
                            "<i>(Bu: 8GB RAM, 5000 mAh batareya, 50 MP kamera va 128 GB xotirani bildiradi)</i>"
                        )
                        send_message(chat_id, param_msg, get_main_keyboard())

                    else:
                        # Tekshiruv 1: Raqamlar yuborilganmi (custom specs)?
                        specs = parse_specs_from_text(text)
                        if specs:
                            ram_g, batt_m, cam_m, stor_g = specs
                            quote = predict_custom_specs(ram_g, batt_m, cam_m, stor_g, live_rate)
                            send_message(chat_id, quote, get_main_keyboard())
                            continue

                        # Tekshiruv 2: Katalogdagi modellar bilan solishtirish
                        matched_key = None
                        for kw, m_key in model_keywords.items():
                            if kw in lower_text:
                                matched_key = m_key
                                break

                        if matched_key:
                            quote = generate_phone_quote(matched_key, live_rate)
                            inline_markup = get_phone_inline_buttons(matched_key)
                            send_message(chat_id, quote, inline_markup)
                        else:
                            fallback = (
                                f"🤖 Kechirasiz, <i>'{text}'</i> bo'yicha ma'lumot topilmadi.\n\n"
                                f"Iltimos, quyidagi tugmalardan birini bosing yoki telefon nomini to'g'riroq yozing "
                                f"(masalan: <b>Galaxy A15</b>, <b>iPhone 15</b>, <b>Redmi Note 13</b>).\n\n"
                                f"Yoki ixtiyoriy parametrlarni kiriting: <code>8 5000 50 128</code>"
                            )
                            send_message(chat_id, fallback, get_main_keyboard())

            time.sleep(1)

        except Exception as err:
            print(f"Xatolik yuz berdi: {err}")
            time.sleep(3)

if __name__ == '__main__':
    main()
