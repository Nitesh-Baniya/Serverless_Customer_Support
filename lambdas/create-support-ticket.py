
import json
import os
import re
import uuid
from datetime import datetime, timezone

import boto3

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["TABLE_NAME"])

stepfunctions = boto3.client("stepfunctions")


def response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps(body)
    }


def lambda_handler(event, context):
    try:
        body = event.get("body", event)

        if isinstance(body, str):
            body = json.loads(body)

        if not isinstance(body, dict):
            return response(400, {
                "error": "Invalid request body"
            })

        name = body.get("name", "").strip()
        email = body.get("email", "").strip()
        subject = body.get("subject", "").strip()
        description = body.get("description", "").strip()

        if not all([name, email, subject, description]):
            return response(400, {
                "error": "All fields are required"
            })

        if (
            len(name) > 100
            or len(email) > 254
            or len(subject) > 200
            or len(description) > 5000
        ):
            return response(400, {
                "error": "One or more fields are too long"
            })

        if not re.fullmatch(
            r"[^@\s]+@[^@\s]+\.[^@\s]+", email
        ):
            return response(400, {
                "error": "Invalid email address"
            })

        ticket_id = str(uuid.uuid4())

        item = {
            "ticketId": ticket_id,
            "name": name,
            "email": email,
            "subject": subject,
            "description": description,
            "status": "OPEN",
            "processingStatus": "PENDING",
            "createdAt": datetime.now(
                timezone.utc
            ).isoformat()
        }

        # Save the ticket before starting the workflow.
        table.put_item(
            Item=item,
            ConditionExpression="attribute_not_exists(ticketId)"
        )

        # Workflow startup failure must not hide successful ticket creation.
        workflow_started = False

        try:
            stepfunctions.start_execution(
                stateMachineArn=os.environ["STATE_MACHINE_ARN"],
                name=ticket_id,
                input=json.dumps({
                    "ticketId": ticket_id
                })
            )
            workflow_started = True

        except Exception as e:
            print(
                f"Ticket {ticket_id} was saved, but workflow "
                f"startup failed: {type(e).__name__}"
            )

        return response(201, {
            "message": "Ticket created successfully",
            "ticketId": ticket_id,
            "status": "OPEN",
            "processingStatus": (
                "STARTED" if workflow_started else "PENDING"
            ),
            "workflowStarted": workflow_started
        })

    except json.JSONDecodeError:
        return response(400, {
            "error": "Request body must contain valid JSON"
        })

    except Exception as e:
        print(
            f"Ticket creation failed: {type(e).__name__}"
        )
        return response(500, {
            "error": "Unable to create ticket"
        })
