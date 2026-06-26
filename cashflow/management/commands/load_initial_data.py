from django.core.management.base import BaseCommand
from django.db import transaction
from cashflow.models import Status, TransactionType, Category, SubCategory


class Command(BaseCommand):
    help = 'Загрузка начальных данных для справочников'

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write('🚀 Начинаем загрузку начальных данных...')

        # Создание статусов
        statuses = ['Бизнес', 'Личное', 'Налог']
        for status_name in statuses:
            status, created = Status.objects.get_or_create(name=status_name)
            if created:
                self.stdout.write(f'  ✅ Создан статус: {status_name}')
            else:
                self.stdout.write(f'  ⏭️ Статус уже существует: {status_name}')
        self.stdout.write('✅ Статусы загружены\n')

        # Создание типов транзакций
        types = ['Пополнение', 'Списание']
        for type_name in types:
            trans_type, created = TransactionType.objects.get_or_create(name=type_name)
            if created:
                self.stdout.write(f'  ✅ Создан тип: {type_name}')
            else:
                self.stdout.write(f'  ⏭️ Тип уже существует: {type_name}')
        self.stdout.write('✅ Типы транзакций загружены\n')

        # Создание категорий и подкатегорий для "Списание"
        try:
            expense_type = TransactionType.objects.get(name='Списание')

            expense_categories = {
                'Инфраструктура': ['VPS', 'Proxy', 'Хостинг', 'Домены'],
                'Маркетинг': ['Farpost', 'Avito', 'Яндекс.Директ', 'ВКонтакте'],
                'Офис': ['Аренда', 'Канцтовары', 'Коммунальные услуги', 'Интернет'],
                'Транспорт': ['Топливо', 'Ремонт', 'Обслуживание', 'Страховка'],
                'Разработка': ['Лицензии ПО', 'Облачные сервисы', 'API'],
                'Обучение': ['Курсы', 'Тренинги', 'Книги'],
            }

            for cat_name, subcats in expense_categories.items():
                category, created = Category.objects.get_or_create(
                    name=cat_name,
                    transaction_type=expense_type
                )
                if created:
                    self.stdout.write(f'  ✅ Создана категория: {cat_name} (Списание)')
                else:
                    self.stdout.write(f'  ⏭️ Категория уже существует: {cat_name}')

                for subcat_name in subcats:
                    subcategory, created = SubCategory.objects.get_or_create(
                        name=subcat_name,
                        category=category
                    )
                    if created:
                        self.stdout.write(f'    ✅ Создана подкатегория: {subcat_name}')
            self.stdout.write('✅ Категории и подкатегории для "Списание" загружены\n')

        except TransactionType.DoesNotExist:
            self.stdout.write(self.style.ERROR('❌ Тип "Списание" не найден!'))
            return

        # Создание категорий и подкатегорий для "Пополнение"
        try:
            income_type = TransactionType.objects.get(name='Пополнение')

            income_categories = {
                'Зарплата': ['Основная зарплата', 'Премия', 'Бонусы'],
                'Дополнительный доход': ['Фриланс', 'Инвестиции', 'Аренда', 'Проценты'],
                'Бизнес доход': ['Продажи', 'Услуги', 'Консультации'],
                'Возвраты': ['Возврат от поставщиков', 'Переплата'],
            }

            for cat_name, subcats in income_categories.items():
                category, created = Category.objects.get_or_create(
                    name=cat_name,
                    transaction_type=income_type
                )
                if created:
                    self.stdout.write(f'  ✅ Создана категория: {cat_name} (Пополнение)')
                else:
                    self.stdout.write(f'  ⏭️ Категория уже существует: {cat_name}')

                for subcat_name in subcats:
                    subcategory, created = SubCategory.objects.get_or_create(
                        name=subcat_name,
                        category=category
                    )
                    if created:
                        self.stdout.write(f'    ✅ Создана подкатегория: {subcat_name}')
            self.stdout.write('✅ Категории и подкатегории для "Пополнение" загружены\n')

        except TransactionType.DoesNotExist:
            self.stdout.write(self.style.ERROR('❌ Тип "Пополнение" не найден!'))
            return

        # Проверка связей
        self.stdout.write('\n📊 Проверка связей:')
        for category in Category.objects.all():
            sub_count = category.subcategories.count()
            self.stdout.write(f'  📌 {category.name} ({category.transaction_type.name}) - подкатегорий: {sub_count}')

        self.stdout.write(self.style.SUCCESS('\n✅ Загрузка начальных данных завершена успешно!'))