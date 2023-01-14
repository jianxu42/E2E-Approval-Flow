import datetime as dt
import logging
import os
from datetime import datetime as dt_dt
from typing import Generator

import pytest
from playwright.async_api import expect, BrowserContext
from playwright.sync_api import Playwright, APIRequestContext

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
    if str(portal_flow_run.json()).find("outcome") != -1:
        assert portal_flow_run["outcome"] == "Approve"
    request_context.dispose()


@pytest.mark.asyncio_cooperative
async def test_trigger_approval_flow(api_request_context: APIRequestContext) -> None:
    global APPROVAL_FLOW_TITLE_FOR_PORTAL
    APPROVAL_FLOW_TITLE_FOR_PORTAL = f'github-test_approval_portal@{dt_dt.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M:%S:%f")}'
    approval_flow_for_portal_data = {
        "title": APPROVAL_FLOW_TITLE_FOR_PORTAL,
        "approver": TEST_USER,
        "tag": "github",
    }
    approval_flow_for_portal_flow_run = await api_request_context.post(TEST_FLOW, data=approval_flow_for_portal_data)
    global PORTAL_FLOW_LOCATION
    PORTAL_FLOW_LOCATION = approval_flow_for_portal_flow_run.headers["location"]
    assert approval_flow_for_portal_flow_run.ok
    logging.info(f"The approval flow {APPROVAL_FLOW_TITLE_FOR_PORTAL} for portal was triggered!")


@pytest.mark.asyncio_cooperative
async def test_approval_portal(context: BrowserContext) -> None:
    page = await context.new_page()
    page.set_default_timeout(timeout=60000)
    try:
        await page.goto(TEST_APPROVAL_PORTAL)

        await page.get_by_placeholder("Email, phone, or Skype").click()
        await page.get_by_placeholder("Email, phone, or Skype").fill(TEST_USER)
        await page.get_by_role("button", name="Next").click()
        if await page.locator("'Work or school account'").is_visible():
            await page.locator("'Work or school account'").click()
        await page.get_by_placeholder("Password").click()
        await page.get_by_placeholder("Password").fill(TEST_PWD)
        await page.get_by_role("button", name="Sign in").click()
        await page.get_by_role("button", name="Yes").click()
        logging.info("Login portal successful!")

        await page.wait_for_load_state(state="networkidle", timeout=60000)
        if await page.get_by_role("button", name="Close").is_visible():
            await page.get_by_role("button", name="Close").click()
            logging.info("Found close button and clicked it!")
        if not page.get_by_role("button", name=f"{APPROVAL_FLOW_TITLE_FOR_PORTAL}").is_visible():
            await page.reload(wait_until="networkidle")
            logging.info("Reloaded the portal page!")
        await page.get_by_role("button", name=f"{APPROVAL_FLOW_TITLE_FOR_PORTAL}").click()
        await page.get_by_text("Select an option").click()
        await page.get_by_role("option", name="Approve").click()
        await page.get_by_role("button", name="Confirm").click()
        await page.wait_for_load_state()
        await expect(page.locator("'Response successfully recorded'")).to_be_visible(timeout=30000)
        logging.info(f"Approved {APPROVAL_FLOW_TITLE_FOR_PORTAL} from portal!")

    except Exception as e:
        await page.screenshot(path="portal_error.png")
        logging.error(e)
        exit(1)
