from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.contrib.auth.hashers import make_password, check_password


class UserManager(BaseUserManager):
    use_in_migrations = True


class User(AbstractUser):
    email = models.EmailField(unique=True)
    telegram_user_id = models.CharField(max_length=255, null=True, blank=True)
    is_on_leave = models.BooleanField(default=False)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = UserManager()

    def save(self, *args, **kwargs):
        if self.password and not self.password.startswith('pbkdf2_'):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

    def validate_credentials_and_store_telegram_id(self, email, password, telegram_user_id):
        if self.email == email and check_password(password, self.password):
            self.telegram_user_id = telegram_user_id
            self.save()
            return True
        return False

    def __str__(self):
        return self.email


class HubstaffTask(models.Model):
    task_name = models.CharField(max_length=255)
    start_time = models.DateField()
    end_time = models.DateField()
    user = models.ForeignKey(User, related_name='tasks',
                             on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Task: {self.task_name} ({'Active' if self.is_active else 'Inactive'})"


class DailyUpdate(models.Model):
    user = models.ForeignKey(
        User, related_name='daily_updates', on_delete=models.CASCADE)
    update_message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Update by {self.user.username} at {self.submitted_at}"


class Feedback(models.Model):
    user = models.ForeignKey(
        User, related_name='feedbacks', on_delete=models.CASCADE)
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback from {self.user.username} at {self.submitted_at}"


class Leave(models.Model):
    LEAVE_TYPES = [
        ('sick', 'Sick Leave'),
        ('vacation', 'Vacation Leave'),
        ('personal', 'Personal Leave'),
    ]

    user = models.ForeignKey(
        User, related_name='leaves', on_delete=models.CASCADE)
    leave_type = models.CharField(max_length=10, choices=LEAVE_TYPES)
    leave_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.leave_type} on {self.leave_date}"


class Stats(models.Model):
    user = models.ForeignKey(User, related_name='stats',
                             on_delete=models.CASCADE)
    tasks_completed = models.IntegerField(default=0)
    total_time_spent = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.0)  # Time in hours
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Stats for {self.user.username} - Last Updated: {self.last_updated}"
