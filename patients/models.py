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

class Staff(models.Model):
    """Xodim modeli - Staff model"""

    LAVOZIM_CHOICES = [
        ('doctor', 'Shifokor'),
        ('nurse', 'Hamshira'),
        ('admin', 'Administrator'),
    ]

    ism = models.CharField(max_length=200, verbose_name='Ism')
    lavozim = models.CharField(
        max_length=20,
        choices=LAVOZIM_CHOICES,
        verbose_name='Lavozim'
    )
    bolim = models.CharField(
        max_length=50,
        choices=Appointment.BOLIM_CHOICES,
        verbose_name='Bo‘lim'
    )
    telefon = models.CharField(max_length=20, verbose_name='Telefon')
    email = models.EmailField(blank=True, null=True, verbose_name='Email')
    faol = models.BooleanField(default=True, verbose_name='Faol')
    ishga_olingan_sana = models.DateField(default=timezone.now, verbose_name='Ishga olingan sana')

    class Meta:
        verbose_name = 'Xodim'
        verbose_name_plural = 'Xodimlar'
        ordering = ['ism']

    def __str__(self):
        return f"{self.ism} ({self.get_lavozim_display()})"
