from calendar import monthrange
from datetime import date

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse

from .forms import BudgetForm, RegisterForm, TransactionForm
from .models import Budget, Category, Transaction


def seed_categories_for_user(user):
    defaults = [
        ("Salary", "income"),
        ("Freelance", "income"),
        ("Other Income", "income"),
        ("Food", "expense"),
        ("Transport", "expense"),
        ("Education", "expense"),
        ("Shopping", "expense"),
        ("Bills", "expense"),
        ("Health", "expense"),
        ("Entertainment", "expense"),
        ("Other Expense", "expense"),
    ]
    for name, kind in defaults:
        Category.objects.get_or_create(user=user, name=name, kind=kind)


def register(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            seed_categories_for_user(user)
            login(request, user)
            messages.success(request, "Account created successfully.")
            return redirect("dashboard")
    else:
        form = RegisterForm()
    return render(request, "registration/register.html", {"form": form})


@login_required
def dashboard(request):
    seed_categories_for_user(request.user)
    today = date.today()
    month_start = today.replace(day=1)
    month_end = today.replace(day=monthrange(today.year, today.month)[1])

    qs = Transaction.objects.filter(
        user=request.user, transaction_date__range=(month_start, month_end)
    )
    income = qs.filter(transaction_type=Transaction.INCOME).aggregate(total=Sum("amount"))["total"] or 0
    expenses = qs.filter(transaction_type=Transaction.EXPENSE).aggregate(total=Sum("amount"))["total"] or 0
    balance = income - expenses

    category_totals = (
        qs.filter(transaction_type=Transaction.EXPENSE)
        .values("category__name")
        .annotate(total=Sum("amount"))
        .order_by("-total")
    )

    context = {
        "income": income,
        "expenses": expenses,
        "balance": balance,
        "transactions": Transaction.objects.filter(user=request.user)[:8],
        "category_totals": list(category_totals),
        "month_label": today.strftime("%B %Y"),
    }
    return render(request, "finance/dashboard.html", context)


@login_required
def transactions(request):
    qs = Transaction.objects.filter(user=request.user).select_related("category")
    transaction_type = request.GET.get("type")
    if transaction_type in ("income", "expense"):
        qs = qs.filter(transaction_type=transaction_type)
    return render(request, "finance/transactions.html", {"transactions": qs, "filter_type": transaction_type})


@login_required
def transaction_create(request):
    seed_categories_for_user(request.user)
    if request.method == "POST":
        form = TransactionForm(request.POST, user=request.user)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = request.user
            obj.save()
            messages.success(request, "Transaction added.")
            return redirect("transactions")
    else:
        form = TransactionForm(user=request.user)
    return render(request, "finance/transaction_form.html", {"form": form, "title": "Add Transaction"})


@login_required
def transaction_edit(request, pk):
    # Ownership is enforced here: a user can edit only their own record.
    obj = get_object_or_404(Transaction, pk=pk, user=request.user)
    if request.method == "POST":
        form = TransactionForm(request.POST, instance=obj, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Transaction updated.")
            return redirect("transactions")
    else:
        form = TransactionForm(instance=obj, user=request.user)
    return render(request, "finance/transaction_form.html", {"form": form, "title": "Edit Transaction"})


@login_required
def transaction_delete(request, pk):
    obj = get_object_or_404(Transaction, pk=pk, user=request.user)
    if request.method == "POST":
        obj.delete()
        messages.success(request, "Transaction deleted.")
        return redirect("transactions")
    return render(request, "finance/transaction_confirm_delete.html", {"transaction": obj})


@login_required
def budgets(request):
    seed_categories_for_user(request.user)
    items = Budget.objects.filter(user=request.user).select_related("category")
    return render(request, "finance/budgets.html", {"budgets": items})


@login_required
def budget_create(request):
    seed_categories_for_user(request.user)
    if request.method == "POST":
        form = BudgetForm(request.POST, user=request.user)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = request.user
            obj.save()
            messages.success(request, "Budget created.")
            return redirect("budgets")
    else:
        form = BudgetForm(user=request.user)
    return render(request, "finance/transaction_form.html", {"form": form, "title": "Add Budget"})


@login_required
def reports(request):
    today = date.today()
    try:
        year = int(request.GET.get("year", today.year))
        month = int(request.GET.get("month", today.month))
        if not 1 <= month <= 12:
            raise ValueError
    except ValueError:
        year, month = today.year, today.month

    qs = Transaction.objects.filter(
        user=request.user, transaction_date__year=year, transaction_date__month=month
    )
    income = qs.filter(transaction_type="income").aggregate(total=Sum("amount"))["total"] or 0
    expenses = qs.filter(transaction_type="expense").aggregate(total=Sum("amount"))["total"] or 0
    by_category = list(
        qs.filter(transaction_type="expense")
        .values("category__name")
        .annotate(total=Sum("amount"))
        .order_by("-total")
    )
    return render(
        request,
        "finance/reports.html",
        {
            "income": income,
            "expenses": expenses,
            "balance": income - expenses,
            "by_category": by_category,
            "year": year,
            "month": month,
        },
    )
def debug_test(request):
    result = 10 / 0
    return HttpResponse(result)