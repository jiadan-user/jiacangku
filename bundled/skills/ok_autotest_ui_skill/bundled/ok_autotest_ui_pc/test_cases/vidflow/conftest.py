# test_cases/vidflow/conftest.py
"""
Vidflow 群发任务测试专用：所有用例共用一个浏览器页面（module 作用域），无头运行。
仅对 test_cases/vidflow/ 下的测试生效，不影响其他模块。
"""
import os
import pytest
from utils.testcase_support import finish_managed_page, start_managed_page


@pytest.fixture(scope="module")
def page(config):
    """
    模块内共用一个浏览器页面：只启动一次浏览器，22 个 case 在同一页面中顺序执行。
    配合 _CONFIG["browser"]["headless"]=True 实现无头 + 单页。
    """
    browser_manager, page = start_managed_page(config)
    yield page
    finish_managed_page(browser_manager, page)
