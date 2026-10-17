from decimal import Decimal
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import Budget, Category, Transaction


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ("transaction_type", "amount", "category", "description", "transaction_date")
        widgets = {
            "transaction_date": forms.DateInput(attrs={"type": "date"}),
            "description": forms.TextInput(attrs={"placeholder": "Optional note"}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        if user:
            self.fields["category"].queryset = Category.objects.filter(
                user=user
            )

    def clean_amount(self):
        amount = self.cleaned_data["amount"]
        if amount <= Decimal("0"):
            raise ValidationError("Amount must be greater than zero.")
        return amount

    def clean(self):
        cleaned = super().clean()
        if not self.user:
            return cleaned
        category = cleaned.get("category")
        tx_type = cleaned.get("transaction_type")
        if category and tx_type:
            allowed = category.user_id in (None, self.user.id) and category.kind in (tx_type, "both")
            if not allowed:
                raise ValidationError("Selected category is not available for this transaction type.")
        return cleaned


def models_q_user(user):
    from django.db.models import Q
    return Q(user=user) | Q(user__isnull=True)


class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = ("category", "month", "amount")
        widgets = {
            "month": forms.DateInput(format="%Y-%m-%d",attrs={ "type": "date",},)
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        if user:
            self.fields["category"].queryset = Category.objects.filter(
                models_q_user(user), kind__in=("expense", "both")
            )

    def clean_amount(self):
        amount = self.cleaned_data["amount"]
        if amount <= Decimal("0"):
            raise ValidationError("Budget must be greater than zero.")
        return amount
