# E2E-Approval-Flow

This is for verifying the approval flow from end to end.

Flow diagram
```mermaid
graph LR
    Playwright[GithubAction/Kubernetes]--S1:trigger-->ApprovalFlowEndpoint;
    Playwright[GithubAction/Kubernetes]--S2:approve-->FlowPortalApproval;
    Playwright[GithubAction/Kubernetes]--S2:approve-->TeamsApproval;
    Playwright[GithubAction/Kubernetes]--S2:approve-->MailApproval;
    Playwright[GithubAction/Kubernetes]--S3:check_status-->ApprovalFlowEndpoint;
```