from django.core.management.base import BaseCommand
from dds_app_api.models import Status, TransactionType, Category, Subcategory, Transaction
from django.utils import timezone
from decimal import Decimal
import random
from datetime import datetime, timedelta

class Command(BaseCommand):
    help = 'Загрузка начальных данных в систему ДДС'
    
    def handle(self, *args, **options):
        self.stdout.write('🔄 Загрузка начальных данных...')
        
        # Очищаем существующие данные (опционально)
        self.clean_database()
        
        # Создаем статусы
        self.create_statuses()
        
        # Создаем типы операций
        self.create_transaction_types()
        
        # Создаем категории и подкатегории
        self.create_categories_and_subcategories()
        
        # Создаем тестовые транзакции
        self.create_sample_transactions()
        
        self.stdout.write(self.style.SUCCESS('✅ Начальные данные успешно загружены!'))
    
    def clean_database(self):
        """Очистка базы данных от старых данных"""
        Transaction.objects.all().delete()
        Subcategory.objects.all().delete()
        Category.objects.all().delete()
        TransactionType.objects.all().delete()
        Status.objects.all().delete()
        self.stdout.write('🗑️  База данных очищена')
    
    def create_statuses(self):
        """Создание статусов"""
        statuses = [
            {'name': 'Бизнес', 'description': 'Бизнес операции'},
            {'name': 'Личное', 'description': 'Личные операции'},
            {'name': 'Налог', 'description': 'Налоговые операции'},
            {'name': 'Инвестиции', 'description': 'Инвестиционные операции'},
            {'name': 'Прочее', 'description': 'Прочие операции'},
        ]
        
        for status_data in statuses:
            status, created = Status.objects.get_or_create(
                name=status_data['name'],
                defaults=status_data
            )
            if created:
                self.stdout.write(f'✓ Создан статус: {status.name}')
    
    def create_transaction_types(self):
        """Создание типов операций"""
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
    
    def create_categories_and_subcategories(self):
        """Создание категорий и подкатегорий"""
        income_type = TransactionType.objects.get(name='Пополнение')
        expense_type = TransactionType.objects.get(name='Списание')
        
        # Категории и подкатегории для доходов
        income_categories = [
            {
                'name': 'Продажи',
                'description': 'Доходы от продаж товаров и услуг',
                'subcategories': [
                    {'name': 'Онлайн продажи', 'description': 'Продажи через интернет-магазин'},
                    {'name': 'Оффлайн продажи', 'description': 'Продажи в розничных точках'},
                    {'name': 'Оптовые продажи', 'description': 'Оптовые поставки'},
                    {'name': 'Услуги', 'description': 'Предоставление услуг'},
                ]
            },
            {
                'name': 'Инвестиции',
                'description': 'Доходы от инвестиционной деятельности',
                'subcategories': [
                    {'name': 'Дивиденды', 'description': 'Дивиденды по акциям'},
                    {'name': 'Проценты по вкладам', 'description': 'Проценты по банковским вкладам'},
                    {'name': 'Рост стоимости активов', 'description': 'Прибыль от продажи активов'},
                    {'name': 'Купонные выплаты', 'description': 'Выплаты по облигациям'},
                ]
            },
            {
                'name': 'Фриланс',
                'description': 'Доходы от фриланс работы',
                'subcategories': [
                    {'name': 'Разработка', 'description': 'Разработка программного обеспечения'},
                    {'name': 'Дизайн', 'description': 'Дизайн и графика'},
                    {'name': 'Консультации', 'description': 'Консультационные услуги'},
                    {'name': 'Копирайтинг', 'description': 'Написание текстов'},
                ]
            },
            {
                'name': 'Пассивный доход',
                'description': 'Пассивные источники дохода',
                'subcategories': [
                    {'name': 'Аренда недвижимости', 'description': 'Доход от сдачи в аренду'},
                    {'name': 'Роялти', 'description': 'Авторские отчисления'},
                    {'name': 'Партнерские программы', 'description': 'Партнерский маркетинг'},
                ]
            },
        ]
        
        # Категории и подкатегории для расходов
        expense_categories = [
            {
                'name': 'Маркетинг',
                'description': 'Расходы на маркетинг и рекламу',
                'subcategories': [
                    {'name': 'Контекстная реклама', 'description': 'Реклама в Google Ads, Yandex Direct'},
                    {'name': 'SEO', 'description': 'Поисковая оптимизация'},
                    {'name': 'SMM', 'description': 'Социальные медиа'},
                    {'name': 'Email рассылки', 'description': 'Email маркетинг'},
                    {'name': 'Веб-аналитика', 'description': 'Инструменты аналитики'},
                ]
            },
            {
                'name': 'Инфраструктура',
                'description': 'Расходы на IT инфраструктуру',
                'subcategories': [
                    {'name': 'VPS/Хостинг', 'description': 'Виртуальные серверы и хостинг'},
                    {'name': 'Домены', 'description': 'Регистрация доменных имен'},
                    {'name': 'SSL сертификаты', 'description': 'SSL сертификаты'},
                    {'name': 'CDN', 'description': 'Content Delivery Network'},
                    {'name': 'Софт и лицензии', 'description': 'Программное обеспечение'},
                ]
            },
            {
                'name': 'Зарплаты',
                'description': 'Расходы на оплату труда',
                'subcategories': [
                    {'name': 'Штатные сотрудники', 'description': 'Окладная часть'},
                    {'name': 'Фрилансеры', 'description': 'Внештатные сотрудники'},
                    {'name': 'Премии', 'description': 'Премиальные выплаты'},
                    {'name': 'Налоги на ФОТ', 'description': 'Налоги на фонд оплаты труда'},
                ]
            },
            {
                'name': 'Офис',
                'description': 'Офисные расходы',
                'subcategories': [
                    {'name': 'Аренда помещения', 'description': 'Аренда офиса'},
                    {'name': 'Коммунальные услуги', 'description': 'Электричество, вода, интернет'},
                    {'name': 'Канцелярия', 'description': 'Офисные принадлежности'},
                    {'name': 'Мебель и оборудование', 'description': 'Офисная мебель и техника'},
                ]
            },
            {
                'name': 'Налоги',
                'description': 'Налоговые платежи',
                'subcategories': [
                    {'name': 'НДС', 'description': 'Налог на добавленную стоимость'},
                    {'name': 'Налог на прибыль', 'description': 'Налог на прибыль организаций'},
                    {'name': 'Страховые взносы', 'description': 'Взносы в социальные фонды'},
                    {'name': 'Транспортный налог', 'description': 'Налог на транспорт'},
                ]
            },
            {
                'name': 'Командировки',
                'description': 'Расходы на командировки',
                'subcategories': [
                    {'name': 'Проезд', 'description': 'Авиа и ж/д билеты'},
                    {'name': 'Проживание', 'description': 'Гостиницы и отели'},
                    {'name': 'Суточные', 'description': 'Суточные расходы'},
                    {'name': 'Такси и транспорт', 'description': 'Местный транспорт'},
                ]
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
            for subcat_data in category_data['subcategories']:
                subcategory, created = Subcategory.objects.get_or_create(
                    name=subcat_data['name'],
                    category=category,
                    defaults={'description': subcat_data['description']}
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
            for subcat_data in category_data['subcategories']:
                subcategory, created = Subcategory.objects.get_or_create(
                    name=subcat_data['name'],
                    category=category,
                    defaults={'description': subcat_data['description']}
                )
                if created:
                    self.stdout.write(f'  → Создана подкатегория: {subcategory.name}')
    
    def create_sample_transactions(self):
        """Создание тестовых транзакций"""
        self.stdout.write('💰 Создание тестовых транзакций...')
        
        # Получаем все необходимые объекты
        business_status = Status.objects.get(name='Бизнес')
        personal_status = Status.objects.get(name='Личное')
        tax_status = Status.objects.get(name='Налог')
        
        income_type = TransactionType.objects.get(name='Пополнение')
        expense_type = TransactionType.objects.get(name='Списание')
        
        # Получаем случайные подкатегории для каждого типа
        income_subcategories = list(Subcategory.objects.filter(category__transaction_type=income_type))
        expense_subcategories = list(Subcategory.objects.filter(category__transaction_type=expense_type))
        
        # Создаем 40+ транзакций за последние 6 месяцев
        transactions_data = []
        
        # Доходные транзакции (20 штук)
        for i in range(20):
            date = timezone.now() - timedelta(days=random.randint(1, 180))
            subcategory = random.choice(income_subcategories)
            
            transactions_data.append({
                'transaction_date': date.date(),
                'status': business_status,
                'transaction_type': income_type,
                'category': subcategory.category,
                'subcategory': subcategory,
                'amount': Decimal(str(round(random.uniform(1000, 50000), 2))),
                'comment': f'{subcategory.name} - {date.strftime("%B %Y")}'
            })
        
        # Расходные транзакции (20 штук) - суммы положительные!
        for i in range(20):
            date = timezone.now() - timedelta(days=random.randint(1, 180))
            subcategory = random.choice(expense_subcategories)
            
            amount = Decimal(str(round(random.uniform(500, 20000), 2)))
            
            transactions_data.append({
                'transaction_date': date.date(),
                'status': business_status if random.random() > 0.3 else personal_status,
                'transaction_type': expense_type,  # Тип "Списание" определяет что это расход
                'category': subcategory.category,
                'subcategory': subcategory,
                'amount': amount,  # Положительная сумма!
                'comment': f'{subcategory.name} - {date.strftime("%B %Y")}'
            })
        
        # Налоговые платежи (5 штук) - суммы положительные!
        tax_categories = Category.objects.filter(name='Налоги')
        if tax_categories.exists():
            tax_subcategories = Subcategory.objects.filter(category=tax_categories.first())
            for i in range(5):
                date = timezone.now() - timedelta(days=random.randint(30, 180))
                subcategory = random.choice(list(tax_subcategories))
                
                transactions_data.append({
                    'transaction_date': date.date(),
                    'status': tax_status,
                    'transaction_type': expense_type,  # Тип "Списание"
                    'category': subcategory.category,
                    'subcategory': subcategory,
                    'amount': Decimal(str(round(random.uniform(5000, 30000), 2))),  # Положительная сумма!
                    'comment': f'Налоговый платеж - {subcategory.name}'
                })
        
        # Создаем транзакции в базе данных
        created_count = 0
        for transaction_data in transactions_data:
            transaction, created = Transaction.objects.get_or_create(
                transaction_date=transaction_data['transaction_date'],
                amount=transaction_data['amount'],
                subcategory=transaction_data['subcategory'],
                defaults=transaction_data
            )
            if created:
                created_count += 1
        
        self.stdout.write(f'✓ Создано {created_count} тестовых транзакций')
        
        # Добавляем несколько конкретных примеров для демонстрации
        specific_transactions = [
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
                'transaction_type': expense_type,  # Тип "Списание"
                'category': Category.objects.get(name='Маркетинг'),
                'subcategory': Subcategory.objects.get(name='Контекстная реклама'),
                'amount': Decimal('15000.00'),  # Положительная сумма!
                'comment': 'Рекламная кампания в Google Ads'
            },
            {
                'transaction_date': '2024-01-17',
                'status': business_status,
                'transaction_type': expense_type,  # Тип "Списание"
                'category': Category.objects.get(name='Инфраструктура'),
                'subcategory': Subcategory.objects.get(name='VPS/Хостинг'),
                'amount': Decimal('5000.00'),  # Положительная сумма!
                'comment': 'Оплата виртуального сервера'
            },
        ]
        
        for transaction_data in specific_transactions:
            transaction, created = Transaction.objects.get_or_create(
                transaction_date=transaction_data['transaction_date'],
                amount=transaction_data['amount'],
                subcategory=transaction_data['subcategory'],
                defaults=transaction_data
            )
            if created:
                self.stdout.write(f'✓ Добавлена демо-транзакция: {transaction.amount}р. - {transaction.subcategory.name}')