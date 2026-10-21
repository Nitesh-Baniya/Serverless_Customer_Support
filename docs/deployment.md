# Deployment Guide

## Overview

I deployed this project using the AWS Management Console and configured the services individually. The repository contains the application code and documentation, but it does not currently recreate the entire AWS environment automatically.

The main backend runs in **Mumbai (`ap-south-1`)**, while the chatbot uses **Singapore (`ap-southeast-1`)**.

## Prerequisites

- An AWS account with the required permissions.
- The project source code.
- An email address for monitoring notifications.
- Basic familiarity with the AWS Management Console.

Some AWS services may incur charges. Review usage and monitor your budget during deployment.

## Deployment Steps

### 1. Host the Frontend

1. Create an S3 bucket for the frontend in Mumbai.
2. Keep the bucket private and upload `frontend/index.html`.
3. Create a CloudFront distribution using the S3 bucket as its origin.
4. Configure Origin Access Control (OAC), the bucket policy, HTTPS, and `index.html` as the default root object.
5. Open the CloudFront URL and verify that the website loads.

### 2. Create the Ticket Backend

1. Create the DynamoDB table `SupportTickets` with the key schema expected by the Lambda code.
2. Deploy `CreateSupportTicket`, `GetSupportTicket`, and `GenerateUploadUrl` from the `lambdas/` directory in Mumbai.
3. Configure each Lambda's execution role and required environment variables.
4. Test the functions using synthetic data.
5. Verify that ticket creation stores a record and ticket retrieval returns the expected information.

### 3. Configure API Gateway

Create or configure `SupportPortalAPI` in Mumbai with these routes:

| Method | Route | Lambda |
|---|---|---|
| POST | `/tickets` | `CreateSupportTicket` |
| GET | `/tickets/{ticketId}` | `GetSupportTicket` |
| POST | `/tickets/{ticketId}/attachments` | `GenerateUploadUrl` |

Configure CORS for the frontend origin, deploy the API, and set the correct API base URL in the frontend.


### 4. Configure Step Functions

1. Create or configure `SupportTicketProcessingWorkflow` in Mumbai.
2. Configure its validation, classification, ticket-update, and failure-handling steps according to the workflow implementation.
3. Set the required execution permissions.
4. Configure ticket creation to start the workflow.
5. Test a successful execution and, if implemented, a controlled failure scenario.

### 5. Configure Attachment Storage and Scanning

1. Create or configure the private S3 bucket `support-attachments-aitac-team1-v1`.
2. Enable Block Public Access and configure the required CORS rules.
3. Configure `GenerateUploadUrl` to generate short-lived presigned upload requests for supported files.
4. Verify that new uploads use the `quarantine/` prefix.
5. Enable GuardDuty Malware Protection for S3 in Mumbai and configure the scan scope.
6. Create or verify the EventBridge rule that routes scan-result events to `ProcessAttachmentScanResult`.
7. Check the Lambda invocation permission and S3 permissions for reading quarantine objects, writing accepted objects, and deleting quarantine objects.
8. Test the workflow and verify that eligible clean files move to `accepted/` while non-clean or inconclusive results are not accepted.

### 6. Deploy the Chatbot

In Singapore:

1. Create or configure the Amazon Lex V2 bot `SupportAssistantBot`.
2. Configure the required intents, slots, prompts, and `TestBotAlias`.
3. Deploy `LexChatProxy` and `LexSupportFulfillment`.
4. Configure the fulfillment function to call the Mumbai ticket API over HTTPS.
5. Create or configure `SupportChatAPI` with `POST /chat` integrated with `LexChatProxy`.
6. Configure CORS and deploy the API.
7. Update the frontend with the chatbot API URL.

Test greetings, fallback responses, and ticket operations supported by the configured chatbot.

### 7. Configure Monitoring and Budget Alerts

1. Create CloudWatch alarms in the appropriate Regions for:
   - `CreateSupportTicket-Errors`
   - `ProcessAttachmentScanResult-Errors`
   - `LexChatProxy-Errors`
   - `SupportTicketWorkflow-ExecutionsFailed`
2. Configure the correct metrics, thresholds, and missing-data handling.
3. Create or configure SNS topics and confirm the email subscriptions in the relevant Regions.
4. Test alarm notifications using a safe test condition.
5. Configure the USD 5 monthly AWS Budget and its intended actual-spend and forecast-spend notifications.

Budget alerts provide visibility into spending; they are not a hard spending limit.

## Post-Deployment Checklist

- [ ] CloudFront website loads over HTTPS.
- [ ] Ticket creation and retrieval work.
- [ ] Step Functions processes a ticket.
- [ ] Attachment upload and scan-result processing work.
- [ ] Accepted attachments remain private.
- [ ] Chatbot responds and completes configured ticket operations.
- [ ] CloudWatch logs and alarms are configured.
- [ ] SNS notification delivery has been tested.
- [ ] AWS Budget notifications are configured.

Only mark a test complete after verifying the result.

## Troubleshooting

- **Website/API errors:** Check API URLs, CORS, API Gateway routes, and Lambda logs.
- **Attachment remains in quarantine:** Check GuardDuty scan results, EventBridge rule configuration, Region, Lambda permissions, and S3 permissions.
- **Chatbot fulfillment fails:** Check the Lex alias, Singapore API, Lambda logs, and Mumbai API endpoint.
- **Alarm shows `INSUFFICIENT_DATA`:** Check the metric, Region, evaluation period, and whether metric data is available.

## Cleanup

When finished, review and remove unused resources, including CloudFront, S3 buckets, API Gateway APIs, Lambda functions, DynamoDB, Step Functions, GuardDuty configuration, EventBridge rules, Lex resources, CloudWatch alarms, and SNS topics.

Check dependencies and stored objects before deleting resources. Some services may continue to incur charges until their resources are removed.

## Note

This is a manually deployed learning project. Reproducing it in another AWS account requires configuring the resources and permissions described above. Infrastructure as code using AWS SAM, CDK, or Terraform could be added later to make deployment more repeatable.
