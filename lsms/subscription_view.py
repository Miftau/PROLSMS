from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import timedelta
import json
from django.core.mail import send_mail
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.timezone import now
from django.conf import settings
from .models import User, SubscriptionPlan, ClientSubscription

from .models import ClientSubscription, SubscriptionPlan
from .serializers import ClientSubscriptionSerializer

class UpgradeSubscriptionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        sub_id = request.data.get("subscription_id")
        new_plan_id = request.data.get("new_plan_id")

        try:
            subscription = ClientSubscription.objects.get(id=sub_id, client_institution=request.user.institution)
            new_plan = SubscriptionPlan.objects.get(id=new_plan_id)
        except ClientSubscription.DoesNotExist:
            return Response({"error": "Subscription not found."}, status=404)
        except SubscriptionPlan.DoesNotExist:
            return Response({"error": "New plan not found."}, status=404)

        subscription.plan = new_plan
        subscription.start_date = timezone.now().date()
        subscription.end_date = timezone.now().date() + timedelta(days=30 * new_plan.duration_months)
        subscription.save()

        return Response({"message": "Subscription upgraded successfully."})

class CancelSubscriptionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        sub_id = request.data.get("subscription_id")
        try:
            subscription = ClientSubscription.objects.get(id=sub_id, client_institution=request.user.institution)
        except ClientSubscription.DoesNotExist:
            return Response({"error": "Subscription not found."}, status=404)

        subscription.is_active = False
        subscription.save()

        return Response({"message": "Subscription cancelled."})

class RenewSubscriptionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        sub_id = request.data.get("subscription_id")
        try:
            subscription = ClientSubscription.objects.get(id=sub_id, client_institution=request.user.institution)
        except ClientSubscription.DoesNotExist:
            return Response({"error": "Subscription not found."}, status=404)

        today = timezone.now().date()
        subscription.start_date = max(subscription.end_date, today)
        subscription.end_date = subscription.start_date + timedelta(days=30 * subscription.plan.duration_months)
        subscription.is_active = True
        subscription.save()

        return Response({"message": "Subscription renewed successfully."})

class InitializeFlutterwavePaymentView(APIView):
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

        if data.get("status") != "success":
            return Response({"error": "Flutterwave payment failed to initialize"}, status=400)

        return Response(data["data"])


@csrf_exempt
def flutterwave_callback_view(request):
    tx_ref = request.GET.get("tx_ref")
    transaction_id = request.GET.get("transaction_id")
    status = request.GET.get("status")

    if not tx_ref or not transaction_id:
        return JsonResponse({"error": "Missing transaction reference or ID"}, status=400)

    if status != "successful":
        return JsonResponse({"error": "Payment not successful"}, status=400)

    # === Step 1: Verify Transaction with Flutterwave ===
    headers = {
        "Authorization": f"Bearer {settings.FLUTTERWAVE_SECRET_KEY}"
    }

    verify_url = f"https://api.flutterwave.com/v3/transactions/{transaction_id}/verify"
    response = requests.get(verify_url, headers=headers)
    data = response.json()

    if data.get("status") != "success":
        return JsonResponse({"error": "Transaction verification failed"}, status=400)

    meta = data['data'].get('meta', {})
    user_id = meta.get("user_id")
    plan_id = meta.get("plan_id")

    # === Step 2: Fetch User and Plan ===
    try:
        user = User.objects.get(id=user_id)
        plan = SubscriptionPlan.objects.get(id=plan_id)
    except (User.DoesNotExist, SubscriptionPlan.DoesNotExist):
        return JsonResponse({"error": "Invalid user or plan info from metadata"}, status=400)

        # === Create Subscription ===
    start_date = now().date()
    end_date = start_date + timedelta(days=30 * plan.duration_months)

    # Deactivate previous
    ClientSubscription.objects.filter(client_institution=user.institution, is_active=True).update(is_active=False)

    subscription = ClientSubscription.objects.create(
        client_institution=user.institution,
        plan=plan,
        start_date=start_date,
        end_date=end_date,
        is_active=True
    )

    # === Send Email ===
    subject = "Subscription Confirmation - LSMS"
    message = (
        f"Dear {user.first_name},\n\n"
        f"Your subscription to the '{plan.name}' plan is now active.\n"
        f"Start Date: {start_date}\n"
        f"End Date: {end_date}\n"
        f"Thank you for choosing LSMS.\n\n"
        f"Regards,\nLSMS Team"
    )
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=False)

    return JsonResponse({
        "message": "Subscription successful, email sent.",
        "subscription": {
            "institution": user.institution.name,
            "plan": plan.name,
            "start_date": start_date,
            "end_date": end_date
        }
    })