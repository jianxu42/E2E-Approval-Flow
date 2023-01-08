import logging
import os

from playwright.sync_api import BrowserContext

APPROVAL_FLOW_TITLE = 'test_approval'
TEST_USER = os.environ['TEST_USER']
TEST_PWD = os.environ['TEST_PWD']
TEST_APPROVAL_PORTAL = os.environ['TEST_APPROVAL_PORTAL']


def test_cleanup_approval_flow(context: BrowserContext):
    page = context.new_page()
    page.goto(TEST_APPROVAL_PORTAL)
    page.get_by_placeholder("Email, phone, or Skype").click()
    page.get_by_placeholder("Email, phone, or Skype").fill(TEST_USER)
    page.get_by_role("button", name="Next").click()
    page.get_by_placeholder("Password").click()
    page.get_by_placeholder("Password").fill(TEST_PWD)
    page.get_by_role("button", name="Sign in").click()
    page.get_by_role("button", name="Yes").click()
    page.wait_for_load_state("networkidle")
    if page.get_by_role("button", name="Close").is_visible():
        page.get_by_role("button", name="Close").click()
    while True:
        if len(page.get_by_role("button", name=APPROVAL_FLOW_TITLE).all()) > 0:
            li = page.get_by_role("button", name=APPROVAL_FLOW_TITLE).first
            title = li.text_content()
            li.click()
            page.get_by_text("Select an option").click()
            page.get_by_role("option", name="Approve").click()
            page.get_by_role("button", name="Confirm").click()
            page.get_by_role("button", name="Done").click()
            logging.info(f"Cleanup {title}!")
        else:
            break
