import json
import os
import re

import boto3
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["TABLE_NAME"])


def response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps(body)
    }


def lambda_handler(event, context):
    path_parameters = event.get("pathParameters") or {}
    ticket_id = path_parameters.get("ticketId")

    if not ticket_id:
        return response(400, {
            "error": "ticketId is required"
        })

    try:
        result = table.get_item(
            Key={"ticketId": ticket_id},
            ConsistentRead=True
        )

        ticket = result.get("Item")

        if not ticket:
            return response(404, {
                "error": "Ticket not found"
            })

        # Return only the fields needed for ticket-status tracking.
        public_fields = [
            "ticketId",
            "status",
            "createdAt",
            "category",
            "priority",
            "escalationRequired",
            "processingStatus",
            "processedAt"
        ]

        ticket_details = {
            field: ticket[field]
            for field in public_fields
            if field in ticket
        }

        return response(200, ticket_details)

    except Exception as e:
        print(f"Ticket lookup failed: {type(e).__name__}")
        return response(500, {
            "error": "Unable to retrieve ticket"
        })
