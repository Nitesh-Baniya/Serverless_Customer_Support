# Security Review

## Overview

Security was an important part of this project because it handles support tickets and file uploads. I implemented several AWS security controls, including private S3 buckets, IAM permissions, presigned uploads, malware scanning, and CloudWatch monitoring.

This is a learning project, so some security improvements are still needed before it could be used with real customers.

## Security Measures Implemented

### 1. Frontend and API Security
- Hosted the frontend in a private S3 bucket and served it through CloudFront using Origin Access Control (OAC).
- Used HTTPS for the website and API communication.
- Configured API Gateway throttling to limit request rates.
- Used separate Lambda functions and IAM execution roles for different operations.

### 2. Ticket Data
- Stored tickets in DynamoDB.
- Configured Lambda permissions for the required database operations.
- Used synthetic data for testing and demonstrations.

**Limitation:** The application does not currently have customer authentication or ticket ownership authorization. Knowing a ticket ID should not be treated as proof of ownership.

### 3. Attachment Security
- Kept the attachment bucket private with S3 Block Public Access enabled.
- Used short-lived presigned upload requests with restrictions on supported file types and size.
- Uploaded files to a `quarantine/` prefix before processing.
- Integrated GuardDuty Malware Protection for S3 with EventBridge and Lambda.
- Moved eligible clean files to `accepted/` after scan-result and file validation.
- Kept accepted attachments private.

Failed, skipped, or inconclusive scan results should not be treated as clean.

### 4. Monitoring and Cost Controls
- Configured CloudWatch alarms for selected Lambda errors and Step Functions failed executions.
- Used SNS for email notifications.
- Configured an AWS Budget with spending notifications.
- Applied API Gateway throttling to the public endpoints.

These controls help with monitoring and cost awareness, but budget notifications do not automatically stop spending.

## Remaining Risks

| Risk | Improvement needed |
|---|---|
| No authentication | Add a suitable identity provider, such as Amazon Cognito |
| No ticket ownership checks | Authorize every ticket operation on the backend |
| Public API abuse | Improve abuse protection and request validation |
| Attachment-processing failures | Test duplicate events, partial failures, and scan edge cases |
| Monitoring | Verify alarm notifications end to end |
| Cost overruns | Monitor actual usage and remove unused resources |

## Conclusion

This project helped me understand how security controls fit into a serverless AWS application. Keeping storage private and validating attachments are important, but they do not replace authentication and authorization.

Before using this application with real customers, I would prioritize access control, stronger abuse protection, and more extensive security testing.
