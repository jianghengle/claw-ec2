from django.urls import path
from .views import claw_view

urlpatterns = [
    path('verify-ec2-token/', claw_view.verify_ec2_token, name='verify-ec2-token'),
    path('rotate-ec2-token/', claw_view.rotate_ec2_token, name='rotate-ec2-token'),
    path('get-claw-token/', claw_view.get_claw_token, name='get-claw-token'),
    path('rotate-claw-token/', claw_view.rotate_claw_token, name='rotate-claw-token'),
    path('set-claude-key/', claw_view.set_claude_key, name='set-claude-key'),
]
