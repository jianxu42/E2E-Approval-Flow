# E2E-Approval-Flow

This is for verifying the approval flow from end to end.

Flow diagram
```mermaid
graph LR
    GithubAction[Playwright]--trigger_flow-->FlowEndpoint;
    GithubAction[Playwright]--approve-->FlowPortalApproval;
    GithubAction[Playwright]--trigger_flow-->FlowEndpoint;
    GithubAction[Playwright]--approve-->TeamsApproval;
    GithubAction[Playwright]--trigger_flow-->FlowEndpoint;
    GithubAction[Playwright]--approve-->MailApproval;
    GithubAction[Playwright]--check_status-->FlowEndpoint;
    GithubAction[Playwright]--check_status-->FlowEndpoint;
    GithubAction[Playwright]--check_status-->FlowEndpoint;
```