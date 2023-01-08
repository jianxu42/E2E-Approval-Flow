import logging
import os

import pytest
from playwright.async_api import BrowserContext

APPROVAL_FLOW_TITLE = 'test_approval'
TEST_USER = os.environ['TEST_USER']
TEST_PWD = os.environ['TEST_PWD']
TEST_APPROVAL_PORTAL = os.environ['TEST_APPROVAL_PORTAL']


@pytest.mark.asyncio
async def test_cleanup_approval_flow(context: BrowserContext):
    page = await context.new_page()
    await page.goto(TEST_APPROVAL_PORTAL)
    await page.get_by_placeholder("Email, phone, or Skype").click()
    await page.get_by_placeholder("Email, phone, or Skype").fill(TEST_USER)
    await page.get_by_role("button", name="Next").click()
    await page.get_by_placeholder("Password").click()
    await page.get_by_placeholder("Password").fill(TEST_PWD)
    await page.get_by_role("button", name="Sign in").click()
    await page.get_by_role("button", name="Yes").click()

    await page.wait_for_load_state("networkidle")
    if await page.get_by_role("button", name="Close").is_visible():
        await page.get_by_role("button", name="Close").click()
    # while True:
    #     if len(await page.get_by_role("button", name=APPROVAL_FLOW_TITLE).all()) > 0:
    #         li = page.get_by_role("button", name=APPROVAL_FLOW_TITLE).first
    #         title = li.text_content()
    #         await li.click()
    #         await page.get_by_text("Select an option").click()
    #         await page.get_by_role("option", name="Approve").click()
    #         await page.get_by_role("button", name="Confirm").click()
    #         await page.get_by_role("button", name="Done").click()
    #         logging.info(f"Cleanup {title}!")
    #     else:
    #         break
