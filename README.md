# Hastane Yönetim Sistemi
# Hospital Management System

![Proje Logosu](https://placehold.co/800x200/3498db/ffffff?text=Hastane+Y%C3%B6netim+Sistemi&font=roboto)
[Türkçe](README.tr.md)

Bu proje, Flask ve SQLAlchemy kullanılarak geliştirilmiş, modern ve kullanıcı dostu bir hastane randevu ve yönetim sistemidir. Sistem; hasta, doktor ve sekreter olmak üzere üç farklı kullanıcı rolünü destekler ve her rol için özelleştirilmiş paneller sunar.
![Project Logo](https://placehold.co/800x200/3498db/ffffff?text=Hospital+Management+System&font=roboto)

This is a modern and user-friendly hospital appointment and management system developed using Flask and SQLAlchemy. The system supports three different user roles: patient, doctor, and secretary, offering customized dashboards for each.

---

## 📖 İçindekiler
## 📖 Table of Contents

- [🚀 Proje Hakkında](#-proje-hakkında)
- [✨ Temel Özellikler](#-temel-özellikler)
  - [Hasta Rolü](#hasta-rolü)
  - [Doktor Rolü](#doktor-rolü)
  - [Sekreter Rolü](#sekreter-rolü)
- [📸 Ekran Görüntüleri](#-ekran-görüntüleri)
- [🛠️ Kullanılan Teknolojiler](#️-kullanılan-teknolojiler)
- [⚙️ Kurulum ve Başlatma](#️-kurulum-ve-başlatma)
- [🔑 Varsayılan Kullanıcı Bilgileri](#-varsayılan-kullanıcı-bilgileri)
- [📂 Proje Yapısı](#-proje-yapısı)
- [🚀 About The Project](#-about-the-project)
- [✨ Core Features](#-core-features)
  - [Patient Role](#patient-role)
  - [Doctor Role](#doctor-role)
  - [Secretary Role](#secretary-role)
- [📸 Screenshots](#-screenshots)
- [🛠️ Tech Stack](#️-tech-stack)
- [⚙️ Installation and Setup](#️-installation-and-setup)
- [🔑 Default Credentials](#-default-credentials)
- [📂 Project Structure](#-project-structure)

---

## 🚀 Proje Hakkında
## 🚀 About The Project

Hastane Yönetim Sistemi, randevu alma süreçlerini dijitalleştirerek hem hastalar hem de hastane personeli için verimliliği artırmayı hedefler. Hastalar online olarak kolayca randevu alabilirken, doktorlar kendi takvimlerini yönetebilir ve sekreterler ise tüm sistemin idari kontrolünü sağlayabilir.
The Hospital Management System aims to increase efficiency for both patients and hospital staff by digitizing the appointment booking process. Patients can easily book appointments online, doctors can manage their schedules, and secretaries can handle the administrative control of the entire system.

---

## ✨ Temel Özellikler
## ✨ Core Features

### Hasta Rolü
### Patient Role

- **Kayıt Olma:** Yeni hastalar sisteme kolayca kayıt olabilir.
- **Profil Yönetimi:** Kişisel bilgileri ve şifreyi güncelleme.
- **Randevu Alma:** Branş ve doktora göre uygun tarih ve saatleri listeleyerek randevu oluşturma.
- **Randevu Yönetimi:** Gelecek ve geçmiş randevuları görüntüleme.
- **Randevu İptali:** Gelecek randevuları iptal etme.
- **Detay Görüntüleme:** Randevu detaylarını ve doktorun eklediği notları görme.
- **Sign Up:** New patients can easily register on the system.
- **Profile Management:** Update personal information and password.
- **Book Appointment:** Create an appointment by listing available dates and times based on department and doctor.
- **Appointment Management:** View upcoming and past appointments.
- **Cancel Appointment:** Cancel upcoming appointments.
- **View Details:** See appointment details and notes added by the doctor.

### Doktor Rolü
### Doctor Role

- **Doktor Paneli:** Yaklaşan randevuları ve genel duyuruları listeleme.
- **Randevu Yönetimi:** Randevuları "Tamamlandı" olarak işaretleme.
- **Not Ekleme:** Muayene sonrası randevulara not ekleme.
- **Hasta Geçmişi:** Hastaların geçmiş randevu ve şikayet bilgilerini görüntüleme.
- **Doctor Dashboard:** List upcoming appointments and general announcements.
- **Appointment Management:** Mark appointments as "Completed".
- **Add Notes:** Add post-examination notes to appointments.
- **Patient History:** View patients' past appointment and complaint information.

### Sekreter Rolü
### Secretary Role

- **Yönetim Paneli:** Sistemle ilgili genel istatistikleri (toplam hasta, doktor, bekleyen randevu sayısı vb.) görme.
- **Kapsamlı Randevu Yönetimi:** Tüm randevuları listeleme, filtreleme (hasta, doktor, tarih, durum bazında), düzenleme ve silme.
- **Yeni Randevu Oluşturma:** Hastalar adına randevu oluşturma.
- **Doktor Yönetimi:** Sisteme yeni doktor ekleme.
- **Branş Yönetimi:** Yeni poliklinik/branş tanımlama.
- **Duyuru Yönetimi:** Doktor ve diğer personelin görebileceği duyurular oluşturma.
- **Admin Dashboard:** View general system statistics (total patients, doctors, pending appointments, etc.).
- **Comprehensive Appointment Management:** List, filter (by patient, doctor, date, status), edit, and delete all appointments.
- **Create New Appointment:** Create appointments on behalf of patients.
- **Doctor Management:** Add new doctors to the system.
- **Department Management:** Define new clinics/departments.
- **Announcement Management:** Create announcements visible to doctors and other staff.

---

## 📸 Ekran Görüntüleri
## 📸 Screenshots

*Projenizin çalışan halinden ekran görüntülerini bu bölüme ekleyebilirsiniz.*
Aşağıda sistemin temel sayfalarından bazı ekran görüntüleri yer almaktadır.
Here are some screenshots from the main pages of the system.

| Giriş Sayfası | Hasta Paneli |
| Hasta Giriş & Kayıt | Randevu Alma |
| Patient Login & Sign Up | Book Appointment |
| :---: | :---: |
| ![Giriş Sayfası](https://placehold.co/400x300/ecf0f1/34495e?text=Giriş+Ekranı) | ![Hasta Paneli](https://placehold.co/400x300/ecf0f1/34495e?text=Hasta+Paneli) |
| ![Hasta Giriş](hastane_projesi/assets/hastagiriş.png) | ![Randevu Alma](hastane_projesi/assets/randevual.png) |
| ![Patient Login](hastane_projesi/assets/hastagiriş.png) | ![Book Appointment](hastane_projesi/assets/randevual.png) |

| Randevu Alma Ekranı | Sekreter Paneli |
| Randevu Detayı | Doktor Paneli |
| Appointment Detail | Doctor Dashboard |
| :---: | :---: |
| ![Randevu Alma Ekranı](https://placehold.co/400x300/ecf0f1/34495e?text=Randevu+Alma) | ![Sekreter Paneli](https://placehold.co/400x300/ecf0f1/34495e?text=Sekreter+Paneli) |
| ![Randevu Detayı](hastane_projesi/assets/randevu.png) | ![Doktor Paneli](hastane_projesi/assets/doktorpanel.png) |
| ![Appointment Detail](hastane_projesi/assets/randevu.png) | ![Doctor Dashboard](hastane_projesi/assets/doktorpanel.png) |

| Sekreter Paneli | Sekreter Randevu Yönetimi |
| Secretary Dashboard | Secretary Appointment Management |
| :---: | :---: |
| ![Sekreter Paneli](hastane_projesi/assets/sekreterpanel.png) | ![Sekreter Randevu Yönetimi](hastane_projesi/assets/sekreterrandevu.png) |
| ![Secretary Dashboard](hastane_projesi/assets/sekreterpanel.png) | ![Secretary Appointment Management](hastane_projesi/assets/sekreterrandevu.png) |

| Sekreter Branş Yönetimi | Sekreter Doktor Ekleme |
| Secretary Department Management | Secretary Add Doctor |
| :---: | :---: |
| ![Sekreter Branş Yönetimi](hastane_projesi/assets/sekreterbranş.png) | ![Sekreter Doktor Ekleme](hastane_projesi/assets/sekreterdoktor.png) |
| ![Secretary Department Management](hastane_projesi/assets/sekreterbranş.png) | ![Secretary Add Doctor](hastane_projesi/assets/sekreterdoktor.png) |

| Diğer Giriş Ekranları |
| Other Login Screens |
| :---: |
| ![Doktor Giriş](hastane_projesi/assets/doktorgiriş.png) |
| ![Sekreter Giriş](hastane_projesi/assets/sekretergiriş.png) |
| ![Yeni Kayıt](hastane_projesi/assets/kayıtol.png) |
| ![Doctor Login](hastane_projesi/assets/doktorgiriş.png) |
| ![Secretary Login](hastane_projesi/assets/sekretergiriş.png) |
| ![New Registration](hastane_projesi/assets/kayıtol.png) |


---

## 🛠️ Kullanılan Teknolojiler
## 🛠️ Tech Stack

- **Backend:**
  - ![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
  - ![Flask](https://img.shields.io/badge/Flask-2.x-black?logo=flask)
  - ![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-1.4%2B-orange?logo=sqlalchemy)
  - ![Werkzeug](https://img.shields.io/badge/Werkzeug-2.x-gray) (Şifreleme için)
- **Veritabanı:**
  - ![Werkzeug](https://img.shields.io/badge/Werkzeug-2.x-gray) (for password hashing)
- **Database:**
  - ![SQLite](https://img.shields.io/badge/SQLite-3-blue?logo=sqlite)
- **Frontend:**
  - ![HTML5](https://img.shields.io/badge/HTML5-E34F26?logo=html5&logoColor=white)
  - ![CSS3](https://img.shields.io/badge/CSS3-1572B6?logo=css3&logoColor=white)
  - ![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?logo=javascript&logoColor=black)
  - ![Bootstrap](https://img.shields.io/badge/Bootstrap-5.x-purple?logo=bootstrap)
  - ![Bootstrap](https://img.shields.io/badge/Bootstrap-5.x-purple?logo=bootstrap&logoColor=white)

---

## ⚙️ Kurulum ve Başlatma
## ⚙️ Installation and Setup

Projeyi yerel makinenizde çalıştırmak için aşağıdaki adımları izleyin.
Follow these steps to run the project on your local machine.

1.  **Projeyi Klonlayın:**
1.  **Clone the Project:**
    ```bash
    git clone https://github.com/kullanici-adiniz/proje-repo-adiniz.git
    cd hastane_projesi
    git clone https://github.com/your-username/your-repo-name.git
    cd hospital_system
    ```

2.  **Sanal Ortam Oluşturun ve Aktif Edin (Önerilir):**
2.  **Create and Activate a Virtual Environment (Recommended):**
    ```bash
    # Windows
    python -m venv venv
    venv\Scripts\activate

    # macOS / Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Gerekli Kütüphaneleri Yükleyin:**
    *Projenizde bir `requirements.txt` dosyası oluşturup bağımlılıkları oraya eklemeniz en iyi pratiktir. Eğer yoksa, aşağıdaki komutlarla manuel olarak yükleyebilirsiniz.*
3.  **Install Required Libraries:**
    *It's best practice to create a `requirements.txt` file in your project and add dependencies there. If not, you can install them manually with the commands below.*
    ```bash
    pip install Flask Flask-SQLAlchemy
    ```

4.  **Uygulamayı Başlatın:**
4.  **Run the Application:**
    ```bash
    cd hastane_projesi
    python app.py
    ```

5.  **Tarayıcıda Açın:**
    Uygulama başlatıldığında terminalde belirtilen adrese gidin (genellikle `http://127.0.0.1:5000`).
5.  **Open in Browser:**
    Navigate to the address specified in the terminal when the application starts (usually `http://127.0.0.1:5000`).

    > **Not:** Uygulama ilk kez başlatıldığında `hastane.db` veritabanı dosyası otomatik olarak oluşturulacak ve varsayılan branş, sekreter, hasta ve doktor verileri eklenecektir.
    > **Note:** When the application is run for the first time, the `hastane.db` database file will be automatically created, and default data for departments, secretary, patient, and doctors will be added.

---

## 🔑 Varsayılan Kullanıcı Bilgileri
## 🔑 Default Credentials

Sistemi test etmek için aşağıdaki varsayılan hesapları kullanabilirsiniz:
You can use the following default accounts to test the system:

- **Hasta Hesabı:**
  - **E-posta:** `hasta@hastane.com`
  - **Şifre:** `hasta123`
- **Patient Account:**
  - **Email:** `hasta@hastane.com`
  - **Password:** `hasta123`

- **Doktor Hesabı:**
  - **E-posta:** `mehmet.demir@hastane.com` (ve diğerleri)
  - **Şifre:** `doktor123`
- **Doctor Account:**
  - **Email:** `mehmet.demir@hastane.com` (and others)
  - **Password:** `doktor123`

- **Sekreter Hesabı:**
  - **E-posta:** `sekreter@hastane.com`
  - **Şifre:** `sekreter123`
- **Secretary Account:**
  - **Email:** `sekreter@hastane.com`
  - **Password:** `sekreter123`

---

## 📂 Proje Yapısı
## 📂 Project Structure

```
hastane_projesi/
├── static/
│   └── style.css         # Genel CSS stilleri
├── templates/            # HTML şablonları
│   ├── hasta_paneli.html
│   ├── doktor_paneli.html
│   ├── sekreter_paneli.html
│   └── ... (diğer tüm .html dosyaları)
├── app.py                # Ana Flask uygulaması, veritabanı modelleri ve route'lar
├── hastane.db            # SQLite veritabanı dosyası (ilk çalıştırmada oluşur)
└── README.md             # Bu dosya
```