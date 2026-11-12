"""
====================================================================
SmartPrice AI - Telegram Bot (@telefonnarxx_bot)
Mobil telefonlar narxini aniqlash va baholash bo'yicha Telegram Bot.

Imkoniyatlar:
- 65+ ta mashhur mobil telefonlar bazasi (iPhone, Galaxy, Redmi, POCO, Honor, Realme, Pixel)
- Telefon nomlarini turli xil zamonaviy yozuv turlarida (shriftlarda) chiqarish
- Scikit-learn AI modeli orqali narx toifasini aniqlash (96.5% aniqlik)
- Real vaqtdagi Markaziy Bank (CBU) dollari kursi bilan UZS hisoblash
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

# Foydalanuvchilarning tanlagan yozuv turi (chat_id -> font_mode)
USER_FONTS = {}

def format_styled_phone_name(name, style='bold_sans'):
    """Telefon nomini ko'rkam va zamonaviy yozuv turlariga o'girish"""
    if style == 'standard':
        return name

    out = []
    for c in name:
        if style == 'bold_serif':
            if 'A' <= c <= 'Z': out.append(chr(ord(c) - ord('A') + 0x1D400))
            elif 'a' <= c <= 'z': out.append(chr(ord(c) - ord('a') + 0x1D41A))
            elif '0' <= c <= '9': out.append(chr(ord(c) - ord('0') + 0x1D7CE))
            else: out.append(c)
        elif style == 'mono':
            if 'A' <= c <= 'Z': out.append(chr(ord(c) - ord('A') + 0x1D670))
            elif 'a' <= c <= 'z': out.append(chr(ord(c) - ord('a') + 0x1D68A))
            elif '0' <= c <= '9': out.append(chr(ord(c) - ord('0') + 0x1D7F6))
            else: out.append(c)
        else: # bold_sans (default)
            if 'A' <= c <= 'Z': out.append(chr(ord(c) - ord('A') + 0x1D5D4))
            elif 'a' <= c <= 'z': out.append(chr(ord(c) - ord('a') + 0x1D5EE))
            elif '0' <= c <= '9': out.append(chr(ord(c) - ord('0') + 0x1D7EC))
            else: out.append(c)
    return ''.join(out)

def telegram_api(method, payload=None):
    """Telegram Bot API bilan xavfsiz HTTP so'rov"""
    url = f"{API_URL}/{method}"
    headers = {'Content-Type': 'application/json'}
    data = json.dumps(payload).encode('utf-8') if payload else None
    req = urllib.request.Request(url, data=data, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=35) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        err_body = e.read().decode('utf-8', errors='ignore')
        print(f"❌ Telegram API HTTPError ({method}): {e.code} - {err_body}")
        return None
    except Exception as e:
        print(f"❌ Telegram API xatoligi ({method}): {e}")
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
    res = telegram_api('sendMessage', payload)
    if not res or not res.get('ok'):
        # HTML xatolik bersa, teglarni tozalab oddiy matn ko'rinishida qayta yuborish
        plain_text = re.sub(r'<[^>]+>', '', text)
        payload['text'] = plain_text
        payload.pop('parse_mode', None)
        res = telegram_api('sendMessage', payload)
    return res

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
            [{'text': '🍏 Apple iPhone (12)'}, {'text': '🔷 Samsung Galaxy (15)'}],
            [{'text': '🟠 Xiaomi & Redmi (12)'}, {'text': '🚀 POCO (6)'}],
            [{'text': '🟡 Honor & Realme (13)'}, {'text': '🟢 Pixel & Boshqalar (7)'}],
            [{'text': '🎨 Yozuv turini tanlash'}, {'text': '⚙️ O\'z parametrlaringiz'}],
            [
                {'text': '🌐 Saytni Ochish (Mini App)', 'web_app': {'url': WEB_APP_URL}},
                {'text': '💵 Jonli Dollar Kursi'}
            ],
            [{'text': '🌐 Sayt Havolasi (Brauzer)'}, {'text': 'ℹ️ Bot haqida'}],
            [{'text': '📞 Bog\'lanish / Aloqa'}]
        ],
        'resize_keyboard': True
    }

def get_apple_keyboard():
    return {
        'keyboard': [
            [{'text': '📱 iPhone 16 Pro Max'}, {'text': '📱 iPhone 16 Pro'}],
            [{'text': '📱 iPhone 16'}, {'text': '📱 iPhone 15 Pro Max'}],
            [{'text': '📱 iPhone 15'}, {'text': '📱 iPhone 14 Pro Max'}],
            [{'text': '📱 iPhone 14'}, {'text': '📱 iPhone 13'}],
            [{'text': '📱 iPhone 12'}, {'text': '📱 iPhone 11'}, {'text': '📱 iPhone SE'}],
            [{'text': '🔙 Asosiy Menyu'}]
        ],
        'resize_keyboard': True
    }

def get_samsung_keyboard():
    return {
        'keyboard': [
            [{'text': '📱 Galaxy S24 Ultra'}, {'text': '📱 Galaxy S24+'}],
            [{'text': '📱 Galaxy S24'}, {'text': '📱 Galaxy S23 Ultra'}],
            [{'text': '📱 Galaxy S23 FE'}, {'text': '📱 Galaxy Z Fold 5'}],
            [{'text': '📱 Galaxy A55 5G'}, {'text': '📱 Galaxy A35 5G'}],
            [{'text': '📱 Galaxy A25 5G'}, {'text': '📱 Galaxy A15'}],
            [{'text': '📱 Galaxy A05s'}, {'text': '📱 Galaxy A05'}],
            [{'text': '🔙 Asosiy Menyu'}]
        ],
        'resize_keyboard': True
    }

def get_xiaomi_keyboard():
    return {
        'keyboard': [
            [{'text': '📱 Xiaomi 14 Ultra'}, {'text': '📱 Xiaomi 14'}],
            [{'text': '📱 Xiaomi 13T Pro'}, {'text': '📱 Redmi Note 13 Pro+'}],
            [{'text': '📱 Redmi Note 13 Pro 4G'}, {'text': '📱 Redmi Note 13'}],
            [{'text': '📱 Redmi 13'}, {'text': '📱 Redmi 13C'}],
            [{'text': '📱 Redmi 12'}, {'text': '📱 Redmi A3'}],
            [{'text': '🔙 Asosiy Menyu'}]
        ],
        'resize_keyboard': True
    }

def get_poco_keyboard():
    return {
        'keyboard': [
            [{'text': '📱 POCO F6 Pro'}, {'text': '📱 POCO F6'}],
            [{'text': '📱 POCO X6 Pro 5G'}, {'text': '📱 POCO X6 5G'}],
            [{'text': '📱 POCO M6 Pro'}, {'text': '📱 POCO C65'}],
            [{'text': '🔙 Asosiy Menyu'}]
        ],
        'resize_keyboard': True
    }

def get_honor_realme_keyboard():
    return {
        'keyboard': [
            [{'text': '📱 Honor Magic 6 Pro'}, {'text': '📱 Honor 200 Pro'}],
            [{'text': '📱 Honor 90'}, {'text': '📱 Honor X9b'}],
            [{'text': '📱 Honor X8b'}, {'text': '📱 Honor X7b'}],
            [{'text': '📱 Realme GT 6'}, {'text': '📱 Realme 12 Pro+'}],
            [{'text': '📱 Realme 12 Pro'}, {'text': '📱 Realme C67'}],
            [{'text': '📱 Realme C55'}, {'text': '📱 Realme Note 50'}],
            [{'text': '🔙 Asosiy Menyu'}]
        ],
        'resize_keyboard': True
    }

def get_pixel_other_keyboard():
    return {
        'keyboard': [
            [{'text': '📱 Pixel 8 Pro'}, {'text': '📱 Pixel 8a'}],
            [{'text': '📱 Pixel 7a'}, {'text': '📱 Infinix GT 20 Pro'}],
            [{'text': '📱 Infinix Note 40 Pro'}, {'text': '📱 Tecno Camon 30 Pro'}],
            [{'text': '📱 Tecno Spark 20 Pro'}],
            [{'text': '🔙 Asosiy Menyu'}]
        ],
        'resize_keyboard': True
    }

def get_font_selection_keyboard():
    return {
        'keyboard': [
            [{'text': '✨ 𝟭. 𝗕𝗼𝗹𝗱 𝗦𝗮𝗻𝘀 (Zamonaviy)'}, {'text': '👑 𝟐. 𝐁𝐨𝐥𝐝 𝐒𝐞𝐫𝐢𝐟 (Lyuks)'}],
            [{'text': '🚀 𝟹. 𝙼𝚘𝚗𝚘𝚜𝚙𝚊𝚌𝚎 (Texno)'}, {'text': '📱 4. Standart (Oddiy)'}],
            [{'text': '🔙 Asosiy Menyu'}]
        ],
        'resize_keyboard': True
    }

def get_phone_inline_buttons(model_key):
    clean_key = model_key.replace(' ', '_').strip().lower()
    target_url = f"{WEB_APP_URL}?model={clean_key}"
    return {
        'inline_keyboard': [
            [
                {'text': '🌐 Saytda ko\'rish (Brauzer)', 'url': target_url},
                {'text': '📱 Mini Appda ochish', 'web_app': {'url': target_url}}
            ],
            [
                {'text': '🔄 Boshqa model tanlash', 'callback_data': 'back_to_menu'}
            ]
        ]
    }

def get_competitor_comparison(current_key, usd_price, live_rate):
    """Shu narx toifasidagi boshqa raqobatchi modellarni topish va solishtirish"""
    candidates = []
    brand_prefix = ""
    if current_key and current_key in PHONE_MODELS:
        brand_prefix = PHONE_MODELS[current_key]['name'].split()[0]

    for k, m in PHONE_MODELS.items():
        if k != current_key and (not brand_prefix or not m['name'].startswith(brand_prefix)):
            diff = abs(m['usd_price'] - usd_price)
            candidates.append((diff, m))

    candidates.sort(key=lambda x: x[0])
    comps = candidates[:3]

    res = []
    for diff, c in comps:
        c_uzs = round(c['usd_price'] * live_rate / 10000) * 10000
        res.append(f" • <b>{c['name']}:</b> <code>{format_num(c_uzs)} so'm</code> (≈ ${c['usd_price']})")
    return "\n".join(res)

def get_storage_breakdown(usd_price, base_storage, live_rate):
    """Turli xotira variantlari bo'yicha narxlar"""
    step = 40 if usd_price < 250 else (75 if usd_price < 700 else 120)
    v128_usd = usd_price if base_storage <= 128 else usd_price - step
    v256_usd = (usd_price + step) if base_storage <= 128 else usd_price
    v512_usd = v256_usd + round(step * 1.5)

    v128_uzs = round(v128_usd * live_rate / 10000) * 10000
    v256_uzs = round(v256_usd * live_rate / 10000) * 10000
    v512_uzs = round(v512_usd * live_rate / 10000) * 10000

    return (
        f" • <b>128 GB:</b> <code>{format_num(v128_uzs)} so'm</code> (≈ ${v128_usd})\n"
        f" • <b>256 GB:</b> <code>{format_num(v256_uzs)} so'm</code> (≈ ${v256_usd})\n"
        f" • <b>512 GB:</b> <code>{format_num(v512_uzs)} so'm</code> (≈ ${v512_usd})"
    )

def get_condition_breakdown(uzs_price):
    """Yangi va B/U holatiga ko'ra narxlar"""
    bu_ideal = round(uzs_price * 0.80 / 10000) * 10000
    bu_mid = round(uzs_price * 0.68 / 10000) * 10000
    return (
        f" • 🆕 <b>Yangi (Pachka/Kafolatli):</b> ~<code>{format_num(uzs_price)} so'm</code>\n"
        f" • 📦 <b>B/U Ideal (Tirnalmagan):</b> ~<code>{format_num(bu_ideal)} so'm</code>\n"
        f" • 📱 <b>B/U O'rtacha ishlatilgan:</b> ~<code>{format_num(bu_mid)} so'm</code>"
    )

def get_expert_analysis(ram_mb, batt_mah, clock_ghz, usd_price):
    """Oddiy inson tilidagi batafsil AI xulosasi"""
    if ram_mb >= 3700 and clock_ghz >= 3.0:
        game = "PUBG Mobile (90-120 FPS), Genshin Impact va montaj maksimal grafikada qotmasdan silliq ishlaydi."
    elif ram_mb >= 2200:
        game = "PUBG Mobile (60 FPS), Telegram, Instagram va og'ir ilovalar bemalol ishlaydi."
    else:
        game = "Kundalik qo'ng'iroqlar, Telegram, Instagram, YouTube va yengil ilovalar uchun yetarli."

    batt_text = "1.5 - 2 kunga bemalol yetadi (zaryad tashvish bo'lmaydi)." if batt_mah >= 4800 else "1 kunlik to'liq faol ishlatishga yetadi."

    if usd_price >= 800:
        verdict = "👑 <b>Premium Flagman:</b> Eng sifatli korpus, eng kuchli kamera va uzoq yillik yuqori tezlik kafolatlangan."
    elif usd_price >= 300:
        verdict = "⚖️ <b>Narx/Sifat bo'yicha eng kuchli:</b> O'z sinfida raqobatchilaridan ustun va ommabop tanlov."
    else:
        verdict = "🪙 <b>Hamyonbop va tejamkor:</b> Ortiqcha xarajat qilmasdan barcha kundalik ishlarni bajarishga qulay."

    return (
        f"🎮 <b>O'yin va tezlik:</b> {game}\n"
        f"🔋 <b>Batareya sarfi:</b> {batt_text}\n"
        f"💡 <b>Xulosa:</b> {verdict}"
    )

def generate_phone_quote(model_key, live_rate, font_style='bold_sans'):
    """Telefon haqida to'liq hisob-kitob va chiroyli matn yaratish"""
    key_clean = model_key.replace('_', ' ').strip().lower()
    model = PHONE_MODELS.get(model_key) or PHONE_MODELS.get(key_clean) or PHONE_MODELS.get(model_key.replace(' ', '_').lower())
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

    styled_title = format_styled_phone_name(model['name'], font_style)

    msg = f"✨ ━━━━━━━━━━━━━━━━━━━━━━━ ✨\n"
    msg += f"📱 <b>【 {styled_title} 】</b>\n"
    msg += f"✨ ━━━━━━━━━━━━━━━━━━━━━━━ ✨\n\n"
    msg += f"💰 <b>O'rtacha bozor narxi:</b> <code>{format_num(uzs_price)} so'm</code> (≈ <b>${usd_price}</b>)\n"
    msg += f"📊 <b>Narx oralig'i:</b> {format_num(low_uzs)} — {format_num(high_uzs)} so'm\n"
    msg += f"🎯 <b>AI Toifasi:</b> {tiers[pred]}\n\n"

    msg += f"📦 <b>Xotirasiga ko'ra hozirgi narxlar:</b>\n"
    msg += get_storage_breakdown(usd_price, model.get('ichki_xotira_gb', 128), live_rate) + "\n\n"

    msg += f"🏷️ <b>Bozor holatiga ko'ra narxlar:</b>\n"
    msg += get_condition_breakdown(uzs_price) + "\n\n"

    msg += f"🔄 <b>Shu narxdagi boshqa telefonlar narxi:</b>\n"
    msg += get_competitor_comparison(model_key, usd_price, live_rate) + "\n\n"

    msg += f"💳 <b>Nasiya to'lov rejalari (Muddatli to'lov):</b>\n"
    msg += f" • <b>3 oy:</b> oyiga <code>{format_num(inst_3)}</code> so'mdan\n"
    msg += f" • <b>6 oy:</b> oyiga <code>{format_num(inst_6)}</code> so'mdan\n"
    msg += f" • <b>12 oy:</b> oyiga <code>{format_num(inst_12)}</code> so'mdan\n\n"

    msg += f"⚡ <b>Texnik ko'rsatkichlari:</b>\n"
    msg += f" • <b>RAM:</b> {model['ram_mb']} MB (~{(model['ram_mb']/1024):.1f} GB)\n"
    msg += f" • <b>Batareya:</b> {model['akkumulyator_quvvati']} mAh\n"
    msg += f" • <b>Asosiy kamera:</b> {model['asosiy_kamera_mp']} MP\n"
    msg += f" • <b>Doimiy xotira:</b> {model['ichki_xotira_gb']} GB\n"
    msg += f" • <b>Protsessor:</b> {model['protsessor_tezligi']} GHz\n\n"

    msg += f"📋 <b>Ekspert tahlili:</b>\n"
    msg += get_expert_analysis(model['ram_mb'], model['akkumulyator_quvvati'], model['protsessor_tezligi'], usd_price) + "\n"
    msg += f"━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    msg += f"🏛️ <i>Markaziy Bank kursi: 1 USD = {format_num(round(live_rate, 2))} UZS</i>"
    return msg

def predict_custom_specs(ram_gb, battery_mah, cam_mp, storage_gb, live_rate, font_style='bold_sans'):
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
    inst_3 = round(uzs * 1.06 / 3 / 1000) * 1000
    inst_6 = round(uzs * 1.10 / 6 / 1000) * 1000

    tiers = [
      "🟢 Hamyonbop (0-toifa)",
      "🔵 O'rta-Quyi sinf (1-toifa)",
      "🟣 O'rta-Yuqori sinf (2-toifa)",
      "👑 Flagman / Premium (3-toifa)"
    ]

    custom_title = format_styled_phone_name(f"{ram_gb}GB RAM • {storage_gb}GB Smartfon", font_style)

    msg = f"🔮 <b>【 {custom_title} 】</b>\n"
    msg += f"━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    msg += f"💰 <b>Taxminiy bozor narxi:</b> <code>{format_num(uzs)} so'm</code> (≈ <b>${usd}</b>)\n"
    msg += f"📊 <b>Narx oralig'i:</b> {format_num(low_uzs)} — {format_num(high_uzs)} so'm\n"
    msg += f"🎯 <b>AI Toifasi:</b> {tiers[pred]}\n\n"

    msg += f"🏷️ <b>Bozor holatiga ko'ra narxlar:</b>\n"
    msg += get_condition_breakdown(uzs) + "\n\n"

    msg += f"🔄 <b>Shu narxdagi boshqa telefonlar narxi:</b>\n"
    msg += get_competitor_comparison(None, usd, live_rate) + "\n\n"

    msg += f"💳 <b>Nasiya to'lov rejalari (Muddatli to'lov):</b>\n"
    msg += f" • <b>3 oy:</b> oyiga <code>{format_num(inst_3)}</code> so'mdan\n"
    msg += f" • <b>6 oy:</b> oyiga <code>{format_num(inst_6)}</code> so'mdan\n"
    msg += f" • <b>12 oy:</b> oyiga <code>{format_num(inst_12)}</code> so'mdan\n\n"

    msg += f"⚡ <b>Siz kiritgan parametrlar:</b>\n"
    msg += f" • <b>RAM:</b> {ram_gb} GB\n"
    msg += f" • <b>Batareya:</b> {battery_mah} mAh\n"
    msg += f" • <b>Kamera:</b> {cam_mp} MP\n"
    msg += f" • <b>Xotira:</b> {storage_gb} GB\n\n"

    msg += f"📋 <b>Ekspert tahlili:</b>\n"
    msg += get_expert_analysis(ram_mb, battery_mah, 2.4, usd) + "\n"
    msg += f"━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    msg += f"🟢 <i>Markaziy Bank kursi: 1 USD = {format_num(round(live_rate, 2))} UZS</i>"
    return msg

def parse_specs_from_text(text):
    """Matndan RAM, Batareya, Kamera va Xotira raqamlarini ajratish"""
    numbers = [int(n) for n in re.findall(r'\b\d+\b', text)]
    if len(numbers) >= 4:
        ram = numbers[0] if numbers[0] < 32 else 8
        batt = numbers[1] if numbers[1] >= 1000 else 5000
        cam = numbers[2] if numbers[2] <= 200 else 50
        storage = numbers[3] if numbers[3] >= 16 else 128
        return ram, batt, cam, storage
    return None

def find_best_model_match(query):
    """Kiritilgan matnga eng mos keluvchi telefon modelini topish"""
    q = query.lower().replace("📱", "").strip()
    
    # Generic brend so'zlari bo'lsa model emas, brend menyusi ochilishi kerak
    if q in {'apple', 'samsung', 'galaxy', 'xiaomi', 'redmi', 'poco', 'honor', 'realme', 'pixel', 'infinix', 'tecno', 'ayfon'}:
        return None

    # 1. To'g'ridan-to'g'ri kalit mosligi
    if q in PHONE_MODELS:
        return q

    # 2. Model nomidagi to'liq moslik
    for key, model in PHONE_MODELS.items():
        if q == model['name'].lower():
            return key

    # 3. Model kalitidagi to'liq so'zlar bo'yicha qidiruv (aniq moslikni tanlaydi)
    q_words = [w for w in re.split(r'[\s\-_]+', q) if len(w) > 1]
    if q_words:
        best_key = None
        max_matches = 0
        min_diff = 99
        for key, model in PHONE_MODELS.items():
            name_lower = model['name'].lower()
            combined = f"{key} {name_lower}"
            matches = sum(1 for w in q_words if w in combined)
            k_len = len(key.split())
            diff = abs(k_len - len(q_words))
            if matches > max_matches or (matches == max_matches and diff < min_diff):
                max_matches = matches
                min_diff = diff
                best_key = key
        if max_matches >= max(1, len(q_words)):
            return best_key

    # 4. Substring qidiruvi (kamida 4 ta harf bo'lsa)
    if len(q) >= 4:
        for key, model in PHONE_MODELS.items():
            if q in model['name'].lower() or key in q:
                return key

    return None

def main():
    print("=" * 65)
    print("🚀 SmartPrice AI Telegram Bot ishga tushirilmoqda...")
    print(f"🤖 Bot Token: {BOT_TOKEN[:10]}...{BOT_TOKEN[-5:]}")
    print(f"📱 Mavjud telefon modellari: {len(PHONE_MODELS)} ta")
    print("=" * 65)

    me = telegram_api('getMe')
    if not me or not me.get('ok'):
        print(f"❌ Xatolik: Bot tokeni yaroqsiz yoki internet mavjud emas: {me}")
        return

    bot_info = me['result']
    print(f"✅ Bot muvaffaqiyatli ulandi!")
    print(f"• Nomi: {bot_info.get('first_name')}")
    print(f"• Username: @{bot_info.get('username')}")
    print("Xabarlar qabul qilinmoqda... (Polling faol)\n")

    offset = None
    live_rate = get_live_usd_rate()
    last_rate_time = time.time()

    while True:
        try:
            if time.time() - last_rate_time > 300:
                live_rate = get_live_usd_rate()
                last_rate_time = time.time()

            updates = get_updates(offset)
            if updates and updates.get('ok'):
                for update in updates.get('result', []):
                    offset = update['update_id'] + 1
                    
                    # Inline tugma callback so'rovlarini to'g'ri qayta ishlash
                    if 'callback_query' in update:
                        cb = update['callback_query']
                        cb_id = cb.get('id')
                        cb_data = cb.get('data')
                        chat_id = cb.get('message', {}).get('chat', {}).get('id')
                        telegram_api('answerCallbackQuery', {'callback_query_id': cb_id})
                        if cb_data == 'back_to_menu' and chat_id:
                            send_message(chat_id, "Asosiy menyuga qaytdingiz. Kerakli brendni tanlang yoki telefon nomini yozing:", get_main_keyboard())
                        continue

                    msg = update.get('message', {})
                    chat_id = msg.get('chat', {}).get('id')
                    text = (msg.get('text') or '').strip()
                    lower_text = text.lower()

                    if not chat_id:
                        continue

                    font_style = USER_FONTS.get(chat_id, 'bold_sans')
                    send_chat_action(chat_id, "typing")

                    # Buyruqlar va xabarlar
                    if lower_text.startswith('/start'):
                        # Veb-saytdan chuqur havola (deep linking): masalan /start galaxy_s24_ultra
                        parts = text.split(maxsplit=1)
                        if len(parts) > 1 and parts[1].strip():
                            param = parts[1].strip()
                            matched = find_best_model_match(param)
                            if matched:
                                quote = generate_phone_quote(matched, live_rate, font_style)
                                send_message(
                                    chat_id, 
                                    f"🌐 <b>Veb-saytdan tanlangan model bahosi:</b>\n\n{quote}", 
                                    get_phone_inline_buttons(matched)
                                )
                                continue

                        welcome = (
                            f"👋 Assalomu alaykum! <b>SmartPrice AI</b> rasmiy botiga xush kelibsiz! 📱\n\n"
                            f"Bazada <b>65+ ta</b> eng so'nggi va mashhur telefonlar mavjud.\n"
                            f"Men sun'iy intellekt (Scikit-Learn) va Markaziy Bankning jonli kursi asosida "
                            f"telefonlarning <b>haqqoniy bozor narxi</b> va <b>nasiya to'lovlarini</b> hisoblab beraman.\n\n"
                            f"🔗 <b>Rasmiy Veb-Sayt:</b> {WEB_APP_URL}\n"
                            f"📞 <b>Bog'lanish:</b> @Sbrjonv • <code>+998 94 215 01 21</code>\n\n"
                            f"👇 <i>Kerakli brendni tanlang yoki telefon nomini yozing:</i>"
                        )
                        send_message(chat_id, welcome, get_main_keyboard())

                    # 1. Telefon modeli tugmasi bosilganmi (masalan: "📱 iPhone 16 Pro Max", "📱 Galaxy A15")?
                    elif text.startswith('📱 ') or text.startswith('📱'):
                        matched_key = find_best_model_match(text)
                        if matched_key:
                            print(f"📱 Telefon tanlandi: {matched_key} (chat_id: {chat_id})")
                            quote = generate_phone_quote(matched_key, live_rate, font_style)
                            inline_markup = get_phone_inline_buttons(matched_key)
                            send_message(chat_id, quote, inline_markup)
                        else:
                            send_message(chat_id, f"⚠️ Kechirasiz, '{text}' modeli bazadan topilmadi.", get_main_keyboard())

                    elif lower_text in ['salom', 'assalomu alaykum', '🔙 asosiy menyu', 'menyu', 'menu']:
                        send_message(chat_id, "Asosiy menyudasiz. Kerakli brendni tanlang yoki telefon nomini yozing:", get_main_keyboard())

                    # 2. Menyu bo'limlari (Brendlar menyusi)
                    elif text == '🍏 Apple iPhone (12)' or lower_text in ['apple', 'ayfon', 'apple iphone']:
                        send_message(chat_id, "🍏 <b>Apple iPhone</b> modellaridan birini tanlang (12 ta model):", get_apple_keyboard())

                    elif text == '🔷 Samsung Galaxy (15)' or lower_text in ['samsung', 'galaxy', 'samsung galaxy']:
                        send_message(chat_id, "🔷 <b>Samsung Galaxy</b> modellaridan birini tanlang (15 ta model):", get_samsung_keyboard())

                    elif text == '🟠 Xiaomi & Redmi (12)' or lower_text in ['xiaomi', 'redmi', 'xiaomi redmi', 'mi']:
                        send_message(chat_id, "🟠 <b>Xiaomi / Redmi</b> modellaridan birini tanlang (12 ta model):", get_xiaomi_keyboard())

                    elif text == '🚀 POCO (6)' or lower_text in ['poco']:
                        send_message(chat_id, "🚀 <b>POCO</b> modellaridan birini tanlang (6 ta model):", get_poco_keyboard())

                    elif text == '🟡 Honor & Realme (13)' or lower_text in ['honor', 'realme', 'honor realme']:
                        send_message(chat_id, "🟡 <b>Honor va Realme</b> modellaridan birini tanlang (13 ta model):", get_honor_realme_keyboard())

                    elif text == '🟢 Pixel & Boshqalar (7)' or lower_text in ['pixel', 'infinix', 'tecno', 'boshqalar', 'google pixel']:
                        send_message(chat_id, "🟢 <b>Google Pixel, Infinix & Tecno</b> modellaridan birini tanlang:", get_pixel_other_keyboard())

                    # Yozuv turini o'zgartirish (Shriftlar)
                    elif 'yozuv turi' in lower_text or 'shrift' in lower_text or '/font' in lower_text:
                        font_msg = (
                            f"🎨 <b>Telefon nomlari qaysi yozuv turida (shriftda) chiqsin?</b>\n\n"
                            f"Hozirgi yozuv turi: <b>{font_style}</b>\n\n"
                            f"Quyidagilardan birini tanlang:\n"
                            f"• ✨ <b>𝟭. 𝗕𝗼𝗹𝗱 𝗦𝗮𝗻𝘀</b> — Zamonaviy va qalin\n"
                            f"• 👑 <b>𝟐. 𝐁𝐨𝐥𝐝 𝐒𝐞𝐫𝐢𝐟</b> — Klassik va lyuks\n"
                            f"• 🚀 <b>𝟹. 𝙼𝚘𝚗𝚘𝚜𝚙𝚊𝚌𝚎</b> — Kiber va texno\n"
                            f"• 📱 <b>4. Standart</b> — Oddiy telegram matni"
                        )
                        send_message(chat_id, font_msg, get_font_selection_keyboard())

                    elif 'bold sans' in lower_text or '1.' in lower_text:
                        USER_FONTS[chat_id] = 'bold_sans'
                        send_message(chat_id, "✅ Yozuv turi: <b>𝗕𝗼𝗹𝗱 𝗦𝗮𝗻𝘀</b> qilib belgilandi! Endi barcha telefon nomlari zamonaviy uslubda chiqadi.", get_main_keyboard())

                    elif 'bold serif' in lower_text or '2.' in lower_text:
                        USER_FONTS[chat_id] = 'bold_serif'
                        send_message(chat_id, "✅ Yozuv turi: <b>𝐁𝐨𝐥𝐝 𝐒𝐞𝐫𝐢𝐟</b> qilib belgilandi! Endi barcha telefon nomlari klassik lyuks uslubda chiqadi.", get_main_keyboard())

                    elif 'monospace' in lower_text or '3.' in lower_text:
                        USER_FONTS[chat_id] = 'mono'
                        send_message(chat_id, "✅ Yozuv turi: <b>𝙼𝚘𝚗𝚘𝚜𝚙𝚊𝚌𝚎</b> qilib belgilandi! Endi barcha telefon nomlari texno uslubda chiqadi.", get_main_keyboard())

                    elif 'standart' in lower_text or '4.' in lower_text:
                        USER_FONTS[chat_id] = 'standard'
                        send_message(chat_id, "✅ Yozuv turi: <b>Standart</b> qilib belgilandi.", get_main_keyboard())

                    # Jonli dollar kursi
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

                    # Web sayt
                    elif 'web sayt' in lower_text or 'sayt' in lower_text or 'saytni ochish' in lower_text or '/sayt' in lower_text or '/web' in lower_text:
                        web_msg = (
                            f"🌐 <b>SmartPrice AI Veb-Platformasi:</b>\n\n"
                            f"Siz barcha 65+ modellarni interaktiv slayderlar orqali boshqarishingiz, "
                            f"shriftlarni almashtirishingiz va grafik tahlillarni ko'rishingiz mumkin:\n\n"
                            f"🔗 <b>Jonli veb-sayt:</b> {WEB_APP_URL}\n"
                            f"💻 <b>Lokal server:</b> http://localhost:8000\n"
                            f"📂 <b>GitHub Repo:</b> https://github.com/soxibs48-eng/dataset"
                        )
                        markup = {
                            'inline_keyboard': [
                                [
                                    {'text': '🚀 Brauzerda ochish', 'url': WEB_APP_URL},
                                    {'text': '📱 Mini Appda ochish', 'web_app': {'url': WEB_APP_URL}}
                                ]
                            ]
                        }
                        send_message(chat_id, web_msg, markup)

                    # Info
                    elif 'haqida' in lower_text or '/info' in lower_text:
                        about = (
                            "ℹ️ <b>SmartPrice AI Loyihasi haqida:</b>\n\n"
                            "• <b>Modellar bazasi:</b> 65+ ta mashhur smartfonlar\n"
                            "• <b>ML Model:</b> Scikit-learn (Logistic Regression, 96.5% aniqlik)\n"
                            "• <b>Dataset:</b> Kaggle Mobile Price Classification\n"
                            "• <b>Valyuta kursi:</b> O'zbekiston Markaziy Banki jonli API\n"
                            "• <b>Muallif:</b> Soxibjon (@Sbrjonv)\n"
                            "• <b>Aloqa:</b> @Sbrjonv • +998 94 215 01 21\n"
                            "• <b>Kod ombori:</b> https://github.com/soxibs48-eng/dataset"
                        )
                        send_message(chat_id, about, get_main_keyboard())

                    # Aloqa / Bog'lanish
                    elif 'aloqa' in lower_text or 'bog\'lanish' in lower_text or 'boglanish' in lower_text or '/contact' in lower_text or 'kontakt' in lower_text or 'admin' in lower_text or 'telefon' in lower_text and len(lower_text) < 15:
                        contact_msg = (
                            "📞 <b>Biz bilan bog'lanish:</b>\n\n"
                            "Har qanday savol, taklif yoki hamkorlik bo'yicha bemalol murojaat qilishingiz mumkin:\n\n"
                            "👤 <b>Administrator:</b> @Sbrjonv\n"
                            "💬 <b>Telegram:</b> <a href=\"https://t.me/Sbrjonv\">@Sbrjonv</a>\n"
                            "📞 <b>Telefon raqam:</b> <code>+998 94 215 01 21</code>\n\n"
                            "⏰ <i>24/7 aloqadamiz!</i>"
                        )
                        contact_markup = {
                            'inline_keyboard': [
                                [
                                    {'text': '💬 Telegramda yozish (@Sbrjonv)', 'url': 'https://t.me/Sbrjonv'}
                                ]
                            ]
                        }
                        send_message(chat_id, contact_msg, contact_markup)

                    # Custom parametrlar
                    elif 'parametr' in lower_text or 'o\'z parametr' in lower_text:
                        param_msg = (
                            "⚙️ <b>O'zingiz xohlagan telefon parametrlarini yuboring!</b>\n\n"
                            "Format: <code>RAM Batareya Kamera Xotira</code>\n"
                            "Masalan: <code>8 5000 50 128</code>\n\n"
                            "<i>(Bu: 8GB RAM, 5000 mAh batareya, 50 MP kamera va 128 GB xotirani bildiradi)</i>"
                        )
                        send_message(chat_id, param_msg, get_main_keyboard())

                    else:
                        # Tekshiruv 1: Custom raqamli parametrlar kiritilganmi?
                        specs = parse_specs_from_text(text)
                        if specs:
                            ram_g, batt_m, cam_m, stor_g = specs
                            quote = predict_custom_specs(ram_g, batt_m, cam_m, stor_g, live_rate, font_style)
                            send_message(chat_id, quote, get_main_keyboard())
                            continue

                        # Tekshiruv 2: 65+ telefon modellari bo'yicha qidiruv
                        matched_key = find_best_model_match(text)
                        if matched_key:
                            print(f"🔍 Matn orqali model topildi: {matched_key} (chat_id: {chat_id})")
                            quote = generate_phone_quote(matched_key, live_rate, font_style)
                            inline_markup = get_phone_inline_buttons(matched_key)
                            send_message(chat_id, quote, inline_markup)
                        else:
                            fallback = (
                                f"🤖 Kechirasiz, <i>'{text}'</i> bo'yicha aniq model topilmadi.\n\n"
                                f"Quyidagi tugmalardan birini bosing yoki 65+ modeldan birini yozing "
                                f"(masalan: <b>iPhone 16 Pro</b>, <b>Galaxy S24 Ultra</b>, <b>POCO X6 Pro</b>, <b>Honor 90</b>).\n\n"
                                f"Yoki o'z parametrlaringizni kiriting: <code>8 5000 50 128</code>"
                            )
                            send_message(chat_id, fallback, get_main_keyboard())

            time.sleep(1)

        except Exception as err:
            print(f"Xatolik yuz berdi: {err}")
            time.sleep(3)

if __name__ == '__main__':
    main()
