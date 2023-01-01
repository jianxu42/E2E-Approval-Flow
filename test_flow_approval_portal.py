import datetime as dt
import os
from datetime import datetime as dt_dt
from typing import Generator

import pytest
from playwright.sync_api import expect, Playwright, APIRequestContext, BrowserContext

APPROVAL_FLOW_TITLE_FOR_PORTAL = ''
PORTAL_FLOW_LOCATION = ''
TEST_USER = os.environ['TEST_USER']
TEST_PWD = os.environ['TEST_PWD']
TEST_FLOW = os.environ['TEST_FLOW']
TEST_APPROVAL_PORTAL = os.environ['TEST_APPROVAL_PORTAL']


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
    assert portal_flow_run.json()["outcome"] == "Approve"
    request_context.dispose()


def test_trigger_approval_flow(api_request_context: APIRequestContext) -> None:
    global APPROVAL_FLOW_TITLE_FOR_PORTAL
    APPROVAL_FLOW_TITLE_FOR_PORTAL = f'github-test_approval_portal@{dt_dt.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M:%S:%f")}'
    approval_flow_for_portal_data = {
        "title": APPROVAL_FLOW_TITLE_FOR_PORTAL,
        "tag": "github",
    }
    approval_flow_for_portal_flow_run = api_request_context.post(TEST_FLOW, data=approval_flow_for_portal_data)
    global PORTAL_FLOW_LOCATION
    PORTAL_FLOW_LOCATION = approval_flow_for_portal_flow_run.headers["location"]
    assert approval_flow_for_portal_flow_run.ok


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

    page.wait_for_timeout(3000)
    locator = page.locator("'Respond: Approve'")
    expect(locator).to_contain_text("Respond: Approve")

    context.tracing.stop(path="test_approval_portal_trace.zip")
