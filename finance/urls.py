from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("register/", views.register, name="register"),
    path("transactions/", views.transactions, name="transactions"),
    path("transactions/add/", views.transaction_create, name="transaction_create"),
    path("transactions/<int:pk>/edit/", views.transaction_edit, name="transaction_edit"),
    path("transactions/<int:pk>/delete/", views.transaction_delete, name="transaction_delete"),
    path("budgets/", views.budgets, name="budgets"),
    path("budgets/add/", views.budget_create, name="budget_create"),
    path("reports/", views.reports, name="reports"),
    path("debug-test/", views.debug_test),
]
