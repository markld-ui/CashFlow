from django.shortcuts import render
from django.views import View

class IndexView(View):
    def get(self, request):
        return render(request, 'index.html')

class TransactionFormView(View):
    def get(self, request, transaction_id=None):
        context = {'transaction_id': transaction_id}
        return render(request, 'transaction_form.html', context)

class ReferencesView(View):
    def get(self, request):
        return render(request, 'references.html')