from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone


class Status(models.Model):
    """Модель статуса (Бизнес, Личное, Налог)"""
    name = models.CharField('Название', max_length=100, unique=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)

    class Meta:
        verbose_name = 'Статус'
        verbose_name_plural = 'Статусы'
        ordering = ['name']

    def __str__(self):
        return self.name


class TransactionType(models.Model):
    """Модель типа транзакции (Пополнение, Списание)"""
    name = models.CharField('Название', max_length=100, unique=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)

    class Meta:
        verbose_name = 'Тип транзакции'
        verbose_name_plural = 'Типы транзакций'
        ordering = ['name']

    def __str__(self):
        return self.name


class Category(models.Model):
    """Модель категории (привязана к типу транзакции)"""
    name = models.CharField('Название', max_length=100)
    transaction_type = models.ForeignKey(
        TransactionType,
        on_delete=models.CASCADE,
        verbose_name='Тип транзакции',
        related_name='categories'
    )
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['transaction_type__name', 'name']
        unique_together = ['name', 'transaction_type']

    def __str__(self):
        return f"{self.name} ({self.transaction_type.name})"


class SubCategory(models.Model):
    """Модель подкатегории (привязана к категории)"""
    name = models.CharField('Название', max_length=100)
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        verbose_name='Категория',
        related_name='subcategories'
    )
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)

    class Meta:
        verbose_name = 'Подкатегория'
        verbose_name_plural = 'Подкатегории'
        ordering = ['category__name', 'name']
        unique_together = ['name', 'category']

    def __str__(self):
        return f"{self.name} ({self.category.name})"


class CashFlowRecord(models.Model):
    """Модель записи о движении денежных средств"""
    date = models.DateField('Дата', default=timezone.now)
    status = models.ForeignKey(
        Status,
        on_delete=models.PROTECT,
        verbose_name='Статус',
        related_name='records'
    )
    transaction_type = models.ForeignKey(
        TransactionType,
        on_delete=models.PROTECT,
        verbose_name='Тип',
        related_name='records'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        verbose_name='Категория',
        related_name='records'
    )
    subcategory = models.ForeignKey(
        SubCategory,
        on_delete=models.PROTECT,
        verbose_name='Подкатегория',
        related_name='records'
    )
    amount = models.DecimalField(
        'Сумма (₽)',
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    comment = models.TextField('Комментарий', blank=True, null=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)

    class Meta:
        verbose_name = 'Запись ДДС'
        verbose_name_plural = 'Записи ДДС'
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.date} - {self.status} - {self.amount} ₽"

    def clean(self):
        """Валидация на уровне модели"""
        from django.core.exceptions import ValidationError

        # Проверка: подкатегория должна принадлежать выбранной категории
        if self.category and self.subcategory and self.subcategory.category != self.category:
            raise ValidationError({
                'subcategory': 'Подкатегория не соответствует выбранной категории'
            })

        # Проверка: категория должна принадлежать выбранному типу
        if self.transaction_type and self.category and self.category.transaction_type != self.transaction_type:
            raise ValidationError({
                'category': 'Категория не соответствует выбранному типу транзакции'
            })