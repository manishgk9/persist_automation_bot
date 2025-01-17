from django.urls import path
from .views import *

urlpatterns = [
    path('', StartView.as_view(), name='start'),
    path('check-user/', CheckTelegramUserView.as_view(),
         name='check-user'),

    path('hubstaff/login/', LoginView.as_view(), name='hubstaff-login'),
    path('dailyupdate/', DailyUpdateView.as_view(), name='dailyupdate'),
    path('leave/', LeaveStatusView.as_view(), name='leave'),
    path('feedback/', FeedbackView.as_view(), name='feedback'),
    path('listtask/', TaskListView.as_view(), name='listtask'),
    path('addtask/', AddTaskView.as_view(), name='addtask'),
    path('stats/', StatsView.as_view(), name='stats'),
]
