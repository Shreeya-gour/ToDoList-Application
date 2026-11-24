# TaskFlow - Professional Real-World To-Do List Management Web Application

TaskFlow is a production-ready, full-stack Task Management application built with **Django 6.1**, **Django REST Framework (DRF)**, **Bootstrap 5**, and **SQLite**.

---

## 🌟 Key Highlights

- **Light-Theme Professional UI**: Designed with clean white backgrounds, soft lavender/indigo/sky-blue accents, rounded cards, subtle shadows, modern typography (Plus Jakarta Sans), and responsive grid & table layouts.
- **Strict Business Fields**:
  1. `Name` (max 100 characters, required)
  2. `Date` (target date, required)
  3. `Task Title` (max 200 characters, required)
  4. `Description` (detailed task instructions, required)
- **Zero Extraneous Fields**: Strictly avoids priority, status, phone number, category, or time fields.
- **Full RESTful API**: Built with Django REST Framework providing complete HTTP method support (`GET`, `POST`, `PUT`, `PATCH`, `DELETE`).
- **Complete Test Suite**: 28 automated tests covering models, forms, web views, search/date filtering, and API endpoints.
- **Django Admin Customization**: Filter by date, search across name and task title, hierarchical date drilldown, and custom branding.

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- Python 3.12+ (tested with Python 3.15.2)

### 2. Setup Virtual Environment
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Database Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Create Superuser (Admin)
```bash
python manage.py createsuperuser
```
*(Pre-configured default credentials for quick testing: `admin` / `admin123`)*

### 6. Run the Development Server
```bash
python manage.py runserver
```

---

## 🌐 Application URLs

| Interface | URL | Description |
|---|---|---|
| **Dashboard** | `http://127.0.0.1:8000/` | Main task dashboard with metric cards, search, date filtering, and grid/table views |
| **Add Task** | `http://127.0.0.1:8000/tasks/create/` | Task creation form with backend validation |
| **Edit Task** | `http://127.0.0.1:8000/tasks/<id>/edit/` | Pre-filled task update form |
| **Delete Task** | `http://127.0.0.1:8000/tasks/<id>/delete/` | Safe CSRF-protected deletion confirmation |
| **Django Admin** | `http://127.0.0.1:8000/admin/` | Admin panel with search, filters, and records |
| **REST API** | `http://127.0.0.1:8000/api/tasks/` | DRF Browsable API and JSON endpoints |

---

## 📡 REST API Reference

| Method | Endpoint | Description | Status Code |
|---|---|---|---|
| `GET` | `/api/tasks/` | List all tasks | `200 OK` |
| `POST` | `/api/tasks/` | Create a new task | `201 Created` |
| `GET` | `/api/tasks/<id>/` | Retrieve task details | `200 OK` / `404 Not Found` |
| `PUT` | `/api/tasks/<id>/` | Fully update all 4 fields | `200 OK` / `400 Bad Request` |
| `PATCH` | `/api/tasks/<id>/` | Partially update specified fields | `200 OK` / `400 Bad Request` |
| `DELETE` | `/api/tasks/<id>/` | Delete task record | `204 No Content` / `404 Not Found` |

### Sample JSON Payload (POST / PUT)
```json
{
  "name": "Sarah Jenkins",
  "date": "2026-11-25",
  "task_title": "Revamp Customer Onboarding Funnel",
  "description": "Audit drop-offs, optimize form elements, and collaborate with UX."
}
```

### Sample JSON Payload (PATCH)
```json
{
  "task_title": "Revamp Onboarding Funnel - Stage 2"
}
```

---

## 🧪 Testing

Run all 28 automated tests:
```bash
python manage.py test
```
