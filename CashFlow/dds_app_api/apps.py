from django.apps import AppConfig


class DdsAppApiConfig(AppConfig):
    """Конфигурация приложения DDS API.

    Атрибуты:
        default_auto_field (str): Тип автоинкрементного поля по умолчанию для моделей.
        name (str): Имя приложения, используемое Django.
        verbose_name (str): Человекочитаемое имя приложения для отображения в админке.
    """
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'dds_app_api'
    verbose_name = 'DDS API'