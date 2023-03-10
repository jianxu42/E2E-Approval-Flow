import datetime as dt
import logging
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
TEST_FLOW_ENV = os.environ['TEST_FLOW_ENV']
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
    teams_flow_run = request_context.get(TEAMS_FLOW_LOCATION).json()
    if str(teams_flow_run).find("outcome") != -1:
        assert teams_flow_run["outcome"] == "Approve"
    request_context.dispose()


def test_trigger_approval_flow(api_request_context: APIRequestContext) -> None:
    global APPROVAL_FLOW_TITLE_FOR_TEAMS
    APPROVAL_FLOW_TITLE_FOR_TEAMS = f'github-test_approval_teams@{dt_dt.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M:%S:%f")}'
    approval_flow_for_teams_data = {
        "title": APPROVAL_FLOW_TITLE_FOR_TEAMS,
        "approver": TEST_USER,
        "tag": "github",
    }
    approval_flow_for_teams_flow_run = api_request_context.post(TEST_FLOW, data=approval_flow_for_teams_data)
    global TEAMS_FLOW_LOCATION
    TEAMS_FLOW_LOCATION = approval_flow_for_teams_flow_run.headers["location"]
    assert approval_flow_for_teams_flow_run.ok
    logging.info(f"The approval flow {APPROVAL_FLOW_TITLE_FOR_TEAMS} for Teams was triggered!")


def test_approval_teams(context: BrowserContext) -> None:
    page = context.new_page()
    page.set_default_timeout(timeout=60000)
    try:
        page.goto(TEST_APPROVAL_TEAMS)

        page.get_by_placeholder("Email, phone, or Skype").click()
        page.get_by_placeholder("Email, phone, or Skype").fill(TEST_USER)
        page.get_by_role("button", name="Next").click()
        if page.locator("'Work or school account'").is_visible():
            page.locator("'Work or school account'").click()
        page.get_by_placeholder("Password").click()
        page.get_by_placeholder("Password").fill(TEST_PWD)
        page.get_by_role("button", name="Sign in").click()
        page.get_by_role("button", name="Yes").click()
        logging.info("Login Teams successful!")

        approval_tab_view = page.frame_locator("internal:attr=[title=\"Approvals Tab View\"i]")
        if approval_tab_view.get_by_role("menuitem", name="Export").is_enabled():
            approval_tab_view.get_by_role("menuitem", name="Export").click()
            approval_tab_view.get_by_role("button", name="Close").click()
        approval_tab_view.get_by_role("menuitem", name="Dynamics FTE GCR (default)").click()
        approval_tab_view.get_by_role("menuitemcheckbox", name=TEST_FLOW_ENV).click()
        approval_tab_view.get_by_role("gridcell", name=APPROVAL_FLOW_TITLE_FOR_TEAMS).click()
        approval_tab_view.get_by_role("button", name="Approve").click()
        page.get_by_role("button", name="Approvals Toolbar").click()
        approval_tab_view.get_by_role("gridcell", name=APPROVAL_FLOW_TITLE_FOR_TEAMS).click()
        expect(approval_tab_view.locator("'Final status: Approved'")).to_be_visible()
        logging.info(f"Approved {APPROVAL_FLOW_TITLE_FOR_TEAMS} from Teams!")

    except Exception as e:
        page.screenshot(path="teams_error.png")
        logging.error(e)
        exit(1)
