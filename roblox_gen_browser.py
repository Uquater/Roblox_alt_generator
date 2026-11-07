# roblox_gen_browser.py — Semi-auto Roblox account generator
# Otomatis isi form, lo solve captcha manual, akun tersimpan otomatis
# requires: pip install selenium
# usage: python roblox_gen_browser.py --count 5

import time
import random
import string
import argparse
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options


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
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    year = random.randint(1990, 2004)
    return month, day, year


def setup_driver():
    opts = Options()
    opts.add_argument("--start-maximized")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    opts.add_experimental_option("useAutomationExtension", False)
    driver = webdriver.Chrome(options=opts)
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    })
    return driver


def set_select_value(driver, selector, value):
    """Set dropdown value via JS — bypasses click interception issues."""
    driver.execute_script(f"""
        var el = document.querySelector('{selector}');
        if (el) {{
            var nativeInputValueSetter = Object.getOwnPropertyDescriptor(
                window.HTMLSelectElement.prototype, 'value').set;
            nativeInputValueSetter.call(el, '{value}');
            el.dispatchEvent(new Event('change', {{ bubbles: true }}));
        }}
    """)


def set_input_value(driver, selector, value):
    """Set input value via JS + dispatch events for React."""
    driver.execute_script(f"""
        var el = document.querySelector('{selector}');
        if (el) {{
            var nativeInputValueSetter = Object.getOwnPropertyDescriptor(
                window.HTMLInputElement.prototype, 'value').set;
            nativeInputValueSetter.call(el, '{value}');
            el.dispatchEvent(new Event('input', {{ bubbles: true }}));
            el.dispatchEvent(new Event('change', {{ bubbles: true }}));
        }}
    """)


def fill_signup(driver, username, password):
    wait = WebDriverWait(driver, 15)

    month, day, year = random_birthday()

    wait.until(EC.presence_of_element_located((By.ID, "MonthDropdown")))
    time.sleep(1)

    # Month dropdown: coba beberapa format value (string, padded, text)
    driver.execute_script("""
        var el = document.getElementById('MonthDropdown');
        if (!el) return;
        var val = arguments[0];
        // cari option yang cocok by value atau by index
        for (var i = 0; i < el.options.length; i++) {
            var opt = el.options[i];
            if (opt.value == val || opt.value == String(val).padStart(2,'0') || i == val) {
                el.selectedIndex = i;
                el.dispatchEvent(new Event('change', {bubbles: true}));
                // React synthetic event trigger
                var tracker = el._valueTracker;
                if (tracker) tracker.setValue('');
                el.dispatchEvent(new Event('input', {bubbles: true}));
                el.dispatchEvent(new Event('change', {bubbles: true}));
                break;
            }
        }
    """, month)
    time.sleep(0.5)
    set_select_value(driver, "#DayDropdown", str(day))
    time.sleep(0.5)
    set_select_value(driver, "#YearDropdown", str(year))
    time.sleep(0.5)

    print(f"  birthday: {month}/{day}/{year}")

    set_input_value(driver, "#signup-username", username)
    time.sleep(0.5)
    set_input_value(driver, "#signup-password", password)
    time.sleep(0.5)

    gender = random.choice(["MaleButton", "FemaleButton"])
    driver.execute_script(f"document.getElementById('{gender}')?.click()")
    time.sleep(0.3)


def click_signup(driver):
    driver.execute_script("""
        var btn = document.getElementById('signup-button');
        if (btn) { btn.disabled = false; btn.click(); }
    """)


def wait_for_captcha_and_success(driver, timeout=300):
    """Tunggu user solve captcha manual, lalu deteksi redirect ke home = akun berhasil dibuat."""
    print("\n  ====================================")
    print("  SOLVE CAPTCHA MANUAL DI BROWSER")
    print("  Setelah solve, akun otomatis dibuat")
    print("  ====================================\n")

    start = time.time()
    while time.time() - start < timeout:
        url = driver.current_url
        if "/home" in url or "/discover" in url or "/charts" in url:
            return True
        try:
            error_el = driver.find_elements(By.CSS_SELECTOR, ".alert-warning, .status-error, [class*='error']")
            for el in error_el:
                txt = el.text.strip()
                if txt and "captcha" not in txt.lower():
                    print(f"  error dari roblox: {txt}")
        except Exception:
            pass
        time.sleep(2)

    return False


def get_cookie(driver):
    cookies = driver.get_cookies()
    for c in cookies:
        if c["name"] == ".ROBLOSECURITY":
            return c["value"]
    return ""


def main():
    parser = argparse.ArgumentParser(description="Roblox Account Generator (Browser Semi-Auto)")
    parser.add_argument("--count", type=int, default=1, help="jumlah akun")
    parser.add_argument("--output", default="accounts.txt", help="file output")
    parser.add_argument("--timeout", type=int, default=300, help="timeout captcha per akun (detik)")
    args = parser.parse_args()

    results = []
    driver = None

    try:
        driver = setup_driver()

        for i in range(args.count):
            username = random_username()
            password = random_password()

            print(f"\n[{i+1}/{args.count}] {username}:{password}")

            driver.get("https://www.roblox.com/")
            time.sleep(3)

            fill_signup(driver, username, password)

            print("  form terisi. klik Sign Up...")
            click_signup(driver)

            success = wait_for_captcha_and_success(driver, timeout=args.timeout)

            if success:
                cookie = get_cookie(driver)
                print(f"  BERHASIL: {username}")
                results.append({
                    "username": username,
                    "password": password,
                    "cookie": cookie,
                })

                with open(args.output, "a") as f:
                    f.write(f"{username}:{password}\n")

                cookie_file = args.output.replace(".txt", "_cookies.txt")
                if cookie:
                    with open(cookie_file, "a") as f:
                        f.write(f"{username}:{cookie}\n")

                print(f"  tersimpan ke {args.output}")

                driver.delete_all_cookies()
            else:
                print(f"  GAGAL/TIMEOUT untuk {username}")

    except KeyboardInterrupt:
        print("\ndihentikan.")
    except Exception as e:
        print(f"\nERROR: {e}")
    finally:
        if driver:
            driver.quit()

    print(f"\n{'='*50}")
    print(f"total berhasil: {len(results)}/{args.count}")
    if results:
        print(f"tersimpan di {args.output}")
        for acc in results:
            print(f"  {acc['username']}:{acc['password']}")
    print(f"{'='*50}")


if __name__ == "__main__":
    main()
