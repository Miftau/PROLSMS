from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from lsms.models import ClientSubscription

class SubscriptionDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.role != 'client_admin':
            return Response({"error": "Access denied"}, status=403)

        try:
            subscription = ClientSubscription.objects.filter(client_institution=user.institution).latest('start_date')
        except ClientSubscription.DoesNotExist:
            return Response({"message": "No active subscription found"})

        return Response({
            "plan": subscription.plan.name,
            "price": float(subscription.plan.price),
            "start_date": subscription.start_date,
            "end_date": subscription.end_date,
            "active": subscription.is_active,
        })
