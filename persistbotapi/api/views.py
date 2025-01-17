import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import *
from .serializers import *


class LoginView(APIView):
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            print(serializer.data)
            return Response({"message": "Login successful and Telegram user."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CheckTelegramUserView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            # Parse the JSON body of the request
            data = json.loads(request.body)
            telegram_user_id = data.get('telegram_user_id')

            if telegram_user_id:
                user_exists = User.objects.filter(
                    telegram_user_id=telegram_user_id).exists()
                return Response({'exists': user_exists})
            else:
                return Response({'error': 'Telegram user ID is required'}, status=400)

        except json.JSONDecodeError:
            return Response({'error': 'Invalid JSON format'}, status=400)


class StartView(APIView):
    def get(self, request):
        return Response({
            "message": "Welcome to Hubstaff Operations Bot!",
            "commands": [
                "/dailyupdate - Submit your daily update.",
                "/leave - Mark yourself as on leave.",
                "/feedback - Provide feedback.",
                "/listtask - List all active tasks.",
                "/addtask - Add a new task.",
                "/stats - View statistics."
            ]
        }, status=status.HTTP_200_OK)


class DailyUpdateView(APIView):
    def post(self, request):
        serializer = DailyUpdateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response({"message": "Daily update submitted successfully."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class LeaveStatusView(APIView):
#     def post(self, request):
#         request.user.is_on_leave = True
#         request.user.save()
#         return Response({"message": "You are now marked as on leave."}, status=status.HTTP_200_OK)


class FeedbackView(APIView):
    def post(self, request):
        serializer = FeedbackSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response({"message": "Feedback submitted successfully."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TaskListView(APIView):
    def post(self, request):
        telegram_user_id = request.data.get('telegram_user_id')

        if not telegram_user_id:
            return Response({"error": "Telegram user ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(telegram_user_id=telegram_user_id).first()

        if not user:
            raise Response("User not found for the provided Telegram user ID.",
                           status=status.HTTP_400_BAD_REQUEST)

        tasks = HubstaffTask.objects.filter(user=user)

        serializer = HubstaffTaskSerializer(tasks, many=True)

        return Response({"tasks": serializer.data}, status=status.HTTP_200_OK)


class AddTaskView(APIView):
    def post(self, request):
        serializer = HubstaffTaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response({"message": "Task added successfully."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StatsView(APIView):
    def post(self, request):
        telegram_user_id = request.data.get('telegram_user_id')
        try:
            user = User.objects.get(telegram_user_id=telegram_user_id)
            stats = Stats.objects.get(user=user)
            serializer = StatsSerializer(stats)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        except Stats.DoesNotExist:
            return Response({"detail": "Stats not found for this user."}, status=status.HTTP_404_NOT_FOUND)


class LeaveStatusView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = LeaveSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Leave requested successfully!"}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
