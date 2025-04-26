# lsms/api_views.py

from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.timezone import now
from django.conf import settings
from django.utils.decorators import method_decorator

from .models import User, ClientSubscription, SubscriptionPlan, Notification
from .serializers import UserSerializer, NotificationSerializer
import requests
from datetime import timedelta
from .util.token import account_activation_token


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class NotificationListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(NotificationSerializer(
            Notification.objects.filter(recipient=request.user),
            many=True
        ).data)


class SubscriptionDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.role != 'client_admin':
            return Response({"error": "Access denied"}, status=403)

        try:
            sub = ClientSubscription.objects.filter(
                client_institution=user.institution, is_active=True
            ).latest('start_date')
        except ClientSubscription.DoesNotExist:
            return Response({"message": "No active subscription found"})

        return Response({
            "plan": sub.plan.name,
            "price": float(sub.plan.price),
            "start_date": sub.start_date,
            "end_date": sub.end_date,
            "active": sub.is_active,
        })


class InitializeFlutterwavePaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        plan_id = request.data.get("plan_id")

        try:
            plan = SubscriptionPlan.objects.get(id=plan_id)
        except SubscriptionPlan.DoesNotExist:
            return Response({"error": "Plan not found"}, status=404)

        from uuid import uuid4
        tx_ref = f"LSMS-{uuid4().hex[:10]}"
        amount = float(plan.price)

        headers = {
            "Authorization": f"Bearer {settings.FLUTTERWAVE_SECRET_KEY}",
            "Content-Type": "application/json",
        }

        payload = {
            "tx_ref": tx_ref,
            "amount": str(amount),
            "currency": "NGN",
            "redirect_url": "https://your-domain.com/api/flutterwave/callback/",
            "customer": {
                "email": user.email,
                "name": f"{user.first_name} {user.last_name}"
            },
            "meta": {
                "user_id": user.id,
                "plan_id": plan.id
            },
            "customizations": {
                "title": "LSMS Subscription Payment",
                "description": f"Subscription to {plan.name}",
                "logo": "https://yourdomain.com/static/logo.png"
            }
        }

        response = requests.post("https://api.flutterwave.com/v3/payments", json=payload, headers=headers)
        data = response.json()

        if not data.get("status") == "success":
            return Response({"error": "Flutterwave payment failed to initialize"}, status=400)

        return Response(data["data"])


@csrf_exempt
def flutterwave_callback_view(request):
    tx_ref = request.GET.get("tx_ref")
    transaction_id = request.GET.get("transaction_id")
    status = request.GET.get("status")

    if not tx_ref or not transaction_id or status != "successful":
        return JsonResponse({"error": "Invalid request"}, status=400)

    headers = {
        "Authorization": f"Bearer {settings.FLUTTERWAVE_SECRET_KEY}"
    }

    verify_url = f"https://api.flutterwave.com/v3/transactions/{transaction_id}/verify"
    response = requests.get(verify_url, headers=headers)
    data = response.json()

    if not data.get("status") == "success":
        return JsonResponse({"error": "Transaction verification failed"}, status=400)

    meta = data['data'].get('meta', {})
    user_id = meta.get("user_id")
    plan_id = meta.get("plan_id")

    try:
        user = User.objects.get(id=user_id)
        plan = SubscriptionPlan.objects.get(id=plan_id)
    except (User.DoesNotExist, SubscriptionPlan.DoesNotExist):
        return JsonResponse({"error": "Invalid metadata"}, status=400)

    start_date = now().date()
    end_date = start_date + timedelta(days=30 * plan.duration_months)

    ClientSubscription.objects.filter(client_institution=user.institution, is_active=True).update(is_active=False)

    ClientSubscription.objects.create(
        client_institution=user.institution,
        plan=plan,
        start_date=start_date,
        end_date=end_date,
        is_active=True
    )

    return JsonResponse({"message": "Subscription activated"})
