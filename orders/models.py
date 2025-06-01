from django.db import models
from django.conf import settings
from main.models import Course
from decimal import Decimal


class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'В ожидании'),
        ('processing', 'В обработке'),
        ('completed', 'Завершен'),
        ('cancelled', 'Отменен'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders', verbose_name="Пользователь")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='orders', verbose_name="Курс")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Общая сумма")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Статус")
    yookassa_payment_id = models.CharField(max_length=255, blank=True, null=True, verbose_name="ID платежа ЮKassa")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")


    def __str__(self):
        return f"Заказ {self.id} - {self.course.title} ({self.user.email})"


    def get_discounted_total(self):
        return round(self.total_price, 2)
    