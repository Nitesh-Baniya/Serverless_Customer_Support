# Serverless Customer Support Platform on AWS

A serverless customer support portal built with AWS managed services, featuring ticket management, automated ticket processing, a conversational chatbot, secure attachment uploads, malware scanning, and operational monitoring.

> **Project status:** Working learning project. The core application, attachment-scanning workflow, chatbot, and monitoring have been implemented and tested. Authentication and production-grade customer authorization remain future improvements.

## Why I Built This Project

I built this project to gain hands-on experience with AWS serverless architecture and understand how different cloud services work together in a real application. Rather than stopping at deploying a simple Lambda function, I wanted to build a complete support portal that combines ticket management, workflow automation, secure file uploads, chatbot integration, and monitoring.

As I explored the project, I became particularly interested in the security and operational challenges behind these integrations: keeping S3 buckets private, scanning uploaded files before accepting them, coordinating services across AWS Regions, and detecting failures through CloudWatch. This project has helped me connect individual AWS concepts with practical architecture and security decisions.

## Overview

The Serverless Customer Support Platform demonstrates how to build an event-driven application using AWS services without managing application servers.

Visitors can submit support tickets, look up ticket status, attach files, and interact with a chatbot. AWS Lambda handles backend logic, DynamoDB stores ticket records, Step Functions coordinates ticket processing, and Amazon GuardDuty Malware Protection for S3 helps prevent potentially malicious attachments from being accepted.

The frontend is delivered over HTTPS through Amazon CloudFront, while the underlying S3 website and attachment buckets remain private.

## Features

- **Support ticket management:** Create tickets and retrieve ticket status through API Gateway and Lambda.
- **Automated ticket processing:** Use AWS Step Functions to validate, classify, and update tickets, with a failure-handling path.
- **Conversational chatbot:** Use Amazon Lex V2 to support greetings, ticket creation conversations, ticket-status queries, and fallback responses.
- **Secure attachment uploads:** Generate time-limited presigned upload requests and validate permitted file types and size.
- **Malware scanning:** Scan objects uploaded to the quarantine prefix using GuardDuty Malware Protection for S3.
- **Quarantine and acceptance workflow:** Process scan results through Amazon EventBridge and Lambda. Only eligible clean scans with valid file signatures should be accepted.
- **Operational monitoring:** Use CloudWatch logs and alarms for Lambda errors and failed Step Functions executions, with email notifications through Amazon SNS.
- **Cost awareness:** Configure a monthly AWS budget and billing alerts.

## Architecture

### AWS Regions

| Region | Purpose |
|---|---|
| Asia Pacific (Mumbai), `ap-south-1` | Main application backend, ticket storage, workflow, and attachment scanning |
| Asia Pacific (Singapore), `ap-southeast-1` | Amazon Lex V2 chatbot and chatbot API components |

The chatbot uses Singapore because of the regional availability constraints encountered during implementation.

### Main AWS services

| Service | Responsibility |
|---|---|
| Amazon S3 | Private website origin and attachment storage |
| Amazon CloudFront | Public HTTPS website delivery |
| Amazon API Gateway | HTTP endpoints for tickets, attachments, and chatbot requests |
| AWS Lambda | Ticket operations, upload URL generation, scan processing, and chatbot integration |
| Amazon DynamoDB | Persistent support-ticket records |
| AWS Step Functions | Orchestration of ticket validation, classification, updates, and failure handling |
| Amazon GuardDuty Malware Protection for S3 | Malware scanning for uploaded attachments |
| Amazon EventBridge | Routes scan-result events to processing logic |
| Amazon Lex V2 | Conversational support interface |
| Amazon CloudWatch | Logs, metrics, and alarms |
| Amazon SNS | Email notifications for alarm actions |

## Application flows

### 1. Ticket creation

1. A visitor submits the support form.
2. The frontend sends a request to the Mumbai API.
3. `CreateSupportTicket` creates the ticket record in DynamoDB.
4. The Lambda starts `SupportTicketProcessingWorkflow`.
5. The workflow validates and classifies the ticket, updates its processing information, and follows its configured failure-handling path if needed.

### 2. Ticket-status lookup

1. The visitor provides a ticket ID.
2. The frontend calls `GET /tickets/{ticketId}`.
3. `GetSupportTicket` retrieves the corresponding record from DynamoDB.
4. The API returns the ticket information.

**Security limitation:** Ticket IDs are not authentication credentials. The current public lookup design does not establish that a requester owns a ticket.

### 3. Attachment upload and scanning

1. The frontend requests a presigned upload from `POST /tickets/{ticketId}/attachments`.
2. `GenerateUploadUrl` creates a time-limited upload request.
3. The browser uploads the file to the private attachment bucket under `quarantine/`.
4. GuardDuty Malware Protection for S3 scans the object.
5. Amazon EventBridge routes the scan-result event to `ProcessAttachmentScanResult`.
6. The processing Lambda validates the scan result and file signature.
7. Eligible clean files are copied to `accepted/`, and the quarantined original is deleted according to the processing logic.

Files with failed, skipped, inconclusive, or otherwise ineligible scan results must not be accepted. Duplicate event handling and recovery from partial copy/delete failures should be considered when hardening the workflow further.

### 4. Chatbot

1. The visitor opens the chatbot on the CloudFront website.
2. The frontend sends a message to `SupportChatAPI` in Singapore.
3. `LexChatProxy` invokes Amazon Lex V2 using `RecognizeText`.
4. Lex handles the configured intents and uses `LexSupportFulfillment` where backend fulfillment is required.
5. The fulfillment Lambda can call the Mumbai ticket API over HTTPS.

### 5. Monitoring and alerting

The project has four CloudWatch alarms:

- `CreateSupportTicket-Errors`
- `ProcessAttachmentScanResult-Errors`
- `LexChatProxy-Errors`
- `SupportTicketWorkflow-ExecutionsFailed`

Alarm actions use regional SNS email topics with confirmed subscriptions. Missing metric data is configured as not breaching.

An `INSUFFICIENT_DATA` state is not automatically an error. Verify the selected metric, Region, dimensions, and data availability before concluding that an alarm is working correctly.

## API routes

| Method | Route | Purpose |
|---|---|---|
| `POST` | `/tickets` | Create a support ticket |
| `GET` | `/tickets/{ticketId}` | Retrieve a ticket by ID |
| `POST` | `/tickets/{ticketId}/attachments` | Generate an attachment upload request |
| `POST` | `/chat` | Send a message to the chatbot |

The first three routes belong to `SupportPortalAPI` in Mumbai. The chatbot route belongs to `SupportChatAPI` in Singapore.

## Security controls

Implemented controls include:

- Private S3 buckets with Block Public Access enabled.
- CloudFront Origin Access Control for the private website origin.
- HTTPS delivery through CloudFront.
- IAM permissions scoped to the required resources and operations.
- Time-limited presigned upload requests.
- File-type and upload-size validation.
- Malware scanning and quarantine before acceptance.
- API Gateway throttling.
- CloudWatch alarms and SNS notifications.
- AWS budget and billing alerts.

### Known security limitations

This is a learning project, not a production-ready customer support system.

- The APIs currently permit unauthenticated requests.
- Ticket IDs do not prove ownership; ticket information needs proper authorization before real customer data is used.
- API throttling does not replace authentication, authorization, WAF protections, or cost controls.
- Presigned URLs are bearer credentials while valid and should not be exposed in logs or public repositories.
- Malware scanning and file-signature checks reduce risk but do not guarantee that every file is safe.
- Idempotency, duplicate scan events, and partial failures during object copying and deletion require careful testing.
- Production use would need a defined identity model, access-control policy, abuse protection, data-retention policy, and recovery procedures.

Use synthetic or dummy customer information for public demonstrations.

## Implementation Challenges and Lessons Learned

Building the project involved troubleshooting several issues that were not apparent when considering each AWS service independently.

- **Cross-origin requests and CloudFront:** Ticket-status requests initially failed in the browser because of CORS configuration. Troubleshooting required checking the API response headers and ensuring that the frontend origin and API configuration worked together.
- **Cross-Region chatbot integration:** Amazon Lex V2 and its chatbot API components were deployed in Singapore, while the main ticket backend runs in Mumbai. Connecting the chatbot to the ticket API required coordinating regional endpoints and Lambda permissions.
- **Attachment scanning workflow:** GuardDuty scan results were delivered through EventBridge to a Lambda processor. Troubleshooting required checking event routing, regional configuration, execution logs, and S3 permissions for copying eligible files into the accepted prefix.
- **CloudWatch monitoring:** Creating alarms was only part of the process. I also had to configure SNS email subscriptions, check metric selection and missing-data behavior, and distinguish `INSUFFICIENT_DATA` from an actual alarm state.

These experiences reinforced an important lesson: a cloud application depends not only on individual services, but also on correct permissions, regional configuration, event routing, API behavior, and observability across service boundaries.

## Testing performed

The following application behaviors have been tested during development:

- Ticket creation through the website.
- Ticket retrieval by ID.
- Attachment upload through a presigned request.
- Private attachment storage and denied anonymous S3 access.
- GuardDuty scan-result event processing and quarantine handling.
- Step Functions ticket-processing and failure-handling paths.
- Chatbot integration through the deployed website.
- CloudWatch log generation and alarm configuration.
- SNS email subscription confirmation.
- API Gateway throttling configuration.

Record fresh test evidence before publishing this list. Distinguish a configured alarm from a fully verified end-to-end alarm notification.

## Deployment approach

The initial implementation was configured through the AWS Management Console, with application code deployed to Lambda and the frontend hosted in S3 behind CloudFront.

This repository should contain the frontend source, Lambda source code where appropriate, the architecture diagram, test documentation, and deployment instructions. Do not claim that the infrastructure is reproducible through Terraform or CloudFormation unless those templates have actually been created and tested.

Deployment documentation should identify required AWS Regions, configuration variables, IAM permissions, API endpoints, and the order in which resources must be created.

Never commit AWS credentials, secret keys, session tokens, real customer data, or presigned URLs.

## Future improvements

- Add authentication and ticket ownership enforcement.
- Introduce stronger abuse protection and request validation.
- Make attachment scan processing idempotent and recoverable.
- Add automated integration tests for clean, malicious, skipped, and failed scan outcomes.
- Validate CloudWatch alarms and email delivery with controlled test scenarios.
- Add infrastructure as code using AWS SAM, CloudFormation, or Terraform.
- Document deployment, rollback, and cleanup procedures.
- Evaluate log retention, cost optimization, and data lifecycle policies.

## Learning outcomes

This project provided practical experience with:

- Serverless AWS architecture and event-driven integration.
- API Gateway, Lambda, and DynamoDB.
- Step Functions workflow orchestration.
- S3 security and presigned uploads.
- GuardDuty malware scanning and EventBridge events.
- Amazon Lex V2 integration across AWS Regions.
- IAM least-privilege design.
- CloudWatch monitoring, SNS notifications, and AWS budgets.

## Repository contents

```text
aws-serverless-customer-support/
├── README.md
├── architecture/
│   └── architecture.mmd
├── frontend/
│   └── index.html
├── lambdas/
│   ├── create-support-ticket/
│   ├── get-support-ticket/
│   ├── generate-upload-url/
│   ├── process-attachment-scan-result/
│   ├── lex-chat-proxy/
│   └── lex-support-fulfillment/
├── tests/
│   └── test-plan.md
└── docs/
    ├── screenshots.md
    ├── security-review.md
    └── deployment.md
```

## Author

**Nitesh Baniya**  
Computer Engineering | Pulchowk Campus, Institute of Engineering, Tribhuvan University

Project category: AWS Cloud Computing · Serverless Architecture · Cloud Security