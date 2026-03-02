# Asian Trade Corporation — Management System

A comprehensive business management system built with Django for **Asian Trade Corporation (ATC)**. It manages factory and depot employees, attendance, salaries, loans, expenses, and financial reporting — all from a single web-based interface.

---

## Features

### Factory Management
- **Employee Management** — Add, edit, view, and deactivate factory employees
- **Attendance & Overtime** — Daily attendance tracking with working hours and overtime
- **Weekly Payments** — Record Thursday advance payments per employee
- **Monthly Salary** — Auto-calculated from attendance (hourly rate = basic ÷ 240), with bonuses, deductions, and loan installments
- **Loans** — Track employee loans with monthly installment deductions; auto-creates loans for negative salary balances
- **Performance** — Monthly scoring (quality, punctuality, productivity, teamwork) on a 1–10 scale
- **Increment Recommendations** — Year-end salary increment suggestions based on average performance scores

### Depot Management
- **Depot CRUD** — Manage multiple depot locations
- **Depot Employees** — Employees assigned to specific depots
- **Attendance** — Daily attendance with night bill tracking
- **Monthly Salary** — Daily-rate based (basic ÷ 30), with night bills, bonuses, deductions, and loans
- **Loans** — Same loan system as factory

### Expenses
- Track expenses by type (factory/depot), category (12 categories), and date range
- Category breakdown and total summary

### Finance — Sales vs Cost
- Record sales and cost entries by category
- Monthly/yearly profit calculation with margin percentage
- 12-month trend chart (Chart.js)

### Print Support
- **Print button** on every list and report page
- Professional print layout with company header, report title, date, and signature lines
- Optimized for landscape printing with clean table formatting
- Salary sheets include "Prepared By / Checked By / Approved By" signature area

### Portable Deployment
- PyInstaller spec file included for building a standalone Windows executable
- No Python installation required on target machines
- SQLite database stays portable alongside the executable

---

## Tech Stack

| Component       | Technology                          |
|-----------------|-------------------------------------|
| Backend         | Django 4.2                          |
| Database        | SQLite 3                            |
| Frontend        | Bootstrap 5.3, Font Awesome 6.5    |
| Charts          | Chart.js 4.4                        |
| Font            | Inter (Google Fonts)                |
| Packaging       | PyInstaller 6.x                     |
| Language        | Python 3.11+                        |

---

## Project Structure

```
ATC_Management_System/
├── atc_management/          # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── core/                    # Dashboard app
│   ├── views.py
│   └── templatetags/
│       └── custom_tags.py   # currency, math filters
├── factory/                 # Factory employee management
│   ├── models.py            # FactoryEmployee, Attendance, Salary, Loan, etc.
│   ├── views.py
│   ├── forms.py
│   └── urls.py
├── depot/                   # Depot management
│   ├── models.py            # Depot, DepotEmployee, Attendance, Salary, Loan
│   ├── views.py
│   ├── forms.py
│   └── urls.py
├── expenses/                # Expense tracking
│   ├── models.py            # Expense
│   ├── views.py
│   └── urls.py
├── finance/                 # Sales & cost tracking
│   ├── models.py            # SalesRecord, CostRecord
│   ├── views.py
│   └── urls.py
├── templates/               # HTML templates
│   ├── base.html            # Master layout with sidebar
│   ├── core/
│   ├── factory/             # 17 templates
│   ├── depot/               # 16 templates
│   ├── expenses/            # 3 templates
│   └── finance/             # 3 templates
├── static/
│   ├── css/style.css        # Custom styles + print styles
│   └── js/main.js           # Sidebar toggle, alerts, print handler
├── launcher.py              # Portable launcher (for EXE builds)
├── manage.py                # Django CLI
├── requirements.txt         # Python dependencies
└── atc_management.spec      # PyInstaller build spec
```

---

## Installation & Setup

### Prerequisites
- Python 3.11 or higher

### 1. Clone the Repository

```bash
git clone https://github.com/shohelex/Salary-Management-App_ATC.git
cd Salary-Management-App_ATC
```

### 2. Create Virtual Environment

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run Migrations

```bash
python manage.py migrate
```

### 5. Create Admin User (Optional)

```bash
python manage.py createsuperuser
```

### 6. Start the Server

```bash
python manage.py runserver
```

Open **http://127.0.0.1:8000/** in your browser.

---

## Building a Portable Executable

To create a standalone `.exe` that can run on any Windows machine without Python:

### 1. Install PyInstaller

```bash
pip install pyinstaller
```

### 2. Build

```bash
pyinstaller atc_management.spec --noconfirm
```

### 3. Output

The portable app is at:
```
dist/ATC_Management_System/
├── ATC_Management_System.exe    # Main executable
└── _internal/                   # Bundled dependencies
```

### 4. Deploy

Copy the entire `dist/ATC_Management_System/` folder to any Windows computer. Double-click `ATC_Management_System.exe` to run — it will:
1. Automatically set up the database on first launch
2. Start the web server on an available port
3. Open the browser to the application

> **Important:** Send the entire folder, not just the `.exe` file. The `_internal/` directory contains all required dependencies.

---

## Salary Calculation

### Factory Employees
| Field | Formula |
|-------|---------|
| Hourly Rate | Basic Salary ÷ 240 |
| Earned Salary | Hourly Rate × Total Hours (regular + overtime) |
| Net Salary | Earned + Bonus 1 + Bonus 2 − Deductions − Loan Deduction |
| Balance | Net Salary − Total Weekly Payments |

### Depot Employees
| Field | Formula |
|-------|---------|
| Daily Rate | Basic Salary ÷ 30 |
| Day Salary | Daily Rate × Present Days |
| Calculated Salary | Day Salary + Total Night Bills |
| Net Salary | Calculated + Bonus 1 + Bonus 2 − Deductions − Loan Deduction |
| Balance | Net Salary − Payments Made |

---

## Printing Reports

Every list and report page has a **Print** button. When clicked:
- The sidebar, navbar, buttons, and action columns are hidden
- A professional company header appears with the report title and date
- Tables are formatted with borders for clean printing
- Salary sheets include signature lines at the bottom

**Printable pages include:**
- Employee lists (factory & depot)
- Attendance reports
- Weekly payment summaries
- Loan lists
- Monthly salary sheets
- Performance reports
- Increment recommendations
- Expense reports
- Sales vs cost reports

---

## Currency

All monetary values are in **BDT (৳)** — Bangladeshi Taka.

---

## Timezone

The system uses **Asia/Dhaka** timezone.

---

## License

This project is for internal use by Asian Trade Corporation.
