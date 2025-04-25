from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import SubscriptionPlan, ClientSubscription
import requests
from django.conf import settings

@login_required
def dashboard_view(request):
    try:
        sub = ClientSubscription.objects.filter(client_institution=request.user.institution, is_active=True).latest('start_date')
        subscription = {
            'plan': sub.plan.name,
            'start_date': sub.start_date,
            'end_date': sub.end_date,
            'status': "Active" if sub.is_active else "Inactive"
        }
    except ClientSubscription.DoesNotExist:
        subscription = None

    return render(request, "lsms/dashboard.html", {"subscription": subscription})

@login_required
def subscribe_view(request):
    if request.method == "POST":
        plan_id = request.POST.get("plan_id")
        selected_plan = SubscriptionPlan.objects.get(id=plan_id)

        # Initialize Flutterwave payment
        headers = {
            "Authorization": f"Bearer {settings.FLUTTERWAVE_SECRET_KEY}"
        }
        payload = {
            "tx_ref": f"LSMS-{request.user.id}-{plan_id}",
            "amount": str(selected_plan.price),
            "currency": "NGN",
            "redirect_url": "https://your-domain.com/api/flutterwave/callback/",
            "customer": {
                "email": request.user.email,
                "name": f"{request.user.first_name} {request.user.last_name}"
            },
            "meta": {
                "user_id": request.user.id,
                "plan_id": selected_plan.id
            },
            "customizations": {
                "title": "LSMS Subscription",
                "description": f"Subscribing to {selected_plan.name}",
                "logo": "https://yourdomain.com/static/logo.png"
            }
        }

        response = requests.post("https://api.flutterwave.com/v3/payments", json=payload, headers=headers)
        res_data = response.json()

        if res_data.get("status") == "success":
            return redirect(res_data["data"]["link"])
        else:
            return render(request, "lsms/subscribe.html", {"error": "Failed to initialize payment."})

    plans = SubscriptionPlan.objects.all()
    return render(request, "lsms/subscribe.html", {"plans": plans})
