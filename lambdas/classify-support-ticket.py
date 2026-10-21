
def lambda_handler(event, context):
    subject = str(event.get("subject", ""))
    description = str(event.get("description", ""))

    text = f"{subject} {description}".lower()

    billing_keywords = [
        "payment", "billing", "refund", "invoice"
    ]

    technical_keywords = [
        "error", "bug", "technical", "crash",
        "broken", "not working", "failed",
        "outage", "unavailable", "service down",
        "cannot access", "can't access",
        "connection issue", "server down"
    ]

    high_priority_keywords = [
        "urgent", "outage", "security breach",
        "cannot access", "can't access",
        "unavailable", "compromised",
        "service down", "server down"
    ]

    if any(word in text for word in billing_keywords):
        category = "BILLING"
    elif any(word in text for word in technical_keywords):
        category = "TECHNICAL"
    else:
        category = "GENERAL"

    escalation_required = any(
        word in text for word in high_priority_keywords
    )

    priority = "HIGH" if escalation_required else "NORMAL"

    return {
        "ticketId": event["ticketId"],
        "category": category,
        "priority": priority,
        "escalationRequired": escalation_required
    }
