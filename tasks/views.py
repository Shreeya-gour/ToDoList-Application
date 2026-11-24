import io
import csv
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from datetime import date as dt_date
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from .models import Task
from .forms import TaskForm, UserRegisterForm, UserLoginForm

def register_view(request):
    """User Registration View: saves encrypted password, requires email, redirects to login"""
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(
                request,
                f"Account successfully registered for '{user.username}'! Please log in now with your credentials to access your dashboard."
            )
            return redirect('login')
        else:
            messages.error(request, "Please correct the registration errors below.")
    else:
        form = UserRegisterForm()
        
    return render(request, 'tasks/register.html', {'form': form})

def login_view(request):
    """User Login View: checks if user exists in database; if not, alerts user to register first"""
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        login_input = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        # Check if user exists by username or email
        user_obj = User.objects.filter(Q(username__iexact=login_input) | Q(email__iexact=login_input)).first()

        if not user_obj:
            messages.warning(
                request,
                f"No account found for '{login_input}'. Please register first before logging in!"
            )
            form = UserLoginForm(request, data=request.POST)
            return render(request, 'tasks/login.html', {'form': form, 'not_registered': True, 'entered_user': login_input})

        # User exists, authenticate password
        user = authenticate(request, username=user_obj.username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            next_url = request.GET.get('next') or 'dashboard'
            return redirect(next_url)
        else:
            messages.error(request, "Incorrect password. Please verify your password and try again.")
            form = UserLoginForm(request, data=request.POST)
            return render(request, 'tasks/login.html', {'form': form, 'not_registered': False})
    else:
        form = UserLoginForm()

    return render(request, 'tasks/login.html', {'form': form, 'not_registered': False})

def logout_view(request):
    """User Logout View"""
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect('login')

def _get_filtered_user_tasks(request):
    """Helper to return filtered tasks for the logged in user based on search and date query params."""
    search_query = request.GET.get('q', '').strip()
    date_filter = request.GET.get('date', '').strip()

    tasks = Task.objects.filter(user=request.user)

    if search_query:
        tasks = tasks.filter(
            Q(task_title__icontains=search_query) |
            Q(name__icontains=search_query)
        )

    if date_filter:
        try:
            tasks = tasks.filter(date=date_filter)
        except Exception:
            pass

    return tasks.order_by('-date', '-created_at')

@login_required(login_url='login')
def dashboard(request):
    """
    TaskFlow Dashboard View
    - Fetches ONLY tasks belonging to the logged-in user from SQLite
    - Supports GET search by Task Title or Name
    - Supports GET filtering by Date
    - Calculates user-specific summary statistics
    """
    search_query = request.GET.get('q', '').strip()
    date_filter = request.GET.get('date', '').strip()

    # User-specific query isolation via helper
    tasks = _get_filtered_user_tasks(request)

    # Summary metrics (based on all tasks belonging to current user)
    all_user_tasks = Task.objects.filter(user=request.user)
    total_count = all_user_tasks.count()
    today_date = dt_date.today()
    today_count = all_user_tasks.filter(date=today_date).count()
    upcoming_count = all_user_tasks.filter(date__gt=today_date).count()

    context = {
        'tasks': tasks,
        'total_count': total_count,
        'today_count': today_count,
        'upcoming_count': upcoming_count,
        'search_query': search_query,
        'date_filter': date_filter,
        'today_date': today_date,
        'filtered_count': tasks.count(),
    }
    return render(request, 'tasks/dashboard.html', context)

@login_required(login_url='login')
def export_tasks_csv(request):
    """Export filtered user tasks to a clean CSV / Excel file."""
    tasks = _get_filtered_user_tasks(request)

    response = HttpResponse(content_type='text/csv; charset=utf-8')
    timestamp = dt_date.today().isoformat()
    response['Content-Disposition'] = f'attachment; filename="taskflow_tasks_{request.user.username}_{timestamp}.csv"'

    writer = csv.writer(response)
    writer.writerow(['Task ID', 'Task Title', 'Assignee Name', 'Target Date', 'Description', 'Created At'])

    for task in tasks:
        clean_desc = task.description.replace('\r\n', ' ').replace('\n', ' ')
        writer.writerow([
            task.id,
            task.task_title,
            task.name,
            task.date.isoformat(),
            clean_desc,
            task.created_at.strftime('%Y-%m-%d %H:%M')
        ])

    return response

@login_required(login_url='login')
def export_tasks_pdf(request):
    """Export filtered user tasks to a professional PDF document."""
    tasks = _get_filtered_user_tasks(request)

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(letter),
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    elements = []
    styles = getSampleStyleSheet()

    # Typography & Styles
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        textColor=colors.HexColor('#4338ca'),
        spaceAfter=4
    )
    subtitle_style = ParagraphStyle(
        'SubtitleStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        textColor=colors.HexColor('#64748b'),
        spaceAfter=14
    )
    cell_style = ParagraphStyle(
        'CellStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor('#1e293b')
    )
    header_cell_style = ParagraphStyle(
        'HeaderCellStyle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#ffffff')
    )

    elements.append(Paragraph("TaskFlow &bull; Personal Task Management Report", title_style))
    today_str = dt_date.today().strftime('%B %d, %Y')
    elements.append(Paragraph(
        f"Generated for User: <b>{request.user.username}</b> &bull; Date: {today_str} &bull; Total Tasks: {tasks.count()}",
        subtitle_style
    ))
    elements.append(Spacer(1, 6))

    # Build Table
    data = [
        [
            Paragraph("ID", header_cell_style),
            Paragraph("Task Title", header_cell_style),
            Paragraph("Assignee", header_cell_style),
            Paragraph("Due Date", header_cell_style),
            Paragraph("Description", header_cell_style)
        ]
    ]

    for task in tasks:
        desc_snippet = task.description[:130] + ('...' if len(task.description) > 130 else '')
        data.append([
            Paragraph(str(task.id), cell_style),
            Paragraph(f"<b>{task.task_title}</b>", cell_style),
            Paragraph(task.name, cell_style),
            Paragraph(task.date.strftime('%Y-%m-%d'), cell_style),
            Paragraph(desc_snippet, cell_style)
        ])

    table = Table(data, colWidths=[35, 185, 110, 80, 310])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#6366f1')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 7),
        ('TOPPADDING', (0, 0), (-1, 0), 7),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#ffffff'), colors.HexColor('#f8fafd')]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
    ]))

    elements.append(table)
    doc.build(elements)

    buffer.seek(0)
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    timestamp = dt_date.today().isoformat()
    response['Content-Disposition'] = f'attachment; filename="taskflow_report_{request.user.username}_{timestamp}.pdf"'
    return response

    context = {
        'tasks': tasks,
        'total_count': total_count,
        'today_count': today_count,
        'upcoming_count': upcoming_count,
        'search_query': search_query,
        'date_filter': date_filter,
        'today_date': today_date,
        'filtered_count': tasks.count(),
    }
    return render(request, 'tasks/dashboard.html', context)

@login_required(login_url='login')
def task_create(request):
    """
    Create a new task with EXACTLY the four required fields:
    Name, Date, Task Title, Description.
    Associates the task automatically with request.user.
    """
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.save()
            messages.success(request, f"Task '{task.task_title}' created successfully!")
            return redirect('dashboard')
        else:
            messages.error(request, "Please resolve the validation errors below.")
    else:
        form = TaskForm(initial={'date': dt_date.today().isoformat()})

    context = {
        'form': form,
        'is_edit': False,
        'page_title': 'Add New Task',
        'submit_text': 'Create Task',
    }
    return render(request, 'tasks/task_form.html', context)

@login_required(login_url='login')
def task_update(request, pk):
    """
    Update an existing task owned by request.user with pre-filled field values.
    """
    task = get_object_or_404(Task, pk=pk, user=request.user)

    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            updated_task = form.save()
            messages.success(request, f"Task '{updated_task.task_title}' updated successfully!")
            return redirect('dashboard')
        else:
            messages.error(request, "Please resolve the validation errors below.")
    else:
        form = TaskForm(instance=task)

    context = {
        'form': form,
        'task': task,
        'is_edit': True,
        'page_title': f"Edit Task: {task.task_title}",
        'submit_text': 'Save Changes',
    }
    return render(request, 'tasks/task_form.html', context)

@login_required(login_url='login')
def task_delete(request, pk):
    """
    Delete task view (only allowed for task owner).
    """
    task = get_object_or_404(Task, pk=pk, user=request.user)

    if request.method == 'POST':
        title = task.task_title
        task.delete()
        messages.success(request, f"Task '{title}' has been successfully deleted.")
        return redirect('dashboard')

    context = {
        'task': task,
    }
    return render(request, 'tasks/task_confirm_delete.html', context)
