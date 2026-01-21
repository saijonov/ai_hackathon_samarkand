from django.db import models
from django.utils import timezone


class Patient(models.Model):
    """Bemor modeli - Patient model"""

    JINS_CHOICES = [
        ('E', 'Erkak'),
        ('A', 'Ayol'),
    ]

    QON_GURUHI_CHOICES = [
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
    ]

    ism = models.CharField(max_length=200, verbose_name='Ism')
    yosh = models.IntegerField(verbose_name='Yosh')
    jins = models.CharField(max_length=1, choices=JINS_CHOICES, verbose_name='Jins')
    telefon = models.CharField(max_length=20, verbose_name='Telefon')
    manzil = models.TextField(blank=True, null=True, verbose_name='Manzil')
    qon_guruhi = models.CharField(
        max_length=3,
        choices=QON_GURUHI_CHOICES,
        blank=True,
        null=True,
        verbose_name='Qon guruhi'
    )
    allergiyalar = models.TextField(blank=True, null=True, verbose_name='Allergiyalar')
    qand_kasalligi = models.BooleanField(default=False, verbose_name='Qand kasalligi')
    gipertoniya = models.BooleanField(default=False, verbose_name='Gipertoniya')
    yurak_kasalligi = models.BooleanField(default=False, verbose_name='Yurak kasalligi')
    umumiy_uchrashuvlar = models.IntegerField(default=0, verbose_name='Umumiy uchrashuvlar')
    kelmaganlar_soni = models.IntegerField(default=0, verbose_name='Kelmaganlar soni')
    yaratilgan_sana = models.DateTimeField(auto_now_add=True, verbose_name='Yaratilgan sana')

    class Meta:
        verbose_name = 'Bemor'
        verbose_name_plural = 'Bemorlar'
        ordering = ['-yaratilgan_sana']

    def kelmay_qolish_darajasi(self):
        """Calculate no-show rate as percentage"""
        if self.umumiy_uchrashuvlar == 0:
            return 0
        return round((self.kelmaganlar_soni / self.umumiy_uchrashuvlar) * 100, 1)

    def __str__(self):
        return f"{self.ism} - {self.yosh} yosh"


class Appointment(models.Model):
    """Uchrashuv modeli - Appointment model"""

    BOLIM_CHOICES = [
        ('terapiya', 'Terapiya'),
        ('kardiologiya', 'Kardiologiya'),
        ('endokrinologiya', 'Endokrinologiya'),
        ('nevrologiya', 'Nevrologiya'),
        ('pediatriya', 'Pediatriya'),
        ('ginekologiya', 'Ginekologiya'),
        ('boshqa', 'Boshqa'),
    ]

    HOLAT_CHOICES = [
        ('rejalashtirilgan', 'Rejalashtirilgan'),
        ('yakunlangan', 'Yakunlangan'),
        ('bekor_qilingan', 'Bekor qilingan'),
        ('kelmagan', 'Kelmagan'),
    ]

    bemor = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='uchrashuvlar',
        verbose_name='Bemor'
    )
    uchrashuv_sanasi = models.DateTimeField(verbose_name='Uchrashuv sanasi')
    rejalashtirilgan_sana = models.DateTimeField(auto_now_add=True, verbose_name='Rejalashtirilgan sana')
    shifokor = models.CharField(max_length=200, verbose_name='Shifokor')
    bolim = models.CharField(max_length=50, choices=BOLIM_CHOICES, verbose_name='Bölim')
    sms_yuborildi = models.BooleanField(default=False, verbose_name='SMS yuborildi')
    kelmay_qolish_riski = models.FloatField(null=True, blank=True, verbose_name='Kelmay qolish riski')
    qand_riski = models.FloatField(null=True, blank=True, verbose_name='Qand riski')
    yurak_riski = models.FloatField(null=True, blank=True, verbose_name='Yurak riski')
    holat = models.CharField(
        max_length=50,
        choices=HOLAT_CHOICES,
        default='rejalashtirilgan',
        verbose_name='Holat'
    )
    izoh = models.TextField(blank=True, verbose_name='Izoh')

    class Meta:
        verbose_name = 'Uchrashuv'
        verbose_name_plural = 'Uchrashuvlar'
        ordering = ['-uchrashuv_sanasi']

    def kunlar_farqi(self):
        """Calculate days between scheduling and appointment"""
        if self.uchrashuv_sanasi and self.rejalashtirilgan_sana:
            delta = self.uchrashuv_sanasi - self.rejalashtirilgan_sana
            return delta.days
        return 0

    def __str__(self):
        return f"{self.bemor.ism} - {self.uchrashuv_sanasi.strftime('%d.%m.%Y %H:%M')}"


class HealthScreening(models.Model):
    """Sog'liqni Tekshirish modeli - Health Screening model"""

    bemor = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='tekshiruvlar',
        verbose_name='Bemor'
    )
    uchrashuv = models.ForeignKey(
        Appointment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tekshiruvlar',
        verbose_name='Uchrashuv'
    )
    qon_bosimi_yuqori = models.IntegerField(null=True, blank=True, verbose_name='Qon bosimi (yuqori)')
    qon_bosimi_past = models.IntegerField(null=True, blank=True, verbose_name='Qon bosimi (past)')
    puls = models.IntegerField(null=True, blank=True, verbose_name='Puls')
    harorat = models.FloatField(null=True, blank=True, verbose_name='Harorat')
    glyukoza = models.FloatField(null=True, blank=True, verbose_name='Glyukoza (mg/dL)')
    holesterin = models.FloatField(null=True, blank=True, verbose_name='Holesterin')
    bmi = models.FloatField(null=True, blank=True, verbose_name='BMI')
    qand_ehtimoli = models.FloatField(null=True, blank=True, verbose_name='Qand ehtimoli')
    yurak_ehtimoli = models.FloatField(null=True, blank=True, verbose_name='Yurak ehtimoli')
    tekshirilgan_sana = models.DateTimeField(auto_now_add=True, verbose_name='Tekshirilgan sana')
    izoh = models.TextField(blank=True, verbose_name='Shifokor izohi')

    class Meta:
        verbose_name = 'Sog\'liqni tekshirish'
        verbose_name_plural = 'Sog\'liqni tekshirishlar'
        ordering = ['-tekshirilgan_sana']

    def __str__(self):
        return f"{self.bemor.ism} - {self.tekshirilgan_sana.strftime('%d.%m.%Y')}"


class Protocol(models.Model):
    """Protokol modeli - Protocol model for patient medical records"""

    PROTOCOL_TYPE_CHOICES = [
        ('diabetes', 'Qand kasalligi (Diabetes)'),
        ('heart', 'Yurak kasalligi (Heart Disease)'),
    ]

    QON_GURUHI_CHOICES = [
        ('O(I)', 'O(I)'),
        ('A(II)', 'A(II)'),
        ('B(III)', 'B(III)'),
        ('AB(IV)', 'AB(IV)'),
    ]

    JINS_CHOICES = [
        (1, 'Erkak'),
        (0, 'Ayol'),
    ]

    # Chest Pain Types for Heart Disease
    CHEST_PAIN_CHOICES = [
        (0, 'Asimptomatik'),
        (1, 'Atipik angina'),
        (2, 'Angina bo\'lmagan og\'riq'),
        (3, 'Tipik angina'),
    ]

    # Basic Info
    bemor = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='protokollar',
        verbose_name='Bemor'
    )
    protocol_type = models.CharField(
        max_length=20,
        choices=PROTOCOL_TYPE_CHOICES,
        verbose_name='Protokol turi'
    )
    yaratilgan_sana = models.DateTimeField(auto_now_add=True, verbose_name='Yaratilgan sana')
    shifokor = models.CharField(max_length=200, blank=True, verbose_name='Shifokor')
    izoh = models.TextField(blank=True, verbose_name='Izoh')
    transcript = models.TextField(blank=True, verbose_name='Ovozli yozuv matni')

    # Medical Info (shared)
    qon_guruhi = models.CharField(
        max_length=10,
        choices=QON_GURUHI_CHOICES,
        blank=True,
        null=True,
        verbose_name='Qon guruhi'
    )
    allergiyalar = models.TextField(blank=True, null=True, verbose_name='Allergiyalar')
    qand_kasalligi = models.BooleanField(default=False, verbose_name='Qand kasalligi mavjud')
    gipertoniya = models.BooleanField(default=False, verbose_name='Gipertoniya mavjud')
    yurak_kasalligi = models.BooleanField(default=False, verbose_name='Yurak kasalligi mavjud')

    # ============ DIABETES FIELDS ============
    # From diabetes.csv: Pregnancies, Glucose, BloodPressure, SkinThickness, Insulin, BMI, DiabetesPedigreeFunction, Age
    pregnancies = models.IntegerField(null=True, blank=True, verbose_name='Homiladorlik soni',
                                       help_text='0-17 orasida')
    glucose = models.FloatField(null=True, blank=True, verbose_name='Glyukoza darajasi (mg/dL)',
                                help_text='0-200 orasida')
    blood_pressure = models.IntegerField(null=True, blank=True, verbose_name='Qon bosimi (mm Hg)',
                                         help_text='0-130 orasida')
    skin_thickness = models.IntegerField(null=True, blank=True, verbose_name='Teri qalinligi (mm)',
                                         help_text='0-99 orasida')
    insulin = models.FloatField(null=True, blank=True, verbose_name='Insulin darajasi (mu U/ml)',
                                help_text='0-850 orasida')
    bmi = models.FloatField(null=True, blank=True, verbose_name='BMI (Tana massasi indeksi)',
                            help_text='0-70 orasida')
    diabetes_pedigree = models.FloatField(null=True, blank=True, verbose_name='Irsiy omil koeffitsienti',
                                          help_text='0.0-2.5 orasida')

    # ============ HEART DISEASE FIELDS ============
    # From heart.csv: age, sex, cp, trestbps, chol, fbs, restecg, thalach, exang, oldpeak, slope, ca, thal
    sex = models.IntegerField(null=True, blank=True, choices=JINS_CHOICES, verbose_name='Jins (model uchun)')
    chest_pain_type = models.IntegerField(null=True, blank=True, choices=CHEST_PAIN_CHOICES,
                                          verbose_name='Ko\'krak og\'rig\'i turi')
    resting_bp = models.IntegerField(null=True, blank=True, verbose_name='Dam olishdagi qon bosimi (mm Hg)',
                                     help_text='90-200 orasida')
    cholesterol = models.FloatField(null=True, blank=True, verbose_name='Xolesterin (mg/dl)',
                                    help_text='100-600 orasida')
    fasting_blood_sugar = models.BooleanField(null=True, blank=True,
                                               verbose_name='Och qorindagi qand > 120 mg/dl')
    rest_ecg = models.IntegerField(null=True, blank=True, verbose_name='Dam olishdagi EKG natijasi',
                                   help_text='0=Normal, 1=ST-T anormalligi, 2=Chap qorincha gipertrofiyasi')
    max_heart_rate = models.IntegerField(null=True, blank=True, verbose_name='Maksimal yurak urishi',
                                         help_text='70-210 orasida')
    exercise_angina = models.BooleanField(null=True, blank=True,
                                          verbose_name='Jismoniy mashqda angina')
    oldpeak = models.FloatField(null=True, blank=True, verbose_name='ST depressiyasi',
                                help_text='0.0-6.5 orasida')
    slope = models.IntegerField(null=True, blank=True, verbose_name='ST segment qiyaligi',
                                help_text='0=Pastga, 1=Tekis, 2=Yuqoriga')
    num_vessels = models.IntegerField(null=True, blank=True, verbose_name='Asosiy tomirlar soni (0-3)',
                                      help_text='Fluoroskopiyada ranglangan')
    thal = models.IntegerField(null=True, blank=True, verbose_name='Talassemiya',
                               help_text='1=Normal, 2=Tuzatilgan nuqson, 3=Qaytmas nuqson')

    # AI Prediction Results
    ai_prediction = models.FloatField(null=True, blank=True, verbose_name='AI bashorat natijasi (%)')
    risk_level = models.CharField(max_length=20, blank=True, verbose_name='Xavf darajasi')

    class Meta:
        verbose_name = 'Protokol'
        verbose_name_plural = 'Protokollar'
        ordering = ['-yaratilgan_sana']

    def __str__(self):
        return f"{self.bemor.ism} - {self.get_protocol_type_display()} - {self.yaratilgan_sana.strftime('%d.%m.%Y')}"
