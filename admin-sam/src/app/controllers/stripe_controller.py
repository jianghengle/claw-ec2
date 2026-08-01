import os, json
from .. import MyError
import stripe
from decimal import Decimal
from ..models.user_model import UserModel
from ..models.subscription_model import SubscriptionModel
from ..models.payment_model import PaymentModel
from ..my_http import MyResp


stripe_key = os.environ['STRIPE_KEY']
client = stripe.StripeClient(stripe_key)
stripe_price_key = os.environ['STRIPE_PRICE_KEY']
app_domain = os.environ['APP_DOMAIN']
endpoint_secret = os.environ['STRIPE_WEBHOOK']


def handle(req):
    if req.path.startswith('/stripe/create-checkout-session'):
        return create_checkout_session(req)
    if req.path.startswith('/stripe/webhook'):
        return handle_webhook(req)
    raise MyError('Invalid stripe path', 401)

def create_checkout_session(req):
    data = parse_body(req.body)

    token = data.get('token', None)
    subscription_id = data.get('subscriptionId', None)
    if not token or not subscription_id:
        raise MyError('Missing token or subscriptionId')
    user = UserModel.get_by_token(token)
    if user.token_expired():
        raise MyError('Token expired')
    subscription = SubscriptionModel.get_by_id(subscription_id)
    if subscription.userId != user.id:
        raise MyError('Subscription does not belong to user')
    
    months = int(data.get('months', '0'))
    try:
        checkout_session = client.v1.checkout.sessions.create(params={
            'line_items': [
                {
                    'price': stripe_price_key,
                    'quantity': months,
                },
            ],
            'mode': 'payment',
            'success_url': app_domain,
            # Provide a name (for example, hosted_web_0001) to label this Checkout integration and measure its conversion independently
            'integration_identifier': 'hosted_web_0001',
        })
    except Exception as e:
        return str(e)

    payment_amount = Decimal(checkout_session.amount_total) / Decimal(100)
    PaymentModel.create_new(user.id, subscription.id, checkout_session.id, months, payment_amount)
    return send_redirect(checkout_session.url, code=303)


def handle_webhook(request):
    payload = request.raw_body
    event = None

    try:
        event = stripe.Event.construct_from(json.loads(payload), stripe_key)
    except ValueError as e:
        # Invalid payload
        return MyResp(code=400)

    if endpoint_secret:
        # Only verify the event if you've defined an endpoint secret
        # Otherwise, use the basic event deserialized with JSON
        sig_header = request.headers.get('Stripe-Signature')
        try:
            event = client.construct_event(
                payload, sig_header, endpoint_secret
            )
        except stripe.error.SignatureVerificationError as e:
            print('⚠️  Webhook signature verification failed.' + str(e))
            return MyResp({'success': False})

    # Handle the event
    if event.type == 'checkout.session.completed':
        checkout_session = event.data.object
        handle_checkout_session_complete(checkout_session.id)
    else:
        print('Unhandled event type {}'.format(event.type))

    return MyResp(code=200)

def handle_checkout_session_complete(checkout_session_id):
    payment = PaymentModel.get_by_checkout_session_id(checkout_session_id)
    if not payment:
        print('Cannot find payment from the checkout session id: ' + checkout_session_id)
        return
    if payment.status != 'Pending':
        print('The payment has been paid before ' + payment.id)
        return
    payment.change_status('Paid')

    subscription = SubscriptionModel.get_by_id(payment.subscriptionId)
    if not subscription:
        print('Cannot find subscription from the subscription id: ' + payment.subscriptionId)
        return
    subscription.add_months(payment.months)


def send_redirect(url, code):
    return {
        "statusCode": code,
        "headers": {
            'Location': url,
        },
    }

def parse_body(body):
    data = {}
    fields = body.split('&')
    for fv in fields:
        f, v = fv.split('=')
        data[f] = v
    return data
