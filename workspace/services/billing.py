from typing import Any, Dict
from django.conf import settings
from urllib.parse import urljoin
from rest_framework import serializers
from workspace.services.onboarding import choose_plan, confirm_plan
from common import config as dyn


def _price_for_plan(plan: str, renew_interval: str | None = None) -> str:
    # Try plan + interval first (e.g., STRIPE_PRICE_PRO_YEARLY), then fallback to plan-only
    key = (
        f"STRIPE_PRICE_{plan.upper()}_{(renew_interval or '').upper()}".rstrip("_")
        if renew_interval
        else f"STRIPE_PRICE_{plan.upper()}"
    )
    price = dyn.get(key)
    if not price:
        # fallback: plan-only
        fallback = f"STRIPE_PRICE_{plan.upper()}"
        price = dyn.get(fallback)
        if not price:
            raise serializers.ValidationError(
                f"Stripe price id not configured for plan '{plan}'. Set {key} or {fallback} in Admin (Settings > Constance) or env."
            )
    return price


def create_checkout_session(*, user, workspace, plan: str) -> Dict[str, Any]:
    """Persist pending plan and create a Stripe Checkout Session for subscription.
    Returns { url } to redirect the user.
    """
    if not settings.STRIPE_SECRET_KEY and not dyn.get_secret("STRIPE_TEST_SECRET_KEY") and not dyn.get_secret("STRIPE_LIVE_SECRET_KEY"):
        raise serializers.ValidationError("Stripe not configured. Add keys in Admin (Constance) or env.")

    # Record the user's selection; payment confirmation will finalize
    choose_plan(workspace, plan)

    import stripe
    from djstripe.models import Customer

    # Choose API key based on live mode, with Constance/env fallback
    live = dyn.get_bool("STRIPE_LIVE_MODE", getattr(settings, "STRIPE_LIVE_MODE", False))
    secret = (
        dyn.get_secret("STRIPE_LIVE_SECRET_KEY") if live else dyn.get_secret("STRIPE_TEST_SECRET_KEY")
    ) or settings.STRIPE_SECRET_KEY
    stripe.api_key = secret
    # Use workspace preference if present to select monthly/yearly price
    renew_interval = (
        getattr(workspace, "subscription", None)
        and workspace.subscription.renew_interval
        or None
    )
    price_id = _price_for_plan(plan, renew_interval)

    frontend_base = dyn.get("FRONTEND_URL", "http://localhost:3000/")
    success_url = urljoin(
        frontend_base, "billing/success?session_id={CHECKOUT_SESSION_ID}"
    )
    cancel_url = urljoin(frontend_base, "billing/cancel")

    customer, _ = Customer.get_or_create(subscriber=user)

    session = stripe.checkout.Session.create(
        mode="subscription",
        customer=customer.id,
        line_items=[{"price": price_id, "quantity": 1}],
        success_url=success_url,
        cancel_url=cancel_url,
        allow_promotion_codes=True,
        metadata={"workspace_id": str(workspace.id), "plan": plan},
        client_reference_id=str(workspace.id),
        automatic_tax={"enabled": True},
    )
    return {"url": session.url}


def confirm_checkout_session(*, workspace, session_id: str) -> Dict[str, Any]:
    """Verify the session with Stripe and finalize the plan locally; returns subscription data dict."""
    if not settings.STRIPE_SECRET_KEY and not dyn.get_secret("STRIPE_TEST_SECRET_KEY") and not dyn.get_secret("STRIPE_LIVE_SECRET_KEY"):
        raise serializers.ValidationError("Stripe not configured. Add keys in Admin (Constance) or env.")

    import stripe
    from djstripe.models import CheckoutSession
    from workspace.serializers.subscriptions import SubscriptionSerializer

    live = dyn.get_bool("STRIPE_LIVE_MODE", getattr(settings, "STRIPE_LIVE_MODE", False))
    secret = (
        dyn.get_secret("STRIPE_LIVE_SECRET_KEY") if live else dyn.get_secret("STRIPE_TEST_SECRET_KEY")
    ) or settings.STRIPE_SECRET_KEY
    stripe.api_key = secret
    sess = stripe.checkout.Session.retrieve(session_id, expand=["subscription"])  # type: ignore

    if sess.get("payment_status") not in {"paid", "no_payment_required"}:
        raise serializers.ValidationError("Payment not completed.")

    sid = str(workspace.id)
    sess_ws = str((sess.get("client_reference_id") or ""))
    meta_ws = str((sess.get("metadata", {}) or {}).get("workspace_id") or "")
    if sid not in {sess_ws, meta_ws}:
        raise serializers.ValidationError("Session does not match workspace.")

    try:
        CheckoutSession.sync_from_stripe_data(sess)
    except Exception:
        pass

    sub = confirm_plan(workspace)
    return SubscriptionSerializer(sub).data
