"""
====================================================================
SmartPrice AI - Telegram Bot
Mobil telefonlar narxini aniqlash va baholash bo'yicha Telegram Bot.

Qanday ishga tushirish kerak:
1. @BotFather orqali yangi bot yarating va TOKEN oling.
2. Ushbu faylda BOT_TOKEN o'rniga o'z tokeningizni qo'ying (yoki environment variable orqali).
3. `python telegram_bot.py` buyrug'ini bering.
====================================================================
"""

import os
import json
import urllib.request
import urllib.parse
import time
from predict import PHONE_MODELS, predict_phone, get_live_usd_rate, format_num

# O'z tokeningizni kiriting yoki BOT_TOKEN muhit o'zgaruvchisidan olinadi
BOT_TOKEN = os.environ.get("BOT_TOKEN", "YOUR_TELEGRAM_BOT_TOKEN_HERE")
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

def send_message(chat_id, text, reply_markup=None):
    if BOT_TOKEN == "YOUR_TELEGRAM_BOT_TOKEN_HERE":
        print(f"[TEST REJIMI] Xabar yuborildi ({chat_id}):\n{text}\n")
        return None

    url = f"{API_URL}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'HTML'
    }
    if reply_markup:
        payload['reply_markup'] = json.dumps(reply_markup)

    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except Exception as e:
        print(f"Xabar yuborishda xatolik: {e}")
        return None

def get_updates(offset=None):
    url = f"{API_URL}/getUpdates?timeout=30"
    if offset:
        url += f"&offset={offset}"
    try:
        with urllib.request.urlopen(url, timeout=35) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except Exception:
        return None

def generate_phone_quote(model_key, live_rate):
    model = PHONE_MODELS.get(model_key)
    if not model:
        return "⚠️ Kechirasiz, ushbu model topilmadi."

    pred, probs, price, full = predict_phone(model)
    usd_price = model.get('usd_price', price['total_usd'])
    uzs_price = round(usd_price * live_rate / 10000) * 10000
    low_uzs = round(uzs_price * 0.92 / 10000) * 10000
    high_uzs = round(uzs_price * 1.08 / 10000) * 10000
    inst_12 = round(uzs_price * 1.18 / 12 / 1000) * 1000

    tiers = [
      "0 - Hamyonbop / Oddiy telefon",
      "1 - O'rta-Quyi sinf smartfon",
      "2 - O'rta-Yuqori sinf smartfon",
      "3 - Flagman / Premium telefon"
    ]

    msg = f"📱 <b>{model['name']}</b>\n"
    msg += f"━━━━━━━━━━━━━━━━━━━━\n"
    msg += f"💰 <b>Tavsiya etilgan narx:</b> <code>{format_num(uzs_price)} so'm</code> (≈ ${usd_price})\n"
    msg += f"📊 <b>Bozor oralig'i:</b> {format_num(low_uzs)} — {format_num(high_uzs)} so'm\n"
    msg += f"🎯 <b>Narx toifasi:</b> {tiers[pred]}\n"
    msg += f"💳 <b>12 oyga nasiya:</b> oyiga ~{format_num(inst_12)} so'm\n"
    msg += f"━━━━━━━━━━━━━━━━━━━━\n"
    msg += f"⚡ <b>Xususiyatlari:</b>\n"
    msg += f"• RAM: {model['ram_mb']} MB (~{(model['ram_mb']/1024):.1f} GB)\n"
    msg += f"• Batareya: {model['akkumulyator_quvvati']} mAh\n"
    msg += f"• Asosiy kamera: {model['asosiy_kamera_mp']} MP\n"
    msg += f"• Xotira: {model['ichki_xotira_gb']} GB\n"
    msg += f"━━━━━━━━━━━━━━━━━━━━\n"
    msg += f"🟢 <i>Markaziy Bank kursi: 1 USD = {format_num(round(live_rate, 2))} UZS</i>"
    return msg

def get_main_keyboard():
    return {
        'keyboard': [
            [{'text': '🍏 iPhone 15 Pro Max'}, {'text': '🔷 Galaxy S24 Ultra'}],
            [{'text': '📱 Galaxy A15'}, {'text': '🟠 Redmi Note 13'}],
            [{'text': '🪙 Galaxy A05 (Arzon)'}, {'text': '🚀 POCO X6 Pro'}],
            [{'text': '💵 Jonli Dollar Kursi'}, {'text': 'ℹ️ Bot haqida'}]
        ],
        'resize_keyboard': True
    }

def main():
    print("=" * 65)
    print("🚀 SmartPrice AI Telegram Bot Dasturi")
    print("=" * 65)

    if BOT_TOKEN == "YOUR_TELEGRAM_BOT_TOKEN_HERE":
        print("⚠️ DIQQAT: BOT_TOKEN kiritilmagan.")
        print("Test tariqasida Galaxy A15 xabari shakllantirilmoqda:\n")
        live_rate = get_live_usd_rate()
        print(generate_phone_quote('galaxy a15', live_rate))
        print("Telegramda ishga tushirish uchun @BotFather'dan token olib, BOT_TOKEN ga qo'ying.")
        return

    print("Bot muvaffaqiyatli ishga tushdi va xabarlarni kutmoqda...")
    offset = None
    live_rate = get_live_usd_rate()

    model_mapping = {
        'iphone 15 pro max': 'iphone_15_pro_max',
        'galaxy s24 ultra': 'galaxy_s24_ultra',
        'galaxy a15': 'galaxy_a15',
        'redmi note 13': 'redmi_note_13',
        'galaxy a05': 'galaxy_a05',
        'poco x6 pro': 'poco_x6_pro'
    }

    while True:
        updates = get_updates(offset)
        if updates and updates.get('ok'):
            for update in updates.get('result', []):
                offset = update['update_id'] + 1
                msg = update.get('message', {})
                chat_id = msg.get('chat', {}).get('id')
                text = (msg.get('text') or '').strip().lower()

                if not chat_id:
                    continue

                if text in ['/start', 'start', 'salom']:
                    welcome = (
                        "Assalomu alaykum! <b>SmartPrice AI</b> botiga xush kelibsiz! 📱\n\n"
                        "Ushbu bot mobil telefonlarning texnik parametrlariga qarab ularning "
                        "<b>aniq bozor narxi</b> va <b>nasiya to'lovlarini</b> hisoblab beradi.\n\n"
                        "Quyidagi tugmalardan birini tanlang yoki telefon nomini yozing:"
                    )
                    send_message(chat_id, welcome, get_main_keyboard())

                elif 'dollar' in text or 'kurs' in text:
                    rate = get_live_usd_rate()
                    c_msg = f"🟢 <b>Markaziy Bank Jonli Valyuta Kursi:</b>\n\n1 USD = <b>{format_num(round(rate, 2))} UZS</b>"
                    send_message(chat_id, c_msg, get_main_keyboard())

                elif 'haqida' in text:
                    about = (
                        "ℹ️ <b>SmartPrice AI Bot</b>\n\n"
                        "• AI Modeli: Scikit-learn (96.5% aniqlik)\n"
                        "• Dataset: Kaggle Mobile Price Classification\n"
                        "• Valyuta kursi: Markaziy Bank (CBU API)\n"
                        "• Veb-versiyasi: http://localhost:8000"
                    )
                    send_message(chat_id, about, get_main_keyboard())

                else:
                    matched_key = None
                    for key in model_mapping:
                        if key in text:
                            matched_key = model_mapping[key]
                            break

                    if matched_key:
                        quote = generate_phone_quote(matched_key, get_live_usd_rate())
                        send_message(chat_id, quote, get_main_keyboard())
                    else:
                        send_message(chat_id, "Tugmalardan birini tanlang yoki masalan: 'Galaxy A15', 'iPhone 15' deb yozing.", get_main_keyboard())

        time.sleep(1)

if __name__ == '__main__':
    main()

