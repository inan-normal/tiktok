import os, re, json, time, random, getpass
from pathlib import Path
import requests

TARGETS = "targets.txt"
CONFIG = "config.json"

def oto():
    if not Path(TARGETS).exists():
        with open(TARGETS, "w", encoding="utf-8") as f:
            f.write("khaby.lame\ncznburak\n")
        print(f"[+] {TARGETS} oto oluştu")

oto()

with open(TARGETS, "r", encoding="utf-8") as f:
    targets = [l.strip().replace("@","") for l in f if l.strip()]

if len(targets) < 3:
    raw = input("Takip edilecekler virgülle (örn: orayben,testere): ")
    targets = [x.strip().replace("@","") for x in raw.split(",") if x.strip()]
    with open(TARGETS, "w", encoding="utf-8") as f:
        f.write("\n".join(targets))

print(f"[+] {len(targets)} kişi var")

sess = requests.Session()
sess.headers.update({"User-Agent": "Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36"})

# --- OTO LOGIN - BOT KENDİ YAPIYOR ---
print("\n[>] Oto giriş deneniyor...")
user = input("TikTok mail / kullanıcı adı: ")
pwd = getpass.getpass("Şifre (gizli): ")

try:
    # ilk sayfadan csrf al
    r = sess.get("https://www.tiktok.com/login/phone-or-email/email", timeout=15)
    csrf = sess.cookies.get("tt_csrf_token") or re.search(r'tt_csrf_token=([^;]+)', r.headers.get('set-cookie','')).group(1) if re.search(r'tt_csrf_token', r.headers.get('set-cookie','')) else ""

    login_url = "https://www.tiktok.com/passport/web/user/login/"
    data = {"username": user, "password": pwd, "multi_login": 1}
    h = {"x-tt-passport-csrf-token": csrf, "Referer": "https://www.tiktok.com/login/"}
    
    lr = sess.post(login_url, data=data, headers=h, timeout=15)
    print(f"[i] Login cevabı: {lr.text[:200]}")

    sessionid = sess.cookies.get("sessionid") or ""
    tt_csrf = sess.cookies.get("tt_csrf_token") or csrf

    if not sessionid:
        print("[!] Oto login captcha istedi, manuel cookie moduna geçiyor")
        print("Chrome'da tiktok.com'a gir, F12 > Application > Cookies > sessionid ve tt_csrf_token kopyala")
        sessionid = input("sessionid: ").strip()
        tt_csrf = input("tt_csrf_token: ").strip()
        sess.cookies.set("sessionid", sessionid)
        sess.cookies.set("tt_csrf_token", tt_csrf)
    else:
        print(f"[✓] Bot kendi sessionid'yi aldı!")

except Exception as e:
    print(f"[!] Oto login hata: {e}")
    sessionid = input("sessionid manuel yapıştır: ").strip()
    tt_csrf = input("tt_csrf_token manuel: ").strip()
    sess.cookies.set("sessionid", sessionid)
    sess.cookies.set("tt_csrf_token", tt_csrf)

# takip
for name in targets[:25]:
    try:
        print(f"\n[>] @{name}")
        r = sess.get(f"https://www.tiktok.com/@{name}", timeout=15)
        m = re.search(r'"userId":"(\d+)"', r.text)
        if not m:
            print(f"[X] id bulunamadı @{name}")
            continue
        uid = m.group(1)
        print(f"[i] id: {uid}")

        follow_url = "https://www.tiktok.com/api/commit/follow/user/"
        d = {"user_id": uid, "from_id": "0"}
        fr = sess.post(follow_url, data=d, headers={"x-tt-passport-csrf-token": tt_csrf}, timeout=15)
        
        if "errorCode" not in fr.text or "0" in fr.text:
            print(f"[✓] @{name} takip edildi")
        else:
            print(f"[?] @{name} cevap: {fr.text[:100]}")

        time.sleep(random.randint(40, 80))
    except Exception as e:
        print(f"[X] @{name} hata ama devam: {e}")
        continue

print("\n[BİTTİ]")
