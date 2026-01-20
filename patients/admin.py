from django.contrib import admin
from .models import Patient, Appointment, HealthScreening


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ['ism', 'yosh', 'jins', 'telefon', 'umumiy_uchrashuvlar', 'kelmaganlar_soni', 'yaratilgan_sana']
    list_filter = ['jins', 'qand_kasalligi', 'gipertoniya', 'yurak_kasalligi']
    search_fields = ['ism', 'telefon']
    date_hierarchy = 'yaratilgan_sana'


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['bemor', 'uchrashuv_sanasi', 'shifokor', 'bolim', 'holat', 'kelmay_qolish_riski']
    list_filter = ['holat', 'bolim', 'sms_yuborildi']
    search_fields = ['bemor__ism', 'shifokor']
    date_hierarchy = 'uchrashuv_sanasi'
    raw_id_fields = ['bemor']


@admin.register(HealthScreening)
class HealthScreeningAdmin(admin.ModelAdmin):
    list_display = ['bemor', 'tekshirilgan_sana', 'qand_ehtimoli', 'yurak_ehtimoli']
    list_filter = ['tekshirilgan_sana']
    search_fields = ['bemor__ism']
    date_hierarchy = 'tekshirilgan_sana'
    raw_id_fields = ['bemor', 'uchrashuv']
