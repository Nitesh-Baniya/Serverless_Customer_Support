
import json
import os
import re
import urllib.error
import urllib.request

API_BASE_URL = os.environ["API_BASE_URL"].rstrip("/")
TIMEOUT_SECONDS = 10


def lex_response(message, intent_name, slots=None, state="Fulfilled"):
    return {
        "sessionState": {
            "dialogAction": {"type": "Close"},
            "intent": {
                "name": intent_name,
                "slots": slots or {},
                "state": state
            }
        },
        "messages": [
            {
                "contentType": "PlainText",
                "content": message
            }
        ]
    }


def call_api(method, path, payload=None):
    url = f"{API_BASE_URL}{path}"
    data = None

    headers = {"Accept": "application/json"}

    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"

    request = urllib.request.Request(
        url,
        data=data,
        headers=headers,
        method=method
    )

    try:
        with urllib.request.urlopen(
            request, timeout=TIMEOUT_SECONDS
        ) as response:
            body = response.read().decode("utf-8")
            return response.status, json.loads(body) if body else {}

    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        try:
            result = json.loads(body) if body else {}
        except json.JSONDecodeError:
            result = {}

        return exc.code, result


def slot_value(slots, name):
    slot = (slots or {}).get(name)
    if not slot:
        return ""

    value = slot.get("value") or {}
    return str(value.get("interpretedValue") or "").strip()


def lambda_handler(event, context):
    session_state = event.get("sessionState") or {}
    intent = session_state.get("intent") or {}
    intent_name = intent.get("name", "")
    slots = intent.get("slots") or {}

    try:
        if intent_name == "CreateTicketIntent":
            name = slot_value(slots, "Name")
            email = slot_value(slots, "Email")
            subject = slot_value(slots, "Subject")
            description = slot_value(slots, "Description")

            if not name or not email or not subject or not description:
                return lex_response(
                    "Please provide all the required information: your name, email, subject and description.",
                    intent_name,
                    slots,
                    state="Failed"
                )

            if len(subject) > 200 or len(description) > 5000:
                return lex_response(
                    "Please keep the subject under 200 characters "
                    "and the description under 5000 characters.",
                    intent_name,
                    slots,
                    state="Failed"
                )

            status, result = call_api(
                "POST",
                "/tickets",
                {
                    "name": name,
                    "email": email,
                    "subject": subject,
                    "description": description
                }
            )

            if status not in (200, 201):
                print("Ticket creation API returned:", status, result)
                return lex_response(
                    "Sorry, I couldn't create your ticket right now. "
                    "Please try again later.",
                    intent_name,
                    slots,
                    state="Failed"
                )

            ticket_id = result.get("ticketId")
            if not ticket_id:
                print("Ticket creation response missing ticketId")
                return lex_response(
                    "Your request was received, but I couldn't retrieve "
                    "the ticket ID. Please check the Support Portal.",
                    intent_name,
                    slots,
                    state="Failed"
                )

            return lex_response(
                f"Your support ticket has been created successfully. "
                f"Your ticket ID is {ticket_id}. "
                f"Please save this ID to check its status later.",
                intent_name,
                slots
            )

        elif intent_name == "CheckTicketStatusIntent":
            ticket_id = slot_value(slots, "TicketId")

            # UUID validation prevents malformed paths.
            if not re.fullmatch(
                r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-"
                r"[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-"
                r"[0-9a-fA-F]{12}",
                ticket_id
            ):
                return lex_response(
                    "That doesn't look like a valid ticket ID. "
                    "Please provide the full ticket ID, including hyphens.",
                    intent_name,
                    slots,
                    state="Failed"
                )

            status, result = call_api(
                "GET",
                f"/tickets/{ticket_id}"
            )

            if status == 404:
                return lex_response(
                    "I couldn't find a ticket with that ID. "
                    "Please check the ID and try again.",
                    intent_name,
                    slots,
                    state="Failed"
                )

            if status != 200:
                print("Ticket status API returned:", status, result)
                return lex_response(
                    "Sorry, I couldn't retrieve the ticket status right now. "
                    "Please try again later.",
                    intent_name,
                    slots,
                    state="Failed"
                )

            ticket_status = result.get("status", "Unknown")
            category = result.get("category", "Not yet classified")
            priority = result.get("priority", "Not yet assigned")
            processing_status = result.get(
                "processingStatus", "PENDING"
            )

            message = (
                f"Ticket {ticket_id}: status {ticket_status}. "
                f"Category: {category}. Priority: {priority}. "
                f"Processing: {processing_status}."
            )

            return lex_response(message, intent_name, slots)

        else:
            return lex_response(
                "I can help create a support ticket or check an existing "
                "ticket's status. What would you like to do?",
                intent_name,
                slots,
                state="Failed"
            )

    except Exception as exc:
        # Log technical details in CloudWatch, not in the customer response.
        print("Unexpected fulfilment error:", type(exc).__name__, str(exc))
        return lex_response(
            "Sorry, something went wrong while processing your request. "
            "Please try again later.",
            intent_name or "FallbackIntent",
            slots,
            state="Failed"
        )
