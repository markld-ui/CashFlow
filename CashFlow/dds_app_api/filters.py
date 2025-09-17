import django_filters
from django.db.models import Q
from .models import Transaction, Status, TransactionType, Category, Subcategory
from django_filters import DateFilter, NumberFilter, CharFilter

class TransactionFilter(django_filters.FilterSet):
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
        model = Transaction
        fields = []
    
    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(comment__icontains=value) |
            Q(category__name__icontains=value) |
            Q(subcategory__name__icontains=value)
        )

class StatusFilter(django_filters.FilterSet):
    class Meta:
        model = Status
        fields = ['name']

class TransactionTypeFilter(django_filters.FilterSet):
    class Meta:
        model = TransactionType
        fields = ['name']

class CategoryFilter(django_filters.FilterSet):
    transaction_type = NumberFilter(field_name='transaction_type__id')
    
    class Meta:
        model = Category
        fields = ['name', 'transaction_type']

class SubcategoryFilter(django_filters.FilterSet):
    category = NumberFilter(field_name='category__id')
    transaction_type = NumberFilter(field_name='category__transaction_type__id')
    
    class Meta:
        model = Subcategory
        fields = ['name', 'category', 'transaction_type']