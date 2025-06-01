from django.db import models

class Course(models.Model):
    title = models.CharField(max_length=200, verbose_name="Название курса")
    description = models.TextField(blank=True, verbose_name="Описание курса")
    price = models.DecimalField(max_digits=10, decimal_places=2, 
                                default=129.90, verbose_name="Стоимость (RUB)")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")


    class Meta:
        verbose_name = "Курс"
        verbose_name_plural = "Курсы"


    def __str__(self):
        return self.title


class Block(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, 
                               related_name="blocks", verbose_name="Курс")
    title = models.CharField(max_length=200, verbose_name="Название блока")
    content = models.TextField(verbose_name="Содержимое блока")
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок")


    class Meta:
        verbose_name = "Блок"
        verbose_name_plural = "Блоки"
        ordering = ['order']


    def __str__(self):
        return f"{self.course.title} - {self.title}"


class SubBlock(models.Model):
    block = models.ForeignKey(Block, on_delete=models.CASCADE, related_name="subblocks", verbose_name="Блок")
    title = models.CharField(max_length=200, verbose_name="Название подблока")
    content = models.TextField(verbose_name="Содержимое подблока")
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок")


    class Meta:
        verbose_name = "Подблок"
        verbose_name_plural = "Подблоки"
        ordering = ['order']


    def __str__(self):
        return f"{self.block.title} - {self.title}"
    