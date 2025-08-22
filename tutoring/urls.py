from django.urls import path
from .views import (
    SubjectListView,
    TutorListView,
    TutorDetailView,
    LessonRequestView,
    LessonRequestUpdateView
)

urlpatterns = [
    path('subjects/', SubjectListView.as_view(), name='subject-list'),
    path('tutors/', TutorListView.as_view(), name='tutor-list'),
    path('tutors/<int:pk>/', TutorDetailView.as_view(), name='tutor-detail'),
    path('lesson-requests/', LessonRequestView.as_view(), name='lesson-request-list-create'),
    path('lesson-requests/<int:pk>/', LessonRequestUpdateView.as_view(), name='lesson-request-update'),
]