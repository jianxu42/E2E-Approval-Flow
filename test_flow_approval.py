import datetime as dt
import os
from datetime import datetime as dt_dt
from typing import Generator

import pytest
from playwright.sync_api import expect, Playwright, APIRequestContext, BrowserContext

APPROVAL_FLOW_TITLE_FOR_PORTAL = ''
APPROVAL_FLOW_TITLE_FOR_TEAMS = ''
APPROVAL_FLOW_TITLE_FOR_MAIL = ''
PORTAL_FLOW_LOCATION = ''
TEAMS_FLOW_LOCATION = ''
MAIL_FLOW_LOCATION = ''
TEST_USER = os.environ['TEST_USER']
TEST_PWD = os.environ['TEST_PWD']
TEST_FLOW = os.environ['TEST_FLOW']
TEST_APPROVAL_PORTAL = os.environ['TEST_APPROVAL_PORTAL']
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
    portal_flow_run = request_context.get(PORTAL_FLOW_LOCATION)
    teams_flow_run = request_context.get(TEAMS_FLOW_LOCATION)
    mail_flow_run = request_context.get(MAIL_FLOW_LOCATION)
    assert portal_flow_run.json()["outcome"] == "Approve"
    assert teams_flow_run.json()["outcome"] == "Approve"
    assert mail_flow_run.json()["outcome"] == "Approve"
    request_context.dispose()


def test_trigger_approval_flow(api_request_context: APIRequestContext) -> None:
    global APPROVAL_FLOW_TITLE_FOR_PORTAL
    APPROVAL_FLOW_TITLE_FOR_PORTAL = f'test_approval_portal@{dt_dt.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M:%S:%f")}'
    approval_flow_for_portal_data = {
        "title": APPROVAL_FLOW_TITLE_FOR_PORTAL,
        "tag": "pytest",
    }
    approval_flow_for_portal_flow_run = api_request_context.post(TEST_FLOW, data=approval_flow_for_portal_data)
    global PORTAL_FLOW_LOCATION
    PORTAL_FLOW_LOCATION = approval_flow_for_portal_flow_run.headers["location"]
    assert approval_flow_for_portal_flow_run.ok

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

    global APPROVAL_FLOW_TITLE_FOR_MAIL
    APPROVAL_FLOW_TITLE_FOR_MAIL = f'test_approval_mail@{dt_dt.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M:%S:%f")}'
    approval_flow_for_mail_data = {
        "title": APPROVAL_FLOW_TITLE_FOR_MAIL,
        "tag": "pytest",
    }
    approval_flow_for_mail_flow_run = api_request_context.post(TEST_FLOW, data=approval_flow_for_mail_data)
    global MAIL_FLOW_LOCATION
    MAIL_FLOW_LOCATION = approval_flow_for_mail_flow_run.headers["location"]
    assert approval_flow_for_mail_flow_run.ok


def test_approval_portal(context: BrowserContext):
    context.tracing.start(screenshots=True, snapshots=True, sources=True)
    page = context.new_page()
    page.goto(TEST_APPROVAL_PORTAL)

    page.get_by_placeholder("Email, phone, or Skype").click()
    page.get_by_placeholder("Email, phone, or Skype").fill(TEST_USER)
    page.get_by_role("button", name="Next").click()
    page.get_by_placeholder("Password").click()
    page.get_by_placeholder("Password").fill(TEST_PWD)
    page.get_by_role("button", name="Sign in").click()
    page.get_by_role("button", name="Yes").click()

    page.get_by_role("button", name=f"{APPROVAL_FLOW_TITLE_FOR_PORTAL}").click()
    page.get_by_text("Select an option").click()
    page.get_by_role("option", name="Approve").click()
    page.get_by_role("button", name="Confirm").click()

    locator = page.locator("'Respond: Approve'")
    expect(locator).to_contain_text("Respond: Approve")

    context.tracing.stop(path="test_approval_portal_trace.zip")


def test_approval_teams(context: BrowserContext):
    context.tracing.start(screenshots=True, snapshots=True, sources=True)
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


def test_approval_mail(context: BrowserContext):
    context.tracing.start(screenshots=True, snapshots=True, sources=True)
    page = context.new_page()
    page.goto("https://outlook.office.com/mail/")

    page.get_by_placeholder("Email, phone, or Skype").click()
    page.get_by_placeholder("Email, phone, or Skype").fill(TEST_USER)
    page.get_by_role("button", name="Next").click()
    page.get_by_placeholder("Password").click()
    page.get_by_placeholder("Password").fill(TEST_PWD)
    page.get_by_role("button", name="Sign in").click()
    page.get_by_role("button", name="Yes").click()

    page.get_by_text(APPROVAL_FLOW_TITLE_FOR_MAIL).first.click()
    page.get_by_role("menuitem", name="More mail actions").click()
    page.get_by_role("menuitem", name="View").filter(has_text="View").click()
    with page.expect_popup() as page_info:
        page.get_by_role("menuitem", name="Open in new window").click()
    popup_page = page_info.value
    popup_page.get_by_role("button", name="Approve").click()
    popup_page.get_by_role("button", name="Submit").click()

    locator = popup_page.locator("'Approved'")
    expect(locator).to_contain_text("Approved")

    context.tracing.stop(path="test_approval_mail.zip")
