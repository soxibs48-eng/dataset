import os
import shutil
import json
import kagglehub
import pandas as pd

def main():
    print("1. Kaggle'dan ma'lumotlar to'plami yuklab olinmoqda...")
    raw_path = kagglehub.dataset_download("iabhishekofficial/mobile-price-classification")
    print(f"Dataset yuklangan manzil: {raw_path}")

    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Papkalar yaratish
    dirs = {
        'original': os.path.join(base_dir, 'original'),
        'en': os.path.join(base_dir, 'en'),
        'uz': os.path.join(base_dir, 'uz'),
        'ru': os.path.join(base_dir, 'ru')
    }
    
    for d in dirs.values():
        os.makedirs(d, exist_ok=True)

    # Asl fayllarni o'qish
    train_raw = pd.read_csv(os.path.join(raw_path, 'train.csv'))
    test_raw = pd.read_csv(os.path.join(raw_path, 'test.csv'))

    # 1. Asl fayllarni nusxalash
    train_raw.to_csv(os.path.join(dirs['original'], 'train.csv'), index=False)
    test_raw.to_csv(os.path.join(dirs['original'], 'test.csv'), index=False)
    print("✓ Asl fayllar 'original/' papkasiga saqlandi.")

    # 2. English (Ingliz tili)
    train_raw.to_csv(os.path.join(dirs['en'], 'train_en.csv'), index=False)
    test_raw.to_csv(os.path.join(dirs['en'], 'test_en.csv'), index=False)

    binary_cols = ['blue', 'dual_sim', 'four_g', 'three_g', 'touch_screen', 'wifi']

    # English labeled
    train_en_labeled = train_raw.copy()
    for col in binary_cols:
        train_en_labeled[col] = train_en_labeled[col].map({0: 'No', 1: 'Yes'})
    train_en_labeled['price_range'] = train_en_labeled['price_range'].map({
        0: '0 - Low Cost',
        1: '1 - Medium Cost',
        2: '2 - High Cost',
        3: '3 - Very High Cost'
    })
    train_en_labeled.to_csv(os.path.join(dirs['en'], 'train_en_labeled.csv'), index=False)
    print("✓ Inglizcha fayllar 'en/' papkasiga saqlandi.")

    # 3. O'zbek tili (Uzbek)
    uz_col_map = {
        'id': 'id',
        'battery_power': 'akkumulyator_quvvati',
        'blue': 'bluetooth',
        'clock_speed': 'protsessor_tezligi',
        'dual_sim': 'ikkita_sim',
        'fc': 'old_kamera_mp',
        'four_g': 'tort_g',
        'int_memory': 'ichki_xotira_gb',
        'm_dep': 'qalinligi_sm',
        'mobile_wt': 'telefon_vazni_gr',
        'n_cores': 'yadro_soni',
        'pc': 'asosiy_kamera_mp',
        'px_height': 'piksel_balandligi',
        'px_width': 'piksel_kengligi',
        'ram': 'ram_mb',
        'sc_h': 'ekran_balandligi_sm',
        'sc_w': 'ekran_kengligi_sm',
        'talk_time': 'gaplashish_vaqti_soat',
        'three_g': 'uch_g',
        'touch_screen': 'sensorli_ekran',
        'wifi': 'wifi',
        'price_range': 'narx_toifasi'
    }

    train_uz = train_raw.rename(columns=uz_col_map)
    test_uz = test_raw.rename(columns=uz_col_map)
    train_uz.to_csv(os.path.join(dirs['uz'], 'train_uz.csv'), index=False)
    test_uz.to_csv(os.path.join(dirs['uz'], 'test_uz.csv'), index=False)

    # Uzbek tavsifli (matnli)
    train_uz_tavsifli = train_uz.copy()
    uz_binary_cols = ['bluetooth', 'ikkita_sim', 'tort_g', 'uch_g', 'sensorli_ekran', 'wifi']
    for col in uz_binary_cols:
        train_uz_tavsifli[col] = train_uz_tavsifli[col].map({0: "Yo'q", 1: "Bor"})
    train_uz_tavsifli['narx_toifasi'] = train_uz_tavsifli['narx_toifasi'].map({
        0: "0 - Arzon",
        1: "1 - O'rtacha",
        2: "2 - Qimmat",
        3: "3 - Juda qimmat"
    })
    train_uz_tavsifli.to_csv(os.path.join(dirs['uz'], 'train_uz_tavsifli.csv'), index=False)
    print("✓ O'zbekcha fayllar 'uz/' papkasiga saqlandi.")

    # 4. Rus tili (Russian)
    ru_col_map = {
        'id': 'id',
        'battery_power': 'emkost_batarei_mach',
        'blue': 'bluetooth',
        'clock_speed': 'taktovaya_chastota_ggts',
        'dual_sim': 'dve_sim_karty',
        'fc': 'front_kamera_mp',
        'four_g': 'four_g',
        'int_memory': 'vstroennaya_pamyat_gb',
        'm_dep': 'tolschina_sm',
        'mobile_wt': 'ves_telefona_gr',
        'n_cores': 'kolichestvo_yader',
        'pc': 'osnovnaya_kamera_mp',
        'px_height': 'vysota_razresheniya_px',
        'px_width': 'shirina_razresheniya_px',
        'ram': 'ram_mb',
        'sc_h': 'vysota_ekrana_sm',
        'sc_w': 'shirina_ekrana_sm',
        'talk_time': 'vremya_razgovora_ch',
        'three_g': 'three_g',
        'touch_screen': 'sensornyy_ekran',
        'wifi': 'wifi',
        'price_range': 'diapazon_cen'
    }

    train_ru = train_raw.rename(columns=ru_col_map)
    test_ru = test_raw.rename(columns=ru_col_map)
    train_ru.to_csv(os.path.join(dirs['ru'], 'train_ru.csv'), index=False)
    test_ru.to_csv(os.path.join(dirs['ru'], 'test_ru.csv'), index=False)

    # Russian opisanie (tekstoviy)
    train_ru_opisanie = train_ru.copy()
    ru_binary_cols = ['bluetooth', 'dve_sim_karty', 'four_g', 'three_g', 'sensornyy_ekran', 'wifi']
    for col in ru_binary_cols:
        train_ru_opisanie[col] = train_ru_opisanie[col].map({0: "Нет", 1: "Есть"})
    train_ru_opisanie['diapazon_cen'] = train_ru_opisanie['diapazon_cen'].map({
        0: "0 - Низкая цена",
        1: "1 - Средняя цена",
        2: "2 - Высокая цена",
        3: "3 - Очень высокая цена"
    })
    train_ru_opisanie.to_csv(os.path.join(dirs['ru'], 'train_ru_opisanie.csv'), index=False)
    print("✓ Ruscha fayllar 'ru/' papkasiga saqlandi.")

    # Metadata / Lug'at yaratish
    features_metadata = [
        {
            "original_name": "battery_power",
            "uz": "Akkumulyator quvvati (mAh)",
            "uz_col": "akkumulyator_quvvati",
            "ru": "Емкость аккумулятора (мАч)",
            "ru_col": "emkost_batarei_mach",
            "en": "Battery Power (mAh)",
            "en_col": "battery_power",
            "description_uz": "Akkumulyatorning bir marta to'liq quvvatlangandagi sig'imi (mAh)",
            "description_ru": "Общая емкость батареи за один раз, измеряется в мАч",
            "description_en": "Total energy a battery can store in one time measured in mAh"
        },
        {
            "original_name": "blue",
            "uz": "Bluetooth (Bor/Yo'q)",
            "uz_col": "bluetooth",
            "ru": "Bluetooth (Есть/Нет)",
            "ru_col": "bluetooth",
            "en": "Bluetooth (Yes/No)",
            "en_col": "blue",
            "description_uz": "Bluetooth qo'llab-quvvatlashi: 1 = Bor, 0 = Yo'q",
            "description_ru": "Наличие Bluetooth: 1 = Есть, 0 = Нет",
            "description_en": "Has Bluetooth support: 1 = Yes, 0 = No"
        },
        {
            "original_name": "clock_speed",
            "uz": "Protsessor chastotasi (GHz)",
            "uz_col": "protsessor_tezligi",
            "ru": "Тактовая частота процессора (ГГц)",
            "ru_col": "taktovaya_chastota_ggts",
            "en": "Processor Clock Speed (GHz)",
            "en_col": "clock_speed",
            "description_uz": "Mikroprotsessor ko'rsatmalarni bajarish tezligi (GHz)",
            "description_ru": "Скорость выполнения инструкций микропроцессором (ГГц)",
            "description_en": "Speed at which microprocessor executes instructions (GHz)"
        },
        {
            "original_name": "dual_sim",
            "uz": "Ikkita SIM-karta (Bor/Yo'q)",
            "uz_col": "ikkita_sim",
            "ru": "Две SIM-карты (Есть/Нет)",
            "ru_col": "dve_sim_karty",
            "en": "Dual SIM (Yes/No)",
            "en_col": "dual_sim",
            "description_uz": "Ikkita SIM-kartani qo'llab-quvvatlashi: 1 = Bor, 0 = Yo'q",
            "description_ru": "Поддержка двух SIM-карт: 1 = Есть, 0 = Нет",
            "description_en": "Has dual sim support: 1 = Yes, 0 = No"
        },
        {
            "original_name": "fc",
            "uz": "Old kamera (MP)",
            "uz_col": "old_kamera_mp",
            "ru": "Фронтальная камера (Мп)",
            "ru_col": "front_kamera_mp",
            "en": "Front Camera (MP)",
            "en_col": "fc",
            "description_uz": "Old (selfi) kamera ruxsati megapiksellarda",
            "description_ru": "Разрешение фронтальной камеры в мегапикселях",
            "description_en": "Front Camera megapixels"
        },
        {
            "original_name": "four_g",
            "uz": "4G tarmog'i (Bor/Yo'q)",
            "uz_col": "tort_g",
            "ru": "Сеть 4G (Есть/Нет)",
            "ru_col": "four_g",
            "en": "4G Network (Yes/No)",
            "en_col": "four_g",
            "description_uz": "4G tarmog'ini qo'llab-quvvatlashi: 1 = Bor, 0 = Yo'q",
            "description_ru": "Поддержка связи 4G: 1 = Есть, 0 = Нет",
            "description_en": "Has 4G support: 1 = Yes, 0 = No"
        },
        {
            "original_name": "int_memory",
            "uz": "Ichki xotira (GB)",
            "uz_col": "ichki_xotira_gb",
            "ru": "Встроенная память (ГБ)",
            "ru_col": "vstroennaya_pamyat_gb",
            "en": "Internal Memory (GB)",
            "en_col": "int_memory",
            "description_uz": "Qurilmaning ichki doimiy xotira hajmi gigabaytlarda (GB)",
            "description_ru": "Объем встроенной памяти в гигабайтах (ГБ)",
            "description_en": "Internal memory capacity in Gigabytes (GB)"
        },
        {
            "original_name": "m_dep",
            "uz": "Qalinligi (sm)",
            "uz_col": "qalinligi_sm",
            "ru": "Толщина корпуса (см)",
            "ru_col": "tolschina_sm",
            "en": "Mobile Depth / Thickness (cm)",
            "en_col": "m_dep",
            "description_uz": "Telefonning qalinligi santimetrda",
            "description_ru": "Толщина корпуса телефона в сантиметрах",
            "description_en": "Mobile phone depth / thickness in cm"
        },
        {
            "original_name": "mobile_wt",
            "uz": "Telefon vazni (gramm)",
            "uz_col": "telefon_vazni_gr",
            "ru": "Вес телефона (г)",
            "ru_col": "ves_telefona_gr",
            "en": "Mobile Weight (g)",
            "en_col": "mobile_wt",
            "description_uz": "Telefonning og'irligi grammda",
            "description_ru": "Вес мобильного устройства в граммах",
            "description_en": "Weight of mobile phone in grams"
        },
        {
            "original_name": "n_cores",
            "uz": "Protsessor yadrolari soni",
            "uz_col": "yadro_soni",
            "ru": "Количество ядер процессора",
            "ru_col": "kolichestvo_yader",
            "en": "Number of Processor Cores",
            "en_col": "n_cores",
            "description_uz": "Markaziy protsessordagi yadrolar soni",
            "description_ru": "Количество вычислительных ядер процессора",
            "description_en": "Number of cores of the microprocessor"
        },
        {
            "original_name": "pc",
            "uz": "Asosiy kamera (MP)",
            "uz_col": "asosiy_kamera_mp",
            "ru": "Основная камера (Мп)",
            "ru_col": "osnovnaya_kamera_mp",
            "en": "Primary Camera (MP)",
            "en_col": "pc",
            "description_uz": "Asosiy orqa kamera megapiksellari",
            "description_ru": "Разрешение основной камеры в мегапикселях",
            "description_en": "Primary camera resolution in megapixels"
        },
        {
            "original_name": "px_height",
            "uz": "Piksel balandligi (px)",
            "uz_col": "piksel_balandligi",
            "ru": "Высота разрешения (пикс)",
            "ru_col": "vysota_razresheniya_px",
            "en": "Pixel Resolution Height",
            "en_col": "px_height",
            "description_uz": "Ekran piksellarining vertikal soni",
            "description_ru": "Разрешение экрана по высоте в пикселях",
            "description_en": "Pixel resolution height"
        },
        {
            "original_name": "px_width",
            "uz": "Piksel kengligi (px)",
            "uz_col": "piksel_kengligi",
            "ru": "Ширина разрешения (пикс)",
            "ru_col": "shirina_razresheniya_px",
            "en": "Pixel Resolution Width",
            "en_col": "px_width",
            "description_uz": "Ekran piksellarining gorizontal soni",
            "description_ru": "Разрешение экрана по ширине в пикселях",
            "description_en": "Pixel resolution width"
        },
        {
            "original_name": "ram",
            "uz": "Tezkor xotira RAM (MB)",
            "uz_col": "ram_mb",
            "ru": "Оперативная память ОЗУ (МБ)",
            "ru_col": "ram_mb",
            "en": "RAM (MB)",
            "en_col": "ram",
            "description_uz": "Tezkor operativ xotira megabaytlarda",
            "description_ru": "Объем оперативной памяти в мегабайтах (МБ)",
            "description_en": "Random Access Memory in Megabytes (MB)"
        },
        {
            "original_name": "sc_h",
            "uz": "Ekran balandligi (sm)",
            "uz_col": "ekran_balandligi_sm",
            "ru": "Высота экрана (см)",
            "ru_col": "vysota_ekrana_sm",
            "en": "Screen Height (cm)",
            "en_col": "sc_h",
            "description_uz": "Telefon ekranining balandligi santimetrda",
            "description_ru": "Высота экрана телефона в сантиметрах",
            "description_en": "Screen height of mobile in cm"
        },
        {
            "original_name": "sc_w",
            "uz": "Ekran kengligi (sm)",
            "uz_col": "ekran_kengligi_sm",
            "ru": "Ширина экрана (см)",
            "ru_col": "shirina_ekrana_sm",
            "en": "Screen Width (cm)",
            "en_col": "sc_w",
            "description_uz": "Telefon ekranining kengligi santimetrda",
            "description_ru": "Ширина экрана телефона в сантиметрах",
            "description_en": "Screen width of mobile in cm"
        },
        {
            "original_name": "talk_time",
            "uz": "So'zlashuv vaqti (soat)",
            "uz_col": "gaplashish_vaqti_soat",
            "ru": "Время разговора (ч)",
            "ru_col": "vremya_razgovora_ch",
            "en": "Talk Time (hours)",
            "en_col": "talk_time",
            "description_uz": "To'liq quvvat bilan gaplashish mumkin bo'lgan maksimal vaqt (soat)",
            "description_ru": "Максимальное время непрерывного разговора на одном заряде (в часах)",
            "description_en": "Longest time that a single battery charge will last in call (hours)"
        },
        {
            "original_name": "three_g",
            "uz": "3G tarmog'i (Bor/Yo'q)",
            "uz_col": "uch_g",
            "ru": "Сеть 3G (Есть/Нет)",
            "ru_col": "three_g",
            "en": "3G Network (Yes/No)",
            "en_col": "three_g",
            "description_uz": "3G tarmog'ini qo'llab-quvvatlashi: 1 = Bor, 0 = Yo'q",
            "description_ru": "Поддержка связи 3G: 1 = Есть, 0 = Нет",
            "description_en": "Has 3G support: 1 = Yes, 0 = No"
        },
        {
            "original_name": "touch_screen",
            "uz": "Sensorli ekran (Bor/Yo'q)",
            "uz_col": "sensorli_ekran",
            "ru": "Сенсорный экран (Есть/Нет)",
            "ru_col": "sensornyy_ekran",
            "en": "Touch Screen (Yes/No)",
            "en_col": "touch_screen",
            "description_uz": "Sensorli ekranning mavjudligi: 1 = Bor, 0 = Yo'q",
            "description_ru": "Наличие сенсорного экрана: 1 = Есть, 0 = Нет",
            "description_en": "Has touch screen: 1 = Yes, 0 = No"
        },
        {
            "original_name": "wifi",
            "uz": "Wi-Fi (Bor/Yo'q)",
            "uz_col": "wifi",
            "ru": "Wi-Fi (Есть/Нет)",
            "ru_col": "wifi",
            "en": "Wi-Fi (Yes/No)",
            "en_col": "wifi",
            "description_uz": "Wi-Fi ulanish mavjudligi: 1 = Bor, 0 = Yo'q",
            "description_ru": "Наличие модуля Wi-Fi: 1 = Есть, 0 = Нет",
            "description_en": "Has Wi-Fi support: 1 = Yes, 0 = No"
        },
        {
            "original_name": "price_range",
            "uz": "Narx toifasi (0-3)",
            "uz_col": "narx_toifasi",
            "ru": "Ценовой диапазон (0-3)",
            "ru_col": "diapazon_cen",
            "en": "Price Range (0-3)",
            "en_col": "price_range",
            "description_uz": "Maqsadli o'zgaruvchi: 0=Arzon, 1=O'rtacha, 2=Qimmat, 3=Juda qimmat",
            "description_ru": "Целевая переменная: 0=Низкая, 1=Средняя, 2=Высокая, 3=Очень высокая",
            "description_en": "Target variable: 0=Low Cost, 1=Medium Cost, 2=High Cost, 3=Very High Cost"
        }
    ]

    with open(os.path.join(base_dir, 'metadata_features.json'), 'w', encoding='utf-8') as f:
        json.dump(features_metadata, f, ensure_ascii=False, indent=2)

    print("✓ Metadata 'metadata_features.json' yaratildi.")
    print("\nBarcha ma'lumotlar to'plamlari muvaffaqiyatli tayyorlandi!")

if __name__ == "__main__":
    main()

