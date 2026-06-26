from django.urls import path
from . import views

app_name = 'cashflow'

urlpatterns = [
    # Главная страница
    path('', views.index, name='index'),

    # Записи ДДС
    path('record/create/', views.record_create, name='record_create'),
    path('record/<int:pk>/edit/', views.record_edit, name='record_edit'),
    path('record/<int:pk>/delete/', views.record_delete, name='record_delete'),

    # AJAX для динамической фильтрации
    path('ajax/categories-by-type/', views.get_categories_by_type, name='get_categories_by_type'),
    path('ajax/subcategories-by-category/', views.get_subcategories_by_category, name='get_subcategories_by_category'),

    # Управление справочниками
    path('directory/', views.directory_management, name='directory_management'),

    # Статусы
    path('status/create/', views.status_create, name='status_create'),
    path('status/<int:pk>/edit/', views.status_edit, name='status_edit'),
    path('status/<int:pk>/delete/', views.status_delete, name='status_delete'),

    # Типы
    path('type/create/', views.type_create, name='type_create'),
    path('type/<int:pk>/edit/', views.type_edit, name='type_edit'),
    path('type/<int:pk>/delete/', views.type_delete, name='type_delete'),

    # Категории
    path('category/create/', views.category_create, name='category_create'),
    path('category/<int:pk>/edit/', views.category_edit, name='category_edit'),
    path('category/<int:pk>/delete/', views.category_delete, name='category_delete'),

    # Подкатегории
    path('subcategory/create/', views.subcategory_create, name='subcategory_create'),
    path('subcategory/<int:pk>/edit/', views.subcategory_edit, name='subcategory_edit'),
    path('subcategory/<int:pk>/delete/', views.subcategory_delete, name='subcategory_delete'),
]