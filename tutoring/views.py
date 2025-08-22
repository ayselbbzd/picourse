from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import get_user_model
from django.db.models import Q
from .models import Subject, LessonRequest
from accounts.models import TutorProfile
from .serializers import (
    SubjectSerializer,
    TutorListSerializer,
    TutorDetailSerializer,
    LessonRequestCreateSerializer,
    LessonRequestSerializer,
    LessonRequestUpdateSerializer
)

User = get_user_model()


class SubjectListView(generics.ListAPIView):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    permission_classes = [AllowAny]


class TutorListView(generics.ListAPIView):
    serializer_class = TutorListSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        queryset = TutorProfile.objects.select_related('user').prefetch_related('subjects')
        
        # Filter by subject
        subject_id = self.request.query_params.get('subject')
        if subject_id:
            queryset = queryset.filter(subjects__id=subject_id)
        
        # Search in name and bio
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(user__first_name__icontains=search) |
                Q(user__last_name__icontains=search) |
                Q(bio__icontains=search)
            )
        
        # Ordering
        ordering = self.request.query_params.get('ordering', '-rating')
        if ordering in ['rating', '-rating', 'hourly_rate', '-hourly_rate']:
            queryset = queryset.order_by(ordering)
        
        return queryset.distinct()


class TutorDetailView(generics.RetrieveAPIView):
    queryset = TutorProfile.objects.select_related('user').prefetch_related('subjects')
    serializer_class = TutorDetailSerializer
    permission_classes = [AllowAny]


class LessonRequestView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return LessonRequestCreateSerializer
        return LessonRequestSerializer
    
    def get_queryset(self):
        user = self.request.user
        role = self.request.query_params.get('role', user.role)
        status_filter = self.request.query_params.get('status')
        
        # Get requests based on user role
        if role == 'student':
            queryset = LessonRequest.objects.filter(student=user)
        elif role == 'tutor':
            queryset = LessonRequest.objects.filter(tutor=user)
        else:
            # Fallback: show user's own requests based on their actual role
            if user.role == 'student':
                queryset = LessonRequest.objects.filter(student=user)
            else:
                queryset = LessonRequest.objects.filter(tutor=user)
        
        # Filter by status
        if status_filter and status_filter in ['pending', 'approved', 'rejected']:
            queryset = queryset.filter(status=status_filter)
        
        return queryset.select_related('student', 'tutor', 'subject')
    
    def perform_create(self, serializer):
        # Ensure only students can create lesson requests
        if self.request.user.role != 'student':
            raise PermissionError("Only students can create lesson requests")
        serializer.save()


class LessonRequestUpdateView(generics.UpdateAPIView):
    serializer_class = LessonRequestUpdateSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Only tutors can update lesson requests, and only their own
        return LessonRequest.objects.filter(tutor=self.request.user)
    
    def perform_update(self, serializer):
        # Ensure only tutors can update lesson requests
        if self.request.user.role != 'tutor':
            raise PermissionError("Only tutors can update lesson requests")
        
        lesson_request = self.get_object()
        if lesson_request.tutor != self.request.user:
            raise PermissionError("You can only update your own lesson requests")
        
        serializer.save()