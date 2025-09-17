from rest_framework import serializers
from .models import Status, TransactionType, Category, Subcategory, Transaction

class StatusSerializer(serializers.ModelSerializer):
    """
    Serializer для модели Status.
    
    Используется для создания, чтения, обновления и удаления статусов операций.
    """
    class Meta:
        model = Status
        fields = '__all__'
        read_only_fields = ('id',)

class TransactionTypeSerializer(serializers.ModelSerializer):
    """
    Serializer для модели TransactionType.
    
    Используется для управления типами операций (Пополнение/Списание).
    """
    class Meta:
        model = TransactionType
        fields = '__all__'
        read_only_fields = ('id',)

class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer для модели Category.
    
    Используется для управления категориями операций.
    Включает название типа операции для удобства отображения.
    """
    transaction_type_name = serializers.CharField(source='transaction_type.name', read_only=True)
    
    class Meta:
        model = Category
        fields = '__all__'
        read_only_fields = ('id', 'transaction_type_name')

class SubcategorySerializer(serializers.ModelSerializer):
    """
    Serializer для модели Subcategory.
    
    Используется для управления подкатегориями операций.
    Включает названия категории и типа операции для удобства отображения.
    """
    category_name = serializers.CharField(source='category.name', read_only=True)
    transaction_type_name = serializers.CharField(source='category.transaction_type.name', read_only=True)
    
    class Meta:
        model = Subcategory
        fields = '__all__'
        read_only_fields = ('id', 'category_name', 'transaction_type_name')

class TransactionSerializer(serializers.ModelSerializer):
    """
    Serializer для чтения данных Transaction.
    
    Используется для отображения транзакций с дополнительными полями
    для удобства чтения (названия вместо ID).
    """
    status_name = serializers.CharField(source='status.name', read_only=True)
    transaction_type_name = serializers.CharField(source='transaction_type.name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    subcategory_name = serializers.CharField(source='subcategory.name', read_only=True)
    
    class Meta:
        model = Transaction
        fields = '__all__'
        read_only_fields = ('id', 'created_date', 'status_name', 'transaction_type_name', 
                           'category_name', 'subcategory_name')

class TransactionCreateSerializer(serializers.ModelSerializer):
    """
    Serializer для создания и обновления Transaction.
    
    Используется при создании и изменении транзакций.
    Не включает вычисляемые поля для упрощения валидации.
    """
    class Meta:
        model = Transaction
        fields = '__all__'
        read_only_fields = ('created_date',)

class CategoryDetailSerializer(serializers.ModelSerializer):
    """
    Serializer для детального просмотра Category.
    
    Включает список подкатегорий для данной категории.
    """
    transaction_type_name = serializers.CharField(source='transaction_type.name', read_only=True)
    subcategories = SubcategorySerializer(many=True, read_only=True)
    
    class Meta:
        model = Category
        fields = '__all__'

class TransactionTypeDetailSerializer(serializers.ModelSerializer):
    """
    Serializer для детального просмотра TransactionType.
    
    Включает список категорий для данного типа операции.
    """
    categories = CategorySerializer(many=True, read_only=True)
    
    class Meta:
        model = TransactionType
        fields = '__all__'