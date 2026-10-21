import os
from datetime import datetime, timezone

import boto3

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["TABLE_NAME"])


def lambda_handler(event, context):
    ticket_id = event.get("ticketId")
    category = event.get("category")
    priority = event.get("priority")
    escalation_required = event.get("escalationRequired")

    if not ticket_id:
        raise ValueError("ticketId is required")

    if category not in {"TECHNICAL", "BILLING", "GENERAL"}:
        raise ValueError("Invalid category")

    if priority not in {"NORMAL", "HIGH"}:
        raise ValueError("Invalid priority")

    if not isinstance(escalation_required, bool):
        raise ValueError("escalationRequired must be a boolean")

    processed_at = datetime.now(timezone.utc).isoformat()

    result = table.update_item(
        Key={"ticketId": ticket_id},
        UpdateExpression=(
            "SET #category = :category, "
            "#priority = :priority, "
            "processingStatus = :processing_status, "
            "escalationRequired = :escalation, "
            "processedAt = :processed_at"
        ),
        ConditionExpression="attribute_exists(ticketId)",
        ExpressionAttributeNames={
            "#category": "category",
            "#priority": "priority"
        },
        ExpressionAttributeValues={
            ":category": category,
            ":priority": priority,
            ":processing_status": "COMPLETED",
            ":escalation": escalation_required,
            ":processed_at": processed_at
        },
        ReturnValues="ALL_NEW"
    )

    return {
        "ticketId": ticket_id,
        "processingStatus": "COMPLETED",
        "category": result["Attributes"]["category"],
        "priority": result["Attributes"]["priority"],
        "escalationRequired": result["Attributes"]["escalationRequired"],
        "processedAt": result["Attributes"]["processedAt"]
    }