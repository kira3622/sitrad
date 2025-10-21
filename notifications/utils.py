import json
from typing import Optional
from django.conf import settings
from django.utils import timezone

try:
    from pywebpush import webpush, WebPushException
except Exception:
    # Module optional jusqu'à installation en prod
    webpush = None
    WebPushException = Exception

from .models import WebPushSubscription


def get_vapid_keys():
    """Retourne les clés VAPID depuis settings/env."""
    public_key = getattr(settings, 'VAPID_PUBLIC_KEY', None)
    private_key = getattr(settings, 'VAPID_PRIVATE_KEY', None)
    subject = getattr(settings, 'VAPID_SUBJECT', 'mailto:admin@example.com')

    # Optionnel: support d'un dict settings.SECRETS si présent
    if hasattr(settings, 'SECRETS'):
        public_key = public_key or settings.SECRETS.get('VAPID_PUBLIC_KEY')
        private_key = private_key or settings.SECRETS.get('VAPID_PRIVATE_KEY')
        subject = settings.SECRETS.get('VAPID_SUBJECT', subject)

    return {
        'VAPID_PUBLIC_KEY': public_key,
        'VAPID_PRIVATE_KEY': private_key,
        'VAPID_SUBJECT': subject,
    }


def send_webpush_to_subscription(subscription: WebPushSubscription, data: dict) -> Optional[dict]:
    """
    Envoie une notification Web Push à une subscription.
    Retourne un dict de statut ou None si pywebpush indisponible.
    """
    if webpush is None:
        return None

    if not subscription.active:
        return {'status': 'skipped', 'reason': 'inactive'}

    keys = get_vapid_keys()
    if not keys['VAPID_PRIVATE_KEY'] or not keys['VAPID_PUBLIC_KEY']:
        return {'status': 'error', 'reason': 'missing_vapid_keys'}

    try:
        response = webpush(
            subscription_info={
                'endpoint': subscription.endpoint,
                'keys': {
                    'p256dh': subscription.p256dh,
                    'auth': subscription.auth
                }
            },
            data=json.dumps(data),
            vapid_private_key=keys['VAPID_PRIVATE_KEY'],
            vapid_claims={
                'sub': keys['VAPID_SUBJECT']
            }
        )
        return {
            'status': 'sent',
            'status_code': getattr(response, 'status_code', None),
        }
    except WebPushException as e:
        # Si 410, désactiver la subscription
        message = str(e)
        if '410' in message or 'Not Found' in message:
            subscription.active = False
            subscription.save(update_fields=['active'])
        return {'status': 'error', 'reason': message}


def broadcast_webpush_to_user(user, data: dict) -> dict:
    """Envoie une notification Web Push à toutes les subscriptions actives d'un user."""
    results = []
    for sub in WebPushSubscription.objects.filter(user=user, active=True):
        res = send_webpush_to_subscription(sub, data) or {'status': 'skipped', 'reason': 'pywebpush_not_installed'}
        results.append({'endpoint': sub.endpoint, **res})
    return {
        'count': len(results),
        'results': results,
        'timestamp': timezone.now().isoformat()
    }