from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import StudentProfile, TutorProfile
from tutoring.models import Subject

User = get_user_model()


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['id', 'name']


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['email', 'password', 'password_confirm', 'role', 'first_name', 'last_name']
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        
        # Set username to email for compatibility
        validated_data['username'] = validated_data['email']
        
        user = User.objects.create_user(password=password, **validated_data)
        
        # Create corresponding profile based on role
        if user.role == 'student':
            StudentProfile.objects.create(user=user)
        elif user.role == 'tutor':
            TutorProfile.objects.create(user=user)
        
        return user


class StudentProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentProfile
        fields = ['grade_level']


class TutorProfileSerializer(serializers.ModelSerializer):
    subjects = SubjectSerializer(many=True, read_only=True)
    name = serializers.CharField(read_only=True)
    
    class Meta:
        model = TutorProfile
        fields = ['bio', 'hourly_rate', 'rating', 'subjects', 'name']


class UserProfileSerializer(serializers.ModelSerializer):
    student_profile = StudentProfileSerializer(read_only=True)
    tutor_profile = TutorProfileSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'role', 'student_profile', 'tutor_profile']
        read_only_fields = ['id', 'email', 'role']


class ProfileUpdateSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=150, required=False)
    last_name = serializers.CharField(max_length=150, required=False)
    
    # Student fields
    grade_level = serializers.CharField(max_length=50, required=False, allow_blank=True)
    
    # Tutor fields
    bio = serializers.CharField(required=False, allow_blank=True)
    hourly_rate = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    subject_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=True
    )
    
    def update(self, instance, validated_data):
        # Update user fields
        if 'first_name' in validated_data:
            instance.first_name = validated_data['first_name']
        if 'last_name' in validated_data:
            instance.last_name = validated_data['last_name']
        instance.save()
        
        # Update profile based on role
        if instance.role == 'student' and hasattr(instance, 'student_profile'):
            profile = instance.student_profile
            if 'grade_level' in validated_data:
                profile.grade_level = validated_data['grade_level']
                profile.save()
        
        elif instance.role == 'tutor' and hasattr(instance, 'tutor_profile'):
            profile = instance.tutor_profile
            if 'bio' in validated_data:
                profile.bio = validated_data['bio']
            if 'hourly_rate' in validated_data:
                profile.hourly_rate = validated_data['hourly_rate']
            
            if 'subject_ids' in validated_data:
                subjects = Subject.objects.filter(id__in=validated_data['subject_ids'])
                profile.subjects.set(subjects)
            
            profile.save()
        
        return instance