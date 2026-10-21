# Lambda Functions

This project uses AWS Lambda to handle ticket management, workflow processing, attachment security, and chatbot integration.

| Lambda Function | Description |
|---|---|
| `CreateSupportTicket` | Creates a new support ticket, stores it in DynamoDB, and starts the Step Functions workflow. |
| `GetSupportTicket` | Retrieves ticket details from DynamoDB using the ticket ID. |
| `GenerateUploadUrl` | Generates a presigned upload request so users can upload attachments to the private S3 quarantine folder. |
| `ValidateSupportTicket` | Validates ticket information as part of the Step Functions workflow. |
| `ClassifySupportTicket` | Classifies support tickets based on their details during workflow processing. |
| `UpdateSupportTicket` | Updates ticket information and processing status in DynamoDB. |
| `MarkTicketProcessingFailed` | Records a processing failure when the ticket workflow encounters an error. |
| `ProcessAttachmentScanResult` | Handles GuardDuty scan results and moves clean, valid attachments from `quarantine/` to `accepted/`. |
| `LexChatProxy` | Receives chatbot messages through API Gateway and sends them to Amazon Lex V2. |
| `LexSupportFulfillment` | Handles ticket creation and status-checking requests from Lex and communicates with the main support API. |

## Runtime and Permissions

The functions use Python and AWS service integrations. Each function has an IAM execution role that grants access to the AWS resources required for its tasks.