# E2E-Approval-Flow

This is for verifying the approval flow from end to end.

Flow diagram
```mermaid
graph LR
    Playwright[GithubAction]--S1:trigger-->ApprovalFlowEndpoint;
    Playwright[GithubAction]--S1:trigger-->ApprovalFlowEndpoint;
    Playwright[GithubAction]--S1:trigger-->ApprovalFlowEndpoint;
    Playwright[GithubAction]--S2:approve-->FlowPortalApproval;
    Playwright[GithubAction]--S2:approve-->TeamsApproval;
    Playwright[GithubAction]--S2:approve-->MailApproval;
    Playwright[GithubAction]--S3:check_status-->ApprovalFlowEndpoint;
    Playwright[GithubAction]--S3:check_status-->ApprovalFlowEndpoint;
    Playwright[GithubAction]--S3:check_status-->ApprovalFlowEndpoint;
```