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

options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

for product in products:
    site = product["site"]
    url = product["url"]
    target_price = product["target_price"]

    driver.get(url)

    price = None
    try:
        if site.lower() == "amazon":
            price_elem = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "span.a-price-whole"))
            )
            price = float(price_elem.text.replace(",", "").strip())
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
