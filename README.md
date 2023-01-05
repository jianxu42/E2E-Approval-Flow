# E2E-Approval-Flow

The purpose of this verification is to ensure the end-to-end functionality of the approval process.
It can be deployed on k8s or GitHub Actions.

#### Flow diagram
```mermaid
graph LR
    Playwright[GithubAction/Kubernetes]--S1:trigger-->ApprovalFlow;
    ApprovalFlow--S2:send-->FlowPortalApproval;
    ApprovalFlow--S2:send-->TeamsApproval;
    ApprovalFlow--S2:send-->MailApproval;
    Playwright[GithubAction/Kubernetes]--S3:approve-->FlowPortalApproval;
    Playwright[GithubAction/Kubernetes]--S3:approve-->TeamsApproval;
    Playwright[GithubAction/Kubernetes]--S3:approve-->MailApproval;
    Playwright[GithubAction/Kubernetes]--S4:check_status-->ApprovalFlow;
```

#### Approval Flow
![Alt text](approval_flow.png)

#### Tools
- [Power Automate](https://powerautomate.microsoft.com/)
- [Approvals](https://learn.microsoft.com/en-us/connectors/approvals/)
- [Playwright](https://playwright.dev/python/)
- [Github Actions](https://github.com/actions)
- [Kubernetes](https://kubernetes.io/)
- [Docker](https://www.docker.com/)
