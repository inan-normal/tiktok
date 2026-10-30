import os, time, random, json
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

TARGETS = "targets.txt"
CONFIG = "config.json"
LOG = "log.txt"

def oto_olustur():
    if not Path(TARGETS).exists():
        with open(TARGETS, "w", encoding="utf-8") as f:
            f.write("khaby.lame\ncznburak\n")
        print(f"[+] {TARGETS} oto oluşturuldu")
    if not Path(CONFIG).exists():
        with open(CONFIG, "w") as f:
            json.dump({}, f)
    if not Path(LOG).exists():
        Path(LOG).touch()

oto_olustur()

# hedefleri al
with open(TARGETS, "r", encoding="utf-8") as f:
    users = [l.strip().replace("@","") for l in f if l.strip()]

if len(users) <= 2:
    raw = input("Takip edilecekleri virgülle yaz (örn: orayben,mesutcan): ")
    users = [u.strip().replace("@","") for u in raw.split(",") if u.strip()]
    with open(TARGETS, "w", encoding="utf-8") as f:
        f.write("\n".join(users))

# config oku
with open(CONFIG, "r") as f:
    cfg = json.load(f)

opts = Options()
opts.add_argument("--headless=new")
opts.add_argument("--no-sandbox")
opts.add_argument("--disable-dev-shm-usage")
opts.add_argument("--user-agent=Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36")

driver = webdriver.Chrome(options=opts)

# eğer daha önce giriş yapılmadıysa oto giriş yap
if not cfg.get("sessionid"):
    print("[!] İlk giriş - bot kendi giriş yapacak")
    t_user = input("TikTok kullanıcı adı / mail: ")
    t_pass = input("TikTok şifre: ")

    driver.get("https://www.tiktok.com/login/phone-or-email/email")
    time.sleep(5)
    
    try:
        driver.find_element(By.XPATH, "//input[contains(@placeholder,'Email or username')]").send_keys(t_user)
        time.sleep(1)
        driver.find_element(By.XPATH, "//input[@type='password']").send_keys(t_pass)
        time.sleep(1)
        driver.find_element(By.XPATH, "//button[contains(text(),'Log in')]").click()
    except Exception as e:
        print(f"Form bulunamadı: {e}")
    
    print("[*] Giriş denendi, eğer captcha çıkarsa 30sn bekliyorum - sen elle çöz")
    time.sleep(30)

    # cookieleri BOT kendi çekiyor - sen kopyalamıyorsun
    cookies = driver.get_cookies()
    for c in cookies:
        if c['name'] == 'sessionid':
            cfg['sessionid'] = c['value']
        if c['name'] == 'tt_csrf_token':
            cfg['csrf'] = c['value']
    
    with open(CONFIG, "w") as f:
        json.dump(cfg, f)
    print(f"[✓] Bot cookieleri kendi kaydetti: {list(cfg.keys())}")
else:
    print("[+] Kayıtlı oturum var, direk devam")

# takip döngüsü
for u in users[:25]:
    try:
        print(f"\n[>] @{u}")
        driver.get(f"https://www.tiktok.com/@{u}")
        time.sleep(6)

        if driver.find_elements(By.XPATH, "//*[contains(text(),'Following') or contains(text(),'Takip ediliyor')]"):
            print(f"[=] @{u} zaten takipte")
            continue

        btn = None
        for txt in ["Follow", "Takip Et"]:
            el = driver.find_elements(By.XPATH, f"//button[contains(.,'{txt}')]")
            if el:
                btn = el[0]
                break
        
        if btn:
            btn.click()
            print(f"[✓] @{u} takip edildi")
            with open(LOG, "a", encoding="utf-8") as f:
                f.write(f"{u}\n")
        else:
            print(f"[!] Buton yok @{u}")

        time.sleep(random.randint(35, 75))
    except Exception as e:
        print(f"[X] {u} hata: {e}")
        continue

print("\n[BİTTİ]")
driver.quit()
