from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import sqlite3
import time
import re
import urllib.parse

iran_districts = {
    "تهران": [
        "زعفرانیه", "کامرانیه", "الهیه", "نیاوران", "فرمانیه", "ولنجک", "اقدسیه",
        "قیطریه", "محمودیه", "تجریش", "شهرک غرب", "سعادت آباد", "گیشا", "مرزداران",
        "پونک", "پاسداران", "میرداماد", "جردن (آفریقا)", "بلوار فردوس", "جنت آباد", "چیتگر",
        "تهرانپارس", "نارمک", "آجودانیه", "اوین", "دارآباد", "دربند", "سوهانک", "چیذر"
    ],
    "اصفهان": [
        "مرداویج", "مهرآباد", "شیخ صدوق", "مشتاق", "چهارباغ بالا", "عباس آباد", "جلفا",
        "پل فردوسی", "خواجو", "ملک شهر", "باغ فردوس", "سپاهان شهر", "بهارستان", "شاهین شهر",
        "درچه", "کاوه", "زینبیه", "لاهور", "اقبالیه", "دستگرد", "خرازان", "ساروان", "رودکی"
    ],
    "شیراز": [
        "معالی آباد", "قصر دشت", "فرهنگ شهر", "عفیف آباد", "ستارخان", "ارم", "گلستان",
        "دروازه اصفهان", "سنگ سیاه", "آستانه (شاهچراغ)", "زرگری", "چنچنه", "پاسداران",
        "قصردشت", "ملاصدرا", "ابیوردی", "چمران", "حافظیه", "سعدیه", "بازار وکیل", "مصلی"
    ],
    "تبریز": [
        "میرداماد", "ائل گلی (شاه‌گلی)", "زعفرانیه", "ولیعصر", "بام فرشته", "فرمانداری",
        "آبرسان", "مرزداران", "منظریه", "یاخچیان", "نوبر", "باغمیشه", "میدان ساعت",
        "راسته کوچه", "چایکنار", "سهند", "خسروشاه", "باغلار باغی", "لیقوان", "شهرک اندیشه"
    ],
    "مشهد": [
        "احمدآباد", "بلوار سجاد", "هاشمیه", "کوهسنگی", "خیام جنوبی", "وکیل‌آباد", "مشهد مال (محدوده)",
        "الهیه مشهد", "چهارراه لشکر", "راهنمایی", "سیدی", "ابکوه", "امامیه", "طبرسی", "فضل آباد",
        "باهنر", "هفت تیر", "دانشجو", "سناباد", "نواب صفوی (پایین خیابان)", "بازار رضا", "شهرک شهید رجایی"
    ],
    "کرج": [
        "مهرشهر", "گلشهر", "دهقان ویلا", "عظیمیه", "گوهردشت", "رشت‌نشین", "هفت‌تیر",
        "جهانشهر", "کمالشهر", "ماهدشت", "باغستان", "حسین‌آباد", "مهدی‌آباد", "چهارراه طالقانی",
        "مرادآباد", "بزرگمهر", "کرج نو", "شهرک خرمدشت", "ازارگله", "میان جاده"
    ],
    "رشت": [
        "گلسار", "سبزه میدان", "میدان شهرداری", "خیابان سعدی", "خمیران", "پارک شهر",
        "ولسی", "پیرسرا", "زرگرمحله", "استادسرا", "مقدس", "جیرنده", "سیاه اسطل",
        "بلوار رودباری", "منطقه مسکن مهر", "بازار رشت", "چهارراه تختی", "میدان انتظام"
    ],
    "اهواز": [
        "کیانپارس", "پادادشهر", "فاز دوم", "زرگنده", "عامری", "بستان", "پاداد",
        "خسروی", "منبع آب", "کوی سیدخلف", "امیرالمؤمنین", "ملاشیه", "الهادی",
        "گلدشت", "کیانآباد", "سلیمانیه", "زیتون کارمندی", "کوی علوی", "آریاشهر"
    ],
    "قم": [
        "جمکران", "پردیسان", "بلوار امین", "قدس", "شهرک قدس", "خاکفرج", "چهارمردان",
        "لب چال", "بازار کهنه", "میدان روح الله", "حرم مطهر", "بلوار محمدامین", "نیایش",
        "سلام", "کوهک", "جعفریه", "شهرک امام حسن", "شهرک فاطمیه", "قائم", "مطهریه"
    ],
    "همدان": [
        "بوعلی (میدان آرامگاه)", "شریعتی", "بازار همدان", "هگمتانه", "میدان امام", "محله سنگی",
        "کوی جنت", "شهرک مدنی", "عباس آباد", "جورقان", "مهمان‌شهر", "پایگاه", "سعیدیه",
        "امین آباد", "چهارباغ", "میدان مرکزی", "بلوار بعثت", "شهرک الوند"
    ],
    "ارومیه": [
        "خیابان امام", "میدان انقلاب", "بازار ارومیه", "کوی لاله", "پارک جنگلی", "اقبال",
        "گلشهر", "نازلو", "کوی فرهنگ", "منطقه دریاچه (حاشیه)", "آذرباد", "امیرآباد",
        "شهرک صنعتی", "باغلار", "سرباز", "بلوار مدرس", "دروازه تهران"
    ],
    "کرمانشاه": [
        "آبیدر", "میدان آزادی", "پارک شیرین", "طاق بستان", "معلم", "جلالی", "مهرگان",
        "الهیه کرمانشاه", "شهرک بهشتی", "بازار کرمانشاه", "بلوار شهید بهشتی", "کوی زاگرس",
        "شهرک راهآهن", "سلیمانی", "چهارراه جوانشیر", "بلوار کشاورز"
    ],
    "بندرعباس": [
        "سورو", "اسکله", "نایبند", "شهرک هما", "پهلوان", "چهارراه یکشنبه", "آلودین",
        "پارک ساحلی", "بازار ماهی فروشان", "پل سفید", "گلدشت", "ستاد", "ابراهیم آباد",
        "طاق", "چاهستانی‌ها", "شهرداری قدیم", "باغ بالا"
    ],
    "اراک": [
        "فیضیه", "بازار اراک", "میدان قائم", "پارک جمشید", "امام خمینی", "ولیعصر",
        "سپاه", "شهرک ولیعصر", "خیابان بسیج", "میدان شهدا", "برق شهر", "کوی مدرس",
        "شهرک ذوب‌آهن", "حافظ", "سعدی", "بلوار کاشانی", "شهرک قدس"
    ],
    "یزد": [
        "امیرچقماق", "دولت‌آباد", "صفائیه", "آبشاهی", "بافت تاریخی", "زرتشتی‌ها",
        "میدان شاه طهماسب", "پشت باغ", "ملااسمعیل", "حمام گردون", "سی سالگل", "شهرک مهرآوران",
        "چهارمنار", "کوی ولیعصر", "بلوار دانشجو", "میدان آزادی", "بلوار بسیج", "شهرک کوثر"
    ],
    "قزوین": [
        "سعدالسلطنه", "میدان آزادی", "بازار قزوین", "راه‌آهن", "مینودر", "بلوار طالقانی",
        "امام قزوین", "باراجین", "شهرک مینودر", "کوی فاطمیه", "ناصرآباد", "راه‌آهن قدیم",
        "شهرک الوند", "کاشفیه", "بلوار شهید بهشتی", "میدان شهرداری"
    ],
    "زنجان": [
        "گنبد سلطانیه", "بازار زنجان", "میدان انقلاب", "پارک شهر", "سرچشمه", "سه‌راه",
        "شهرک کارمندان", "شهرک گلگشت", "کوی جهاد", "بلوار معلم", "میدان آزادی",
        "چهارراه سعدی", "کوی انقلاب", "شهرک پونک", "دروازه تهران"
    ],
    "ساری": [
        "پل تجن", "میدان ساعت", "بازار روز", "پارک ملل", "بلوار معلم", "آب انبار",
        "ولیعصر", "کوی رجائی", "شهرک مخابرات", "پاسداران", "کیلومتر ۸", "فرح آباد",
        "پل سفید", "دروازه آمل", "سیدمحله", "بهمن آباد"
    ],
    "گرگان": [
        "ناهارخوران", "پارک شهر", "میدان ولیعصر", "بازار نعلبندان", "مطهری", "چهارشنبه",
        "شهرک جهاد", "بلوار شهید حق شناس", "کوی نرگس", "شهرک امام خمینی", "سعیدآباد",
        "نوده", "شهرک رجائی", "میدان آزادی", "دروازه کلاله"
    ],
    "خرم‌آباد": [
        "فلکه پهلوی", "بازار خرم‌آباد", "پارک کیو", "دریاچه گهر", "برجشیران", "حسینیه",
        "شهرک الهیه", "خیابان شقایق", "بلوار شوریده", "میدان تختی", "کوی معلم",
        "شهرک پاسداران", "دروازه کوهدشت", "شهرک صداوسیما"
    ],
    "سنندج": [
        "بازار سنندج", "میدان آزادی", "پارک آبیدر", "عرش سنندج", "آصف", "قطارچیان",
        "شهرک بهشتی", "بلوار مدرس", "کوی معلم", "میدان قدس", "بلوار امام", "دروازه دیواندره",
        "پایگلان", "نایسر", "مردیخ"
    ],
    "شهرکرد": [
        "پارک کوهستانی", "چهارراه ورزش", "میدان هفده شهریور", "بازار شهرکرد", "محله قلعه",
        "شهرک بهاران", "جاده دره لاشه", "بلوار سیدالشهدا", "کوی قائم", "شهرک فرخشهر",
        "میدان بسیج", "دروازه سامان", "حافظ", "بلوار اردل"
    ],
    "بوشهر": [
        "بازار قدیم بوشهر", "میدان سادات", "عمارت ملک", "ساحل بندرگاه", "کوی عطاران",
        "بهرام آباد", "جفره", "شهرک شغاب", "میدان صباح", "بلوار بوشهر", "چهارراه کشتی",
        "خیابان نوفل‌لوشاتو", "شهرک برازجانی", "علی‌آباد", "دریاکنار"
    ],
    "بیرجند": [
        "بازار بیرجند", "باغ اکبریه", "سجاد", "بلوار معلم", "ارگ بیرجند", "پارک شوکت آباد",
        "شهرک مهرگان", "خیابان شهید منتظری", "میدان آزادی", "کوی جانبازان", "چهارراه مرکزی",
        "دروازه بیرجند", "شهرک عدالت", "شهرک فرهنگ"
    ],
    "بجنورد": [
        "میدان کارگر", "بازار بجنورد", "پارک باباامان", "بلوار جمهوری", "بهارستان",
        "شهرک فرهنگیان", "منطقه توریستی اسفراین", "کوی حافظ", "بلوار شریعتی", "چهارراه مخابرات",
        "میدان ارتش", "شهرک مهندسین", "دروازه آشخانه", "باباامان", "زیتون"
    ],
    "زاهدان": [
        "میدان آزادی", "بازار مرزی", "خیابان زاهدان", "پارک شهر", "مدرس", "کارگران",
        "شهرک حضرت رسول", "کوی سیدی", "میدان امام علی", "بلوار معلم", "خیابان طالقانی",
        "شهرک مهرآباد", "چهارراه فرمانداری", "شهرک شهید بهشتی"
    ],
    "سمنان": [
        "بازار سمنان", "میدان امام", "درچه", "پارک ابوذر", "برج چهل دختر", "زاویه",
        "شهرک گلستان", "خیابان امام خمینی", "بلوار نیایش", "میدان ولیعصر", "کوی ملک",
        "شهرک عدالت", "دروازه تهران", "باغ نرگس", "خیابان آرش"
    ],
    "قزوین": [  
        "سعدالسلطنه", "میدان آزادی", "بازار قزوین", "راه‌آهن", "مینودر", "بلوار طالقانی",
        "امام قزوین", "باراجین", "شهرک مینودر", "کوی فاطمیه", "ناصرآباد", "راه‌آهن قدیم",
        "شهرک الوند", "کاشفیه", "بلوار شهید بهشتی", "میدان شهرداری"
    ],
    "ارومیه": [  
        "خیابان امام", "میدان انقلاب", "بازار ارومیه", "کوی لاله", "پارک جنگلی", "اقبال",
        "گلشهر", "نازلو", "کوی فرهنگ", "منطقه دریاچه (حاشیه)", "آذرباد", "امیرآباد",
        "شهرک صنعتی", "باغلار", "سرباز", "بلوار مدرس", "دروازه تهران"
    ],
    "ایلام": [
        "میدان شهید قدوسی", "بازار ایلام", "پارک جنگلی", "چهارراه کشاورزی", "مصلی",
        "شهرک مخابرات", "گردنه دالانی", "بلوار امام", "میدان نماز", "خیابان طالقانی",
        "کوی مطهری", "شهرک ولیعصر", "کوی شهید فهمیده", "دروازه مهران"
    ],
    "یاسوج": [
        "میدان هفت تیر", "پارک دانشجو", "آبشار یاسوج", "بلوار مدرس", "سادات",
        "شهرک پمپ بنزین", "میدان امام حسین", "خیابان منتظری", "شهرک قدس", "بلوار رجایی",
        "کوی شاهد", "چهارراه پرستار", "دروازه دهدشت", "سرآب"
    ],
    "اردبیل": [
        "میدان عالی قاپو", "بقعه شیخ صفی", "بازار اردبیل", "دریاچه شورابیل", "دریاچه نئور",
        "پیست اسکی آلوارس", "سرچشمه", "کوی فلسطین", "بلوار سجاد", "میدان دانشگاه",
        "خیابان سبلان", "شهرک کوثر", "دروازه گیلان", "کوی بهارستان", "چهارراه جانبازان"
    ]
}

# ==================================================
# BROWSER SETUP
# ==================================================
def setup_driver():
    """Setup Chrome driver in headless mode"""
    print("🔄 Setting up browser...")
    # options = Options()
    # options.add_argument("--headless=new")
    # options.add_argument("--no-sandbox")
    # options.add_argument("--disable-dev-shm-usage")
    # options.add_argument("--disable-gpu")
    # options.add_argument("--start-maximized")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    print("✅ Browser ready")
    return driver

# ==================================================
# DATABASE SETUP
# ==================================================
def setup_database(db_name):
    """Setup SQLite database and create table if not exists"""
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS places (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            city TEXT NOT NULL,
            district TEXT NOT NULL,
            search_term TEXT NOT NULL,
            name TEXT NOT NULL,
            phone TEXT,
            address TEXT,
            working_hours TEXT,
            extracted_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    print(f"✅ Database '{db_name}' ready")
    return conn, cursor

# ==================================================
# PHONE NUMBER EXTRACTION
# ==================================================
def extract_phone(driver):
    """Extract phone number using multiple patterns and methods"""
    
    phone_patterns = [
        r'09\d{9}',           
        r'۰۹\d{۹}',          
        r'021\d{8}',          
        r'۰۲۱\d{۸}',         
        r'0\d{2,3}[-\s]?\d{8}',  
        r'09\d{2}[-\s]?\d{3}[-\s]?\d{4}', 
        r'\(0\d{2,3}\)\s?\d{8}', 
        r'\+98\s?9\d{9}',    
        r'00989\d{9}',        
    ]
    
    # Method 1: Search entire page
    try:
        page_text = driver.find_element(By.TAG_NAME, "body").text
        for pattern in phone_patterns:
            match = re.search(pattern, page_text)
            if match:
                phone = match.group()
                phone = re.sub(r'[\(\)\-\s]', '', phone)
                return phone
    except:
        pass
    
    # Method 2: Search in specific phone-related classes
    phone_classes = [
        ".SWIQUYQ",
        "[class*='phone']",
        "[class*='tel']",
        "[class*='call']",
        "[class*='contact']"
    ]
    
    for selector in phone_classes:
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            for elem in elements:
                text = elem.text
                for pattern in phone_patterns:
                    match = re.search(pattern, text)
                    if match:
                        phone = match.group()
                        phone = re.sub(r'[\(\)\-\s]', '', phone)
                        return phone
        except:
            continue
    
    return ""

# ==================================================
# ADDRESS EXTRACTION
# ==================================================
def extract_address(driver):
    """Extract address from the opened card"""
    address = ""
    
    # Method 1: Find address using img with pin.png
    try:
        address_elements = driver.find_elements(By.CSS_SELECTOR, ".SWIQUYQ img[src*='pin.png']")
        for img_elem in address_elements:
            parent = img_elem.find_element(By.XPATH, "..")
            while parent:
                try:
                    if parent.get_attribute("class") and "SWIQUYQ" in parent.get_attribute("class"):
                        span = parent.find_element(By.TAG_NAME, "span")
                        address = span.text.strip()
                        return address
                except:
                    parent = parent.find_element(By.XPATH, "..")
    except:
        pass
    
    # Method 2: Find address using keywords
    if not address:
        try:
            page_text = driver.find_element(By.TAG_NAME, "body").text
            lines = page_text.split('\n')
            keywords = ['خیابان', 'میدان', 'کوچه', 'بلوار', 'شهر', 'منطقه']
            for line in lines:
                if len(line) > 20 and any(k in line for k in keywords):
                    address = line.strip()[:200]
                    return address
        except:
            pass
    
    return ""

# ==================================================
# SEARCH AND EXTRACT FOR SINGLE DISTRICT
# ==================================================
def search_and_extract_district(driver, cursor, conn, city, district, search_term):
    """Search for a specific district and extract all data"""
    
    # Build search query
    search_query = f"{search_term} {district} {city}"
    encoded_query = urllib.parse.quote(search_query)
    url = f"https://neshan.org/maps/search/{encoded_query}"
    
    print(f"\n🔍 Opening: {url}")
    driver.get(url)
    print("⏳ Waiting 3 seconds for initial load...")
    time.sleep(3)
    
    max_attempts = 2
    for attempt in range(max_attempts):
        try:
            search_box = driver.find_element(By.CSS_SELECTOR, "input[type='search']")
            search_box.send_keys(Keys.RETURN)
            print(f"   Pressed Enter to load results (attempt {attempt + 1})...")
            time.sleep(2)
        except:
            pass
        
        if attempt == 0:
            try:
                no_result_div = driver.find_element(By.CSS_SELECTOR, "div.wtfezuH span")
                if "هیچ نتیجه‌ای" in no_result_div.text or "یافت نشد" in no_result_div.text:
                    driver.refresh()
                    time.sleep(2)
                    search_box.send_keys(Keys.RETURN)
                    print("   ⚠️ 'No results' detected. Retrying one more time...")
                    continue 
                else:
                    break
            except:
                print("   ✅ Results loaded successfully.")
                break
        
    print("⏳ Waiting 2 seconds for results...")
    time.sleep(2)
    

    for i in range(5):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
    
    # Scroll back to top
    driver.execute_script("window.scrollTo(0, 0);")
    time.sleep(2)
    
    # Find all popups
    popups = driver.find_elements(By.CSS_SELECTOR, ".search_result_popup")
    total = len(popups)
    print(f"   Found {total} boxes for district '{district}'")
    
    if total == 0:
        return 0, 0
    
    saved_count = 0
    skipped_count = 0
    
    for idx in range(total):
        try:
            # Get fresh list of popups each time
            current_popups = driver.find_elements(By.CSS_SELECTOR, ".search_result_popup")
            
            if idx >= len(current_popups):
                continue
            
            popup = current_popups[idx]
            
            # Extract name preview
            name_preview = ""
            try:
                name_elem = popup.find_element(By.CSS_SELECTOR, "h2, .title, .name")
                name_preview = name_elem.text.strip()
            except:
                lines = popup.text.split('\n')
                if lines:
                    name_preview = lines[0].strip()
            
            # Scroll to box
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", popup)
            time.sleep(0.5)
            
            # Click on box
            driver.execute_script("arguments[0].click();", popup)
            
            # Wait for card to open
            time.sleep(4)
            
            # Extract name from h1 tag
            name = ""
            try:
                name_elem = driver.find_element(By.TAG_NAME, "h1")
                name = name_elem.text.strip()
            except:
                name = name_preview
            
            # Extract working hours
            hours = ""
            try:
                hours_elem = driver.find_element(By.CSS_SELECTOR, ".mgVQQJ0")
                hours = hours_elem.text.strip()
            except:
                pass
            
            # Extract address
            address = extract_address(driver)
            
            # Extract phone number
            phone = extract_phone(driver)
            
            # Save to database (avoid duplicates)
            if name:
                cursor.execute('''
                    SELECT COUNT(*) FROM places 
                    WHERE name = ? AND city = ? AND district = ? AND search_term = ?
                ''', (name, city, district, search_term))
                
                exists = cursor.fetchone()[0]
                
                if exists == 0:
                    cursor.execute('''
                        INSERT INTO places (city, district, search_term, name, phone, address, working_hours)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (city, district, search_term, name, phone, address, hours))
                    conn.commit()
                    saved_count += 1
                    print(f"   ✅ Saved: {name} (District: {district})")
                else:
                    skipped_count += 1
            else:
                pass
            
            # Close the card
            try:
                close_btn = driver.find_element(By.CSS_SELECTOR, ".qWHyUGd, .close, [aria-label='Close']")
                driver.execute_script("arguments[0].click();", close_btn)
                time.sleep(0.5)
            except:
                try:
                    driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
                    time.sleep(0.5)
                except:
                    pass
            
        except Exception as e:
            continue
    
    return saved_count, skipped_count

# ==================================================
# SEARCH ALL DISTRICTS
# ==================================================
def search_all_districts(driver, cursor, conn, city, search_term):
    """Search through all districts of a city"""
    
    # Get districts list for the city
    districts = iran_districts.get(city, [])
    
    if not districts:
        print(f"❌ No districts found for city: {city}")
        print(f"   Available cities: {', '.join(iran_districts.keys())}")
        return 0, 0
    
    print(f"\n📍 Found {len(districts)} districts for {city}")
    print(f"   Districts: {', '.join(districts[:5])}{'...' if len(districts) > 5 else ''}")
    
    total_saved = 0
    total_skipped = 0
    
    for idx, district in enumerate(districts, 1):
        print(f"\n{'='*60}")
        print(f"📍 Processing district {idx}/{len(districts)}: {district}")
        print('='*60)
        
        saved, skipped = search_and_extract_district(driver, cursor, conn, city, district, search_term)
        
        total_saved += saved
        total_skipped += skipped
        
        print(f"\n   📊 District '{district}' summary: {saved} saved, {skipped} duplicates")
        
        # Small delay between districts
        time.sleep(2)
    
    return total_saved, total_skipped

# ==================================================
# DISPLAY DATABASE CONTENTS
# ==================================================
def display_database_contents(cursor):
    """Display all saved records from database"""
    print("\n📋 Database contents:")
    print("-" * 70)
    cursor.execute("SELECT id, district, name, phone, address FROM places ORDER BY id")
    for row in cursor.fetchall():
        print(f"{row[0]}. [{row[1]}] {row[2]}")
        print(f"   📞 {row[3] if row[3] else 'Not found'}")
        addr_short = row[4][:80] + "..." if row[4] and len(row[4]) > 80 else row[4] if row[4] else 'Not found'
        print(f"   📍 {addr_short}")
        print("-" * 50)

# ==================================================
# SHOW AVAILABLE CITIES
# ==================================================
def show_available_cities():
    """Display list of available cities"""
    print("\n📌 Available cities:")
    print("-" * 30)
    for idx, city in enumerate(iran_districts.keys(), 1):
        district_count = len(iran_districts[city])
        print(f"   {idx}. {city} ({district_count} districts)")
    print("-" * 30)

# ==================================================
# MAIN FUNCTION
# ==================================================
def main():
    """Main program entry point"""
    
    print("="*60)
    print("🗺️  NESHAN MAP SCRAPER - DISTRICT MODE")
    print("="*60)
    
    # Show available cities
    show_available_cities()
    
    # Get user input
    city = input("\n🏙️  Enter city name (e.g., تهران): ").strip()
    search_term = input("🔍  Enter search term (e.g., cafe, restaurant): ").strip()
    
    # Validate city
    if city not in iran_districts:
        print(f"❌ City '{city}' not found in database!")
        print(f"   Available cities: {', '.join(iran_districts.keys())}")
        return
    
    if not search_term:
        print("❌ Please enter a search term!")
        return
    
    db_name = f"{city}_districts.db"
    print(f"\n📌 City: {city}")
    print(f"📌 Search term: {search_term}")
    print(f"📌 Database file: {db_name}")
    
    # Setup browser
    driver = setup_driver()
    
    # Setup database
    conn, cursor = setup_database(db_name)
    
    try:
        # Search through all districts
        total_saved, total_skipped = search_all_districts(driver, cursor, conn, city, search_term)
        
        # Display results
        print("\n" + "="*60)
        print(f"✅ ALL DISTRICTS COMPLETED!")
        print(f"📊 Total for city '{city}':")
        print(f"   ✅ Saved: {total_saved} new places")
        print(f"   ⏭️ Duplicate: {total_skipped} places")
        print(f"💾 Database file: {db_name}")
        print("="*60)
        
        # Display database contents
        display_database_contents(cursor)
        
    except Exception as e:
        print(f"\n❌ Error in main process: {e}")
    
    finally:
        # Close connections
        driver.quit()
        conn.close()
        print(f"\n🎉 Program finished successfully!")

# ==================================================
# PROGRAM ENTRY POINT
# ==================================================
if __name__ == "__main__":
    main()