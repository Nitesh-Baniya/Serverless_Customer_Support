# Serverless Customer Support Platform on AWS

A serverless customer support portal built using AWS managed services. It supports ticket creation and tracking, automated ticket processing, chatbot interactions, secure attachment uploads, malware scanning, and monitoring.

## Why I Built This Project

I built this project to gain hands-on experience with AWS serverless services and understand how they work together in a real application. Instead of deploying individual services separately, I wanted to build a complete application that combines backend development, workflow automation, cloud security, and monitoring.

Working on this project also helped me understand practical challenges such as S3 permissions, CORS configuration, cross-region communication, and troubleshooting AWS service integrations.

## Features

- **Ticket management:** Create support tickets and check their status.
- **Automated processing:** Use AWS Step Functions to validate, classify, and update tickets.
- **Chatbot:** Integrate Amazon Lex V2 for greetings, ticket creation, and status queries.
- **Secure file uploads:** Generate presigned upload requests for attachments.
- **Malware scanning:** Use GuardDuty Malware Protection for S3 to scan uploaded files.
- **Quarantine workflow:** Process scan results through EventBridge and Lambda, accepting only eligible clean and valid files.
- **Monitoring:** Use CloudWatch logs and alarms with SNS email notifications.
- **Cost monitoring:** Configure AWS Budget alerts to monitor spending.

## Architecture

The application uses two AWS Regions:

| Region | Purpose |
|---|---|
| Mumbai (`ap-south-1`) | Main API, ticket management, DynamoDB, Step Functions, and attachment scanning |
| Singapore (`ap-southeast-1`) | Amazon Lex V2 chatbot and chatbot API |

The frontend is hosted in a private S3 bucket and delivered over HTTPS through CloudFront using Origin Access Control (OAC).

### Architecture Diagram

![AWS Architecture Diagram](architecture/Architecture.png)

The diagram source is available at [`architecture/architecture.mmd`](architecture/architecture.mmd).

For a brief explanation of the components and their interactions, see [`docs/architecture.md`](docs/architecture.md).

## How It Works

### 1. Ticket Management

Users submit support tickets through the website. API Gateway invokes Lambda functions to create tickets in DynamoDB or retrieve existing ticket details.

### 2. Automated Ticket Processing

After ticket creation, Step Functions runs the validation, classification, and update steps. A separate failure-handling step records processing failures.

### 3. Attachment Upload and Scanning

Users upload files through presigned requests. Attachments are stored in the private S3 bucket under `quarantine/` and scanned by GuardDuty. EventBridge sends scan-result events to a Lambda function, which moves eligible clean and valid files to `accepted/`.

### 4. Chatbot

Amazon Lex V2 powers the website chatbot. It supports greetings, ticket creation conversations, and ticket-status queries. The chatbot runs in Singapore and communicates with the main ticket API in Mumbai when required.

### 5. Monitoring

CloudWatch collects logs and monitors configured Lambda errors and Step Functions failures. SNS provides email notifications for configured alarms.

## Screenshots

The screenshots below demonstrate the main application features and AWS configurations.

| Feature | Screenshot |
|---|---|
| Website | [CloudFront website](screenshots/CloudFront_website.png) |
| Ticket creation | [Ticket creation](screenshots/Ticket_creation.png) |
| Ticket status | [Ticket status](screenshots/Ticket_status.png) |
| Chatbot greeting | [Chatbot greeting](screenshots/Chatbot_greeting.png) |
| Chatbot ticket workflow | [Chatbot ticket workflow](screenshots/Chatbot_ticket_workflow.png) |
| Chatbot status lookup | [Chatbot status lookup](screenshots/Chatbot_status_lookup.png) |
| Attachment upload | [Attachment upload](screenshots/Attachment_upload.png) |
| CloudFront configuration | [CloudFront origin configuration](screenshots/CloudFront_origin_configuration.png) |
| API Gateway | [API Gateway routes](screenshots/API_Gateway_routes.png) |
| DynamoDB | [Ticket record](screenshots/DynamoDB_ticket_record.png) |
| Successful workflow | [Step Functions success](screenshots/Step_Functions_success.png) |
| Failure handling | [Step Functions failure handling](screenshots/Step_Functions_failure_handling.png) |
| Amazon Lex | [Lex configuration](screenshots/Amazon_Lex_configuration.png) |
| Private attachment storage | [Private attachment bucket](screenshots/Private_attachment_bucket.png) |
| GuardDuty | [GuardDuty configuration](screenshots/GuardDuty_configuration.png) |
| EventBridge | [EventBridge rule](screenshots/EventBridge_rule.png) |
| CloudWatch | [CloudWatch alarms](screenshots/CloudWatch_alarms.png) |
| Logs | [CloudWatch logs](screenshots/CloudWatch_logs.png) |
| Email alerts | [SNS email subscription](screenshots/SNS_email_subscription.png) |
| Budget monitoring | [AWS Budget](screenshots/AWS_Budget.png) |

For the full screenshot list, see [`docs/screenshots.md`](docs/screenshots.md).

## Security Considerations

Security measures implemented in this project include:

- Private S3 buckets with Block Public Access enabled.
- CloudFront OAC for private website content.
- HTTPS delivery through CloudFront.
- IAM roles with scoped permissions for Lambda functions.
- Time-limited presigned upload requests and file validation.
- Malware scanning before accepting attachments.
- API Gateway throttling.
- CloudWatch alarms and AWS Budget alerts.

**Limitations:** The current application does not implement user authentication or ticket ownership enforcement. API throttling and malware scanning alone do not make it production-ready. See [`docs/security-review.md`](docs/security-review.md) for more details.

## Testing

The application was tested during development, including:

- Creating and retrieving tickets.
- Executing successful and failed Step Functions workflows.
- Uploading attachments and checking private S3 access.
- Processing attachment scan results.
- Testing chatbot interactions and ticket-related requests.
- Checking monitoring configuration and API throttling.

See [`tests/test-plan.md`](tests/test-plan.md) for the test cases and results.

## Repository Structure

```text
.
├── README.md
├── architecture/
│   ├── architecture.mmd
│   └── Architecture.png
├── docs/
│   ├── architecture.md
│   ├── deployment.md
│   ├── lambdas.md
│   ├── screenshots.md
│   └── security-review.md
├── frontend/
│   └── index.html
├── lambdas/
│   ├── classify-support-ticket.py
│   ├── create-support-ticket.py
│   ├── generate-upload-url.py
│   ├── get-support-ticket.py
│   ├── lex-chat-proxy.py
│   ├── lex-support-fulfillment.py
│   ├── mark-ticketi-processing-failed.py
│   ├── process-attachment-scan-result.py
│   ├── update-support-ticket.py
│   └── validate-support-ticket.py
├── screenshots/
│   └── [Project screenshots]
└── tests/
    └── test-plan.md
```

## Documentation

- [Architecture overview](docs/architecture.md)
- [Deployment guide](docs/deployment.md)
- [Lambda function descriptions](docs/lambdas.md)
- [Screenshots](docs/screenshots.md)
- [Security review](docs/security-review.md)
- [Test plan and results](tests/test-plan.md)

## Lessons Learned

Through this project, I gained practical experience with AWS serverless architecture, IAM permissions, API integration, workflow orchestration, secure S3 uploads, malware scanning, cross-region communication, and monitoring.

One of the main lessons was that getting individual services working is only part of the process. Correct permissions, event routing, regional configuration, and error handling are equally important.

## Future Improvements

- Add authentication and ticket ownership checks.
- Improve abuse protection and request validation.
- Strengthen attachment-processing idempotency and recovery.
- Add automated integration tests.
- Explore infrastructure as code using AWS SAM, CloudFormation, or Terraform.

## Author

**Nitesh Baniya**  
Computer Engineering, Pulchowk Campus  
Institute of Engineering, Tribhuvan University

Project focus: AWS Cloud Computing, Serverless Architecture, and Cloud Security.