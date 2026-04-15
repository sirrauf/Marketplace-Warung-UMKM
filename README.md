# 🛒 UMKM Online — Marketplace Warung UMKM

Platform marketplace berbasis web yang dirancang khusus untuk menghubungkan Warung dan pelaku Usaha Mikro Kecil Menengah (UMKM) langsung dengan pembeli secara online, dilengkapi portal manajemen admin.

---

## 📑 Table of Contents

- [1. Overview](#1-overview)
- [2. Technology Stack](#2-technology-stack)
- [3. Fitur Aplikasi](#3-fitur-aplikasi)
  - [3.1 Fitur Pembeli](#31-fitur-pembeli)
  - [3.2 Fitur Penjual / Pemilik Warung](#32-fitur-penjual--pemilik-warung)
  - [3.3 Fitur Admin](#33-fitur-admin)
- [4. Arsitektur Database](#4-arsitektur-database)
  - [4.1 Entity Relationship](#41-entity-relationship)
  - [4.2 Penjelasan Entity](#42-penjelasan-entity)
- [5. Struktur Direktori](#5-struktur-direktori)
- [6. Routing & API Endpoints](#6-routing--api-endpoints)
  - [6.1 Public Routes](#61-public-routes)
  - [6.2 Authentication Routes](#62-authentication-routes)
  - [6.3 Buyer Routes](#63-buyer-routes)
  - [6.4 Seller Routes](#64-seller-routes)
  - [6.5 Admin Routes](#65-admin-routes)
- [7. Alur Bisnis Aplikasi](#7-alur-bisnis-aplikasi)
  - [7.1 Alur Registrasi & Verifikasi](#71-alur-registrasi--verifikasi)
  - [7.2 Alur Pembelian Produk](#72-alur-pembelian-produk)
  - [7.3 Alur Penjualan Produk](#73-alur-penjualan-produk)
  - [7.4 Alur Admin](#74-alur-admin)
- [8. Keamanan](#8-keamanan)
- [9. Instalasi & Konfigurasi](#9-instalasi--konfigurasi)
- [10. Menjalankan Aplikasi](#10-menjalankan-aplikasi)
- [11. Akses Admin Dashboard](#11-akses-admin-dashboard)
- [12. Konfigurasi Environment](#12-konfigurasi-environment)
- [13. Troubleshooting](#13-troubleshooting)

---

## 1. Overview

Sistem **UMKM Online Marketplace** dibagi menjadi tiga peran utama (role):

| Role                 | Deskripsi                                                                                     |
| :------------------- | :-------------------------------------------------------------------------------------------- |
| **Pembeli (Buyer)**  | Menjelajahi produk, melihat detail, mengelola wishlist & keranjang, dan melakukan checkout.   |
| **Penjual (Seller)** | Mengelola warung, menambah/edit/hapus produk, mengelola stok, dan menerima pesanan.           |
| **Admin**            | Mengawasi seluruh platform, approve/reject penjual, melihat statistik pendapatan dan pembeli. |

---

## 2. Technology Stack

| Komponen              | Teknologi                    |
| :-------------------- | :--------------------------- |
| Backend Framework     | Python 3.x + Flask           |
| Database ORM          | PonyORM                      |
| Database Engine       | MySQL                        |
| Template Engine       | Jinja2                       |
| Password Hashing      | bcrypt                       |
| File Upload           | werkzeug (`secure_filename`) |
| Unique Identifier     | Python `uuid`                |
| Environment Variables | python-dotenv                |
| Frontend              | HTML5, CSS3                  |

---

## 3. Fitur Aplikasi

### 3.1 Fitur Pembeli

| Fitur                | Deskripsi                                                                             |
| :------------------- | :------------------------------------------------------------------------------------ |
| 🏠 Beranda Produk    | Menampilkan seluruh produk yang tersedia (stok > 0) dalam grid card yang bisa diklik. |
| 📄 Detail Produk     | Halaman dedicated per produk dengan gambar, deskripsi, harga, stok, dan tombol beli.  |
| 🤍 Wishlist          | Menandai produk favorit untuk dibeli nanti. Toggle tambah/hapus dari halaman detail.  |
| 🛒 Keranjang Belanja | Menambahkan produk ke keranjang dengan jumlah tertentu. Duplikat otomatis digabung.   |
| 💳 Checkout          | Memproses transaksi, mengurangi stok penjual, dan mencatat pesanan ke database.       |
| ⬆ Upgrade ke Penjual | Pembeli dapat meng-upgrade akunnya menjadi penjual.                                   |

### 3.2 Fitur Penjual / Pemilik Warung

| Fitur            | Deskripsi                                                                            |
| :--------------- | :----------------------------------------------------------------------------------- |
| 📦 Tambah Produk | Form lengkap: nama warung, nama produk, deskripsi, stok, harga, upload gambar.       |
| ✏️ Edit Produk   | Mengubah semua data produk termasuk mengganti gambar (gambar lama dihapus otomatis). |
| 🗑️ Hapus Produk  | Menghapus produk beserta gambar, cart item, dan wishlist item terkait.               |
| 📋 Daftar Produk | Tabel produk milik penjual dengan kolom aksi (edit/hapus).                           |

### 3.3 Fitur Admin

| Fitur                        | Deskripsi                                                                            |
| :--------------------------- | :----------------------------------------------------------------------------------- |
| 📊 Ringkasan Platform        | 4 kartu statistik: Total Pendapatan, Total Pesanan, Total Penjual, Total Pembeli.    |
| 🏪 Kelola Penjual            | Tabel penjual dengan tombol **Approve** dan **Reject**.                              |
| 💰 Keuntungan Penjualan      | Menampilkan total pendapatan per penjual dari seluruh pesanan yang masuk.            |
| 📦 Detail Produk per Penjual | Expandable: harga, stok, jumlah terjual, jumlah pembeli unik, pendapatan per produk. |
| 👥 Data Pembeli              | Tabel pembeli dengan nama, email, telepon, dan jumlah pembelian.                     |

---

## 4. Arsitektur Database

### 4.1 Entity Relationship

```
User (users)
 ├── 1:N ──▶ Product (products)         [seller]
 ├── 1:N ──▶ CartItem (cart_items)       [user]
 ├── 1:N ──▶ WishlistItem (wishlist_items) [user]
 ├── 1:N ──▶ Order (orders)             [seller]
 └── 1:N ──▶ OrderItem (order_items)    [buyer]

Product (products)
 ├── N:1 ──▶ User (users)               [seller]
 ├── 1:N ──▶ CartItem (cart_items)
 ├── 1:N ──▶ WishlistItem (wishlist_items)
 └── 1:N ──▶ OrderItem (order_items)

Order (orders)
 ├── N:1 ──▶ User (users)               [seller]
 └── 1:N ──▶ OrderItem (order_items)

OrderItem (order_items)
 ├── N:1 ──▶ Order (orders)
 ├── N:1 ──▶ Product (products)
 └── N:1 ──▶ User (users)               [buyer]
```

### 4.2 Penjelasan Entity

#### `User` (Tabel: `users`)

| Kolom           | Tipe                  | Keterangan                       |
| :-------------- | :-------------------- | :------------------------------- |
| `id`            | PrimaryKey, int, auto | ID unik user                     |
| `name`          | Required, str         | Nama lengkap                     |
| `email`         | Required, str, unique | Email login (unik)               |
| `phone`         | Optional, str         | Nomor telepon                    |
| `address`       | Optional, str         | Alamat                           |
| `password_hash` | Required, str         | Hash bcrypt dari password        |
| `role`          | Required, str         | `buyer` / `seller` / `admin`     |
| `is_verified`   | Required, bool        | Status verifikasi email          |
| `verify_token`  | Optional, str         | Token verifikasi satu kali pakai |

#### `Product` (Tabel: `products`)

| Kolom         | Tipe                  | Keterangan                            |
| :------------ | :-------------------- | :------------------------------------ |
| `id`          | PrimaryKey, int, auto | ID unik produk                        |
| `warung_name` | Required, str         | Nama warung pemilik                   |
| `name`        | Required, str         | Nama produk                           |
| `description` | Optional, str         | Deskripsi produk                      |
| `price`       | Required, float       | Harga produk (Rupiah)                 |
| `stock`       | Required, int         | Jumlah stok tersedia                  |
| `image_path`  | Optional, str         | Nama file gambar di `static/uploads/` |
| `seller`      | Required, FK → User   | Penjual pemilik produk                |

#### `CartItem` (Tabel: `cart_items`)

| Kolom      | Tipe                   | Keterangan                |
| :--------- | :--------------------- | :------------------------ |
| `id`       | PrimaryKey, int, auto  | ID unik                   |
| `user`     | Required, FK → User    | Pembeli pemilik keranjang |
| `product`  | Required, FK → Product | Produk dalam keranjang    |
| `quantity` | Required, int          | Jumlah item               |

#### `WishlistItem` (Tabel: `wishlist_items`)

| Kolom     | Tipe                   | Keterangan              |
| :-------- | :--------------------- | :---------------------- |
| `id`      | PrimaryKey, int, auto  | ID unik                 |
| `user`    | Required, FK → User    | Pembeli                 |
| `product` | Required, FK → Product | Produk yang di-wishlist |

#### `Order` (Tabel: `orders`)

| Kolom          | Tipe                  | Keterangan                                        |
| :------------- | :-------------------- | :------------------------------------------------ |
| `id`           | PrimaryKey, int, auto | ID unik pesanan                                   |
| `seller`       | Required, FK → User   | Penjual yang menerima pesanan                     |
| `total_amount` | Required, float       | Total jumlah pembayaran                           |
| `created_at`   | Required, str         | Tanggal & waktu pembuatan (`YYYY-MM-DD HH:MM:SS`) |

#### `OrderItem` (Tabel: `order_items`)

| Kolom          | Tipe                   | Keterangan                          |
| :------------- | :--------------------- | :---------------------------------- |
| `id`           | PrimaryKey, int, auto  | ID unik                             |
| `order`        | Required, FK → Order   | Pesanan induk                       |
| `product`      | Required, FK → Product | Referensi produk                    |
| `buyer`        | Required, FK → User    | Pembeli yang memesan                |
| `product_name` | Required, str          | Snapshot nama produk saat pembelian |
| `warung_name`  | Required, str          | Snapshot nama warung saat pembelian |
| `price`        | Required, float        | Harga saat pembelian                |
| `quantity`     | Required, int          | Jumlah yang dibeli                  |

---

## 5. Struktur Direktori

```
Data Website Marketplace Warung UMKM Online/
├── app.py                          # Backend utama (models, routes, logic)
├── .env                            # Variabel environment (DB credentials, secret key)
├── README.md                       # Dokumentasi teknis ini
├── requirements.txt                # Daftar dependensi Python
├── static/
│   └── uploads/                    # Penyimpanan gambar produk
└── templates/                      # 14 halaman HTML (Jinja2)
    ├── index.html                  # Beranda / Halaman utama produk
    ├── product_detail.html         # Detail produk + beli + wishlist
    ├── login.html                  # Form login
    ├── register.html               # Form registrasi
    ├── verify.html                 # Halaman verifikasi email
    ├── about-us.html               # Tentang Kami
    ├── contact-us.html             # Kontak Kami
    ├── buyer_dashboard.html        # Dashboard pembeli (keranjang)
    ├── cart.html                   # Halaman keranjang belanja
    ├── wishlist.html               # Halaman wishlist
    ├── checkout.html               # Halaman checkout
    ├── seller_dashboard.html       # Dashboard penjual + tambah produk
    ├── edit_product.html           # Form edit produk
    └── admin_dashboard.html        # Dashboard admin (statistik & kelola)
```

---

## 6. Routing & API Endpoints

### 6.1 Public Routes

| Endpoint        | Method | Deskripsi                                                |
| :-------------- | :----: | :------------------------------------------------------- |
| `/`             |  GET   | Beranda — menampilkan produk dengan stok > 0             |
| `/product/<id>` |  GET   | Detail produk (gambar, deskripsi, harga, wishlist, beli) |
| `/about-us`     |  GET   | Halaman Tentang Kami                                     |
| `/contact-us`   |  GET   | Halaman Kontak                                           |

### 6.2 Authentication Routes

| Endpoint          |  Method   | Deskripsi                             |
| :---------------- | :-------: | :------------------------------------ |
| `/register`       | GET, POST | Registrasi akun baru (default: buyer) |
| `/verify/<token>` |    GET    | Verifikasi email via token unik       |
| `/login`          | GET, POST | Login — redirect sesuai role          |
| `/logout`         |    GET    | Logout & hapus session                |

### 6.3 Buyer Routes

| Endpoint                |  Method   | Role  | Deskripsi                              |
| :---------------------- | :-------: | :---: | :------------------------------------- |
| `/dashboard/buyer`      |    GET    | Buyer | Dashboard pembeli + keranjang          |
| `/cart`                 |    GET    | Buyer | Halaman keranjang belanja              |
| `/cart/add/<id>`        |   POST    | Buyer | Tambah produk ke keranjang             |
| `/cart/remove/<id>`     |   POST    | Buyer | Hapus item dari keranjang              |
| `/wishlist`             |    GET    | Buyer | Halaman wishlist                       |
| `/wishlist/toggle/<id>` |   POST    | Buyer | Toggle tambah/hapus wishlist           |
| `/checkout`             | GET, POST | Buyer | Form checkout → buat Order + OrderItem |
| `/upgrade-seller`       |    GET    | Buyer | Upgrade akun ke role seller            |

### 6.4 Seller Routes

| Endpoint               |  Method   |  Role  | Deskripsi                               |
| :--------------------- | :-------: | :----: | :-------------------------------------- |
| `/dashboard/seller`    | GET, POST | Seller | Dashboard penjual + tambah produk       |
| `/product/edit/<id>`   | GET, POST | Seller | Edit data dan gambar produk             |
| `/product/delete/<id>` |   POST    | Seller | Hapus produk (+ gambar, cart, wishlist) |

### 6.5 Admin Routes

| Endpoint              | Method | Role  | Deskripsi                             |
| :-------------------- | :----: | :---: | :------------------------------------ |
| `/admin`              |  GET   | Admin | Dashboard utama admin                 |
| `/admin/approve/<id>` |  GET   | Admin | Approve penjual (set verified = true) |
| `/admin/reject/<id>`  |  GET   | Admin | Reject penjual (set verified = false) |

---

## 7. Alur Bisnis Aplikasi

### 7.1 Alur Registrasi & Verifikasi

```
[User] → Buka /register → Isi form (nama, email, telp, password, role)
       → Sistem buat akun (is_verified=False, generate token)
       → Redirect ke /verify/<token>
       → Klik verifikasi → is_verified=True
       → Redirect ke /login
```

### 7.2 Alur Pembelian Produk

```
[Buyer] → Login → Diarahkan ke Beranda (/)
        → Klik produk → Halaman detail produk
        → Tambah ke Keranjang (qty) atau Tambah ke Wishlist
        → Buka /cart → Review item & total
        → Klik "Proses Pembayaran" → /checkout
        → Isi alamat, metode pembayaran, kurir
        → Submit → Sistem buat Order + OrderItem per penjual
        → Stok produk dikurangi → Cart dibersihkan
```

### 7.3 Alur Penjualan Produk

```
[Seller] → Login → Diarahkan ke /dashboard/seller
         → Isi form tambah produk (nama warung, produk, desc, stok, harga, gambar)
         → Submit → Produk tersimpan di database + gambar di static/uploads/
         → Edit / Hapus produk dari tabel "Produk Saya"
```

### 7.4 Alur Admin

```
[Admin] → Login (email: anandatechnologysolution@gmail.com, password: admin123)
        → Diarahkan ke /admin
        → Melihat ringkasan platform (pendapatan, pesanan, jumlah user)
        → Kelola penjual: Approve ✔ atau Reject ✖
        → Expand detail produk per penjual (terjual, pembeli, pendapatan)
        → Review data pembeli + jumlah pembelian
```

---

## 8. Keamanan

| Aspek                  | Implementasi                                                                                                                              |
| :--------------------- | :---------------------------------------------------------------------------------------------------------------------------------------- |
| **Password Hashing**   | bcrypt dengan salt otomatis (tidak disimpan plain text).                                                                                  |
| **Session**            | Flask session dengan `SECRET_KEY` dari environment variable.                                                                              |
| **Role-Based Access**  | Decorator `require_role()` memvalidasi role & verifikasi di setiap route.                                                                 |
| **File Upload**        | Hanya menerima MIME type: `image/jpeg`, `image/png`, `image/webp`. Nama file di-sanitasi dengan `secure_filename` dan diberi prefix UUID. |
| **Email Verification** | Token UUID unik per registrasi. Akun tidak bisa login sebelum diverifikasi.                                                               |
| **Ownership Check**    | Edit/hapus produk divalidasi — hanya pemilik produk yang bisa mengakses.                                                                  |

---

## 9. Instalasi & Konfigurasi

### Prasyarat

- Python 3.8+
- MySQL Server (aktif & running)
- pip (Python package manager)

### Langkah Instalasi

```bash
# 1. Masuk ke direktori project
cd "Data Website Marketplace Warung UMKM Online"

# 2. Buat virtual environment
python -m venv venv

# 3. Aktifkan virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 4. Install dependensi
pip install flask pony pymysql bcrypt werkzeug python-dotenv
```

### Buat Database MySQL

```sql
CREATE DATABASE marketplace_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

> **Catatan:** Tabel akan dibuat otomatis oleh PonyORM saat aplikasi pertama kali dijalankan (`create_tables=True`).

---

## 10. Menjalankan Aplikasi

```bash
python app.py
```

Aplikasi akan berjalan di:

```
http://127.0.0.1:5000
```

Port dapat diubah melalui variabel `PORT` di file `.env`.

---

## 11. Akses Admin Dashboard

Akun admin dibuat otomatis saat aplikasi pertama kali dijalankan (auto-seeding).

| Field             | Value                                |
| :---------------- | :----------------------------------- |
| **Email**         | `anandatechnologysolution@gmail.com` |
| **Password**      | `admin123`                           |
| **URL Dashboard** | `http://127.0.0.1:5000/admin`        |

### Langkah Akses:

1. Jalankan aplikasi (`python app.py`).
2. Buka browser dan navigasi ke `http://127.0.0.1:5000/login`.
3. Login menggunakan kredensial admin di atas.
4. Sistem otomatis mengarahkan ke halaman **Admin Dashboard**.

### Fitur Dashboard Admin:

- **📊 Stat Cards** — Total pendapatan platform, total pesanan, jumlah penjual & pembeli.
- **🏪 Kelola Penjual** — Tabel penjual lengkap dengan tombol Approve/Reject.
- **📦 Detail Produk** — Klik "Lihat Produk" untuk expand detail per penjual: nama produk, harga, stok, terjual, pembeli unik, pendapatan.
- **👥 Data Pembeli** — Informasi pembeli dan jumlah item yang telah dibeli.

---

## 12. Konfigurasi Environment

Buat file `.env` di root project:

```env
SECRET_KEY=supersecurekey123
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=yourpassword
DB_NAME=marketplace_db
PORT=5000
```

| Variabel      | Deskripsi                               | Default             |
| :------------ | :-------------------------------------- | :------------------ |
| `SECRET_KEY`  | Secret key Flask untuk enkripsi session | `supersecurekey123` |
| `DB_HOST`     | Hostname MySQL server                   | —                   |
| `DB_USER`     | Username MySQL                          | —                   |
| `DB_PASSWORD` | Password MySQL                          | —                   |
| `DB_NAME`     | Nama database MySQL                     | —                   |
| `PORT`        | Port server Flask                       | `5000`              |

---

## 13. Troubleshooting

| Error                                         | Penyebab                                                 | Solusi                                                                       |
| :-------------------------------------------- | :------------------------------------------------------- | :--------------------------------------------------------------------------- |
| `ERDiagramError: Reverse attribute not found` | Entity PonyORM tidak memiliki relasi balik (Set).        | Pastikan setiap `Required(Entity)` punya `Set('Entity')` di sisi sebaliknya. |
| `DatabaseSessionIsOver`                       | Akses atribut entity di luar `db_session`.               | Pindahkan `render_template()` ke **dalam** blok `with db_session`.           |
| `ValueError: cannot be set to None`           | PonyORM `Optional(str)` tidak menerima `None`.           | Gunakan string kosong `''` sebagai pengganti `None`.                         |
| `Access denied for user`                      | Kredensial MySQL salah.                                  | Periksa `DB_USER` dan `DB_PASSWORD` di `.env`.                               |
| `Can't connect to MySQL server`               | MySQL server tidak berjalan.                             | Pastikan MySQL service aktif dan `DB_HOST` benar.                            |
| Login gagal biasa                             | Password atau email salah, atau akun belum diverifikasi. | Verifikasi akun terlebih dahulu via `/verify/<token>`.                       |

---

> **© 2026 UMKM Online — Marketplace Warung UMKM. All rights reserved.**
