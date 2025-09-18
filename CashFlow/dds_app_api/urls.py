from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views


router = DefaultRouter()
router.register(r'statuses', views.StatusViewSet)
router.register(r'transaction-types', views.TransactionTypeViewSet)
router.register(r'categories', views.CategoryViewSet)
router.register(r'subcategories', views.SubcategoryViewSet)
router.register(r'transactions', views.TransactionViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('reference-data/', views.ReferenceDataView.as_view(), name='reference-data'),
    path('api-auth/', include('rest_framework.urls')),
]