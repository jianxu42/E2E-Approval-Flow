import datetime
import os
import re
from typing import Generator

import pytest
from playwright.sync_api import Page, expect, Playwright, APIRequestContext

APPROVAL_FLOW_TITLE_FOR_PORTAL = ""
APPROVAL_FLOW_TITLE_FOR_MAIL = ""
APPROVAL_FLOW_TITLE_FOR_TEAMS = ""
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
    request_context.dispose()


def test_trigger_approval_flow_for_portal(api_request_context: APIRequestContext) -> None:
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S:%f")
    global APPROVAL_FLOW_TITLE_FOR_PORTAL
    APPROVAL_FLOW_TITLE_FOR_PORTAL = f'test_approval@{now}'
    data = {
        "title": APPROVAL_FLOW_TITLE_FOR_PORTAL,
        "tag": "pytest",
    }
    flow_run = api_request_context.post(TEST_FLOW, data=data)
    assert flow_run.ok


def test_trigger_approval_flow_for_mail(api_request_context: APIRequestContext) -> None:
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S:%f")
    global APPROVAL_FLOW_TITLE_FOR_MAIL
    APPROVAL_FLOW_TITLE_FOR_MAIL = f'test_approval@{now}'
    data = {
        "title": APPROVAL_FLOW_TITLE_FOR_MAIL,
        "tag": "pytest",
    }
    flow_run = api_request_context.post(TEST_FLOW, data=data)
    assert flow_run.ok


def test_trigger_approval_flow_for_teams(api_request_context: APIRequestContext) -> None:
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S:%f")
    global APPROVAL_FLOW_TITLE_FOR_TEAMS
    APPROVAL_FLOW_TITLE_FOR_TEAMS = f'test_approval@{now}'
    data = {
        "title": APPROVAL_FLOW_TITLE_FOR_TEAMS,
        "tag": "pytest",
    }
    flow_run = api_request_context.post(TEST_FLOW, data=data)
    assert flow_run.ok


def test_approval_portal(page: Page):
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

    page.wait_for_timeout(5000)
    page.screenshot(path="approval.png", full_page=True)

    locator = page.locator("'Respond: Approve'")
    expect(locator).to_contain_text("Respond: Approve")
    expect(page).to_have_url(re.compile(".*approvals.*"))


def test_approval_teams(page: Page):
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
    page.wait_for_timeout(5000)
    page.screenshot(path="teams.png", full_page=True)

    locator = approval_tab_view.locator("'Final status: Approved'")
    expect(locator).to_contain_text("Final status: Approved")
    expect(page).to_have_url(re.compile(".*teams.*"))


def test_approval_mail(page: Page):
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

    popup_page.wait_for_timeout(5000)
    popup_page.screenshot(path="mail.png", full_page=True)

    locator = popup_page.locator("'Approved'")
    expect(locator).to_contain_text("Approved")
