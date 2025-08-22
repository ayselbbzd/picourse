from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from accounts.models import StudentProfile, TutorProfile

User = get_user_model()


class AuthTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
    
    def test_user_registration_student(self):
        """Test student user registration"""
        data = {
            'email': 'student@test.com',
            'password': 'TestPass123!',
            'password_confirm': 'TestPass123!',
            'role': 'student',
            'first_name': 'Test',
            'last_name': 'Student'
        }
        
        response = self.client.post(reverse('register'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Check user was created
        user = User.objects.get(email='student@test.com')
        self.assertEqual(user.role, 'student')
        self.assertTrue(hasattr(user, 'student_profile'))
    
    def test_user_registration_tutor(self):
        """Test tutor user registration"""
        data = {
            'email': 'tutor@test.com',
            'password': 'TestPass123!',
            'password_confirm': 'TestPass123!',
            'role': 'tutor',
            'first_name': 'Test',
            'last_name': 'Tutor'
        }
        
        response = self.client.post(reverse('register'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Check user was created
        user = User.objects.get(email='tutor@test.com')
        self.assertEqual(user.role, 'tutor')
        self.assertTrue(hasattr(user, 'tutor_profile'))
    
    def test_user_login(self):
        """Test user login"""
        # Create user first
        user = User.objects.create_user(
            username='test@test.com',
            email='test@test.com',
            password='TestPass123!',
            role='student'
        )
        
        data = {
            'email': 'test@test.com',
            'password': 'TestPass123!'
        }
        
        response = self.client.post(reverse('login'), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
    
    def test_get_user_profile(self):
        """Test retrieving user profile"""
        user = User.objects.create_user(
            username='test@test.com',
            email='test@test.com',
            password='TestPass123!',
            role='student'
        )
        StudentProfile.objects.create(user=user, grade_level='10th')
        
        self.client.force_authenticate(user=user)
        response = self.client.get(reverse('me'))
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'test@test.com')
        self.assertEqual(response.data['role'], 'student')


# tests/test_permissions.py
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from tutoring.models import Subject, LessonRequest
from accounts.models import TutorProfile, StudentProfile

User = get_user_model()


class PermissionsTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        
        # Create student user
        self.student = User.objects.create_user(
            username='student@test.com',
            email='student@test.com',
            password='TestPass123!',
            role='student'
        )
        StudentProfile.objects.create(user=self.student)
        
        # Create tutor user
        self.tutor = User.objects.create_user(
            username='tutor@test.com',
            email='tutor@test.com',
            password='TestPass123!',
            role='tutor'
        )
        TutorProfile.objects.create(user=self.tutor)
        
        # Create subject
        self.subject = Subject.objects.create(name='Mathematics')
    
    def test_student_can_create_lesson_request(self):
        """Test that students can create lesson requests"""
        self.client.force_authenticate(user=self.student)
        
        data = {
            'tutor_id': self.tutor.id,
            'subject_id': self.subject.id,
            'start_time': '2025-08-25T10:00:00Z',
            'duration_minutes': 60,
            'note': 'Help with algebra'
        }
        
        response = self.client.post(reverse('lesson-request-create'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_tutor_cannot_create_lesson_request(self):
        """Test that tutors cannot create lesson requests"""
        self.client.force_authenticate(user=self.tutor)
        
        data = {
            'tutor_id': self.tutor.id,
            'subject_id': self.subject.id,
            'start_time': '2025-08-25T10:00:00Z',
            'duration_minutes': 60,
            'note': 'Help with algebra'
        }
        
        response = self.client.post(reverse('lesson-request-create'), data)
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def test_tutor_can_update_lesson_request(self):
        """Test that tutors can approve/reject their lesson requests"""
        # Create lesson request
        lesson_request = LessonRequest.objects.create(
            student=self.student,
            tutor=self.tutor,
            subject=self.subject,
            start_time='2025-08-25T10:00:00Z',
            duration_minutes=60
        )
        
        self.client.force_authenticate(user=self.tutor)
        
        data = {'status': 'approved'}
        response = self.client.patch(
            reverse('lesson-request-update', kwargs={'pk': lesson_request.id}),
            data
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_student_cannot_update_lesson_request(self):
        """Test that students cannot update lesson requests"""
        # Create lesson request
        lesson_request = LessonRequest.objects.create(
            student=self.student,
            tutor=self.tutor,
            subject=self.subject,
            start_time='2025-08-25T10:00:00Z',
            duration_minutes=60
        )
        
        self.client.force_authenticate(user=self.student)
        
        data = {'status': 'approved'}
        response = self.client.patch(
            reverse('lesson-request-update', kwargs={'pk': lesson_request.id}),
            data
        )
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)


# tests/test_lesson_flow.py
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from tutoring.models import Subject, LessonRequest
from accounts.models import TutorProfile, StudentProfile

User = get_user_model()


class LessonFlowTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        
        # Create student
        self.student = User.objects.create_user(
            username='student@test.com',
            email='student@test.com',
            password='TestPass123!',
            role='student'
        )
        StudentProfile.objects.create(user=self.student)
        
        # Create tutor
        self.tutor = User.objects.create_user(
            username='tutor@test.com',
            email='tutor@test.com',
            password='TestPass123!',
            role='tutor'
        )
        TutorProfile.objects.create(user=self.tutor)
        
        # Create subject
        self.subject = Subject.objects.create(name='Mathematics')
    
    def test_complete_lesson_request_flow(self):
        """Test the complete lesson request flow: create -> approve"""
        
        # Step 1: Student creates lesson request
        self.client.force_authenticate(user=self.student)
        
        create_data = {
            'tutor_id': self.tutor.id,
            'subject_id': self.subject.id,
            'start_time': '2025-08-25T10:00:00Z',
            'duration_minutes': 60,
            'note': 'Need help with calculus'
        }
        
        response = self.client.post(reverse('lesson-request-create'), create_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        lesson_request_id = response.data['id']
        
        # Step 2: Check that lesson request is pending
        lesson_request = LessonRequest.objects.get(id=lesson_request_id)
        self.assertEqual(lesson_request.status, 'pending')
        
        # Step 3: Tutor approves the lesson request
        self.client.force_authenticate(user=self.tutor)
        
        update_data = {'status': 'approved'}
        response = self.client.patch(
            reverse('lesson-request-update', kwargs={'pk': lesson_request_id}),
            update_data
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Step 4: Verify status changed
        lesson_request.refresh_from_db()
        self.assertEqual(lesson_request.status, 'approved')