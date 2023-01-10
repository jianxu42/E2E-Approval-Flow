import datetime as dt
import logging
import os
from datetime import datetime as dt_dt
from typing import Generator

import pytest
from playwright.sync_api import Playwright, APIRequestContext, BrowserContext, expect

APPROVAL_FLOW_TITLE_FOR_PORTAL = ''
PORTAL_FLOW_LOCATION = ''
APPROVAL_FLOW_TITLE_FOR_MAIL = ''
MAIL_FLOW_LOCATION = ''
APPROVAL_FLOW_TITLE_FOR_TEAMS = ''
TEAMS_FLOW_LOCATION = ''
TEST_USER = os.environ['TEST_USER']
TEST_PWD = os.environ['TEST_PWD']
TEST_FLOW = os.environ['TEST_FLOW']
TEST_FLOW_ENV = os.environ['TEST_FLOW_ENV']
TEST_APPROVAL_PORTAL = os.environ['TEST_APPROVAL_PORTAL']
TEST_APPROVAL_MAIL = os.environ['TEST_APPROVAL_MAIL']
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
    portal_flow_run = request_context.get(PORTAL_FLOW_LOCATION).json()
    if str(portal_flow_run).find("outcome") != -1:
        assert portal_flow_run["outcome"] == "Approve"
    mail_flow_run = request_context.get(MAIL_FLOW_LOCATION).json()
    if str(mail_flow_run).find("outcome") != -1:
        assert mail_flow_run["outcome"] == "Approve"
    teams_flow_run = request_context.get(TEAMS_FLOW_LOCATION).json()
    if str(teams_flow_run).find("outcome") != -1:
        assert teams_flow_run["outcome"] == "Approve"
    request_context.dispose()


def test_trigger_approval_flow(api_request_context: APIRequestContext) -> None:
    global APPROVAL_FLOW_TITLE_FOR_PORTAL
    APPROVAL_FLOW_TITLE_FOR_PORTAL = f'k8s-test_approval_portal@{dt_dt.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M:%S:%f")}'
    approval_flow_for_portal_data = {
        "title": APPROVAL_FLOW_TITLE_FOR_PORTAL,
        "approver": TEST_USER,
        "tag": "k8s",
    }
    approval_flow_for_portal_flow_run = api_request_context.post(TEST_FLOW, data=approval_flow_for_portal_data)
    global PORTAL_FLOW_LOCATION
    PORTAL_FLOW_LOCATION = approval_flow_for_portal_flow_run.headers["location"]
    assert approval_flow_for_portal_flow_run.ok
    logging.info(f"The approval flow {APPROVAL_FLOW_TITLE_FOR_PORTAL} was triggered!")

    global APPROVAL_FLOW_TITLE_FOR_MAIL
    APPROVAL_FLOW_TITLE_FOR_MAIL = f'k8s-test_approval_mail@{dt_dt.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M:%S:%f")}'
    approval_flow_for_mail_data = {
        "title": APPROVAL_FLOW_TITLE_FOR_MAIL,
        "approver": TEST_USER,
        "tag": "k8s",
    }
    approval_flow_for_mail_flow_run = api_request_context.post(TEST_FLOW, data=approval_flow_for_mail_data)
    global MAIL_FLOW_LOCATION
    MAIL_FLOW_LOCATION = approval_flow_for_mail_flow_run.headers["location"]
    assert approval_flow_for_mail_flow_run.ok
    logging.info(f"The approval flow {APPROVAL_FLOW_TITLE_FOR_MAIL} was triggered!")

    global APPROVAL_FLOW_TITLE_FOR_TEAMS
    APPROVAL_FLOW_TITLE_FOR_TEAMS = f'k8s-test_approval_teams@{dt_dt.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M:%S:%f")}'
    approval_flow_for_teams_data = {
        "title": APPROVAL_FLOW_TITLE_FOR_TEAMS,
        "approver": TEST_USER,
        "tag": "k8s",
    }
    approval_flow_for_teams_flow_run = api_request_context.post(TEST_FLOW, data=approval_flow_for_teams_data)
    global TEAMS_FLOW_LOCATION
    TEAMS_FLOW_LOCATION = approval_flow_for_teams_flow_run.headers["location"]
    assert approval_flow_for_teams_flow_run.ok
    logging.info(f"The approval flow {APPROVAL_FLOW_TITLE_FOR_TEAMS} was triggered!")


def test_approval_portal(context: BrowserContext):
    page = context.new_page()
    page.set_default_timeout(timeout=60000)
    page.goto(TEST_APPROVAL_PORTAL)

    page.get_by_placeholder("Email, phone, or Skype").click()
    page.get_by_placeholder("Email, phone, or Skype").fill(TEST_USER)
    page.get_by_role("button", name="Next").click()
    page.get_by_placeholder("Password").click()
    page.get_by_placeholder("Password").fill(TEST_PWD)
    page.get_by_role("button", name="Sign in").click()
    page.get_by_role("button", name="Yes").click()
    logging.info("Login portal successful!")

    page.wait_for_load_state()
    if page.get_by_role("button", name="Close").is_visible():
        page.get_by_role("button", name="Close").click()
    if not page.get_by_role("button", name=f"{APPROVAL_FLOW_TITLE_FOR_PORTAL}").is_visible():
        page.reload(wait_until="networkidle")
    page.get_by_role("button", name=f"{APPROVAL_FLOW_TITLE_FOR_PORTAL}").click()
    page.get_by_text("Select an option").click()
    page.get_by_role("option", name="Approve").click()
    page.get_by_role("button", name="Confirm").click()
    page.wait_for_load_state()
    expect(page.locator("'Response successfully recorded'")).to_be_visible(timeout=30000)
    logging.info(f"Approved {APPROVAL_FLOW_TITLE_FOR_PORTAL} from portal!")


def test_approval_mail(context: BrowserContext):
    page = context.new_page()
    page.set_default_timeout(timeout=60000)
    page.goto(TEST_APPROVAL_MAIL)

    page.get_by_placeholder("Email, phone, or Skype").click()
    page.get_by_placeholder("Email, phone, or Skype").fill(TEST_USER)
    page.get_by_role("button", name="Next").click()
    page.get_by_placeholder("Password").click()
    page.get_by_placeholder("Password").fill(TEST_PWD)
    page.get_by_role("button", name="Sign in").click()
    page.get_by_role("button", name="Yes").click()
    logging.info("Login mail successful!")

    page.wait_for_load_state()
    while True:
        with page.expect_popup() as popup:
            page.get_by_text(APPROVAL_FLOW_TITLE_FOR_MAIL).first.dblclick()
        page_popup = popup.value
        if not page_popup.get_by_role("button", name="Approve").is_visible():
            page_popup.close()
        else:
            break
    page_popup.get_by_role("button", name="Approve").click()
    page_popup.get_by_role("button", name="Submit").click()
    page_popup.wait_for_load_state()
    expect(page_popup.locator("'The action completed successfully.'")).to_be_visible(timeout=30000) or expect(
        page_popup.locator("'Approved'")).to_be_visible(timeout=30000) or expect(
        page_popup.locator("'Date Submitted:'")).to_be_visible(timeout=30000)
    logging.info(f"Approved {APPROVAL_FLOW_TITLE_FOR_MAIL} from mail!")


def test_approval_teams(context: BrowserContext):
    page = context.new_page()
    page.set_default_timeout(timeout=60000)
    page.goto(TEST_APPROVAL_TEAMS)

    page.get_by_placeholder("Email, phone, or Skype").click()
    page.get_by_placeholder("Email, phone, or Skype").fill(TEST_USER)
    page.get_by_role("button", name="Next").click()
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
