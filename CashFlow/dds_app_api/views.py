from rest_framework import viewsets, generics, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import Status, TransactionType, Category, Subcategory, Transaction
from .serializers import (
    StatusSerializer, TransactionTypeSerializer, CategorySerializer, 
    SubcategorySerializer, TransactionSerializer, TransactionCreateSerializer,
    CategoryDetailSerializer, TransactionTypeDetailSerializer
)
from .filters import (
    TransactionFilter, StatusFilter, TransactionTypeFilter, 
    CategoryFilter, SubcategoryFilter
)

class StatusViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления статусами операций.
    
    Предоставляет CRUD операции для модели Status.
    Поддерживает фильтрацию, поиск и сортировку.
    """
    queryset = Status.objects.all()
    serializer_class = StatusSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = StatusFilter
    search_fields = ['name', 'description']
    ordering_fields = ['name']

class TransactionTypeViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления типами операций.
    
    Предоставляет CRUD операции для модели TransactionType.
    Включает дополнительные endpoints для получения категорий по типу.
    """
    queryset = TransactionType.objects.all()
    serializer_class = TransactionTypeSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = TransactionTypeFilter
    search_fields = ['name', 'description']
    ordering_fields = ['name']
    
    @swagger_auto_schema(
        operation_description="Получить список категорий для указанного типа операции",
        responses={200: CategorySerializer(many=True)}
    )
    @action(detail=True, methods=['get'])
    def categories(self, request, pk=None):
        """
        Получить категории для конкретного типа операции.
        
        Returns:
            List[Category]: Список категорий, связанных с данным типом операции
        """
        transaction_type = self.get_object()
        categories = transaction_type.category_set.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)

class CategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления категориями операций.
    
    Предоставляет CRUD операции для модели Category.
    Включает дополнительные endpoints для получения подкатегорий по категории.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = CategoryFilter
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'transaction_type__name']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CategoryDetailSerializer
        return CategorySerializer
    
    @swagger_auto_schema(
        operation_description="Получить список подкатегорий для указанной категории",
        responses={200: SubcategorySerializer(many=True)}
    )
    @action(detail=True, methods=['get'])
    def subcategories(self, request, pk=None):
        """
        Получить подкатегории для конкретной категории.
        
        Returns:
            List[Subcategory]: Список подкатегорий, связанных с данной категорией
        """
        category = self.get_object()
        subcategories = category.subcategory_set.all()
        serializer = SubcategorySerializer(subcategories, many=True)
        return Response(serializer.data)

class SubcategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления подкатегориями операций.
    
    Предоставляет CRUD операции для модели Subcategory.
    Поддерживает фильтрацию по категории и типу операции.
    """
    queryset = Subcategory.objects.all()
    serializer_class = SubcategorySerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = SubcategoryFilter
    search_fields = ['name', 'description', 'category__name']
    ordering_fields = ['name', 'category__name']

class TransactionViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления транзакциями ДДС.
    
    Предоставляет полный CRUD для операций движения денежных средств.
    Включает расширенную фильтрацию, поиск и статистические endpoints.
    """
    queryset = Transaction.objects.select_related(
        'status', 'transaction_type', 'category', 'subcategory'
    ).order_by('-transaction_date')
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = TransactionFilter
    search_fields = ['comment', 'category__name', 'subcategory__name']
    ordering_fields = ['transaction_date', 'amount', 'created_date']
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return TransactionCreateSerializer
        return TransactionSerializer
    
    def perform_create(self, serializer):
        serializer.save()
    
    @swagger_auto_schema(
        operation_description="Получить статистику по транзакциям",
        manual_parameters=[
            openapi.Parameter('date_from', openapi.IN_QUERY, description="Начальная дата периода", type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE),
            openapi.Parameter('date_to', openapi.IN_QUERY, description="Конечная дата периода", type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE),
            openapi.Parameter('transaction_type', openapi.IN_QUERY, description="ID типа операции", type=openapi.TYPE_INTEGER),
        ],
        responses={200: openapi.Response('Статистика транзакций')}
    )
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """
        Получить статистическую сводку по транзакциям.
        
        Parameters:
            date_from (date): Начальная дата периода (опционально)
            date_to (date): Конечная дата периода (опционально)
            transaction_type (int): ID типа операции для фильтрации (опционально)
        
        Returns:
            object: Статистика включающая общее количество, сумму, среднее значение,
                   группировку по типам и категориям операций
        """
        from django.db.models import Sum, Count
        
        queryset = self.filter_queryset(self.get_queryset())
        
        summary = queryset.aggregate(
            total_count=Count('id'),
            total_amount=Sum('amount'),
            average_amount=Sum('amount') / Count('id') if Count('id') > 0 else 0
        )
        
        # Группировка по типам
        by_type = queryset.values('transaction_type__name').annotate(
            count=Count('id'),
            total=Sum('amount')
        )
        
        # Группировка по категориям
        by_category = queryset.values('category__name').annotate(
            count=Count('id'),
            total=Sum('amount')
        ).order_by('-total')[:10]
        
        return Response({
            'summary': summary,
            'by_type': by_type,
            'by_category': by_category
        })

class ReferenceDataView(generics.GenericAPIView):
    """
    API View для получения всех справочных данных.
    """
    
    @swagger_auto_schema(
        operation_description="Получить все справочные данные системы",
        responses={
            200: openapi.Response(
                'Справочные данные',
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'statuses': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(type=openapi.TYPE_OBJECT)
                        ),
                        'transaction_types': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(type=openapi.TYPE_OBJECT)
                        ),
                        'categories': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(type=openapi.TYPE_OBJECT)
                        ),
                        'subcategories': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(type=openapi.TYPE_OBJECT)
                        ),
                    }
                )
            )
        }
    )
    def get(self, request):
        """
        Получить все справочные данные для фронтенда.
        """
        statuses = Status.objects.all()
        transaction_types = TransactionType.objects.all()
        categories = Category.objects.all()
        subcategories = Subcategory.objects.all()
        
        status_serializer = StatusSerializer(statuses, many=True)
        type_serializer = TransactionTypeSerializer(transaction_types, many=True)
        category_serializer = CategorySerializer(categories, many=True)
        subcategory_serializer = SubcategorySerializer(subcategories, many=True)
        
        return Response({
            'statuses': status_serializer.data,
            'transaction_types': type_serializer.data,
            'categories': category_serializer.data,
            'subcategories': subcategory_serializer.data,
        })