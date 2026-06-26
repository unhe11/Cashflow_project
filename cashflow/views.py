from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from django.http import JsonResponse
from .models import (
    Status, TransactionType, Category, SubCategory, CashFlowRecord
)
from .forms import (
    CashFlowRecordForm, StatusForm, TransactionTypeForm,
    CategoryForm, SubCategoryForm
)
from datetime import datetime


def index(request):
    """Главная страница - список записей с фильтрацией"""

    # Получаем все записи
    records = CashFlowRecord.objects.select_related(
        'status', 'transaction_type', 'category', 'subcategory'
    ).all()

    # Фильтрация по дате
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')

    if date_from:
        try:
            date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
            records = records.filter(date__gte=date_from)
        except ValueError:
            pass

    if date_to:
        try:
            date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
            records = records.filter(date__lte=date_to)
        except ValueError:
            pass

    # По статусу
    status_id = request.GET.get('status')
    if status_id:
        records = records.filter(status_id=status_id)

    # По типу
    type_id = request.GET.get('type')
    if type_id:
        records = records.filter(transaction_type_id=type_id)

    # По категории
    category_id = request.GET.get('category')
    if category_id:
        records = records.filter(category_id=category_id)

    # По подкатегории
    subcategory_id = request.GET.get('subcategory')
    if subcategory_id:
        records = records.filter(subcategory_id=subcategory_id)

    # Сортировка (по умолчанию - новые сверху)
    sort_by = request.GET.get('sort', '-date')
    records = records.order_by(sort_by)

    # Пагинация
    paginator = Paginator(records, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Для фильтров в шаблоне
    contexts = {
        'statuses': Status.objects.all(),
        'types': TransactionType.objects.all(),
        'categories': Category.objects.all(),
        'subcategories': SubCategory.objects.all(),
    }

    return render(request, 'cashflow/index.html', {
        'page_obj': page_obj,
        'filter_data': request.GET,
        **contexts
    })


def record_create(request):
    """Создание новой записи"""
    if request.method == 'POST':
        form = CashFlowRecordForm(request.POST)
        if form.is_valid():
            record = form.save()
            messages.success(request, f'Запись создана успешно!')
            return redirect('cashflow:index')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме')
    else:
        form = CashFlowRecordForm()

    return render(request, 'cashflow/record_form.html', {
        'form': form,
        'title': 'Создание записи',
        'button_text': 'Создать'
    })


def record_edit(request, pk):
    """Редактирование записи"""
    record = get_object_or_404(CashFlowRecord, pk=pk)

    if request.method == 'POST':
        form = CashFlowRecordForm(request.POST, instance=record)
        if form.is_valid():
            form.save()
            messages.success(request, f'Запись успешно обновлена!')
            return redirect('cashflow:index')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме')
    else:
        form = CashFlowRecordForm(instance=record)

    return render(request, 'cashflow/record_form.html', {
        'form': form,
        'title': 'Редактирование записи',
        'button_text': 'Сохранить',
        'record': record
    })


def record_delete(request, pk):
    """Удаление записи"""
    record = get_object_or_404(CashFlowRecord, pk=pk)

    if request.method == 'POST':
        record.delete()
        messages.success(request, f'Запись успешно удалена!')
        return redirect('cashflow:index')

    return render(request, 'cashflow/record_confirm_delete.html', {
        'record': record
    })


def get_categories_by_type(request):
    """AJAX: Получить категории по выбранному типу"""
    type_id = request.GET.get('type_id')
    if type_id:
        categories = Category.objects.filter(
            transaction_type_id=type_id
        ).values('id', 'name')
        return JsonResponse(list(categories), safe=False)
    return JsonResponse([], safe=False)


def get_subcategories_by_category(request):
    """AJAX: Получить подкатегории по выбранной категории"""
    category_id = request.GET.get('category_id')
    if category_id:
        subcategories = SubCategory.objects.filter(
            category_id=category_id
        ).values('id', 'name')
        return JsonResponse(list(subcategories), safe=False)
    return JsonResponse([], safe=False)


# Управление справочниками
def directory_management(request):
    """Страница управления справочниками"""
    return render(request, 'cashflow/directory_management.html', {
        'statuses': Status.objects.all(),
        'types': TransactionType.objects.all(),
        'categories': Category.objects.select_related('transaction_type').all(),
        'subcategories': SubCategory.objects.select_related('category').all(),
    })
# Статусы
def status_create(request):
    if request.method == 'POST':
        form = StatusForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Статус создан')
            return redirect('cashflow:directory_management')
    else:
        form = StatusForm()
    return render(request, 'cashflow/directory_form.html', {
        'form': form, 'title': 'Добавить статус'
    })

def status_edit(request, pk):
    status = get_object_or_404(Status, pk=pk)
    if request.method == 'POST':
        form = StatusForm(request.POST, instance=status)
        if form.is_valid():
            form.save()
            messages.success(request, 'Статус обновлен')
            return redirect('cashflow:directory_management')
    else:
        form = StatusForm(instance=status)
    return render(request, 'cashflow/directory_form.html', {
        'form': form, 'title': 'Редактировать статус'
    })

def status_delete(request, pk):
    status = get_object_or_404(Status, pk=pk)
    if request.method == 'POST':
        try:
            status.delete()
            messages.success(request, 'Статус удален')
        except:
            messages.error(request, 'Невозможно удалить статус, он используется в записях')
        return redirect('cashflow:directory_management')
    return render(request, 'cashflow/directory_confirm_delete.html', {
        'object': status, 'type': 'статус'
    })

# Типы транзакций
def type_create(request):
    if request.method == 'POST':
        form = TransactionTypeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Тип создан')
            return redirect('cashflow:directory_management')
    else:
        form = TransactionTypeForm()
    return render(request, 'cashflow/directory_form.html', {
        'form': form, 'title': 'Добавить тип'
    })

def type_edit(request, pk):
    type_obj = get_object_or_404(TransactionType, pk=pk)
    if request.method == 'POST':
        form = TransactionTypeForm(request.POST, instance=type_obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Тип обновлен')
            return redirect('cashflow:directory_management')
    else:
        form = TransactionTypeForm(instance=type_obj)
    return render(request, 'cashflow/directory_form.html', {
        'form': form, 'title': 'Редактировать тип'
    })

def type_delete(request, pk):
    type_obj = get_object_or_404(TransactionType, pk=pk)
    if request.method == 'POST':
        try:
            type_obj.delete()
            messages.success(request, 'Тип удален')
        except:
            messages.error(request, 'Невозможно удалить тип, он используется в записях')
        return redirect('cashflow:directory_management')
    return render(request, 'cashflow/directory_confirm_delete.html', {
        'object': type_obj, 'type': 'тип'
    })

# Категории
def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Категория создана')
            return redirect('cashflow:directory_management')
    else:
        form = CategoryForm()
    return render(request, 'cashflow/directory_form.html', {
        'form': form, 'title': 'Добавить категорию'
    })

def category_edit(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Категория обновлена')
            return redirect('cashflow:directory_management')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'cashflow/directory_form.html', {
        'form': form, 'title': 'Редактировать категорию'
    })

def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        try:
            category.delete()
            messages.success(request, 'Категория удалена')
        except:
            messages.error(request, 'Невозможно удалить категорию, она используется')
        return redirect('cashflow:directory_management')
    return render(request, 'cashflow/directory_confirm_delete.html', {
        'object': category, 'type': 'категорию'
    })

# Подкатегории
def subcategory_create(request):
    if request.method == 'POST':
        form = SubCategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Подкатегория создана')
            return redirect('cashflow:directory_management')
    else:
        form = SubCategoryForm()
    return render(request, 'cashflow/directory_form.html', {
        'form': form, 'title': 'Добавить подкатегорию'
    })

def subcategory_edit(request, pk):
    subcategory = get_object_or_404(SubCategory, pk=pk)
    if request.method == 'POST':
        form = SubCategoryForm(request.POST, instance=subcategory)
        if form.is_valid():
            form.save()
            messages.success(request, 'Подкатегория обновлена')
            return redirect('cashflow:directory_management')
    else:
        form = SubCategoryForm(instance=subcategory)
    return render(request, 'cashflow/directory_form.html', {
        'form': form, 'title': 'Редактировать подкатегорию'
    })

def subcategory_delete(request, pk):
    subcategory = get_object_or_404(SubCategory, pk=pk)
    if request.method == 'POST':
        try:
            subcategory.delete()
            messages.success(request, 'Подкатегория удалена')
        except:
            messages.error(request, 'Невозможно удалить подкатегорию, она используется')
        return redirect('cashflow:directory_management')
    return render(request, 'cashflow/directory_confirm_delete.html', {
        'object': subcategory, 'type': 'подкатегорию'
    })