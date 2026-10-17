import random
from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction as db_transaction
from django.db.models import Sum

from finance.models import Category, Transaction, Budget


class Command(BaseCommand):
    help = "Generate synthetic users, categories, transactions and budgets."

    def add_arguments(self, parser):
        parser.add_argument(
            "--users",
            type=int,
            default=100,
            help="Number of users to generate (default: 100)",
        )

        parser.add_argument(
            "--months",
            type=int,
            default=12,
            help="Number of months of financial data (default: 12)",
        )

        parser.add_argument(
            "--transactions",
            type=int,
            default=80,
            help="Average transactions per user per month (default: 80)",
        )

        parser.add_argument(
            "--seed",
            type=int,
            default=42,
            help="Random seed for reproducible data (default: 42)",
        )

        parser.add_argument(
            "--clear",
            action="store_true",
            help="Delete previously generated synthetic users and their data.",
        )

    def handle(self, *args, **options):

        random.seed(options["seed"])

        number_of_users = options["users"]
        number_of_months = options["months"]
        transactions_per_month = options["transactions"]

        self.stdout.write(
            self.style.SUCCESS(
                "\nStarting synthetic finance data generation...\n"
            )
        )

        # ---------------------------------------------------------
        # 1. CLEAR PREVIOUS SYNTHETIC DATA
        # ---------------------------------------------------------

        if options["clear"]:
            self.stdout.write("Removing previously generated synthetic users...")

            synthetic_users = User.objects.filter(
                username__startswith="synthetic_"
            )

            count = synthetic_users.count()

            synthetic_users.delete()

            self.stdout.write(
                self.style.SUCCESS(
                    f"Deleted {count} synthetic users and related data."
                )
            )

        # ---------------------------------------------------------
        # 2. CATEGORY DEFINITIONS
        # ---------------------------------------------------------

        income_categories = [
            "Salary",
            "Freelance",
            "Other Income",
        ]

        expense_categories = [
            "Food",
            "Transport",
            "Education",
            "Shopping",
            "Bills",
            "Health",
            "Entertainment",
            "Other Expense",
        ]

        # ---------------------------------------------------------
        # 3. NAMES
        # ---------------------------------------------------------

        first_names = [
            "Aarav",
            "Aditi",
            "Akash",
            "Aman",
            "Ananya",
            "Aniket",
            "Anjali",
            "Arjun",
            "Aryan",
            "Ashish",
            "Ayush",
            "Deepak",
            "Divya",
            "Gaurav",
            "Harsh",
            "Isha",
            "Karan",
            "Kavya",
            "Manish",
            "Meera",
            "Mohit",
            "Neha",
            "Nikhil",
            "Pooja",
            "Pranav",
            "Priya",
            "Rahul",
            "Riya",
            "Rohit",
            "Sachin",
            "Sakshi",
            "Sameer",
            "Sanjay",
            "Shivam",
            "Shreya",
            "Sneha",
            "Sonia",
            "Suresh",
            "Tanvi",
            "Varun",
            "Vikas",
            "Vikram",
            "Yash",
        ]

        last_names = [
            "Patil",
            "Sharma",
            "Joshi",
            "Deshmukh",
            "Pawar",
            "Jadhav",
            "Kulkarni",
            "More",
            "Chavan",
            "Gaikwad",
            "Shinde",
            "Kadam",
            "Thakur",
            "Bhosale",
            "Mishra",
            "Verma",
            "Gupta",
            "Singh",
            "Yadav",
            "Mehta",
            "Reddy",
            "Nair",
            "Iyer",
            "Rao",
        ]

        # ---------------------------------------------------------
        # 4. INCOME / EXPENSE DESCRIPTIONS
        # ---------------------------------------------------------

        income_descriptions = {
            "Salary": [
                "Monthly Salary",
                "Salary Credit",
                "Monthly Pay",
                "Salary Deposit",
            ],
            "Freelance": [
                "Freelance Project",
                "Freelance Payment",
                "Consulting Income",
                "Part-time Work",
            ],
            "Other Income": [
                "Cashback",
                "Interest Income",
                "Refund Received",
                "Other Income",
            ],
        }

        expense_descriptions = {
            "Food": [
                "Lunch",
                "Dinner",
                "Breakfast",
                "Restaurant",
                "Food Delivery",
                "Snacks",
                "Coffee",
            ],
            "Transport": [
                "Bus Ticket",
                "Auto Rickshaw",
                "Cab Ride",
                "Petrol",
                "Metro",
                "Train Ticket",
            ],
            "Education": [
                "Course Fee",
                "Books",
                "Study Material",
                "Online Course",
                "Exam Fee",
            ],
            "Shopping": [
                "Clothes",
                "Electronics",
                "Online Shopping",
                "Shoes",
                "Household Items",
            ],
            "Bills": [
                "Electricity Bill",
                "Mobile Recharge",
                "Internet Bill",
                "Water Bill",
                "Gas Bill",
                "Rent",
            ],
            "Health": [
                "Medicine",
                "Doctor Consultation",
                "Pharmacy",
                "Medical Test",
                "Health Checkup",
            ],
            "Entertainment": [
                "Movie",
                "OTT Subscription",
                "Gaming",
                "Concert",
                "Restaurant",
                "Sports",
            ],
            "Other Expense": [
                "Miscellaneous",
                "Personal Expense",
                "Donation",
                "Other Expense",
            ],
        }

        # ---------------------------------------------------------
        # 5. BUDGET RANGES
        # ---------------------------------------------------------

        budget_ranges = {
            "Food": (3000, 8000),
            "Transport": (1500, 5000),
            "Education": (1000, 6000),
            "Shopping": (2000, 8000),
            "Bills": (2000, 7000),
            "Health": (1000, 5000),
            "Entertainment": (1000, 5000),
            "Other Expense": (1000, 4000),
        }

        # ---------------------------------------------------------
        # 6. MONTH RANGE
        # ---------------------------------------------------------

        today = date.today()

        current_month_start = today.replace(day=1)

        start_month = self.subtract_months(
            current_month_start,
            number_of_months - 1,
        )

        months = []

        for i in range(number_of_months):
            month = self.add_months(start_month, i)
            months.append(month)

        # ---------------------------------------------------------
        # 7. CREATE USERS
        # ---------------------------------------------------------

        users_created = 0
        categories_created = 0
        transactions_created = 0
        budgets_created = 0

        self.stdout.write(
            f"Generating {number_of_users} users...\n"
        )

        with db_transaction.atomic():

            for user_number in range(1, number_of_users + 1):

                first_name = random.choice(first_names)
                last_name = random.choice(last_names)

                username = f"synthetic_{user_number:03d}"

                email = (
                    f"{username}@example.com"
                )

                # ---------------------------------------------
                # Create user
                # ---------------------------------------------

                user, created = User.objects.get_or_create(
                    username=username,
                    defaults={
                        "first_name": first_name,
                        "last_name": last_name,
                        "email": email,
                    },
                )

                if created:
                    user.set_password("Finance@123")
                    user.save()

                    users_created += 1

                # ---------------------------------------------
                # Create categories
                # ---------------------------------------------

                category_map = {}

                for category_name in income_categories:

                    category, category_created = (
                        Category.objects.get_or_create(
                            user=user,
                            name=category_name,
                            kind="income",
                        )
                    )

                    category_map[category_name] = category

                    if category_created:
                        categories_created += 1

                for category_name in expense_categories:

                    category, category_created = (
                        Category.objects.get_or_create(
                            user=user,
                            name=category_name,
                            kind="expense",
                        )
                    )

                    category_map[category_name] = category

                    if category_created:
                        categories_created += 1

                # ---------------------------------------------
                # Determine user's financial profile
                # ---------------------------------------------

                monthly_salary = random.choice(
                    [
                        18000,
                        22000,
                        25000,
                        28000,
                        30000,
                        35000,
                        40000,
                        45000,
                        50000,
                        55000,
                        60000,
                        70000,
                        80000,
                        90000,
                        100000,
                    ]
                )

                # ---------------------------------------------
                # Generate data for every month
                # ---------------------------------------------

                for month_start in months:

                    year = month_start.year
                    month = month_start.month

                    # =========================================
                    # SALARY
                    # =========================================

                    # Small salary variation to make the data
                    # more realistic.
                    salary_variation = Decimal(
                        random.choice(
                            [
                                "0",
                                "0",
                                "0",
                                "500",
                                "-500",
                                "1000",
                                "-1000",
                            ]
                        )
                    )

                    salary = Decimal(
                        monthly_salary
                    ) + salary_variation

                    if salary < Decimal("10000"):
                        salary = Decimal("10000")

                    Transaction.objects.create(
                        user=user,
                        transaction_type=Transaction.INCOME,
                        amount=salary,
                        category=category_map["Salary"],
                        description=random.choice(
                            income_descriptions["Salary"]
                        ),
                        transaction_date=month_start
                        + timedelta(days=random.randint(0, 3)),
                    )

                    transactions_created += 1

                    # =========================================
                    # FREELANCE
                    # =========================================

                    if random.random() < 0.25:

                        freelance_amount = Decimal(
                            random.randint(2000, 15000)
                        )

                        Transaction.objects.create(
                            user=user,
                            transaction_type=Transaction.INCOME,
                            amount=freelance_amount,
                            category=category_map["Freelance"],
                            description=random.choice(
                                income_descriptions["Freelance"]
                            ),
                            transaction_date=self.random_date_in_month(
                                year,
                                month,
                            ),
                        )

                        transactions_created += 1

                    # =========================================
                    # OTHER INCOME
                    # =========================================

                    if random.random() < 0.15:

                        other_income = Decimal(
                            random.randint(500, 5000)
                        )

                        Transaction.objects.create(
                            user=user,
                            transaction_type=Transaction.INCOME,
                            amount=other_income,
                            category=category_map["Other Income"],
                            description=random.choice(
                                income_descriptions["Other Income"]
                            ),
                            transaction_date=self.random_date_in_month(
                                year,
                                month,
                            ),
                        )

                        transactions_created += 1

                    # =========================================
                    # BUDGETS
                    # =========================================

                    for category_name in expense_categories:

                        minimum, maximum = budget_ranges[
                            category_name
                        ]

                        budget_amount = Decimal(
                            random.randint(
                                minimum,
                                maximum,
                            )
                        )

                        Budget.objects.update_or_create(
                            user=user,
                            category=category_map[category_name],
                            month=month_start,
                            defaults={
                                "amount": budget_amount,
                            },
                        )

                        budgets_created += 1

                    # =========================================
                    # EXPENSE TRANSACTIONS
                    # =========================================

                    # Number of expenses varies between months.
                    expense_count = random.randint(
                        max(20, transactions_per_month - 20),
                        transactions_per_month + 20,
                    )

                    # Category probability.
                    expense_weights = {
                        "Food": 22,
                        "Transport": 12,
                        "Education": 6,
                        "Shopping": 12,
                        "Bills": 15,
                        "Health": 5,
                        "Entertainment": 8,
                        "Other Expense": 5,
                    }

                    categories = list(
                        expense_weights.keys()
                    )

                    weights = list(
                        expense_weights.values()
                    )

                    for _ in range(expense_count):

                        category_name = random.choices(
                            categories,
                            weights=weights,
                            k=1,
                        )[0]

                        # -------------------------------------
                        # Amount ranges
                        # -------------------------------------

                        amount_ranges = {
                            "Food": (80, 1200),
                            "Transport": (50, 1000),
                            "Education": (300, 5000),
                            "Shopping": (300, 10000),
                            "Bills": (300, 8000),
                            "Health": (200, 5000),
                            "Entertainment": (150, 3000),
                            "Other Expense": (100, 3000),
                        }

                        minimum, maximum = amount_ranges[
                            category_name
                        ]

                        amount = Decimal(
                            random.randint(
                                minimum,
                                maximum,
                            )
                        )

                        Transaction.objects.create(
                            user=user,
                            transaction_type=Transaction.EXPENSE,
                            amount=amount,
                            category=category_map[category_name],
                            description=random.choice(
                                expense_descriptions[
                                    category_name
                                ]
                            ),
                            transaction_date=self.random_date_in_month(
                                year,
                                month,
                            ),
                        )

                        transactions_created += 1

        # ---------------------------------------------------------
        # 8. DISPLAY SUMMARY
        # ---------------------------------------------------------

        self.stdout.write("\n")
        self.stdout.write(
            self.style.SUCCESS(
                "=========================================="
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                " SYNTHETIC DATA GENERATION COMPLETED"
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                "=========================================="
            )
        )

        self.stdout.write(
            f"Users created       : {users_created}"
        )

        self.stdout.write(
            f"Categories created  : {categories_created}"
        )

        self.stdout.write(
            f"Transactions created: {transactions_created}"
        )

        self.stdout.write(
            f"Budgets created     : {budgets_created}"
        )

        self.stdout.write("\n")

        self.stdout.write(
            self.style.SUCCESS(
                "Generated users can login using:"
            )
        )

        self.stdout.write(
            "Username : synthetic_001"
        )

        self.stdout.write(
            "Password : Finance@123"
        )

        self.stdout.write("\n")

        self.stdout.write(
            self.style.SUCCESS(
                "Example:"
            )
        )

        self.stdout.write(
            "python manage.py generate_finance_data --users 100 --months 12"
        )

    # =========================================================
    # HELPER FUNCTIONS
    # =========================================================

    @staticmethod
    def add_months(source_date, months):
        """
        Add a number of months to a date.
        """

        month = source_date.month - 1 + months

        year = source_date.year + month // 12

        month = month % 12 + 1

        return date(
            year,
            month,
            1,
        )

    @staticmethod
    def subtract_months(source_date, months):
        """
        Subtract a number of months from a date.
        """

        return Command.add_months(
            source_date,
            -months,
        )

    @staticmethod
    def random_date_in_month(year, month):
        """
        Return a random date inside the specified month.
        """

        if month == 12:
            next_month = date(
                year + 1,
                1,
                1,
            )
        else:
            next_month = date(
                year,
                month + 1,
                1,
            )

        first_day = date(
            year,
            month,
            1,
        )

        days_in_month = (
            next_month - first_day
        ).days

        random_day = random.randint(
            0,
            days_in_month - 1,
        )

        return first_day + timedelta(
            days=random_day
        )
