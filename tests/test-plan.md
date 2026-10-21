# Test Plan

## 1. Overview

This document covers the tests performed on the Serverless Customer Support Platform during development. The tests verify ticket management, chatbot interactions, attachment security, workflow execution, and monitoring.

## 2. Test Cases and Results

| ID | Test | Expected Result | Status |
|---|---|---|---|
| TC-01 | Open the website through CloudFront | Website loads over HTTPS | Passed |
| TC-02 | Submit a support ticket with valid details | Ticket is created and stored in DynamoDB | Passed |
| TC-03 | Submit a ticket with missing or invalid details | Invalid input is handled appropriately | Passed |
| TC-04 | Retrieve a ticket using its ID | Correct ticket details are returned | Passed |
| TC-05 | Retrieve a non-existent ticket | An appropriate response is returned | Passed |
| TC-06 | Submit a ticket for processing | Step Functions executes the workflow | Passed |
| TC-07 | Trigger a workflow failure | Failure handling runs and the failure is recorded | Passed |
| TC-08 | Upload an allowed attachment | A valid PNG, JPEG, or PDF file can be uploaded | Passed |
| TC-09 | Upload an oversized or unsupported file | The upload is rejected | Passed |
| TC-10 | Process a clean attachment scan | A clean, valid file is moved to `accepted/` | Passed |
| TC-11 | Process an unsafe, failed, or inconclusive scan result | The file is not moved to `accepted/` | Passed |
| TC-12 | Access an attachment without authorization | Private S3 access is denied | Passed |
| TC-13 | Interact with the chatbot | Supported intents and fallback messages work | Passed |
| TC-14 | Create or check a ticket through the chatbot | The fulfillment function communicates with the main API correctly | Passed |
| TC-15 | Trigger a monitored Lambda error or workflow failure | CloudWatch alarm and configured email notification work as expected | Passed |
| TC-16 | Exceed API Gateway throttling limits | Excess requests are throttled | Passed |

## 3. Test Environment

- **Frontend:** Amazon CloudFront and private Amazon S3 bucket
- **Backend:** Amazon API Gateway, AWS Lambda, and DynamoDB
- **Workflow:** AWS Step Functions
- **Attachment security:** Amazon S3 and GuardDuty Malware Protection for S3
- **Chatbot:** Amazon Lex V2 and AWS Lambda
- **Monitoring:** Amazon CloudWatch and Amazon SNS

## 4. Test Summary

All listed test cases were tested during project development and passed in the tested scenarios. The results cover the main application features, workflow execution, attachment handling, chatbot integration, and configured monitoring controls.

These results reflect the tests performed during development; they do not guarantee that every possible input, attack, or failure scenario has been tested.