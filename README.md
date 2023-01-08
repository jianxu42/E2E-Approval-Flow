# E2E-Approval-Flow

The purpose of this verification is to ensure the end-to-end functionality of the approval process.
It can be deployed on k8s or GitHub Actions.

[![Synthetic Tests](https://github.com/jianxu42/E2E-Approval-Flow/actions/workflows/sch.yml/badge.svg?branch=main)](https://github.com/jianxu42/E2E-Approval-Flow/actions/workflows/sch.yml)

#### Flow diagram

```mermaid
graph LR
    Playwright[GithubAction/Kubernetes]--S1:trigger-->ApprovalFlow;
    ApprovalFlow--S2:send-->PortalApproval;
    ApprovalFlow--S2:send-->TeamsApproval;
    ApprovalFlow--S2:send-->MailApproval;
    Playwright[GithubAction/Kubernetes]--S3:approve-->PortalApproval;
    Playwright[GithubAction/Kubernetes]--S3:approve-->TeamsApproval;
    Playwright[GithubAction/Kubernetes]--S3:approve-->MailApproval;
    Playwright[GithubAction/Kubernetes]--S4:check_status-->ApprovalFlow;
```

#### Approval Flow

![Alt text](approval_flow.png)

#### Tools & Documents

- [Power Automate](https://powerautomate.microsoft.com/)
- [Approvals](https://learn.microsoft.com/en-us/connectors/approvals/)
- [Playwright](https://playwright.dev/python/)
- [GitHub Actions](https://github.com/actions)
- [Kubernetes](https://kubernetes.io/)
- [Docker](https://www.docker.com/)
- [Foresight](https://www.runforesight.com/)
- [Synthetic Monitoring Tests](https://microsoft.github.io/code-with-engineering-playbook/automated-testing/synthetic-monitoring-tests/)
