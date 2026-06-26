from django import forms
from django.core.exceptions import ValidationError
from .models import (
    Status, TransactionType, Category, SubCategory, CashFlowRecord
)


class CashFlowRecordForm(forms.ModelForm):
    """Форма для создания/редактирования записи"""

    class Meta:
        model = CashFlowRecord
        fields = ['date', 'status', 'transaction_type', 'category',
                  'subcategory', 'amount', 'comment']
        widgets = {
            'date': forms.DateInput(
                attrs={'type': 'date', 'class': 'form-control'}
            ),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'transaction_type': forms.Select(
                attrs={'class': 'form-control', 'id': 'id_transaction_type'}
            ),
            'category': forms.Select(
                attrs={'class': 'form-control', 'id': 'id_category'}
            ),
            'subcategory': forms.Select(
                attrs={'class': 'form-control', 'id': 'id_subcategory'}
            ),
            'amount': forms.NumberInput(
                attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01'}
            ),
            'comment': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 3,
                       'placeholder': 'Необязательный комментарий'}
            ),
        }
        labels = {
            'date': 'Дата',
            'status': 'Статус',
            'transaction_type': 'Тип операции',
            'category': 'Категория',
            'subcategory': 'Подкатегория',
            'amount': 'Сумма (₽)',
            'comment': 'Комментарий',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Если есть выбранный тип, фильтруем категории
        if self.instance and self.instance.pk:
            # При редактировании
            if self.instance.transaction_type:
                self.fields['category'].queryset = Category.objects.filter(
                    transaction_type=self.instance.transaction_type
                )
            if self.instance.category:
                self.fields['subcategory'].queryset = SubCategory.objects.filter(
                    category=self.instance.category
                )
        elif 'transaction_type' in self.data:
            # При создании с POST-запросом
            try:
                type_id = int(self.data.get('transaction_type'))
                self.fields['category'].queryset = Category.objects.filter(
                    transaction_type_id=type_id
                )
            except (ValueError, TypeError):
                pass

            if 'category' in self.data:
                try:
                    cat_id = int(self.data.get('category'))
                    self.fields['subcategory'].queryset = SubCategory.objects.filter(
                        category_id=cat_id
                    )
                except (ValueError, TypeError):
                    pass
        else:
            # При создании (GET-запрос) - показываем все
            self.fields['category'].queryset = Category.objects.none()
            self.fields['subcategory'].queryset = SubCategory.objects.none()

    def clean(self):
        cleaned_data = super().clean()
        transaction_type = cleaned_data.get('transaction_type')
        category = cleaned_data.get('category')
        subcategory = cleaned_data.get('subcategory')

        # Валидация: категория должна принадлежать выбранному типу
        if transaction_type and category:
            if category.transaction_type != transaction_type:
                raise ValidationError({
                    'category': 'Категория не соответствует выбранному типу операции'
                })

        # Валидация: подкатегория должна принадлежать выбранной категории
        if category and subcategory:
            if subcategory.category != category:
                raise ValidationError({
                    'subcategory': 'Подкатегория не соответствует выбранной категории'
                })

        # Валидация: сумма должна быть положительной
        amount = cleaned_data.get('amount')
        if amount and amount <= 0:
            raise ValidationError({
                'amount': 'Сумма должна быть больше нуля'
            })

        return cleaned_data


class StatusForm(forms.ModelForm):
    """Форма для управления статусами"""

    class Meta:
        model = Status
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'})
        }
        labels = {'name': 'Название статуса'}


class TransactionTypeForm(forms.ModelForm):
    """Форма для управления типами транзакций"""

    class Meta:
        model = TransactionType
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'})
        }
        labels = {'name': 'Название типа'}


class CategoryForm(forms.ModelForm):
    """Форма для управления категориями"""

    class Meta:
        model = Category
        fields = ['name', 'transaction_type']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'transaction_type': forms.Select(attrs={'class': 'form-control'})
        }
        labels = {
            'name': 'Название категории',
            'transaction_type': 'Тип операции'
        }


class SubCategoryForm(forms.ModelForm):
    """Форма для управления подкатегориями"""

    class Meta:
        model = SubCategory
        fields = ['name', 'category']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'})
        }
        labels = {
            'name': 'Название подкатегории',
            'category': 'Категория'
        }