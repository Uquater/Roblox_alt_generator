# roblox_gen.py — Roblox account generator with proxy rotation
# requires: pip install requests
# usage: python roblox_gen.py --count 5 --captcha-key YOUR_KEY
# capsolver: python roblox_gen.py --count 5 --captcha-key CAP-xxx --solver capsolver
# proxy: python roblox_gen.py --count 50 --captcha-key KEY --proxy-file proxies.txt

import requests
import random
import string
import time
import json
import argparse
import sys
import itertools

ROBLOX_SIGNUP_URL = "https://auth.roblox.com/v2/signup"
ROBLOX_CSRF_URL = "https://auth.roblox.com/v2/login"
FUNCAPTCHA_PUBLIC_KEY = "A2A14B1D-1AF3-C791-9BBC-EE33CC7A0A6F"
FUNCAPTCHA_SITE_URL = "https://www.roblox.com"
TWO_CAPTCHA_URL = "https://2captcha.com/in.php"
TWO_CAPTCHA_RESULT_URL = "https://2captcha.com/res.php"
CAPSOLVER_URL = "https://api.capsolver.com/createTask"
CAPSOLVER_RESULT_URL = "https://api.capsolver.com/getTaskResult"


def load_proxies(path):
    """Load proxies from file. Supports formats:
    ip:port
    user:pass@ip:port
    http://ip:port
    http://user:pass@ip:port
    socks5://ip:port
    """
    proxies = []
    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "://" not in line:
                line = "http://" + line
            proxies.append(line)
    if not proxies:
        raise Exception(f"no proxies found in {path}")
    print(f"loaded {len(proxies)} proxies")
    return proxies


def proxy_dict(proxy_url):
    if proxy_url is None:
        return None
    return {"http": proxy_url, "https": proxy_url}


def random_username(length=12):
    prefix = random.choice(["Cool", "Pro", "Epic", "Fast", "Real", "Top", "Big", "New",
                            "Red", "Blu", "Max", "Ace", "Sky", "Ice", "Fox", "Zen"])
    suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=length - len(prefix)))
    return prefix + suffix


def random_password(length=16):
    chars = string.ascii_letters + string.digits + "!@#$"
    pwd = [
        random.choice(string.ascii_uppercase),
        random.choice(string.ascii_lowercase),
        random.choice(string.digits),
        random.choice("!@#$"),
    ]
    pwd += random.choices(chars, k=length - 4)
    random.shuffle(pwd)
    return ''.join(pwd)


def random_birthday():
    year = random.randint(1990, 2004)
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    return f"{year}-{month:02d}-{day:02d}T00:00:00.000Z"


def get_csrf_token(session):
    resp = session.post(ROBLOX_CSRF_URL, json={})
    token = resp.headers.get("x-csrf-token")
    if not token:
        raise Exception(f"no csrf token. status={resp.status_code}")
    return token


def solve_funcaptcha(api_key, proxy_url=None, max_retries=3):
    for attempt in range(1, max_retries + 1):
        print(f"  mengirim captcha ke 2captcha (attempt {attempt}/{max_retries})...")
        data = {
            "key": api_key,
            "method": "funcaptcha",
            "publickey": FUNCAPTCHA_PUBLIC_KEY,
            "surl": "https://roblox-api.arkoselabs.com",
            "pageurl": FUNCAPTCHA_SITE_URL,
            "json": 1,
        }
        if proxy_url:
            clean = proxy_url.replace("http://", "").replace("https://", "").replace("socks5://", "")
            data["proxy"] = clean
            data["proxytype"] = "SOCKS5" if "socks5" in proxy_url else "HTTP"

        resp = requests.post(TWO_CAPTCHA_URL, data=data)
        result = resp.json()
        if result.get("status") != 1:
            raise Exception(f"2captcha submit gagal: {result}")

        task_id = result["request"]
        print(f"  captcha task: {task_id}, polling...")

        solved = False
        for _ in range(60):
            time.sleep(5)
            resp = requests.get(TWO_CAPTCHA_RESULT_URL, params={
                "key": api_key,
                "action": "get",
                "id": task_id,
                "json": 1,
            })
            r = resp.json()
            if r.get("status") == 1:
                print("  captcha solved.")
                return r["request"]
            if r.get("request") == "ERROR_CAPTCHA_UNSOLVABLE":
                print(f"  worker gagal solve, {'retry...' if attempt < max_retries else 'habis attempt.'}")
                break
            if r.get("request") != "CAPCHA_NOT_READY":
                raise Exception(f"2captcha error: {r}")

        if attempt < max_retries:
            time.sleep(2)

    raise Exception(f"2captcha gagal solve setelah {max_retries} attempt")


def solve_funcaptcha_capsolver(api_key, proxy_url=None):
    print("  mengirim captcha ke capsolver...")
    task = {
        "type": "AntiArkoseLabsTaskProxyLess",
        "websiteURL": FUNCAPTCHA_SITE_URL,
        "websitePublicKey": FUNCAPTCHA_PUBLIC_KEY,
        "funcaptchaApiJSSubdomain": "roblox-api.arkoselabs.com",
    }
    if proxy_url:
        clean = proxy_url.replace("http://", "").replace("https://", "").replace("socks5://", "")
        parts = clean.split("@")
        if len(parts) == 2:
            auth, host = parts
            user, pwd = auth.split(":")
            ip, port = host.split(":")
            task["type"] = "AntiArkoseLabsTask"
            task["proxyType"] = "socks5" if "socks5" in proxy_url else "http"
            task["proxyAddress"] = ip
            task["proxyPort"] = int(port)
            task["proxyLogin"] = user
            task["proxyPassword"] = pwd
        else:
            ip, port = clean.split(":")
            task["type"] = "AntiArkoseLabsTask"
            task["proxyType"] = "http"
            task["proxyAddress"] = ip
            task["proxyPort"] = int(port)

    resp = requests.post(CAPSOLVER_URL, json={"clientKey": api_key, "task": task})
    data = resp.json()
    if data.get("errorId", 0) != 0:
        raise Exception(f"capsolver submit gagal: {data.get('errorDescription', data)}")

    task_id = data["taskId"]
    print(f"  captcha task: {task_id}, polling...")

    for _ in range(60):
        time.sleep(3)
        resp = requests.post(CAPSOLVER_RESULT_URL, json={"clientKey": api_key, "taskId": task_id})
        r = resp.json()
        if r.get("status") == "ready":
            token = r["solution"]["token"]
            print("  captcha solved.")
            return token
        if r.get("status") != "processing":
            raise Exception(f"capsolver error: {r}")

    raise Exception("captcha timeout (3 menit)")


def generate_account(session, csrf_token, captcha_token, username, password):
    payload = {
        "username": username,
        "password": password,
        "birthday": random_birthday(),
        "gender": random.choice([2, 3]),
        "isTosAgreementBoxChecked": True,
        "agreementIds": [
            "adf95b84-cd26-4a3e-6036-ccd8e09a7914",
            "91b5fe13-cbbf-4e04-a495-7f4e304a9cde",
        ],
        "captchaToken": captcha_token,
        "captchaProvider": "PROVIDER_ARKOSE_LABS",
    }
    headers = {
        "x-csrf-token": csrf_token,
        "Content-Type": "application/json",
        "Origin": "https://www.roblox.com",
        "Referer": "https://www.roblox.com/",
    }
    return session.post(ROBLOX_SIGNUP_URL, json=payload, headers=headers)


def main():
    parser = argparse.ArgumentParser(description="Roblox Account Generator")
    parser.add_argument("--count", type=int, default=1, help="jumlah akun")
    parser.add_argument("--captcha-key", required=True, help="2captcha API key")
    parser.add_argument("--output", default="accounts.txt", help="file output")
    parser.add_argument("--solver", default="2captcha", choices=["2captcha", "capsolver"], help="captcha solver service")
    parser.add_argument("--proxy-file", default=None, help="file daftar proxy (1 per baris)")
    parser.add_argument("--delay-min", type=float, default=3.0, help="delay minimum antar akun (detik)")
    parser.add_argument("--delay-max", type=float, default=8.0, help="delay maksimum antar akun (detik)")
    args = parser.parse_args()

    proxy_pool = None
    proxy_cycle = None
    if args.proxy_file:
        proxy_pool = load_proxies(args.proxy_file)
        random.shuffle(proxy_pool)
        proxy_cycle = itertools.cycle(proxy_pool)

    results = []

    for i in range(args.count):
        current_proxy = next(proxy_cycle) if proxy_cycle else None
        proxy_label = current_proxy.split("@")[-1] if current_proxy and "@" in current_proxy else (current_proxy or "direct")

        print(f"\n[{i+1}/{args.count}] membuat akun... (proxy: {proxy_label})")

        session = requests.Session()
        session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "Accept": "application/json",
        })
        if current_proxy:
            session.proxies = proxy_dict(current_proxy)

        try:
            csrf = get_csrf_token(session)
            print(f"  csrf: {csrf[:12]}...")

            if args.solver == "capsolver":
                captcha_token = solve_funcaptcha_capsolver(args.captcha_key, current_proxy)
            else:
                captcha_token = solve_funcaptcha(args.captcha_key, current_proxy)

            username = random_username()
            password = random_password()
            print(f"  mencoba: {username}")

            resp = generate_account(session, csrf, captcha_token, username, password)

            if resp.status_code == 200:
                data = resp.json()
                user_id = data.get("userId", "?")
                cookie = session.cookies.get(".ROBLOSECURITY", "")
                print(f"  BERHASIL: {username} (id: {user_id})")
                results.append({
                    "username": username,
                    "password": password,
                    "user_id": user_id,
                    "cookie": cookie,
                })
            else:
                err = resp.text[:200]
                print(f"  GAGAL ({resp.status_code}): {err}")

                if "Token Validation Failed" in resp.text:
                    csrf = resp.headers.get("x-csrf-token", csrf)
                    print("  csrf dirotasi, mencoba ulang...")
                    resp = generate_account(session, csrf, captcha_token, username, password)
                    if resp.status_code == 200:
                        data = resp.json()
                        user_id = data.get("userId", "?")
                        cookie = session.cookies.get(".ROBLOSECURITY", "")
                        print(f"  BERHASIL (retry): {username} (id: {user_id})")
                        results.append({
                            "username": username,
                            "password": password,
                            "user_id": user_id,
                            "cookie": cookie,
                        })

        except Exception as e:
            print(f"  ERROR: {e}")

        if i < args.count - 1:
            delay = random.uniform(args.delay_min, args.delay_max)
            print(f"  tunggu {delay:.1f}s...")
            time.sleep(delay)

    if results:
        with open(args.output, "w") as f:
            for acc in results:
                f.write(f"{acc['username']}:{acc['password']}\n")

        print(f"\n{'='*50}")
        print(f"berhasil {len(results)}/{args.count} akun")
        print(f"tersimpan di {args.output}")
        print(f"{'='*50}")
        for acc in results:
            print(f"  {acc['username']}:{acc['password']} (id: {acc['user_id']})")

        cookie_file = args.output.replace(".txt", "_cookies.txt")
        with open(cookie_file, "w") as f:
            for acc in results:
                if acc["cookie"]:
                    f.write(f"{acc['username']}:{acc['cookie']}\n")
        print(f"cookie tersimpan di {cookie_file}")
    else:
        print("\ntidak ada akun yang berhasil dibuat.")


if __name__ == "__main__":
    main()
