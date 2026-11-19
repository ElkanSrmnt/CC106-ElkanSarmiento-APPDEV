from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from .models import Student


class StaffAuthenticationTests(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user(
            username='staff_test',
            password='TestPass123!',
            is_staff=True,
        )
        self.normal_user = User.objects.create_user(
            username='student_test',
            password='TestPass123!',
            is_staff=False,
        )

    def test_login_page_is_public(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Staff Login')

    def test_staff_login_always_redirects_to_dashboard(self):
        response = self.client.post(
            reverse('login'),
            {
                'username': 'staff_test',
                'password': 'TestPass123!',
                'next': reverse('student_list'),
            },
        )
        self.assertRedirects(response, reverse('staff_dashboard'))

    def test_anonymous_user_is_redirected_to_login(self):
        response = self.client.get(reverse('student_list'))
        self.assertRedirects(
            response,
            f"{reverse('login')}?next={reverse('student_list')}",
        )

    def test_student_directory_ignores_search_query(self):
        self.client.login(username='staff_test', password='TestPass123!')
        Student.objects.create(
            student_id='SRCC-TEST-001',
            first_name='Alex',
            last_name='Santos',
            gender='Male',
            date_of_birth='2004-02-15',
            contact_no='09170000001',
        )
        Student.objects.create(
            student_id='SRCC-TEST-002',
            first_name='Jamie',
            last_name='Reyes',
            gender='Female',
            date_of_birth='2003-11-08',
            contact_no='09170000002',
        )

        response = self.client.get(reverse('student_list'), {'q': 'not found'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Alex Santos')
        self.assertContains(response, 'Jamie Reyes')
        self.assertNotContains(response, 'Search student')

    def test_staff_user_can_open_dashboard(self):
        self.client.login(username='staff_test', password='TestPass123!')
        response = self.client.get(reverse('staff_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'staff_test')

    def test_non_staff_user_cannot_open_dashboard(self):
        self.client.login(username='student_test', password='TestPass123!')
        response = self.client.get(reverse('staff_dashboard'))
        self.assertRedirects(
            response,
            f"{reverse('login')}?next={reverse('staff_dashboard')}",
        )

    def test_anonymous_user_is_redirected_from_registration_pages(self):
        for view_name in ('student_registration', 'registration_success'):
            with self.subTest(view_name=view_name):
                response = self.client.get(reverse(view_name))
                self.assertRedirects(
                    response,
                    f"{reverse('login')}?next={reverse(view_name)}",
                )

    def test_home_registration_route_is_public(self):
        response = self.client.get(reverse('public_student_registration'))
        self.assertEqual(response.status_code, 200)

    def test_public_registration_submission_reaches_public_success_page(self):
        response = self.client.post(
            reverse('public_student_registration'),
            {
                'student_id': 'SRCC-PUBLIC-001',
                'first_name': 'Alex',
                'last_name': 'Santos',
                'gender': 'Male',
                'date_of_birth': '2004-02-15',
                'contact_no': '09170000001',
            },
        )
        self.assertRedirects(
            response,
            reverse('public_registration_success'),
        )
        self.assertTrue(
            Student.objects.filter(student_id='SRCC-PUBLIC-001').exists()
        )

    def test_staff_user_can_open_registration_pages(self):
        self.client.login(username='staff_test', password='TestPass123!')
        for view_name in ('student_registration', 'registration_success'):
            with self.subTest(view_name=view_name):
                response = self.client.get(reverse(view_name))
                self.assertEqual(response.status_code, 200)
