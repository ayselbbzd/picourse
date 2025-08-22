from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Subject, LessonRequest
from accounts.models import TutorProfile

User = get_user_model()


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['id', 'name']


class TutorListSerializer(serializers.ModelSerializer):
    name = serializers.CharField(read_only=True)
    subjects = SubjectSerializer(many=True, read_only=True)
    
    class Meta:
        model = TutorProfile
        fields = ['id', 'name', 'bio', 'hourly_rate', 'rating', 'subjects']


class TutorDetailSerializer(serializers.ModelSerializer):
    name = serializers.CharField(read_only=True)
    subjects = SubjectSerializer(many=True, read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    
    class Meta:
        model = TutorProfile
        fields = [
            'id', 'name', 'email', 'first_name', 'last_name', 
            'bio', 'hourly_rate', 'rating', 'subjects'
        ]


class LessonRequestCreateSerializer(serializers.ModelSerializer):
    tutor_id = serializers.IntegerField(write_only=True)
    subject_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = LessonRequest
        fields = ['tutor_id', 'subject_id', 'start_time', 'duration_minutes', 'note']
    
    def validate_tutor_id(self, value):
        try:
            tutor = User.objects.get(id=value, role='tutor')
            return value
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid tutor ID")
    
    def validate_subject_id(self, value):
        try:
            Subject.objects.get(id=value)
            return value
        except Subject.DoesNotExist:
            raise serializers.ValidationError("Invalid subject ID")
    
    def create(self, validated_data):
        tutor_id = validated_data.pop('tutor_id')
        subject_id = validated_data.pop('subject_id')
        
        lesson_request = LessonRequest.objects.create(
            student=self.context['request'].user,
            tutor_id=tutor_id,
            subject_id=subject_id,
            **validated_data
        )
        return lesson_request


class LessonRequestSerializer(serializers.ModelSerializer):
    student_email = serializers.CharField(source='student.email', read_only=True)
    tutor_email = serializers.CharField(source='tutor.email', read_only=True)
    tutor_name = serializers.SerializerMethodField()
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    
    class Meta:
        model = LessonRequest
        fields = [
            'id', 'student_email', 'tutor_email', 'tutor_name', 'subject_name',
            'start_time', 'duration_minutes', 'status', 'note', 'created_at'
        ]
        read_only_fields = ['id', 'student_email', 'tutor_email', 'tutor_name', 'subject_name', 'created_at']
    
    def get_tutor_name(self, obj):
        if hasattr(obj.tutor, 'tutor_profile'):
            return obj.tutor.tutor_profile.name
        return obj.tutor.email


class LessonRequestUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = LessonRequest
        fields = ['status']
    
    def validate_status(self, value):
        if value not in ['approved', 'rejected']:
            raise serializers.ValidationError("Status can only be 'approved' or 'rejected'")
        return value