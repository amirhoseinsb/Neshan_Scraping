from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import sqlite3
import time
import re
import urllib.parse

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
            search_term TEXT NOT NULL,
            name TEXT NOT NULL,
            phone TEXT,
            address TEXT,
            working_hours TEXT,
            extracted_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    print(f"✅ Database '{db_name}' ready (existing data preserved)")
    return conn, cursor

# ==================================================
# PHONE NUMBER EXTRACTION
# ==================================================
def extract_phone(driver):
    """Extract phone number"""
    
    # phone number
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
    
    try:
        all_spans = driver.find_elements(By.TAG_NAME, "span")
        for span in all_spans:
            text = span.text
            for pattern in phone_patterns:
                match = re.search(pattern, text)
                if match:
                    phone = match.group()
                    phone = re.sub(r'[\(\)\-\s]', '', phone)
                    return phone
    except:
        pass
    
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
# SEARCH AND EXTRACT DATA
# ==================================================
def search_and_extract(driver, cursor, conn, search_city, search_term, db_city):
    """Main function to search and extract all data"""
    
    # Build URL and open page
    encoded_city = urllib.parse.quote(search_city)
    url = f"https://neshan.org/maps/search/{encoded_city}"
    print(f"\n🔍 Opening: {url}")
    driver.get(url)
    print("⏳ Waiting 3 seconds for initial load...")
    time.sleep(3)
    
    # Search for term (cafe, restaurant, etc.)
    search_box = driver.find_element(By.CSS_SELECTOR, "input[type='search']")
    search_box.clear()
    search_box.send_keys(search_term)
    search_box.send_keys(Keys.RETURN)
    print(f"\n🔎 Searching for '{search_term}'...")
    print("⏳ Waiting 3 seconds for results...")
    time.sleep(3)
    
    # Find all search_result_popup boxes
    print("\n📋 Searching for search_result_popup boxes...")
    
    # Scroll to load all boxes
    for i in range(5):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        print(f"   Scroll {i+1}/5...")
        time.sleep(2)
    
    # Scroll back to top
    driver.execute_script("window.scrollTo(0, 0);")
    time.sleep(2)
    
    # Find all popups
    popups = driver.find_elements(By.CSS_SELECTOR, ".search_result_popup")
    total = len(popups)
    print(f"\n✅ Found {total} boxes (search_result_popup)")
    
    if total == 0:
        print("❌ No boxes found!")
        return 0, 0
    
    # Process each box
    print("\n" + "="*60)
    print("Starting data extraction...")
    print("="*60)
    
    saved_count = 0
    skipped_count = 0
    
    for idx in range(total):
        print(f"\n📌 Processing box {idx+1} of {total}")
        
        try:
            # Get fresh list of popups each time
            current_popups = driver.find_elements(By.CSS_SELECTOR, ".search_result_popup")
            
            if idx >= len(current_popups):
                print(f"   ⚠️ Box {idx+1} no longer exists, continuing...")
                continue
            
            popup = current_popups[idx]
            
            # Extract name from box (before click for preview)
            name_preview = ""
            try:
                name_elem = popup.find_element(By.CSS_SELECTOR, "h2, .title, .name")
                name_preview = name_elem.text.strip()
            except:
                lines = popup.text.split('\n')
                if lines:
                    name_preview = lines[0].strip()
            
            print(f"   📝 Name: {name_preview}")
            
            # Scroll to box
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", popup)
            time.sleep(0.5)
            
            # Click on box
            driver.execute_script("arguments[0].click();", popup)
            print(f"   ✅ Clicked")
            
            # Wait for card to open
            print(f"   ⏳ Waiting 5 seconds for card to open...")
            time.sleep(5)
            
            # Extract name from h1 tag
            name = ""
            try:
                name_elem = driver.find_element(By.TAG_NAME, "h1")
                name = name_elem.text.strip()
                print(f"   📛 Name from h1: {name}")
            except:
                print(f"   ⚠️ h1 tag not found!")
                name = name_preview
            
            # Extract working hours
            hours = ""
            try:
                hours_elem = driver.find_element(By.CSS_SELECTOR, ".mgVQQJ0")
                hours = hours_elem.text.strip()
                print(f"   🕒 Working hours: {hours}")
            except:
                print(f"   ⚠️ Working hours not found!")
            
            # Extract address
            address = extract_address(driver)
            if address:
                print(f"   📍 Address: {address[:100]}")
            else:
                print(f"   ⚠️ Address not found!")
            
            # Extract phone number
            phone = extract_phone(driver)
            if phone:
                print(f"   📞 Phone: {phone}")
            else:
                print(f"   ⚠️ Phone number not found!")
            
            # Save to database (avoid duplicates)
            if name:
                cursor.execute('''
                    SELECT COUNT(*) FROM places 
                    WHERE name = ? AND city = ? AND search_term = ?
                ''', (name, db_city, search_term))
                
                exists = cursor.fetchone()[0]
                
                if exists == 0:
                    cursor.execute('''
                        INSERT INTO places (city, search_term, name, phone, address, working_hours)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (db_city, search_term, name, phone, address, hours))
                    conn.commit()
                    saved_count += 1
                    
                    print(f"   ✅ Saved to database")
                    print(f"   📛 Name: {name}")
                    print(f"   📞 Phone: {phone if phone else 'Not found'}")
                    addr_short = address[:50] + "..." if len(address) > 50 else address if address else "Not found"
                    print(f"   📍 Address: {addr_short}")
                    print(f"   🕒 Working hours: {hours if hours else 'Not found'}")
                else:
                    skipped_count += 1
                    print(f"   ⏭️ Duplicate: {name} (already in database)")
            else:
                print(f"   ❌ Name not found, not saved!")
            
            # Close the card
            try:
                close_btn = driver.find_element(By.CSS_SELECTOR, ".qWHyUGd, .close, [aria-label='Close']")
                driver.execute_script("arguments[0].click();", close_btn)
                print(f"   🔘 Card closed")
                time.sleep(0.5)
            except:
                try:
                    driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
                    print(f"   🔘 Card closed with Escape")
                    time.sleep(0.5)
                except:
                    pass
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            continue
    
    return saved_count, skipped_count

# ==================================================
# DISPLAY DATABASE CONTENTS
# ==================================================
def display_database_contents(cursor):
    """Display all saved records from database"""
    print("\n📋 Database contents:")
    print("-" * 60)
    cursor.execute("SELECT id, name, phone, address, working_hours FROM places ORDER BY id")
    for row in cursor.fetchall():
        print(f"{row[0]}. {row[1]}")
        print(f"   📞 {row[2] if row[2] else 'Not found'}")
        addr_short = row[3][:80] + "..." if row[3] and len(row[3]) > 80 else row[3] if row[3] else 'Not found'
        print(f"   📍 {addr_short}")
        print(f"   🕒 {row[4] if row[4] else 'Not found'}")
        print("-" * 40)

# ==================================================
# MAIN FUNCTION
# ==================================================
def main():
    """Main program entry point"""
    
    # Get user input
    search_city = input("🏙️  Enter city and region (e.g., Tehran Vanak): ").strip()
    search_term = input("🔍  Enter search term (e.g., cafe, restaurant): ").strip()
    
    if not search_city or not search_term:
        print("❌ Please fill both fields!")
        return
    
    # Extract city name for database filename (first part only)
    db_city = search_city.split()[0]
    db_name = f"{db_city}.db"
    
    print(f"\n📌 Search on Neshan map: {search_city}")
    print(f"📌 Search term in database: {search_term}")
    print(f"📌 Database filename: {db_name}")
    
    # Setup browser
    driver = setup_driver()
    
    # Setup database
    conn, cursor = setup_database(db_name)
    
    try:
        # Search and extract data
        saved, skipped = search_and_extract(driver, cursor, conn, search_city, search_term, db_city)
        
        # Display results
        print("\n" + "="*60)
        print(f"✅ Done!")
        print(f"📊 From {saved + skipped} total boxes:")
        print(f"   ✅ Saved: {saved} new places")
        print(f"   ⏭️ Duplicate: {skipped} places")
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