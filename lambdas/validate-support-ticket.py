import os
import boto3

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["TABLE_NAME"])


def lambda_handler(event, context):
    ticket_id = event.get("ticketId")

    if not ticket_id:
        raise ValueError("ticketId is required")

    result = table.get_item(
        Key={"ticketId": ticket_id},
        ConsistentRead=True
    )

    ticket = result.get("Item")

    if not ticket:
        raise ValueError(f"Ticket not found: {ticket_id}")

    return {
        "ticketId": ticket_id,
        "validated": True,
        "subject": ticket.get("subject", ""),
        "description": ticket.get("description", ""),
        "status": ticket.get("status", "OPEN")
    }