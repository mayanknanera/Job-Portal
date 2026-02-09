from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()


class UserModelTests(TestCase):

    def test_create_jobseeker_user(self):
        """
        Ensure a JOB_SEEKER user is created correctly
        and password hashing works.
        """
        user = User.objects.create_user(
            email="jobseeker@test.com",
            password="testpass123",
            role="JOB_SEEKER"
        )

        self.assertEqual(user.email, "jobseeker@test.com")
        self.assertEqual(user.role, "JOB_SEEKER")
        self.assertTrue(user.check_password("testpass123"))

    def test_create_employer_user(self):
        """
        Ensure an EMPLOYER user is created correctly.
        """
        user = User.objects.create_user(
            email="employer@test.com",
            password="testpass123",
            role="EMPLOYER"
        )

        self.assertEqual(user.email, "employer@test.com")
        self.assertEqual(user.role, "EMPLOYER")
        self.assertTrue(user.check_password("testpass123"))