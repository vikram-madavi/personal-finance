from django.contrib import admin
from .models import Budget, Category, Transaction

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "kind", "user")
    list_filter = ("kind",)
    search_fields = ("name", "user__username")

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("user", "transaction_type", "amount", "category", "transaction_date")
    list_filter = ("transaction_type", "category")
    search_fields = ("user__username", "description")
    date_hierarchy = "transaction_date"

@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ("user", "category", "month", "amount")
    list_filter = ("month", "category")
    search_fields = ("user__username",)
