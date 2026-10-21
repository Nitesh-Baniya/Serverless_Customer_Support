import os
from datetime import datetime, timezone

import boto3

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["TABLE_NAME"])


def lambda_handler(event, context):
    ticket_id = event.get("ticketId")

    if not ticket_id:
        raise ValueError("ticketId is required")

    error_info = event.get("error", {})
    error_name = str(error_info.get("Error", "ProcessingError"))[:200]

    result = table.update_item(
        Key={"ticketId": ticket_id},
        UpdateExpression=(
            "SET processingStatus = :failed, "
            "processingError = :error, "
            "processedAt = :time"
        ),
        ConditionExpression="attribute_exists(ticketId)",
        ExpressionAttributeValues={
            ":failed": "FAILED",
            ":error": error_name,
            ":time": datetime.now(timezone.utc).isoformat()
        },
        ReturnValues="UPDATED_NEW"
    )

    return {
        "ticketId": ticket_id,
        "processingStatus": result["Attributes"]["processingStatus"]
    }