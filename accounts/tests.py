from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()


class UserModelTests(TestCase):

    def test_create_jobseeker_user(self):
        user = User.objects.create_user(
            email="jobseeker@test.com",
            password="testpass123",
            role="JOB_SEEKER"
        )

        self.assertEqual(user.email, "jobseeker@test.com")
        self.assertEqual(user.role, "JOB_SEEKER")
        self.assertTrue(user.check_password("testpass123"))

    def test_create_employer_user(self):
        user = User.objects.create_user(
            email="employer@test.com",
            password="testpass123",
            role="EMPLOYER"
        )

        self.assertEqual(user.email, "employer@test.com")
        self.assertEqual(user.role, "EMPLOYER")
        self.assertTrue(user.check_password("testpass123"))


class JobSeekerDashboardTests(TestCase):
    def setUp(self):
        self.jobseeker_email = "dashboard@test.com"
        self.password = "pass12345"
        self.jobseeker = User.objects.create_user(
            email=self.jobseeker_email,
            password=self.password,
            role="JOB_SEEKER",
        )
        self.employer = User.objects.create_user(
            email="emp@test.com",
            password="pass12345",
            role="EMPLOYER",
        )

    def test_requires_login(self):
        url = reverse("jobseeker_dashboard")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)

    def test_jobseeker_with_profile_gets_200(self):
        self.client.login(email=self.jobseeker_email, password=self.password)
        url = reverse("jobseeker_dashboard")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_employer_redirects_to_select_role(self):
        self.client.login(email="emp@test.com", password="pass12345")
        url = reverse("jobseeker_dashboard")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/select-role/", response.url)
