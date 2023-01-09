import datetime as dt
import logging
import os
from datetime import datetime as dt_dt
from typing import Generator

import pytest
from playwright.sync_api import Playwright, APIRequestContext, expect, BrowserContext, TimeoutError

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
    portal_flow_run = request_context.get(PORTAL_FLOW_LOCATION).json()
    if str(portal_flow_run).find("outcome") != -1:
        assert portal_flow_run["outcome"] == "Approve"
    request_context.dispose()


def test_trigger_approval_flow(api_request_context: APIRequestContext) -> None:
    global APPROVAL_FLOW_TITLE_FOR_PORTAL
    APPROVAL_FLOW_TITLE_FOR_PORTAL = f'github-test_approval_portal@{dt_dt.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M:%S:%f")}'
    approval_flow_for_portal_data = {
        "title": APPROVAL_FLOW_TITLE_FOR_PORTAL,
        "approver": TEST_USER,
        "tag": "github",
    }
    approval_flow_for_portal_flow_run = api_request_context.post(TEST_FLOW, data=approval_flow_for_portal_data)
    global PORTAL_FLOW_LOCATION
    PORTAL_FLOW_LOCATION = approval_flow_for_portal_flow_run.headers["location"]
    assert approval_flow_for_portal_flow_run.ok
    logging.info(f"The approval flow {APPROVAL_FLOW_TITLE_FOR_PORTAL} for portal was triggered!")


def test_approval_portal(context: BrowserContext) -> None:
    page = context.new_page()
    page.set_default_timeout(timeout=60000)
    try:
        page.goto(TEST_APPROVAL_PORTAL)

        page.get_by_placeholder("Email, phone, or Skype").click()
        page.get_by_placeholder("Email, phone, or Skype").fill(TEST_USER)
        page.get_by_role("button", name="Next").click()
        page.get_by_placeholder("Password").click()
        page.get_by_placeholder("Password").fill(TEST_PWD)
        page.get_by_role("button", name="Sign in").click()
        page.get_by_role("button", name="Yes").click()
        logging.info("Login portal successful!")

        page.wait_for_load_state("networkidle")
        while True:
            if page.get_by_role("button", name="Close").is_visible():
                page.get_by_role("button", name="Close").click()
            if not page.get_by_role("button", name=f"{APPROVAL_FLOW_TITLE_FOR_PORTAL}").is_visible():
                page.reload()
            else:
                break
        page.get_by_role("button", name=f"{APPROVAL_FLOW_TITLE_FOR_PORTAL}").click()
        page.get_by_text("Select an option").click()
        page.get_by_role("option", name="Approve").click()
        page.get_by_role("button", name="Confirm").click()
        page.wait_for_load_state()
        expect(page.locator("'Response successfully recorded'")).to_be_visible()
        logging.info(f"Approved {APPROVAL_FLOW_TITLE_FOR_PORTAL} from portal!")

    except (TimeoutError, AssertionError) as e:
        page.screenshot(path="portal_error.png")
        logging.error(e)
        exit(1)
