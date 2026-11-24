import datetime
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Task
from .forms import TaskForm

class TaskModelTest(TestCase):
    """Unit tests for the Task database model."""

    def setUp(self):
        self.task = Task.objects.create(
            name="Alice Smith",
            date=datetime.date(2026, 11, 25),
            task_title="Complete Project Milestone",
            description="Finalize the architecture and complete all deliverables."
        )

    def test_task_creation_and_fields(self):
        """Verify Task fields are correctly stored and retrieved."""
        self.assertEqual(self.task.name, "Alice Smith")
        self.assertEqual(self.task.date, datetime.date(2026, 11, 25))
        self.assertEqual(self.task.task_title, "Complete Project Milestone")
        self.assertEqual(self.task.description, "Finalize the architecture and complete all deliverables.")
        self.assertIsNotNone(self.task.created_at)
        self.assertIsNotNone(self.task.updated_at)

    def test_task_string_representation(self):
        """Verify __str__ returns 'task_title (name)'."""
        expected_str = "Complete Project Milestone (Alice Smith)"
        self.assertEqual(str(self.task), expected_str)


class TaskFormTest(TestCase):
    """Unit tests for the TaskForm validating the 4 required fields."""

    def test_valid_form(self):
        """Form is valid when all four fields are properly provided."""
        data = {
            'name': 'Bob Davis',
            'date': '2026-12-01',
            'task_title': 'Quarterly Financial Review',
            'description': 'Review all revenue forecasts and balance sheets.'
        }
        form = TaskForm(data=data)
        self.assertTrue(form.is_valid())

    def test_missing_name_invalid(self):
        """Form is invalid if name is missing or blank."""
        data = {
            'name': '   ',
            'date': '2026-12-01',
            'task_title': 'Valid Title',
            'description': 'Valid Description'
        }
        form = TaskForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)

    def test_missing_task_title_invalid(self):
        """Form is invalid if task_title is missing."""
        data = {
            'name': 'Valid Name',
            'date': '2026-12-01',
            'task_title': '',
            'description': 'Valid Description'
        }
        form = TaskForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('task_title', form.errors)

    def test_missing_date_invalid(self):
        """Form is invalid if date is missing."""
        data = {
            'name': 'Valid Name',
            'date': '',
            'task_title': 'Valid Title',
            'description': 'Valid Description'
        }
        form = TaskForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('date', form.errors)

    def test_missing_description_invalid(self):
        """Form is invalid if description is missing."""
        data = {
            'name': 'Valid Name',
            'date': '2026-12-01',
            'task_title': 'Valid Title',
            'description': ''
        }
        form = TaskForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('description', form.errors)


class TaskWebViewsTest(TestCase):
    """Tests for the frontend HTML views (CRUD, search, filters, auth)."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.client.login(username='testuser', password='password123')
        self.task1 = Task.objects.create(
            user=self.user,
            name="Charlie Brown",
            date=datetime.date(2026, 11, 23),
            task_title="Design System Implementation",
            description="Build tokenized styling components."
        )
        self.task2 = Task.objects.create(
            user=self.user,
            name="Diana Prince",
            date=datetime.date(2026, 11, 30),
            task_title="Database Backup Strategy",
            description="Establish automated snapshot procedures."
        )

    def test_unauthenticated_user_redirected_to_login(self):
        """Unauthenticated user trying to access dashboard is redirected to login."""
        self.client.logout()
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response.url)

    def test_user_isolation(self):
        """User A cannot see or edit User B's tasks."""
        other_user = User.objects.create_user(username='otheruser', password='password123')
        other_task = Task.objects.create(
            user=other_user,
            name="Other Person",
            date=datetime.date(2026, 11, 28),
            task_title="Confidential Task",
            description="This belongs to otheruser only."
        )
        # testuser visits dashboard
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Confidential Task")

        # testuser attempts to edit other_task -> 404
        edit_response = self.client.get(reverse('task_update', kwargs={'pk': other_task.pk}))
        self.assertEqual(edit_response.status_code, 404)

        # testuser attempts to delete other_task -> 404
        del_response = self.client.post(reverse('task_delete', kwargs={'pk': other_task.pk}))
        self.assertEqual(del_response.status_code, 404)

    def test_user_registration(self):
        """New user registers, is redirected to login page, password is encrypted in database."""
        self.client.logout()
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'ComplexPassword123!',
            'password2': 'ComplexPassword123!'
        }
        response = self.client.post(reverse('register'), data=data)
        self.assertRedirects(response, reverse('login'))
        
        user = User.objects.get(username='newuser')
        self.assertEqual(user.email, 'newuser@example.com')
        # Verify password is encrypted
        self.assertNotEqual(user.password, 'ComplexPassword123!')
        self.assertTrue(user.password.startswith('pbkdf2_sha256$'))

    def test_unregistered_user_login_shows_register_first_message(self):
        """Attempting to log in without registering prompts user to register first."""
        self.client.logout()
        response = self.client.post(reverse('login'), data={
            'username': 'nonexistentuser',
            'password': 'anyPassword123'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Please register first")

    def test_user_login_and_logout(self):
        """User can log in and log out."""
        self.client.logout()
        response = self.client.post(reverse('login'), data={
            'username': 'testuser',
            'password': 'password123'
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Welcome back, testuser!")

        logout_response = self.client.get(reverse('logout'), follow=True)
        self.assertEqual(logout_response.status_code, 200)
        self.assertContains(logout_response, "You have been logged out successfully.")

    def test_dashboard_view_loads_successfully(self):
        """Dashboard renders with 200 OK and contains existing tasks."""
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Design System Implementation")
        self.assertContains(response, "Database Backup Strategy")
        self.assertEqual(response.context['total_count'], 2)

    def test_dashboard_search_by_title(self):
        """Search query filters tasks by title."""
        response = self.client.get(reverse('dashboard'), {'q': 'Design'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Design System Implementation")
        self.assertNotContains(response, "Database Backup Strategy")

    def test_dashboard_search_by_name(self):
        """Search query filters tasks by name."""
        response = self.client.get(reverse('dashboard'), {'q': 'Diana'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Database Backup Strategy")
        self.assertNotContains(response, "Design System Implementation")

    def test_dashboard_filter_by_date(self):
        """Date parameter filters tasks by date."""
        response = self.client.get(reverse('dashboard'), {'date': '2026-11-23'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Design System Implementation")
        self.assertNotContains(response, "Database Backup Strategy")

    def test_create_task_get(self):
        """GET create task returns form page."""
        response = self.client.get(reverse('task_create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tasks/task_form.html')

    def test_create_task_post_valid(self):
        """POST valid task data saves to database and redirects to dashboard."""
        data = {
            'name': 'Evan Wright',
            'date': '2026-12-05',
            'task_title': 'Setup CI/CD Pipeline',
            'description': 'Configure automated testing and deployment.'
        }
        response = self.client.post(reverse('task_create'), data=data)
        self.assertRedirects(response, reverse('dashboard'))
        self.assertTrue(Task.objects.filter(task_title='Setup CI/CD Pipeline').exists())

    def test_create_task_post_invalid(self):
        """POST invalid data does not save and returns form with errors."""
        data = {'name': '', 'date': '', 'task_title': '', 'description': ''}
        response = self.client.post(reverse('task_create'), data=data)
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response.context['form'], 'name', 'Name is required and cannot be blank.')

    def test_update_task_get(self):
        """GET update task pre-fills the form with existing task data."""
        response = self.client.get(reverse('task_update', kwargs={'pk': self.task1.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.task1.task_title)
        self.assertContains(response, self.task1.name)

    def test_update_task_post_valid(self):
        """POST updated task data modifies record in database."""
        data = {
            'name': 'Charlie Brown',
            'date': '2026-11-24',
            'task_title': 'Design System - Updated',
            'description': 'Updated component descriptions.'
        }
        response = self.client.post(reverse('task_update', kwargs={'pk': self.task1.pk}), data=data)
        self.assertRedirects(response, reverse('dashboard'))
        self.task1.refresh_from_db()
        self.assertEqual(self.task1.task_title, 'Design System - Updated')
        self.assertEqual(self.task1.date, datetime.date(2026, 11, 24))

    def test_delete_task_get(self):
        """GET delete task displays confirmation page."""
        response = self.client.get(reverse('task_delete', kwargs={'pk': self.task1.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tasks/task_confirm_delete.html')
        self.assertContains(response, self.task1.task_title)

    def test_delete_task_post(self):
        """POST delete task removes record from database and redirects."""
        task_id = self.task1.pk
        response = self.client.post(reverse('task_delete', kwargs={'pk': task_id}))
        self.assertRedirects(response, reverse('dashboard'))
        self.assertFalse(Task.objects.filter(pk=task_id).exists())

    def test_invalid_task_id_404(self):
        """Accessing non-existent task ID returns 404."""
        response = self.client.get(reverse('task_update', kwargs={'pk': 99999}))
        self.assertEqual(response.status_code, 404)
        response = self.client.get(reverse('task_delete', kwargs={'pk': 99999}))
        self.assertEqual(response.status_code, 404)

    def test_export_tasks_csv(self):
        """Export CSV returns 200 with formatted CSV attachment."""
        response = self.client.get(reverse('export_csv'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv; charset=utf-8')
        self.assertIn('attachment; filename="taskflow_tasks_testuser_', response['Content-Disposition'])
        content = response.content.decode('utf-8')
        self.assertIn("Task ID,Task Title,Assignee Name", content)
        self.assertIn("Design System Implementation", content)

    def test_export_tasks_pdf(self):
        """Export PDF returns 200 with valid binary PDF attachment."""
        response = self.client.get(reverse('export_pdf'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertIn('attachment; filename="taskflow_report_testuser_', response['Content-Disposition'])
        self.assertTrue(len(response.content) > 1000)
        self.assertTrue(response.content.startswith(b'%PDF'))

    def test_export_unauthenticated_redirects(self):
        """Unauthenticated requests to export endpoints are redirected to login."""
        self.client.logout()
        csv_resp = self.client.get(reverse('export_csv'))
        self.assertEqual(csv_resp.status_code, 302)
        pdf_resp = self.client.get(reverse('export_pdf'))
        self.assertEqual(pdf_resp.status_code, 302)


class TaskAPITestCase(APITestCase):
    """
    Tests for DRF REST API endpoints:
    GET    /api/tasks/        (List all tasks)
    POST   /api/tasks/        (Create new task)
    GET    /api/tasks/<id>/   (Retrieve single task)
    PUT    /api/tasks/<id>/   (Fully update an existing task)
    PATCH  /api/tasks/<id>/   (Partially update an existing task)
    DELETE /api/tasks/<id>/   (Delete an existing task)
    """

    def setUp(self):
        self.user = User.objects.create_user(username='apiuser', password='password123')
        self.client.force_authenticate(user=self.user)
        self.task = Task.objects.create(
            user=self.user,
            name="Fiona Gallagher",
            date=datetime.date(2026, 12, 10),
            task_title="Audit Security Compliance",
            description="Verify SSL certificates, CORS, and vulnerability patches."
        )
        self.list_url = '/api/tasks/'
        self.detail_url = f'/api/tasks/{self.task.id}/'

    def test_api_list_tasks(self):
        """GET /api/tasks/ returns 200 OK and list containing the task."""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) >= 1)
        self.assertEqual(response.data[0]['task_title'], self.task.task_title)

    def test_api_retrieve_single_task(self):
        """GET /api/tasks/<id>/ returns 200 OK with accurate serialized task."""
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.task.id)
        self.assertEqual(response.data['name'], "Fiona Gallagher")
        self.assertEqual(response.data['date'], "2026-12-10")
        self.assertEqual(response.data['task_title'], "Audit Security Compliance")

    def test_api_retrieve_nonexistent_task(self):
        """GET /api/tasks/99999/ returns 404 Not Found."""
        response = self.client.get('/api/tasks/99999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_api_create_task_success(self):
        """POST /api/tasks/ creates task and returns 201 Created."""
        payload = {
            'name': 'George Clark',
            'date': '2026-12-15',
            'task_title': 'API Gateway Integration',
            'description': 'Configure route mappings and rate limiting.'
        }
        response = self.client.post(self.list_url, data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['task_title'], 'API Gateway Integration')
        self.assertTrue(Task.objects.filter(task_title='API Gateway Integration').exists())

    def test_api_create_task_missing_fields(self):
        """POST /api/tasks/ with missing required fields returns 400 Bad Request."""
        payload = {
            'name': 'Incomplete Task'
            # Missing date, task_title, description
        }
        response = self.client.post(self.list_url, data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('task_title', response.data)
        self.assertIn('date', response.data)
        self.assertIn('description', response.data)

    def test_api_put_full_update(self):
        """PUT /api/tasks/<id>/ fully updates all fields and returns 200 OK."""
        payload = {
            'name': 'Fiona Gallagher Updated',
            'date': '2026-12-20',
            'task_title': 'Audit Security Compliance v2',
            'description': 'Comprehensive security audit with revised checklist.'
        }
        response = self.client.put(self.detail_url, data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task.refresh_from_db()
        self.assertEqual(self.task.name, 'Fiona Gallagher Updated')
        self.assertEqual(self.task.task_title, 'Audit Security Compliance v2')
        self.assertEqual(self.task.date, datetime.date(2026, 12, 20))

    def test_api_put_missing_field_fails(self):
        """PUT /api/tasks/<id>/ fails with 400 if a required field is omitted."""
        payload = {
            'name': 'Only Name Provided'
            # Missing date, task_title, description
        }
        response = self.client.put(self.detail_url, data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_api_patch_partial_update(self):
        """PATCH /api/tasks/<id>/ allows updating a single field without affecting others."""
        payload = {
            'task_title': 'Partially Updated Title Only'
        }
        response = self.client.patch(self.detail_url, data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task.refresh_from_db()
        self.assertEqual(self.task.task_title, 'Partially Updated Title Only')
        # Ensure other fields remained intact
        self.assertEqual(self.task.name, 'Fiona Gallagher')
        self.assertEqual(self.task.date, datetime.date(2026, 12, 10))

    def test_api_delete_task(self):
        """DELETE /api/tasks/<id>/ removes task and returns 204 No Content."""
        task_id = self.task.id
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Task.objects.filter(id=task_id).exists())

        # Successive retrieval yields 404
        get_response = self.client.get(self.detail_url)
        self.assertEqual(get_response.status_code, status.HTTP_404_NOT_FOUND)
