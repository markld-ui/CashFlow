from django.db import models


class Status(models.Model):
    """
    Модель для представления статусов операций.

    Статусы определяют принадлежность или тип операции (бизнес, личное, налоги и т.д.).

    Attributes:
        name (CharField): Название статуса (уникальное).
        description (TextField): Описание статуса (необязательное).
    """

    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Название"
    )
    description = models.TextField(
        blank=True,
        verbose_name="Описание"
    )

    class Meta:
        """Метаданные модели Status."""
        verbose_name = "Статус"
        verbose_name_plural = "Статусы"

    def __str__(self):
        """
        Строковое представление объекта Status.

        Returns:
            str: Название статуса.
        """
        return self.name


class TransactionType(models.Model):
    """
    Модель для представления типов финансовых операций.

    Определяет основные типы операций: пополнение (доход) и списание (расход).

    Attributes:
        name (CharField): Название типа операции (уникальное).
        description (TextField): Описание типа операции (необязательное).
    """

    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Название"
    )
    description = models.TextField(
        blank=True,
        verbose_name="Описание"
    )

    class Meta:
        """Метаданные модели TransactionType."""
        verbose_name = "Тип операции"
        verbose_name_plural = "Типы операций"

    def __str__(self):
        """
        Строковое представление объекта TransactionType.

        Returns:
            str: Название типа операции.
        """
        return self.name


class Category(models.Model):
    """
    Модель для представления категорий операций.

    Категории группируют операции по тематике и связаны с определенным типом операции.

    Attributes:
        name (CharField): Название категории.
        transaction_type (ForeignKey): Ссылка на тип операции.
        description (TextField): Описание категории (необязательное).
    """

    name = models.CharField(
        max_length=100,
        verbose_name="Название"
    )
    transaction_type = models.ForeignKey(
        TransactionType,
        on_delete=models.CASCADE,
        verbose_name="Тип операции"
    )
    description = models.TextField(
        blank=True,
        verbose_name="Описание"
    )

    class Meta:
        """Метаданные модели Category."""
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        unique_together = ("name", "transaction_type")

    def __str__(self):
        """
        Строковое представление объекта Category.

        Returns:
            str: Название категории с указанием типа операции.
        """
        return f"{self.name} ({self.transaction_type})"


class Subcategory(models.Model):
    """
    Модель для представления подкатегорий операций.

    Подкатегории предоставляют более детальную классификацию внутри категорий.

    Attributes:
        name (CharField): Название подкатегории.
        category (ForeignKey): Ссылка на родительскую категорию.
        description (TextField): Описание подкатегории (необязательное).
    """

    name = models.CharField(
        max_length=100,
        verbose_name="Название"
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        verbose_name="Категория"
    )
    description = models.TextField(
        blank=True,
        verbose_name="Описание"
    )

    class Meta:
        """Метаданные модели Subcategory."""
        verbose_name = "Подкатегория"
        verbose_name_plural = "Подкатегории"
        unique_together = ("name", "category")

    def __str__(self):
        """
        Строковое представление объекта Subcategory.

        Returns:
            str: Название подкатегории с указанием родительской категории.
        """
        return f"{self.name} ({self.category})"


class Transaction(models.Model):
    """
    Модель для представления финансовых транзакций.

    Содержит полную информацию о финансовой операции включая даты, суммы,
    категоризацию и статус.

    Attributes:
        created_date (DateTimeField): Дата и время создания записи.
        transaction_date (DateField): Дата совершения операции.
        status (ForeignKey): Статус операции.
        transaction_type (ForeignKey): Тип операции.
        category (ForeignKey): Категория операции.
        subcategory (ForeignKey): Подкатегория операции.
        amount (DecimalField): Сумма операции.
        comment (TextField): Комментарий к операции (необязательный).
    """

    created_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )
    transaction_date = models.DateField(
        verbose_name="Дата операции"
    )
    status = models.ForeignKey(
        Status,
        on_delete=models.PROTECT,
        verbose_name="Статус"
    )
    transaction_type = models.ForeignKey(
        TransactionType,
        on_delete=models.PROTECT,
        verbose_name="Тип операции"
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        verbose_name="Категория"
    )
    subcategory = models.ForeignKey(
        Subcategory,
        on_delete=models.PROTECT,
        verbose_name="Подкатегория"
    )
    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name="Сумма"
    )
    comment = models.TextField(
        blank=True,
        verbose_name="Комментарий"
    )

    class Meta:
        """Метаданные модели Transaction."""
        verbose_name = "Транзакция"
        verbose_name_plural = "Транзакции"
        ordering = ["-transaction_date"]

    def __str__(self):
        """
        Строковое представление объекта Transaction.

        Returns:
            str: Дата, сумма и категория операции.
        """
        return f"{self.transaction_date} - {self.amount}р. - {self.category}"