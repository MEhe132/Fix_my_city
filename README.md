# Fix My City (Bangladesh Civic Infrastructure Issue Tracker) 🇧🇩

An advanced civic technology platform designed to track, triage, and resolve broken public infrastructure (potholes, water leaks, streetlights, sanitation dumps, and drainage waterlogging) across Dhaka municipal wards (DNCC & DSCC) in Bangladesh.

---

## 🏛️ System Architecture & Core Features

### 1. Two-Tier User Roles
* **Citizen**: Reports infrastructure hazards, upvotes issues, tracks lifecycle progression, generates statutory PDF petitions, and shares social campaigns on Facebook & WhatsApp.
* **Municipal Authority / Admin Console (`/authority/dashboard/`)**: Dedicated triage desk for ward councillors and municipal engineers to review issues, dispatch work orders (`In Progress`), upload before/after photographic proof of resolution, and mark issues `Resolved`.
* **Immutable Audit Trail (`StatusHistory`)**: Logs every status update with the officer's identity, remarks, and proof images.

### 2. AI-Generated Image & Spam Verification (Combine Method)
* **Camera Hardware EXIF Fast-Path**: If an image possesses authentic phone camera hardware tags (`Make`, `Model`, `FocalLength`, or `GPSInfo`) from manufacturers (Apple, Samsung, Xiaomi, Google Pixel, Realme, etc.), it is instantly approved (`Auto-Verified (Camera EXIF)`).
* **Synthetic & Digital Art Detector**: Scans binary headers for generative AI prompt markers (`midjourney`, `dall-e`, `stablediffusion`, `comfyui`, `prompt:`, etc.) and evaluates local sensor noise variance and saturation clustering.
* **Citizen Alert**: Prevents fraudulent reporting by flagging synthetic images:
  > *"⚠️ Image detected as AI-generated or digital art. Please upload a genuine on-site photograph."*

### 3. Real-World Bangladesh Civic Action Mechanism
* **1-Click Social Campaign Generator**: Formats viral civic alert cards with jurisdiction ward tags (`#Ward19 #DNCC #FixMyCityBD`), councillor mentions, and upvote milestones. Provides 1-click **Share on WhatsApp**, **Share on Facebook**, and clipboard copy.
* **Automated Official PDF Petition Generator (`ReportLab`)**: Generates formal municipal grievance petitions under the **Local Government (City Corporation) Act 2009** and **Right to Information (RTI) Act 2009 (Section 8)**, complete with metadata tables, embedded photographs with GPS watermarks, and citizen delegation signature lines.
* **Public Ward Accountability Board (`/accountability/`)**: Live municipal leaderboard displaying total reported issues, resolved counts, in-progress backlogs, resolution rates (`%`), and average turnaround delay (`days`) per ward.

### 4. Interactive Leaflet.js GIS Mapping
* Centered on Dhaka (`23.8103°N, 90.4125°E`).
* Dynamic Ward filter dropdown (Ward 19 Banani/Gulshan, Ward 18 Baridhara, Ward 11 Mirpur, Ward 32 Dhanmondi, Ward 7 Lalbagh).
* 1-Click Map Layer Switcher:
  * 🗺️ **Civic Clean** (Carto Voyager via Cloudflare CDN)
  * 🏙️ **Esri Streets** (Esri World Street Map)
  * 🛰️ **Satellite Aerial** (Esri World Imagery)
  * 🌙 **Dark Mode** (Carto Dark Matter)
* **Live Geolocation & Auto-Address Geocoding**:
  * `🎯 Locate Me`: Reads live browser GPS with automatic fallback to network IP geolocation.
  * Auto-translates pin coordinates into real Bangladesh street addresses (via OpenStreetMap Nominatim proxy).

---

## 🚀 Quickstart & Setup Guide

### 1. Clone the Repository
```bash
git clone https://github.com/MEhe132/Fix_my_city.git
cd Fix_my_city
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Apply Migrations & Seed Sample Data
```bash
python manage.py migrate
python populate_bd_sample_data.py
```

### 4. Run the Development Server
```bash
python manage.py runserver
```
Visit **[http://127.0.0.1:8000/](http://127.0.0.1:8000/)** in your browser.

---

## 🧪 Automated Test Suite

Run the full automated unit and integration test suite:
```bash
python manage.py test issues
```
All 13 tests verify user roles, AI image detection, ReportLab PDF generation, social campaigns, and accountability views.

---

## 🔑 Pre-Seeded Accounts for Testing

| Role | Username | Password | Jurisdiction |
| :--- | :--- | :--- | :--- |
| **Municipal Official** | `ward19_official` | `password123` | **Ward 19 (DNCC)** & Road Engineering |
| **Citizen** | `arif_ahmed` | `password123` | Citizen Reporter |
| **Super Admin** | `admin` | `adminpassword123` | City Administrator / Admin Console |

---

## 📄 License & Attribution
Developed for 3rd Year Software Engineering Project under the Bangladesh Civic Infrastructure Framework.
