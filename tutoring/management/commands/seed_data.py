from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from tutoring.models import Subject, LessonRequest
from accounts.models import TutorProfile, StudentProfile
from datetime import timedelta
from django.utils import timezone

User = get_user_model()


class Command(BaseCommand):
    help = 'Create sample data for Pi Course project'
    
    def handle(self, *args, **options):
        self.stdout.write('Creating seed data...')
        
        # Create subjects
        subjects_data = ['Mathematics', 'Physics', 'Chemistry', 'Biology', 'English']
        subjects = []
        
        for subject_name in subjects_data:
            subject, created = Subject.objects.get_or_create(name=subject_name)
            subjects.append(subject)
            if created:
                self.stdout.write(f'Created subject: {subject_name}')
        
        # Create demo students
        students_data = [
            {
                'email': 'student@demo.com',
                'password': 'DemoPass123!',
                'first_name': 'Ali',
                'last_name': 'Yılmaz',
                'grade_level': '11th Grade'
            },
            {
                'email': 'student2@demo.com',
                'password': 'DemoPass123!',
                'first_name': 'Ayşe',
                'last_name': 'Kaya',
                'grade_level': '12th Grade'
            }
        ]
        
        for student_data in students_data:
            email = student_data['email']
            if not User.objects.filter(email=email).exists():
                user = User.objects.create_user(
                    username=email,
                    email=email,
                    password=student_data['password'],
                    first_name=student_data['first_name'],
                    last_name=student_data['last_name'],
                    role='student'
                )
                StudentProfile.objects.create(
                    user=user,
                    grade_level=student_data['grade_level']
                )
                self.stdout.write(f'Created student: {email}')
        
        # Create demo tutors
        tutors_data = [
            {
                'email': 'tutor@demo.com',
                'password': 'DemoPass123!',
                'first_name': 'Dr. Mehmet',
                'last_name': 'Özkan',
                'bio': 'Mathematics PhD from ODTU. 10+ years teaching experience.',
                'hourly_rate': 500.00,
                'rating': 4.8,
                'subjects': ['Mathematics', 'Physics']
            },
            {
                'email': 'tutor2@demo.com',
                'password': 'DemoPass123!',
                'first_name': 'Dr. Fatma',
                'last_name': 'Demir',
                'bio': 'Physics PhD from ITU. Expert in quantum mechanics.',
                'hourly_rate': 600.00,
                'rating': 4.9,
                'subjects': ['Physics', 'Mathematics']
            },
            {
                'email': 'tutor3@demo.com',
                'password': 'DemoPass123!',
                'first_name': 'Prof. Ahmet',
                'last_name': 'Yıldız',
                'bio': 'Chemistry professor with 15+ years experience.',
                'hourly_rate': 550.00,
                'rating': 4.7,
                'subjects': ['Chemistry', 'Biology']
            },
            {
                'email': 'tutor4@demo.com',
                'password': 'DemoPass123!',
                'first_name': 'Zeynep',
                'last_name': 'Arslan',
                'bio': 'English Literature graduate, CELTA certified.',
                'hourly_rate': 400.00,
                'rating': 4.6,
                'subjects': ['English']
            },
            {
                'email': 'tutor5@demo.com',
                'password': 'DemoPass123!',
                'first_name': 'Dr. Can',
                'last_name': 'Şahin',
                'bio': 'Biology PhD, specializing in molecular biology.',
                'hourly_rate': 520.00,
                'rating': 4.5,
                'subjects': ['Biology', 'Chemistry']
            }
        ]
        
        for tutor_data in tutors_data:
            email = tutor_data['email']
            if not User.objects.filter(email=email).exists():
                user = User.objects.create_user(
                    username=email,
                    email=email,
                    password=tutor_data['password'],
                    first_name=tutor_data['first_name'],
                    last_name=tutor_data['last_name'],
                    role='tutor'
                )
                
                tutor_profile = TutorProfile.objects.create(
                    user=user,
                    bio=tutor_data['bio'],
                    hourly_rate=tutor_data['hourly_rate'],
                    rating=tutor_data['rating']
                )
                
                # Add subjects to tutor
                tutor_subjects = Subject.objects.filter(name__in=tutor_data['subjects'])
                tutor_profile.subjects.set(tutor_subjects)
                
                self.stdout.write(f'Created tutor: {email}')
        
        # Create some sample lesson requests
        students = User.objects.filter(role='student')
        tutors = User.objects.filter(role='tutor')
        
        if students.exists() and tutors.exists():
            student = students.first()
            tutor = tutors.first()
            math_subject = Subject.objects.filter(name='Mathematics').first()
            
            if math_subject and not LessonRequest.objects.filter(student=student).exists():
                LessonRequest.objects.create(
                    student=student,
                    tutor=tutor,
                    subject=math_subject,
                    start_time=timezone.now() + timedelta(days=3),
                    duration_minutes=60,
                    note='Need help with calculus',
                    status='pending'
                )
                self.stdout.write('Created sample lesson request')
        
        self.stdout.write(self.style.SUCCESS('Seed data created successfully!'))
        self.stdout.write('Demo accounts:')
        self.stdout.write('  Student: student@demo.com / DemoPass123!')
        self.stdout.write('  Student: student2@demo.com / DemoPass123!')
        self.stdout.write('  Tutor: tutor@demo.com / DemoPass123!')
        self.stdout.write('  Tutor: tutor2@demo.com / DemoPass123!')