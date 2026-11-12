# Roblox Alt Generator

Tool otomatisasi untuk membuat akun alternatif (alt account) Roblox dengan Python. Repository ini menyediakan **2 metode generator**:

1. **Semi-Auto (Browser / Selenium)** — **GRATIS**, form terisi otomatis dan captcha diselesaikan secara manual lewat browser Chrome. Tidak butuh API key atau saldo captcha.
2. **Full-Auto (HTTP API)** — **OTOMATIS PENUH**, langsung lewat request API Roblox menggunakan bantuan layanan pemecah captcha berbayar (2Captcha atau CapSolver) dan mendukung rotasi proxy.

---

## 🛠️ Prasyarat (Prerequisites)

1. **Python 3.8+** sudah terpasang di komputer ([Unduh Python](https://www.python.org/downloads/)).
   > *Pastikan mencentang opsi **"Add Python to PATH"** saat instalasi.*
2. **Google Chrome** terpasang (jika ingin menggunakan mode Browser Semi-Auto).

---

## 📦 Instalasi Dependensi

Buka Command Prompt (CMD) atau PowerShell di folder ini, lalu jalankan:

```bash
pip install requests selenium
```

---

## 🚀 Cara Penggunaan

### Metode 1: Semi-Auto Browser (Direkomendasikan & Gratis)
File: `roblox_gen_browser.py`

Cocok jika kamu hanya ingin membuat beberapa akun tanpa perlu membayar layanan captcha solver.

#### Cara Menjalankan:
```bash
# Membuat 1 akun (default)
python roblox_gen_browser.py

# Membuat 5 akun berurutan
python roblox_gen_browser.py --count 5

# Menentukan nama file output dan timeout solve captcha (detik)
python roblox_gen_browser.py --count 3 --output hasil_akun.txt --timeout 180
```

#### Alur Kerja:
1. Jendela browser Chrome akan otomatis terbuka dan memuat halaman registrasi Roblox.
2. Script otomatis mengisikan Tanggal Lahir acak, Username acak, Password acak, dan memilih Gender.
3. Tombol **Sign Up** akan diklik otomatis.
4. Jendela verifikasi / FunCaptcha akan muncul: **Selesaikan captcha secara manual di jendela browser tersebut**.
5. Begitu verifikasi berhasil, script otomatis mendeteksi login, mengambil cookie `.ROBLOSECURITY`, dan menyimpan data akun ke file.
6. Browser akan otomatis membersihkan cookie dan lanjut ke akun berikutnya sampai `--count` terpenuhi.

---

### Metode 2: Full-Auto API (Otomatis Penuh)
File: `roblox_gen.py`

Cocok untuk membuat akun dalam jumlah banyak secara headless (tanpa buka browser). Metode ini memerlukan API Key dari layanan pemecah captcha (2Captcha atau CapSolver) dan disarankan menggunakan proxy.

#### Cara Menjalankan:

**A. Menggunakan 2Captcha:**
```bash
python roblox_gen.py --count 5 --captcha-key "MASUKKAN_API_KEY_2CAPTCHA" --solver 2captcha
```

**B. Menggunakan CapSolver:**
```bash
python roblox_gen.py --count 5 --captcha-key "CAP-xxxxxxxxxxxxxxxx" --solver capsolver
```

**C. Menggunakan Proxy (Direkomendasikan agar tidak kena Rate Limit IP):**
```bash
python roblox_gen.py --count 20 --captcha-key "KEY_KAMU" --proxy-file proxies.txt
```

#### Format File Proxy (`proxies.txt`):
Buat file teks bernama `proxies.txt` (satu proxy per baris), mendukung format berikut:
```text
ip:port
user:password@ip:port
http://ip:port
socks5://user:password@ip:port
```

---

## ⚙️ Opsi Parameter Perintah (Argumen Lengkap)

### Parameter `roblox_gen_browser.py`:
| Argumen | Default | Keterangan |
| :--- | :--- | :--- |
| `--count` | `1` | Jumlah akun yang ingin dibuat |
| `--output` | `accounts.txt` | Nama file teks hasil penyimpanan akun |
| `--timeout` | `300` | Batas waktu tunggu solve captcha manual per akun (dalam detik) |

### Parameter `roblox_gen.py`:
| Argumen | Default | Keterangan |
| :--- | :--- | :--- |
| `--captcha-key` | *(Wajib)* | API Key 2captcha / CapSolver |
| `--count` | `1` | Jumlah akun yang ingin dibuat |
| `--solver` | `2captcha` | Layanan solver (`2captcha` atau `capsolver`) |
| `--output` | `accounts.txt` | Nama file penyimpanan akun |
| `--proxy-file` | `None` | Path file teks daftar proxy |
| `--delay-min` | `3.0` | Jeda waktu minimum antar akun (detik) |
| `--delay-max` | `8.0` | Jeda waktu maksimum antar akun (detik) |

---

## 📁 Format File Output

Setelah akun berhasil dibuat, tool akan otomatis menyimpan hasilnya ke dalam beberapa file:

1. **`accounts.txt`**  
   Format: `username:password`  
   *(Cocok untuk login manual di aplikasi atau web)*

2. **`accounts_cookies.txt`**  
   Format: `username:password:cookie` atau `username:cookie`  
   *(Berisi token `.ROBLOSECURITY` untuk login otomatis / bot)*

3. **`accounts_bulk.txt`** *(pada mode browser)*  
   Format: `cookie` (1 per baris)  
   *(Khusus untuk di-import langsung ke Cookie Manager atau bulk bot Roblox)*

---

## ⚠️ Tips & Troubleshooting

- **Muncul Error "ChromeDriver" / Selenium tidak bisa membuka Chrome:**  
  Pastikan versi Google Chrome kamu sudah ter-update ke versi terbaru. Di Selenium versi 4+, driver akan diunduh otomatis tanpa perlu download chromedriver manual.
- **Akun gagal dibuat / Roblox memblokir registrasi:**  
  Roblox memiliki sistem anti-spam & rate limiting IP. Jika membuat akun beruntun dari IP yang sama, Roblox akan memunculkan captcha yang lebih sulit atau menolak request. Gunakan VPN/Proxy atau berikan jeda waktu antar pembuatan akun.
- **Jangan jalankan di sembarang jaringan:**  
  Gunakan akun alt untuk keperluan riset, testing game, atau bot pribadi. Patuhi selalu ketentuan layanan (Terms of Service) Roblox.
