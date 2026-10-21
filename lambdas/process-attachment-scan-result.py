
import json
import logging
import urllib.parse

import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3 = boto3.client("s3")

BUCKET = "support-attachments-aitac-team1-v1"
QUARANTINE_PREFIX = "quarantine/"
ACCEPTED_PREFIX = "accepted/"

def matches_signature(content_type, data):
    if content_type == "image/png":
        return data.startswith(b"\x89PNG\r\n\x1a\n")

    if content_type == "image/jpeg":
        return data.startswith(b"\xff\xd8\xff")

    if content_type == "application/pdf":
        return data.startswith(b"%PDF-")

    return False

def lambda_handler(event, context):
    detail = event.get("detail", {})

    if event.get("source") != "aws.guardduty":
        return {"result": "ignored", "reason": "unexpected source"}

    if event.get("detail-type") != \
            "GuardDuty Malware Protection Object Scan Result":
        return {"result": "ignored", "reason": "unexpected event type"}

    obj = detail.get("s3ObjectDetails", {})
    bucket = obj.get("bucketName", "")
    key = urllib.parse.unquote_plus(obj.get("objectKey", ""))

    if bucket != BUCKET or not key.startswith(QUARANTINE_PREFIX):
        return {"result": "ignored", "reason": "outside quarantine scope"}

    scan_status = detail.get("scanStatus")
    scan_result = detail.get("scanResultDetails", {}).get(
        "scanResultStatus"
    )

    if scan_status != "COMPLETED" or scan_result != "NO_THREATS_FOUND":
        logger.warning(
            "Object remains quarantined: key=%s scan=%s result=%s",
            key, scan_status, scan_result
        )
        return {"result": "quarantined", "key": key}

    head = s3.head_object(Bucket=bucket, Key=key)
    content_type = head.get("ContentType", "")
    size = head.get("ContentLength", 0)

    if size < 1 or size > 5 * 1024 * 1024:
        logger.warning("Invalid object size: %s", key)
        return {"result": "quarantined", "reason": "invalid size"}

    response = s3.get_object(
        Bucket=bucket,
        Key=key,
        Range="bytes=0-15"
    )
    signature_bytes = response["Body"].read()
    response["Body"].close()

    if not matches_signature(content_type, signature_bytes):
        logger.warning("Signature mismatch: %s", key)
        return {"result": "quarantined", "reason": "signature mismatch"}

    destination_key = ACCEPTED_PREFIX + key[len(QUARANTINE_PREFIX):]

    s3.copy_object(
        Bucket=bucket,
        Key=destination_key,
        CopySource={"Bucket": bucket, "Key": key},
        MetadataDirective="COPY",
        TaggingDirective="COPY"
    )

    # Delete only after the copy operation succeeds.
    s3.delete_object(Bucket=bucket, Key=key)

    logger.info("Attachment accepted: %s", destination_key)
    return {"result": "accepted", "key": destination_key}
