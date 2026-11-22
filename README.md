![AID.uz](readme_images/banner.png)

Klinikalar uchun AI yordamchi CRM. Shifokor gapiradi, AI bemor kartasini to'ldiradi va qand, yurak kasalligi hamda kelmay qolish xavfini oldindan aytadi.

![Bosh sahifa](readme_images/1.png)

| | |
|---|---|
| ![Bemorlar](readme_images/2.png) | ![Bemor kartasi](readme_images/3.png) |
| ![Ovoz bilan yangi bemor](readme_images/4.png) | ![Protokol va AI bashorat](readme_images/5.png) |
| ![Uchrashuvlar](readme_images/6.png) | ![Obuna](readme_images/7.png) |

![Mobil versiya](readme_images/mobile.png)

## Ishga tushirish

```bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python3 manage.py migrate
python3 manage.py runserver
```

Brauzerda: http://localhost:8000

Django, scikit-learn, OpenAI, ElevenLabs. AI Hackathon 2026.
