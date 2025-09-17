from django.db import models


class Status(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Название")
    description = models.TextField(blank=True, verbose_name="Описание")


    class Meta:
        verbose_name = "Статус"
        verbose_name_plural = "Статусы"

    
    def __str__(self):
        return self.name
    

class TransactionType(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Название")
    description = models.TextField(blank=True, verbose_name="Описание")


    class Meta:
        verbose_name = "Тип операции"
        verbose_name_plural = "Типы операций"

    
    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Название")
    transaction_type = models.ForeignKey(TransactionType, on_delete=models.CASCADE, 
                                         verbose_name="Тип операции")
    description = models.TextField(blank=True, verbose_name="Описание")


    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        uniq_together = ("name", "transaction_type")


    
    def __str__(self):
        return f"{self.name} ({self.transaction_type})"
    

class Subcategory(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Название")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, 
                                         verbose_name="Категория")
    description = models.TextField(blank=True, verbose_name="Описание")


    class Meta:
        verbose_name = "Подкатегория"
        verbose_name_plural = "Подкатегории"
        uniq_together = ("name", "category")


    
    def __str__(self):
        return f"{self.name} ({self.category})"
    

class Transaction(models.Model):
    creacted_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    transaction_date = models.DateField(verbose_name="Дата операции")
    status = models.ForeignKey(Status, on_delete=models.PROTECT, verbose_name="Статус")
    transaction_type = models.ForeignKey(TransactionType, on_delete=models.PROTECT, verbose_name="Тип операции")
    category = models.ForeignKey(Category, on_delete=models.PROTECT, verbose_name="Категория")
    subcategory = models.ForeignKey(Subcategory, on_delete=models.PROTECT, verbose_name="Подкатегория")
    amount = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Сумма")
    comment = models.TextField(blank=True, verbose_name="Комментарий")


    class Meta:
        verbose_name = "Транзакция"
        verbose_name_plural = "Транзакции"
        ordering  = ["-transaction_date"]


    def __str__(self):
        return f"{self.transaction_date} - {self.amount}р. - {self.Category}"