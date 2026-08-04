from django.urls import path
from .views import claw_view

urlpatterns = [
    path('verify-ec2-token/', claw_view.verify_ec2_token, name='verify-ec2-token'),
    path('rotate-ec2-token/', claw_view.rotate_ec2_token, name='rotate-ec2-token'),
]
