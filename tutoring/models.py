from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Subject(models.Model):
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']


class LessonRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    student = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='student_lesson_requests'
    )
    tutor = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='tutor_lesson_requests'
    )
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    duration_minutes = models.PositiveIntegerField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Lesson Request: {self.student.email} -> {self.tutor.email} ({self.subject.name})"
    
    class Meta:
        ordering = ['-created_at']