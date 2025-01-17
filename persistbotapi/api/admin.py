from django.contrib import admin
from .models import User, HubstaffTask, DailyUpdate, Feedback, Stats, Leave
from django.contrib.auth.hashers import make_password


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'telegram_user_id',
                    'is_on_leave', 'is_staff', 'is_active')
    list_filter = ('is_on_leave', 'is_staff', 'is_active')
    search_fields = ('username', 'email', 'telegram_user_id')
    ordering = ('username',)

    def save_model(self, request, obj, form, change):
        # Hash password if it's being set or changed
        if form.cleaned_data.get('password') and not obj.password.startswith('pbkdf2_'):
            obj.password = make_password(form.cleaned_data['password'])
        super().save_model(request, obj, form, change)


@admin.register(HubstaffTask)
class HubstaffTaskAdmin(admin.ModelAdmin):
    list_display = ('task_name', 'user', 'start_time', 'end_time')
    # list_filter = ('is_active', 'user')
    search_fields = ('task_name', 'user__username', 'user__email')
    ordering = ('-start_time',)


@admin.register(DailyUpdate)
class DailyUpdateAdmin(admin.ModelAdmin):
    list_display = ('user', 'update_message', 'submitted_at')
    list_filter = ('user',)
    search_fields = ('user__username', 'user__email', 'update_message')
    ordering = ('-submitted_at',)


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'submitted_at')
    list_filter = ('user',)
    search_fields = ('user__username', 'user__email', 'message')
    ordering = ('-submitted_at',)


@admin.register(Stats)
class StatsAdmin(admin.ModelAdmin):
    list_display = ('user', 'tasks_completed',
                    'total_time_spent', 'last_updated')
    search_fields = ('user__username',)
    list_filter = ('last_updated',)

    def tasks_completed(self, obj):
        return HubstaffTask.objects.filter(user=obj.user, is_active=False).count()
    tasks_completed.short_description = 'Completed Tasks'


@admin.register(Leave)
class LeaveAdmin(admin.ModelAdmin):
    list_display = ('user', 'leave_type', 'leave_date')
    list_filter = ('leave_type', 'leave_date')
    search_fields = ('user__username', 'leave_type')

    fieldsets = (
        (None, {
            'fields': ('user', 'leave_type', 'leave_date')
        }),
    )
