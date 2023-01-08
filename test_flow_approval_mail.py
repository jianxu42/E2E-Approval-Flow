import datetime as dt
import logging
import os
import time
from datetime import datetime as dt_dt
from typing import Generator

import pytest
from playwright.sync_api import expect, Playwright, APIRequestContext, BrowserContext, TimeoutError

APPROVAL_FLOW_TITLE_FOR_MAIL = ''
MAIL_FLOW_LOCATION = ''
TEST_USER = os.environ['TEST_USER']
TEST_PWD = os.environ['TEST_PWD']
TEST_FLOW = os.environ['TEST_FLOW']
TEST_APPROVAL_MAIL = os.environ['TEST_APPROVAL_MAIL']
page_popup = None


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
    mail_flow_run = request_context.get(MAIL_FLOW_LOCATION).json()
    if str(mail_flow_run).find("outcome") != -1:
        assert mail_flow_run["outcome"] == "Approve"
    request_context.dispose()


def test_trigger_approval_flow(api_request_context: APIRequestContext) -> None:
    global APPROVAL_FLOW_TITLE_FOR_MAIL
    APPROVAL_FLOW_TITLE_FOR_MAIL = f'github-test_approval_mail@{dt_dt.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M:%S:%f")}'
    approval_flow_for_mail_data = {
        "title": APPROVAL_FLOW_TITLE_FOR_MAIL,
        "approver": TEST_USER,
        "tag": "github",
    }
    approval_flow_for_mail_flow_run = api_request_context.post(TEST_FLOW, data=approval_flow_for_mail_data)
    global MAIL_FLOW_LOCATION
    MAIL_FLOW_LOCATION = approval_flow_for_mail_flow_run.headers["location"]
    assert approval_flow_for_mail_flow_run.ok
    logging.info("The approval flow for mail was triggered!")


def test_approval_mail(context: BrowserContext) -> None:
    global page_popup
    page = context.new_page()
    try:
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
        page.get_by_text(APPROVAL_FLOW_TITLE_FOR_MAIL).first.click()
        # this depends on the render time for adaptive card from the server, set 8 seconds for now
        time.sleep(8)
        with page.expect_popup() as popup:
            page.get_by_text(APPROVAL_FLOW_TITLE_FOR_MAIL).first.dblclick()
        page_popup = popup.value
        if page_popup.get_by_role("button", name="Approve").is_visible():
            page_popup.get_by_role("button", name="Approve").click()
        else:
            page_popup.close()
            with page.expect_popup() as popup:
                page.get_by_text(APPROVAL_FLOW_TITLE_FOR_MAIL).first.dblclick()
            page_popup = popup.value
            page_popup.get_by_role("button", name="Approve").click()
        page_popup.get_by_role("button", name="Submit").click()

        locator = page_popup.locator("'Approved'")
        expect(locator).to_contain_text("Approved", timeout=30000)
        logging.info(f"Approved {APPROVAL_FLOW_TITLE_FOR_MAIL} from mail!")

    except (TimeoutError, AssertionError) as e:
        page.screenshot(path="mail_page_error.png")
        page_popup.screenshot(path="mail_page_popup_error.png")
        logging.error(e)
        exit(1)
