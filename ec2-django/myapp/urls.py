from django.urls import path
from .views import claw_view

urlpatterns = [
    path('verify-ec2-token/', claw_view.verify_ec2_token, name='verify-ec2-token'),
]
