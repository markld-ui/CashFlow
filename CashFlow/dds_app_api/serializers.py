from rest_framework import serializers
from .models import Status, TransactionType, Category, Subcategory, Transaction


class StatusSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Status.

    Используется для операций CRUD (Create, Read, Update, Delete)
    со статусами операций через API.

    Attributes:
        id (int): Уникальный идентификатор статуса (только для чтения).
        name (str): Название статуса.
        description (str): Описание статуса.
    """

    class Meta:
        model = Status
        fields = '__all__'
        read_only_fields = ('id',)


class TransactionTypeSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели TransactionType.

    Используется для управления типами финансовых операций
    (Пополнение/Списание) через API.

    Attributes:
        id (int): Уникальный идентификатор типа операции (только для чтения).
        name (str): Название типа операции.
        description (str): Описание типа операции.
    """

    class Meta:
        model = TransactionType
        fields = '__all__'
        read_only_fields = ('id',)


class CategorySerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Category.

    Используется для управления категориями операций через API.
    Включает дополнительное поле с названием типа операции для удобства.

    Attributes:
        transaction_type_name (str): Название типа операции (только для чтения).
    """

    transaction_type_name = serializers.CharField(
        source='transaction_type.name',
        read_only=True
    )

    class Meta:
        model = Category
        fields = '__all__'
        read_only_fields = ('id', 'transaction_type_name')


class SubcategorySerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Subcategory.

    Используется для управления подкатегориями операций через API.
    Включает дополнительные поля с названиями категории и типа операции.

    Attributes:
        category_name (str): Название родительской категории (только для чтения).
        transaction_type_name (str): Название типа операции (только для чтения).
    """

    category_name = serializers.CharField(
        source='category.name',
        read_only=True
    )
    transaction_type_name = serializers.CharField(
        source='category.transaction_type.name',
        read_only=True
    )

    class Meta:
        model = Subcategory
        fields = '__all__'
        read_only_fields = (
            'id',
            'category_name',
            'transaction_type_name'
        )


class TransactionSerializer(serializers.ModelSerializer):
    """
    Сериализатор для чтения данных модели Transaction.

    Используется для отображения транзакций с дополнительными полями
    для удобства чтения (названия вместо ID).

    Attributes:
        status_name (str): Название статуса операции (только для чтения).
        transaction_type_name (str): Название типа операции (только для чтения).
        category_name (str): Название категории (только для чтения).
        subcategory_name (str): Название подкатегории (только для чтения).
    """

    status_name = serializers.CharField(
        source='status.name',
        read_only=True
    )
    transaction_type_name = serializers.CharField(
        source='transaction_type.name',
        read_only=True
    )
    category_name = serializers.CharField(
        source='category.name',
        read_only=True
    )
    subcategory_name = serializers.CharField(
        source='subcategory.name',
        read_only=True
    )

    class Meta:
        model = Transaction
        fields = '__all__'
        read_only_fields = (
            'id',
            'created_date',
            'status_name',
            'transaction_type_name',
            'category_name',
            'subcategory_name'
        )


class TransactionCreateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания и обновления модели Transaction.

    Используется при создании и изменении транзакций.
    Не включает вычисляемые поля для упрощения валидации.
    Выполняет проверку согласованности данных между связанными моделями.
    """

    class Meta:
        model = Transaction
        fields = '__all__'
        read_only_fields = ('created_date',)

    def validate(self, data):
        """
        Проверяет согласованность данных между связанными моделями.

        Args:
            data (dict): Данные для валидации.

        Returns:
            dict: Проверенные данные.

        Raises:
            serializers.ValidationError: Если обнаружена несогласованность данных.
        """
        if data['category'].transaction_type != data['transaction_type']:
            raise serializers.ValidationError(
                "Категория не соответствует типу операции"
            )

        if data['subcategory'].category != data['category']:
            raise serializers.ValidationError(
                "Подкатегория не соответствует категории"
            )

        return data


class CategoryDetailSerializer(serializers.ModelSerializer):
    """
    Сериализатор для детального просмотра модели Category.

    Включает список подкатегорий для данной категории и название типа операции.

    Attributes:
        transaction_type_name (str): Название типа операции (только для чтения).
        subcategories (list): Список подкатегорий (только для чтения).
    """

    transaction_type_name = serializers.CharField(
        source='transaction_type.name',
        read_only=True
    )
    subcategories = SubcategorySerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = '__all__'


class TransactionTypeDetailSerializer(serializers.ModelSerializer):
    """
    Сериализатор для детального просмотра модели TransactionType.

    Включает список категорий для данного типа операции.

    Attributes:
        categories (list): Список категорий (только для чтения).
    """

    categories = CategorySerializer(many=True, read_only=True)

    class Meta:
        model = TransactionType
        fields = '__all__'