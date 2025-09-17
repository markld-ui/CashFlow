from django.core.management.base import BaseCommand
from dds_app_api.models import Status, TransactionType, Category, Subcategory

class Command(BaseCommand):
    help = 'Загрузка начальных данных в систему ДДС'
    
    def handle(self, *args, **options):
        self.stdout.write('Загрузка начальных данных...')
        
        # Создаем статусы
        statuses = [
            {'name': 'Бизнес', 'description': 'Бизнес операции'},
            {'name': 'Личное', 'description': 'Личные операции'},
            {'name': 'Налог', 'description': 'Налоговые операции'},
        ]
        
        for status_data in statuses:
            status, created = Status.objects.get_or_create(
                name=status_data['name'],
                defaults=status_data
            )
            if created:
                self.stdout.write(f'✓ Создан статус: {status.name}')
        
        # Создаем типы операций
        transaction_types = [
            {'name': 'Пополнение', 'description': 'Поступление средств'},
            {'name': 'Списание', 'description': 'Расход средств'},
        ]
        
        for type_data in transaction_types:
            transaction_type, created = TransactionType.objects.get_or_create(
                name=type_data['name'],
                defaults=type_data
            )
            if created:
                self.stdout.write(f'✓ Создан тип операции: {transaction_type.name}')
        
        # Получаем типы операций
        income_type = TransactionType.objects.get(name='Пополнение')
        expense_type = TransactionType.objects.get(name='Списание')
        
        # Создаем категории и подкатегории для пополнений
        income_categories = [
            {
                'name': 'Продажи',
                'description': 'Доходы от продаж',
                'subcategories': ['Онлайн продажи', 'Оффлайн продажи', 'Оптовые продажи']
            },
            {
                'name': 'Инвестиции',
                'description': 'Доходы от инвестиций',
                'subcategories': ['Дивиденды', 'Проценты по вкладам', 'Рост стоимости активов']
            },
            {
                'name': 'Фриланс',
                'description': 'Доходы от фриланс работы',
                'subcategories': ['Разработка', 'Дизайн', 'Консультации']
            },
        ]
        
        # Создаем категории и подкатегории для списаний
        expense_categories = [
            {
                'name': 'Маркетинг',
                'description': 'Расходы на маркетинг',
                'subcategories': ['Контекстная реклама', 'SEO', 'SMM', 'Email рассылки']
            },
            {
                'name': 'Инфраструктура',
                'description': 'Расходы на инфраструктуру',
                'subcategories': ['VPS', 'Proxy', 'Домены', 'Хостинг', 'Софт']
            },
            {
                'name': 'Зарплаты',
                'description': 'Расходы на зарплаты',
                'subcategories': ['Штатные сотрудники', 'Фрилансеры', 'Премии']
            },
            {
                'name': 'Офис',
                'description': 'Офисные расходы',
                'subcategories': ['Аренда', 'Коммунальные услуги', 'Канцелярия']
            },
            {
                'name': 'Налоги',
                'description': 'Налоговые платежи',
                'subcategories': ['НДС', 'Налог на прибыль', 'Страховые взносы']
            },
        ]
        
        # Создаем категории доходов
        for category_data in income_categories:
            category, created = Category.objects.get_or_create(
                name=category_data['name'],
                transaction_type=income_type,
                defaults={'description': category_data['description']}
            )
            if created:
                self.stdout.write(f'✓ Создана категория: {category.name}')
            
            # Создаем подкатегории
            for subcat_name in category_data['subcategories']:
                subcategory, created = Subcategory.objects.get_or_create(
                    name=subcat_name,
                    category=category,
                    defaults={'description': f'Подкатегория {subcat_name.lower()}'}
                )
                if created:
                    self.stdout.write(f'  → Создана подкатегория: {subcategory.name}')
        
        # Создаем категории расходов
        for category_data in expense_categories:
            category, created = Category.objects.get_or_create(
                name=category_data['name'],
                transaction_type=expense_type,
                defaults={'description': category_data['description']}
            )
            if created:
                self.stdout.write(f'✓ Создана категория: {category.name}')
            
            # Создаем подкатегории
            for subcat_name in category_data['subcategories']:
                subcategory, created = Subcategory.objects.get_or_create(
                    name=subcat_name,
                    category=category,
                    defaults={'description': f'Подкатегория {subcat_name.lower()}'}
                )
                if created:
                    self.stdout.write(f'  → Создана подкатегория: {subcategory.name}')
        
        # Создаем тестовые транзакции (опционально)
        try:
            from django.utils import timezone
            from decimal import Decimal
            
            # Получаем объекты
            business_status = Status.objects.get(name='Бизнес')
            personal_status = Status.objects.get(name='Личное')
            
            # Примеры транзакций
            transactions_data = [
                {
                    'transaction_date': '2024-01-15',
                    'status': business_status,
                    'transaction_type': income_type,
                    'category': Category.objects.get(name='Продажи'),
                    'subcategory': Subcategory.objects.get(name='Онлайн продажи'),
                    'amount': Decimal('50000.00'),
                    'comment': 'Продажа товаров через интернет-магазин'
                },
                {
                    'transaction_date': '2024-01-16',
                    'status': business_status,
                    'transaction_type': expense_type,
                    'category': Category.objects.get(name='Маркетинг'),
                    'subcategory': Subcategory.objects.get(name='Контекстная реклама'),
                    'amount': Decimal('15000.00'),
                    'comment': 'Рекламная кампания в Google Ads'
                },
                {
                    'transaction_date': '2024-01-17',
                    'status': business_status,
                    'transaction_type': expense_type,
                    'category': Category.objects.get(name='Инфраструктура'),
                    'subcategory': Subcategory.objects.get(name='VPS'),
                    'amount': Decimal('5000.00'),
                    'comment': 'Оплата виртуального сервера'
                },
            ]
            
            from dds_app_api.models import Transaction
            
            for transaction_data in transactions_data:
                transaction, created = Transaction.objects.get_or_create(
                    transaction_date=transaction_data['transaction_date'],
                    amount=transaction_data['amount'],
                    defaults=transaction_data
                )
                if created:
                    self.stdout.write(f'✓ Создана транзакция: {transaction.amount}р. от {transaction.transaction_date}')
                    
        except Exception as e:
            self.stdout.write(f'ℹ Тестовые транзакции не созданы: {e}')
        
        self.stdout.write(self.style.SUCCESS('✅ Начальные данные успешно загружены!'))