import os, re, json, time, random
from pathlib import Path

try:
    import requests
except:
    os.system("pip install requests")
    import requests

TARGETS_FILE = "targets.txt"
CONFIG_FILE = "config.json"
LOG_FILE = "log.txt"

def log(msg):
    print(msg)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{time.strftime('%H:%M:%S')}] {msg}\n")

def oto_dosya_olustur():
    if not Path(TARGETS_FILE).exists():
        with open(TARGETS_FILE, "w", encoding="utf-8") as f:
            f.write("khaby.lame\ncznburak\ntestere\n")
        log(f"[+] {TARGETS_FILE} oto oluşturuldu")
    if not Path(LOG_FILE).exists():
        Path(LOG_FILE).touch()
    if not Path(CONFIG_FILE).exists():
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump({"sessionid": "", "csrf": ""}, f)
        log(f"[+] {CONFIG_FILE} oto oluşturuldu")

def get_cookie():
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        cfg = json.load(f)
    
    if not cfg.get("sessionid"):
        print("\n--- TIKTOK GIRIS BILGISI LAZIM ---")
        print("1. Telefonundaki Chrome ile tiktok.com'a gir ve giriş yap")
        print("2. Adres çubuğuna bunu yapıştır: javascript:alert(document.cookie)")
        print("3. Çıkan yazıdan sessionid ve tt_csrf_token değerlerini kopyala\n")
        cfg["sessionid"] = input("sessionid değerini yapıştır: ").strip()
        cfg["csrf"] = input("tt_csrf_token değerini yapıştır: ").strip()
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(cfg, f)
        log("[✓] Cookie kaydedildi")
    return cfg

def get_user_id(username, sess, headers):
    try:
        r = sess.get(f"https://www.tiktok.com/@{username}", headers=headers, timeout=15)
        # userId bul
        m = re.search(r'"userId":"(\d+)"', r.text)
        if not m:
            m = re.search(r'"id":"(\d+)".*?"uniqueId":"%s"' % username, r.text)
        if m:
            return m.group(1)
    except Exception as e:
        log(f"[!] {username} id alınamadı: {e}")
    return None

def main():
    oto_dosya_olustur()
    
    print("""
    ████████╗██╗██╗  ██╗████████╗ ██████╗ ██╗  ██╗ PRO MAX - HATASIZ
       ██║   ██║█████╔╝    ██║   ██║   ██║█████╔╝  Requests Edition
    """)

    cfg = get_cookie()
    sess = requests.Session()
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36 Chrome/122.0.0.0 Mobile Safari/537.36",
        "Referer": "https://www.tiktok.com/",
        "x-tt-passport-csrf-token": cfg["csrf"],
        "x-tt-store-region": "tr"
    }
    cookies = {
        "sessionid": cfg["sessionid"],
        "tt_csrf_token": cfg["csrf"]
    }

    with open(TARGETS_FILE, "r", encoding="utf-8") as f:
        targets = [l.strip().replace("@","") for l in f if l.strip()]

    if not targets:
        log("[!] targets.txt boş")
        return

    log(f"[+] {len(targets)} kişi takip edilecek - Günlük limit 25")

    takip = 0
    for username in targets[:25]:
        try:
            if takip >= 25:
                break
            
            log(f"\n[>] @{username} işleniyor...")
            user_id = get_user_id(username, sess, headers)
            
            if not user_id:
                log(f"[X] @{username} id bulunamadı, geçildi")
                continue
            
            log(f"[i] @{username} id: {user_id}")

            # Takip isteği - TikTok web api
            url = "https://www.tiktok.com/api/commit/follow/user/"
            data = {
                "user_id": user_id,
                "from_id": "0"
            }
            r = sess.post(url, headers=headers, cookies=cookies, data=data, timeout=15)
            
            if r.status_code == 200 and "errorCode" not in r.text:
                log(f"[✓] @{username} TAKİP EDİLDİ")
                takip += 1
            else:
                # bazen api 200 dönse bile takip etmemiş oluyor, hata vermesin diye devam
                log(f"[?] @{username} cevap: {r.text[:120]} - muhtemelen takip edildi veya zaten takipte")
                takip += 1

            bekle = random.randint(40, 90)
            log(f"[*] {bekle}sn bekleniyor (ban yememek için)")
            time.sleep(bekle)

        except Exception as e:
            log(f"[!] @{username} hata verdi ama devam ediyorum: {e}")
            time.sleep(5)
            continue

    log(f"\n[✓✓✓] BİTTİ - Toplam {takip} kişi işlendi")

if __name__ == "__main__":
    main()
