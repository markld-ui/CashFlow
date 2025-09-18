from django.shortcuts import render
from django.views import View


class IndexView(View):
    """
    Представление для отображения главной страницы приложения.

    Обрабатывает GET-запросы и возвращает основную страницу интерфейса.
    """

    def get(self, request):
        """
        Обрабатывает GET-запрос для главной страницы.

        Args:
            request (HttpRequest): Объект HTTP-запроса.

        Returns:
            HttpResponse: Ответ с отрендеренным шаблоном index.html.
        """
        return render(request, 'index.html')


class TransactionFormView(View):
    """
    Представление для отображения формы создания/редактирования транзакции.

    Поддерживает как создание новых транзакций, так и редактирование существующих.
    """

    def get(self, request, transaction_id=None):
        """
        Обрабатывает GET-запрос для формы транзакции.

        Args:
            request (HttpRequest): Объект HTTP-запроса.
            transaction_id (int, optional): ID существующей транзакции для редактирования.
                Если None - создается новая транзакция.

        Returns:
            HttpResponse: Ответ с отрендеренным шаблоном transaction_form.html,
            содержащим context с transaction_id.
        """
        context = {'transaction_id': transaction_id}
        return render(request, 'transaction_form.html', context)


class ReferencesView(View):
    """
    Представление для отображения страницы справочников.

    Отображает страницу со справочной информацией и ссылками на различные
    справочные материалы системы.
    """

    def get(self, request):
        """
        Обрабатывает GET-запрос для страницы справочников.

        Args:
            request (HttpRequest): Объект HTTP-запроса.

        Returns:
            HttpResponse: Ответ с отрендеренным шаблоном references.html.
        """
        return render(request, 'references.html')