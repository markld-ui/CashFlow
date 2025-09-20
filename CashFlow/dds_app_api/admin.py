from django.contrib import admin
from .models import Status, TransactionType, Category, Subcategory, Transaction


class StatusAdmin(admin.ModelAdmin):
    """Админка для модели Status"""
    list_display = ('name', 'description')
    search_fields = ('name', 'description')
    list_per_page = 20


class TransactionTypeAdmin(admin.ModelAdmin):
    """Админка для модели TransactionType"""
    list_display = ('name', 'description')
    search_fields = ('name', 'description')
    list_per_page = 20


class CategoryAdmin(admin.ModelAdmin):
    """Админка для модели Category"""
    list_display = ('name', 'transaction_type', 'description')
    list_filter = ('transaction_type',)
    search_fields = ('name', 'description', 'transaction_type__name')
    list_per_page = 20
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('transaction_type')


class SubcategoryAdmin(admin.ModelAdmin):
    """Админка для модели Subcategory"""
    list_display = ('name', 'category', 'transaction_type', 'description')
    list_filter = ('category__transaction_type', 'category')
    search_fields = ('name', 'description', 'category__name')
    list_per_page = 20
    
    def transaction_type(self, obj):
        return obj.category.transaction_type
    transaction_type.short_description = 'Тип операции'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('category__transaction_type')


class TransactionAdmin(admin.ModelAdmin):
    """Админка для модели Transaction"""
    list_display = (
        'transaction_date', 
        'status', 
        'transaction_type', 
        'category', 
        'subcategory', 
        'amount', 
        'created_date'
    )
    list_filter = (
        'status',
        'transaction_type',
        'category',
        'subcategory',
        'transaction_date'
    )
    search_fields = (
        'comment',
        'category__name',
        'subcategory__name',
        'status__name'
    )
    readonly_fields = ('created_date',)
    date_hierarchy = 'transaction_date'
    list_per_page = 50
    
    fieldsets = (
        ('Основная информация', {
            'fields': (
                'transaction_date',
                'status',
                'transaction_type',
                'category',
                'subcategory',
                'amount'
            )
        }),
        ('Дополнительная информация', {
            'fields': (
                'comment',
                'created_date'
            )
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'status', 'transaction_type', 'category', 'subcategory'
        )


# Регистрация моделей в админке
admin.site.register(Status, StatusAdmin)
admin.site.register(TransactionType, TransactionTypeAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Subcategory, SubcategoryAdmin)
admin.site.register(Transaction, TransactionAdmin)