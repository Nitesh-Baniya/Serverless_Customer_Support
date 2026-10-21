
import json
import os
import re
import uuid

import boto3

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["TABLE_NAME"])
s3 = boto3.client("s3")

BUCKET = os.environ["ATTACHMENT_BUCKET"]
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MiB
URL_EXPIRY_SECONDS = 300

ALLOWED_TYPES = {
    "image/jpeg",
    "image/png",
    "application/pdf",
}


def response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body),
    }


def lambda_handler(event, context):
    try:
        path_params = event.get("pathParameters") or {}
        ticket_id = path_params.get("ticketId", "")

        if not re.fullmatch(
            r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-"
            r"[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-"
            r"[0-9a-fA-F]{12}",
            ticket_id,
        ):
            return response(400, {"error": "Invalid ticket ID"})

        body = event.get("body", {})
        if isinstance(body, str):
            body = json.loads(body)

        if not isinstance(body, dict):
            return response(400, {"error": "Invalid request body"})

        content_type = body.get("contentType")
        file_size = body.get("fileSize")

        if content_type not in ALLOWED_TYPES:
            return response(400, {
                "error": "Only JPEG, PNG, and PDF files are allowed"
            })

        # Reject booleans and non-integer sizes.
        if type(file_size) is not int:
            return response(400, {"error": "Invalid file size"})

        if not 1 <= file_size <= MAX_FILE_SIZE:
            return response(400, {
                "error": "File must be between 1 byte and 5 MiB"
            })

        # Confirm the ticket exists before issuing an upload URL.
        ticket = table.get_item(
            Key={"ticketId": ticket_id},
            ProjectionExpression="ticketId",
        ).get("Item")

        if not ticket:
            return response(404, {"error": "Ticket not found"})

        # Never accept the object's key from the browser.
        object_key = (
            f"quarantine/{ticket_id}/{uuid.uuid4()}"
        )

        upload = s3.generate_presigned_post(
            Bucket=BUCKET,
            Key=object_key,
            Fields={
                "Content-Type": content_type,
                "x-amz-meta-ticket-id": ticket_id,
            },
            Conditions=[
                {"Content-Type": content_type},
                {"x-amz-meta-ticket-id": ticket_id},
                ["content-length-range", 1, MAX_FILE_SIZE],
            ],
            ExpiresIn=URL_EXPIRY_SECONDS,
        )

        return response(200, {
            "upload": upload,
            "objectKey": object_key,
            "expiresInSeconds": URL_EXPIRY_SECONDS,
            "message": "Upload authorization generated",
        })

    except json.JSONDecodeError:
        return response(400, {"error": "Invalid JSON"})

    except Exception:
        print("Upload authorization failed; inspect CloudWatch logs.")
        return response(500, {
            "error": "Unable to prepare upload"
        })
