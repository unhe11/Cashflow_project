from django.contrib import admin
from .models import (
    Status, TransactionType, Category, SubCategory, CashFlowRecord
)


@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'created_at']
    search_fields = ['name']


@admin.register(TransactionType)
class TransactionTypeAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'created_at']
    search_fields = ['name']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'transaction_type', 'created_at']
    list_filter = ['transaction_type']
    search_fields = ['name']


@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'category', 'created_at']
    list_filter = ['category']
    search_fields = ['name']


@admin.register(CashFlowRecord)
class CashFlowRecordAdmin(admin.ModelAdmin):
    list_display = ['id', 'date', 'status', 'transaction_type', 'category',
                    'subcategory', 'amount', 'comment_short']
    list_filter = ['status', 'transaction_type', 'category', 'subcategory', 'date']
    search_fields = ['comment']
    date_hierarchy = 'date'
    readonly_fields = ['created_at', 'updated_at']

    def comment_short(self, obj):
        return obj.comment[:50] + '...' if obj.comment and len(obj.comment) > 50 else obj.comment

    comment_short.short_description = 'Комментарий (кратко)'