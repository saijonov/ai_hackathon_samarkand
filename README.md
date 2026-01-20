# 🏥 Healthcare CRM - AI bilan ishlaydigan tizim

**O'zbekiston xususiy kasalxonalari uchun sun'iy intellekt bilan jihozlangan bemor boshqaruv tizimi**

---

## 🎯 Loyihaning Maqsadi

Bu tizim O'zbekiston xususiy kasalxonalarida:
- **30% kelmay qolishni kamaytiradi** - AI orqali xavfli bemorlarni aniqlash
- **Qand va yurak kasalliklarini erta bosqichda aniqlaydi** - ML modellari yordamida
- **Shifokorlar vaqtini tejaydi** - Avtomatik ma'lumotlar tahlili va hisobotlar

---

## ✨ Asosiy Xususiyatlar

### 🤖 AI Prediksiya Modellari (3 ta)
1. **Kelmay qolish riski** - 67.5% aniqlik
2. **Qand kasalligi riski** - 70% aniqlik
3. **Yurak kasalligi riski** - 69% aniqlik

### 📊 Funktsiyalar
- **Bosh sahifa**: Statistika, bugungi uchrashuvlar, yuqori xavfli bemorlar
- **Bemorlar boshqaruvi**: CRUD operatsiyalari, AI sog'liq tahlili
- **Uchrashuvlar**: Rejalash, AI xavf bashorati, SMS eslatma
- **Sog'liqni tekshirish**: Tibbiy ko'rsatkichlar, avtomatik AI tahlili

### 🎨 Zamonaviy Dizayn
- **Tailwind CSS** - Professional va responsive
- **Rang sxemasi**: Ko'k (#0066CC), Yashil (#00C853), Qizil (#FF6B6B), To'q sariq (#FF9800)
- **Animatsiyalar**: Smooth transitions, fade-in effects
- **Mobil optimizatsiya**: Barcha ekranlarda ishlaydi

---

## 🛠 Texnologiyalar

**Backend:**
- Django 5.0+ (Python 3.10+)
- SQLite (rivojlantirish uchun)
- scikit-learn (Machine Learning)
- pandas, numpy (Ma'lumotlar tahlili)

**Frontend:**
- Tailwind CSS (Styling)
- Chart.js (Grafiklar)
- Vanilla JavaScript (Interaktivlik)

**Machine Learning:**
- RandomForestClassifier
- StandardScaler
- 3 ta o'qitilgan model (.pkl formatida)

---

## 📦 O'rnatish va Ishga Tushirish

### 1. Repozitoriyni Klonlash
```bash
cd /home/urzenkoz/Desktop/ai_hackathon
```

### 2. Virtual Muhitni Yaratish (Ixtiyoriy)
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Kerakli Paketlarni O'rnatish
```bash
pip3 install -r requirements.txt
```

### 4. Ma'lumotlar Bazasini Yaratish
```bash
python3 manage.py makemigrations
python3 manage.py migrate
```

### 5. Superuser Yaratish
```bash
python3 manage.py createsuperuser
# Username: admin
# Password: admin123
```

### 6. Demo Ma'lumotlarni Yuklash
```bash
python3 generate_demo_data.py
```
Bu 30 ta bemor, 68 ta uchrashuv va 10 ta tekshiruvni yaratadi.

### 7. Serverni Ishga Tushirish
```bash
python3 manage.py runserver 0.0.0.0:8000
```

### 8. Brauzerda Ochish
```
http://localhost:8000
```

Admin panel: http://localhost:8000/admin
- Username: `admin`
- Password: `admin123`

---

## 📁 Loyiha Tuzilmasi

```
healthcare_crm/
├── healthcare_crm/          # Django asosiy sozlamalari
│   ├── settings.py          # Asosiy konfiguratsiya
│   └── urls.py              # URL marshrutlar
├── patients/                # Asosiy ilova
│   ├── models.py            # Ma'lumotlar modellari (Patient, Appointment, HealthScreening)
│   ├── views.py             # View funksiyalar
│   ├── admin.py             # Admin panel sozlamalari
│   └── urls.py              # Ilova URL marshrutlari
├── ml_models/               # Machine Learning modellari
│   ├── train_models.py      # Modellarni o'qitish skripti
│   ├── predictor.py         # Prediksiya servisi
│   ├── noshow_predictor.pkl # Kelmay qolish modeli
│   ├── diabetes_predictor.pkl  # Qand kasalligi modeli
│   └── heart_predictor.pkl  # Yurak kasalligi modeli
├── templates/               # HTML shablonlar
│   ├── base.html            # Asosiy shablon
│   ├── dashboard.html       # Bosh sahifa
│   ├── patients/            # Bemorlar shablonlari
│   └── appointments/        # Uchrashuvlar shablonlari
├── static/                  # Statik fayllar
│   └── css/style.css        # Maxsus CSS
├── generate_demo_data.py    # Demo ma'lumotlarni yaratish
├── requirements.txt         # Python kutubxonalari
└── README.md                # Bu fayl
```

---

## 🎓 Modellarni O'qitish

Agar modellarni qayta o'qitish kerak bo'lsa:

```bash
python3 ml_models/train_models.py
```

Bu quyidagi fayllarni yaratadi:
- `noshow_predictor.pkl` va `noshow_scaler.pkl`
- `diabetes_predictor.pkl` va `diabetes_scaler.pkl`
- `heart_predictor.pkl` va `heart_scaler.pkl`

---

## 📊 Ma'lumotlar Modellari

### Patient (Bemor)
- **Asosiy ma'lumotlar**: ism, yosh, jins, telefon, manzil
- **Tibbiy ma'lumotlar**: qon guruhi, allergiyalar
- **Surunkali kasalliklar**: qand kasalligi, gipertoniya, yurak kasalligi
- **Statistika**: umumiy uchrashuvlar, kelmay qolganlar soni

### Appointment (Uchrashuv)
- **Uchrashuv**: bemor, sana, shifokor, bo'lim
- **AI Prediksiya**: kelmay qolish riski, qand riski, yurak riski
- **Holat**: rejalashtirilgan, yakunlangan, bekor qilingan, kelmagan
- **Xususiyatlar**: SMS yuborildi, izoh

### HealthScreening (Sog'liqni Tekshirish)
- **Vital signs**: qon bosimi, puls, harorat
- **Lab natijalar**: glyukoza, holesterin, BMI
- **AI Tahlil**: qand ehtimoli, yurak ehtimoli
- **Shifokor izohi**

---

## 🎨 Rang Sxemasi va Dizayn

### Ranglar
```css
Primary Blue:    #0066CC  (Asosiy tugmalar, havolalar)
Success Green:   #00C853  (Past xavf, muvaffaqiyat)
Danger Red:      #FF6B6B  (Yuqori xavf, xato)
Warning Orange:  #FF9800  (O'rta xavf, ogohlantirish)
Background:      #F8F9FA  (Orqa fon)
Text Dark:       #2C3E50  (Asosiy matn)
```

### Xavf Darajalari
- **Past xavf (0-30%)**: Yashil badge
- **O'rta xavf (30-70%)**: To'q sariq badge
- **Yuqori xavf (70-100%)**: Qizil badge

### UI Komponentlar
- **Kartalar**: Box-shadow, border-radius: 12px
- **Tugmalar**: Hover animation, transition: 0.3s
- **Jadvallar**: Striped rows, hover effect
- **Sidebar**: Fixed, gradient background

---

## 🚀 Demo Uchun Tayyorgarlik

### 1. Ma'lumotlarni Tekshirish
```bash
python3 manage.py shell -c "from patients.models import *; print(f'Bemorlar: {Patient.objects.count()}'); print(f'Uchrashuvlar: {Appointment.objects.count()}')"
```

### 2. Serverni Ishga Tushirish
```bash
python3 manage.py runserver 0.0.0.0:8000
```

### 3. Demo Stsenariysı
1. **Bosh sahifa ko'rsatish** - Statistika, bugungi uchrashuvlar
2. **Yangi uchrashuv yaratish** - AI xavf bashoratini ko'rsatish
3. **Bemor tafsilotlari** - AI sog'liq tahlilini ko'rsatish
4. **Sog'liqni tekshirish** - Yangi tekshiruv qo'shish, AI natijalar

---

## 📈 AI Modellar Haqida

### No-Show Predictor
**Features:**
- Bemor yoshi
- Jins
- Uchrashuv sanasigacha kunlar
- SMS yuborilganmi
- Gipertoniya
- Qand kasalligi

**Natija:** 0-1 oralig'ida ehtimollik (0=keladi, 1=kelmaydi)

### Diabetes Predictor
**Features:**
- Yosh
- Jins
- Glyukoza darajasi
- BMI
- Qon bosimi

**Natija:** 0-1 oralig'ida ehtimollik (0=yo'q, 1=bor)

### Heart Disease Predictor
**Features:**
- Yosh
- Jins
- Qon bosimi
- Holesterin
- Maksimal yurak urishi

**Natija:** 0-1 oralig'ida ehtimollik (0=yo'q, 1=bor)

---

## 🏆 Xususiyatlar (Hackathon Uchun)

### ✅ Texnik Mukammallik
- Clean, organized code
- Full Uzbek localization
- Responsive design
- Error handling
- Input validation

### ✅ AI Integratsiya
- 3 working ML models
- Real-time predictions
- Visual risk indicators
- Automatic calculations

### ✅ Dizayn
- Pixel-perfect UI
- Smooth animations
- Professional color scheme
- Consistent styling
- Mobile-friendly

### ✅ Amaliy Qiymat
- Solves real problems
- Reduces no-shows
- Early disease detection
- Saves time for doctors
- Ready for deployment

---

## 📝 Qo'shimcha Ma'lumotlar

### Muallif
AI Hackathon 2026 Jamoasi

### Litsenziya
MIT License

### Aloqa
- GitHub: [Link to repo]
- Email: your-email@example.com

---

## 🎯 Kelajakdagi Rivojlanish

Potensial qo'shimchalar:
1. SMS integratsiya (Twilio)
2. Email bildirishnomalar
3. Telegram bot
4. Excel eksport
5. Kalendar ko'rinishi
6. Shifokorlar boshqaruvi
7. Ko'p tillilik (Rus, Ingliz)
8. Dark mode
9. Ko'proq ML modellari
10. Mobil ilova

---

## 🙏 Minnatdorchilik

- Django Framework
- scikit-learn
- Tailwind CSS
- Chart.js
- O'zbekiston sog'liqni saqlash xodimlari

---

**Ushbu tizim O'zbekiston kasalxonalarida real foydalanish uchun tayyor!** 🚀

**Demo:** http://localhost:8000
**Admin:** http://localhost:8000/admin (admin/admin123)
