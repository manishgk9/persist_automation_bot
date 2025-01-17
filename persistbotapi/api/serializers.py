from rest_framework import serializers
from .models import User, HubstaffTask, DailyUpdate, Feedback, Stats, Leave
from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)
    telegram_user_id = serializers.CharField(required=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        telegram_user_id = data.get('telegram_user_id')

        user = User.objects.filter(email=email).first()

        if not user:
            raise serializers.ValidationError("User not found.")

        if not user.validate_credentials_and_store_telegram_id(email, password, telegram_user_id):
            raise serializers.ValidationError("Invalid credentials.")

        return data


class HubstaffTaskSerializer(serializers.ModelSerializer):
    telegram_user_id = serializers.CharField(write_only=True, required=True)
    task_name = serializers.CharField(required=True)
    start_time = serializers.DateField(required=True)
    end_time = serializers.DateField(required=True)

    class Meta:
        model = HubstaffTask
        fields = ['telegram_user_id', 'task_name',
                  'start_time', 'end_time']

    def create(self, validated_data):
        telegram_user_id = validated_data['telegram_user_id']
        task_name = validated_data['task_name']
        start_time = validated_data['start_time']
        end_time = validated_data['end_time']
        try:
            user = User.objects.get(telegram_user_id=telegram_user_id)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                "User with the given Telegram ID not found.")
        hubstaff_task = HubstaffTask.objects.create(
            user=user,
            task_name=task_name,
            start_time=start_time,
            end_time=end_time,
        )
        return hubstaff_task


class DailyUpdateSerializer(serializers.Serializer):
    telegram_user_id = serializers.CharField(required=True)
    update_message = serializers.CharField(required=True)

    def validate_telegram_user_id(self, value):
        try:
            user = User.objects.get(telegram_user_id=value)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                "User not found with the provided Telegram ID.")
        return user

    def create(self, validated_data):
        user = validated_data['telegram_user_id']
        update_message = validated_data['update_message']
        daily_update = DailyUpdate.objects.create(
            user=user,
            update_message=update_message
        )
        return daily_update


class FeedbackSerializer(serializers.ModelSerializer):
    telegram_user_id = serializers.CharField(write_only=True, required=True)
    message = serializers.CharField(required=True)

    class Meta:
        model = Feedback
        fields = ['telegram_user_id', 'message']

    def create(self, validated_data):
        telegram_user_id = validated_data['telegram_user_id']
        message = validated_data['message']

        # Fetch the user using the telegram_user_id
        try:
            user = User.objects.get(telegram_user_id=telegram_user_id)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                "User with the given Telegram ID not found.")

        # Create and return the feedback
        feedback = Feedback.objects.create(user=user, message=message)
        return feedback


class StatsSerializer(serializers.ModelSerializer):
    task_names = serializers.SerializerMethodField()

    class Meta:
        model = Stats
        fields = ['tasks_completed',
                  'total_time_spent', 'last_updated', 'task_names']

    def get_task_names(self, obj):
        # Fetch the tasks for the user linked to the Stats object
        tasks = HubstaffTask.objects.filter(user=obj.user)
        task_names = [task.task_name for task in tasks]
        return task_names

    def get_tasks_completed(self, obj):
        # Count completed tasks for the user
        return HubstaffTask.objects.filter(user=obj.user, is_active=False).count()


class LeaveSerializer(serializers.ModelSerializer):
    telegram_user_id = serializers.CharField(write_only=True, required=True)
    leave_type = serializers.ChoiceField(
        choices=Leave.LEAVE_TYPES, required=True)
    # leave_date = serializers.DateField()

    class Meta:
        model = Leave
        fields = ['telegram_user_id', 'leave_type']

    def create(self, validated_data):
        telegram_user_id = validated_data.pop('telegram_user_id')

        try:
            user = User.objects.get(telegram_user_id=telegram_user_id)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                "User with the given telegram_user_id does not exist.")
        leave = Leave.objects.create(user=user, **validated_data)
        return leave
