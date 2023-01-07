import datetime as dt
import logging
import os
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
mail_popup_page = None


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


def test_approval_mail(context: BrowserContext):
    global mail_popup_page
    page = context.new_page()
    page.set_default_timeout(60000)
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

        page.get_by_text(APPROVAL_FLOW_TITLE_FOR_MAIL).first.click()
        page.wait_for_load_state()
        page.get_by_role("menuitem", name="More mail actions").click()
        page.get_by_role("menuitem", name="View").filter(has_text="View").click()
        with page.expect_popup() as popup_page:
            page.get_by_role("menuitem", name="Open in new window").click()
        mail_popup_page = popup_page.value
        mail_popup_page.set_default_timeout(timeout=120000)
        mail_popup_page.wait_for_load_state()
        mail_popup_page.get_by_role("button", name="Approve").click()
        mail_popup_page.get_by_role("button", name="Submit").click()

        locator = mail_popup_page.locator("'Approved'")
        expect(locator).to_contain_text("Approved", timeout=30000)
        logging.info("Approved from mail!")

    except (TimeoutError, AssertionError) as e:
        page.screenshot(path="mail_error.png")
        mail_popup_page.screenshot(path="popup_mail_error.png")
        logging.error(e)
        exit(1)
