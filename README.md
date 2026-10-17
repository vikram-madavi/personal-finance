# Personal Finance Management System 

AI-assisted Week 1 project for Cyber Security coursework.

## Features
- User registration/login/logout
- Personal dashboard
- Income and expense transactions
- Categories
- Monthly budgets
- Monthly/category reports
- Transaction ownership checks
- CSRF-protected forms
- Django password hashing/authentication
- Demo data can be entered manually

## Important
This Version 0 is for local coursework/demo use. Do not connect it to real bank accounts,
real payment credentials, or real financial APIs.

## Setup
Windows PowerShell:
```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open http://127.0.0.1:8000/

Admin: http://127.0.0.1:8000/admin/
