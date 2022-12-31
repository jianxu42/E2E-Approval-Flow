import datetime as dt
import os
from datetime import datetime as dt_dt
from typing import Generator

import pytest
from playwright.sync_api import expect, Playwright, APIRequestContext, BrowserContext

APPROVAL_FLOW_TITLE_FOR_TEAMS = ''
TEAMS_FLOW_LOCATION = ''
TEST_USER = os.environ['TEST_USER']
TEST_PWD = os.environ['TEST_PWD']
TEST_FLOW = os.environ['TEST_FLOW']
TEST_APPROVAL_TEAMS = os.environ['TEST_APPROVAL_TEAMS']


@pytest.fixture(scope="session")
def api_request_context(
        playwright: Playwright,
) -> Generator[APIRequestContext, None, None]:
    headers = {
        "Accept": "application/json",
    }
    request_context = playwright.request.new_context(
        base_url="https://make.powerautomate.com",
        extra_http_headers=headers
    )
    yield request_context
    teams_flow_run = request_context.get(TEAMS_FLOW_LOCATION)
    assert teams_flow_run.json()["outcome"] == "Approve"
    request_context.dispose()


def test_trigger_approval_flow(api_request_context: APIRequestContext) -> None:
    global APPROVAL_FLOW_TITLE_FOR_TEAMS
    APPROVAL_FLOW_TITLE_FOR_TEAMS = f'test_approval_teams@{dt_dt.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M:%S:%f")}'
    approval_flow_for_teams_data = {
        "title": APPROVAL_FLOW_TITLE_FOR_TEAMS,
        "tag": "pytest",
    }
    approval_flow_for_teams_flow_run = api_request_context.post(TEST_FLOW, data=approval_flow_for_teams_data)
    global TEAMS_FLOW_LOCATION
    TEAMS_FLOW_LOCATION = approval_flow_for_teams_flow_run.headers["location"]
    assert approval_flow_for_teams_flow_run.ok


def test_approval_teams(context: BrowserContext):
    context.tracing.start(screenshots=False, snapshots=True, sources=False)
    page = context.new_page()
    page.goto("https://teams.microsoft.com/")

    page.get_by_placeholder("Email, phone, or Skype").click()
    page.get_by_placeholder("Email, phone, or Skype").fill(TEST_USER)
    page.get_by_role("button", name="Next").click()
    page.get_by_placeholder("Password").click()
    page.get_by_placeholder("Password").fill(TEST_PWD)
    page.get_by_role("button", name="Sign in").click()
    page.get_by_role("button", name="Yes").click()

    page.goto(TEST_APPROVAL_TEAMS)
    approval_tab_view = page.frame_locator("internal:attr=[title=\"Approvals Tab View\"i]")
    approval_tab_view.get_by_role("button", name="Got it").click()
    approval_tab_view.get_by_role("menuitem", name="Dynamics FTE GCR (default)").click()
    approval_tab_view.get_by_role("menuitemcheckbox", name="JianTestSolution").click()
    approval_tab_view.get_by_role("gridcell", name=APPROVAL_FLOW_TITLE_FOR_TEAMS).click()
    approval_tab_view.get_by_role("button", name="Approve").click()
    page.get_by_role("button", name="Approvals Toolbar").click()

    approval_tab_view.get_by_role("gridcell", name=APPROVAL_FLOW_TITLE_FOR_TEAMS).click()
    locator = approval_tab_view.locator("'Final status: Approved'")
    expect(locator).to_contain_text("Final status: Approved")

    context.tracing.stop(path="test_approval_teams.zip")
