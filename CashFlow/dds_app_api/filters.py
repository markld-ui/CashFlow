import django_filters
from django.db.models import Q
from .models import Transaction, Status, TransactionType, Category, Subcategory
from django_filters import DateFilter, NumberFilter, CharFilter


class TransactionFilter(django_filters.FilterSet):
    """Фильтр для модели Transaction, позволяющий фильтровать по различным полям.

    Атрибуты:
        date_from (DateFilter): Фильтрация транзакций по дате, начиная с указанной.
        date_to (DateFilter): Фильтрация транзакций по дате, до указанной.
        status (NumberFilter): Фильтрация транзакций по ID статуса.
        transaction_type (NumberFilter): Фильтрация транзакций по ID типа транзакции.
        category (NumberFilter): Фильтрация транзакций по ID категории.
        subcategory (NumberFilter): Фильтрация транзакций по ID подкатегории.
        search (CharFilter): Пользовательский фильтр для поиска по комментарию, категории или подкатегории.
        amount_min (NumberFilter): Фильтрация транзакций по минимальной сумме.
        amount_max (NumberFilter): Фильтрация транзакций по максимальной сумме.
    """
    
    date_from = DateFilter(field_name='transaction_date', lookup_expr='gte')
    date_to = DateFilter(field_name='transaction_date', lookup_expr='lte')
    status = NumberFilter(field_name='status__id')
    transaction_type = NumberFilter(field_name='transaction_type__id')
    category = NumberFilter(field_name='category__id')
    subcategory = NumberFilter(field_name='subcategory__id')
    search = CharFilter(method='filter_search')
    amount_min = NumberFilter(field_name='amount', lookup_expr='gte')
    amount_max = NumberFilter(field_name='amount', lookup_expr='lte')


    class Meta:
        """Метаданные для TransactionFilter."""
        model = Transaction
        fields = []


    def filter_search(self, queryset, name, value):
        """Фильтрация транзакций по комментарию, названию категории или подкатегории.

        Аргументы:
            queryset (QuerySet): Исходный набор данных для фильтрации.
            name (str): Имя поля фильтра.
            value (str): Значение для поиска.

        Возвращает:
            QuerySet: Отфильтрованный набор данных, соответствующий критериям поиска.
        """
        return queryset.filter(
            Q(comment__icontains=value) |
            Q(category__name__icontains=value) |
            Q(subcategory__name__icontains=value)
        )


class StatusFilter(django_filters.FilterSet):
    """Фильтр для модели Status, позволяющий фильтровать по имени.

    Атрибуты:
        name (CharFilter): Фильтрация статусов по имени (автоматически включено через Meta).
    """

    class Meta:
        """Метаданные для StatusFilter."""
        model = Status
        fields = ['name']


class TransactionTypeFilter(django_filters.FilterSet):
    """Фильтр для модели TransactionType, позволяющий фильтровать по имени.

    Атрибуты:
        name (CharFilter): Фильтрация типов транзакций по имени (автоматически включено через Meta).
    """

    class Meta:
        """Метаданные для TransactionTypeFilter."""
        model = TransactionType
        fields = ['name']


class CategoryFilter(django_filters.FilterSet):
    """Фильтр для модели Category, позволяющий фильтровать по имени и типу транзакции.

    Атрибуты:
        transaction_type (NumberFilter): Фильтрация категорий по ID типа транзакции.
        name (CharFilter): Фильтрация категорий по имени (автоматически включено через Meta).
    """

    transaction_type = NumberFilter(field_name='transaction_type__id')


    class Meta:
        """Метаданные для CategoryFilter."""
        model = Category
        fields = ['name', 'transaction_type']


class SubcategoryFilter(django_filters.FilterSet):
    """Фильтр для модели Subcategory, позволяющий фильтровать по имени, категории и типу транзакции.

    Атрибуты:
        category (NumberFilter): Фильтрация подкатегорий по ID категории.
        transaction_type (NumberFilter): Фильтрация подкатегорий по ID типа транзакции через категорию.
        name (CharFilter): Фильтрация подкатегорий по имени (автоматически включено через Meta).
    """

    category = NumberFilter(field_name='category__id')
    transaction_type = NumberFilter(field_name='category__transaction_type__id')


    class Meta:
        """Метаданные для SubcategoryFilter."""
        model = Subcategory
        fields = ['name', 'category', 'transaction_type']