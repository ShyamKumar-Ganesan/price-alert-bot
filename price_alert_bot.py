import os
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from twilio.rest import Client

# Twilio WhatsApp via environment variables
ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")
FROM_WHATSAPP = os.environ.get("TWILIO_FROM")
TO_WHATSAPP = os.environ.get("TWILIO_TO")

if not all([ACCOUNT_SID, AUTH_TOKEN, FROM_WHATSAPP, TO_WHATSAPP]):
    raise ValueError("Twilio credentials are missing!")

client = Client(ACCOUNT_SID, AUTH_TOKEN)

def send_whatsapp(site, url, price, target):
    message = f"📢 Price Alert!\n\n🛒 {site}\n💰 Current Price: ₹{price}\n🎯 Target Price: ₹{target}\n🔗 {url}"
    msg = client.messages.create(
        from_=FROM_WHATSAPP,
        body=message,
        to=TO_WHATSAPP
    )
    print(f"✅ WhatsApp message sent for {site} (SID: {msg.sid})")

with open("products.json", "r") as f:
    products = json.load(f)

# -------------------------
# Chrome options
options = webdriver.ChromeOptions()
options.add_argument("--headless")   # run in headless mode
options.add_argument("window-size=1920,1080")  # set window size
options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/140.0.7339.185 Safari/537.36"
)
# -------------------------

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

for product in products:
    site = product["site"]
    url = product["url"]
    target_price = product["target_price"]

    driver.get(url)

    price = None
    try:
        if site.lower() == "amazon":
            price = None
            selectors = [
                "span.a-price-whole",  # Common case
                "#priceblock_ourprice",  # Standard price
                "#priceblock_dealprice",  # Deal price
                "#priceblock_saleprice"  # Sale price
            ]

            for sel in selectors:
                try:
                    elem = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, sel))
                    )
                    price_text = elem.text.replace("₹", "").replace(",", "").strip()
                    if price_text:  # check it's not empty
                        price = float(price_text)
                        break
                except:
                    continue

            if not price:
                print(f"❌ Could not fetch price for Amazon: no selector matched")
        elif site.lower() == "flipkart":
            try:
                close_btn = driver.find_element(By.CSS_SELECTOR, "button._2KpZ6l._2doB4z")
                close_btn.click()
            except:
                pass
            price_elem = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.Nx9bqj, div._30jeq3"))
            )
            price = float(price_elem.text.replace("₹", "").replace(",", "").strip())
        elif site.lower() == "myntra":
            price_elem = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "span.pdp-price"))
            )
            price = float(price_elem.text.replace("₹", "").replace(",", "").strip())
    except Exception as e:
        print(f"❌ Could not fetch price for {site}: {e}")

    if price:
        print(f"{site} Price: ₹{price} (Target: ₹{target_price})")
        if price <= target_price:
            send_whatsapp(site, url, price, target_price)

driver.quit()
