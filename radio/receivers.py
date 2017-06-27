# receivers.py
import json
import logging
import datetime

from django.dispatch import receiver
from django.contrib.auth.models import User

from pinax.stripe.signals import WEBHOOK_SIGNALS

from radio.models import Plan, StripePlanMatrix, Profile
from pinax.stripe.models import Plan as pinax_Plan

# Get an instance of a logger
logger = logging.getLogger(__name__)


@receiver(WEBHOOK_SIGNALS["invoice.payment_succeeded"])
def handle_payment_succeeded(sender, event, **kwargs):
    logger.error('----------------------------------------')
    logger.error('Stripe Payment Posted')
    logger.error(event.customer)
    #logger.error(event.webhook_message)

@receiver(WEBHOOK_SIGNALS["customer.subscription.created"])
def handle_subscription_created(sender, event, **kwargs):

    hook_message = event.webhook_message

    customer = event.customer
    stripe_subscription_end = hook_message['data']['object']['current_period_end']
    stripe_subscription_plan_id = hook_message['data']['object']['items']['data'][0]['plan']['id']

    user = User.objects.get(username=customer)
    user_profile = Profile.objects.get(user=user)
    stripe_plan = pinax_Plan.objects.get(stripe_id=stripe_subscription_plan_id)

    plan_matrix = StripePlanMatrix.objects.get(stripe_plan=stripe_plan)
    user_profile.plan = plan_matrix.radio_plan
    user_profile.save()

    logger.error('Moving Customer {} to plan {}'.format(user, plan_matrix.radio_plan))
    
    logger.error('Stripe customer.subscription.created {}'.format(event.customer))
    end_date = datetime.datetime.fromtimestamp(hook_message['data']['object']['current_period_end']).strftime('%c')
    logger.error('END TS {}'.format(end_date))
    #logger.error('TESTING {}'.format(hook_message['data']['object']['data'][0]))
    logger.error('TESTING ID {}'.format(hook_message['data']['object']['items']['data'][0]['plan']['id']))

