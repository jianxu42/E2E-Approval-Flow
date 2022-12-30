# E2E-Approval-Flow

This is for verifying the approval flow from end to end.

```mermaid
graph TD;
    GithubAction-->PowerAutomateEndpoint;
    GithubAction-->PowerAutomateApprovalPortal;
    GithubAction-->TeamsApproval;
    GithubAction-->MailApproval;
```