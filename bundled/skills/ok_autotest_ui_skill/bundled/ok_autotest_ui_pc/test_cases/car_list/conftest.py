# test_cases/explore_list/conftest.py
#
# 覆盖父级 conftest 中的 page fixture，改为 module 级别：
# 同一个测试文件内的所有用例共享一个浏览器实例，减少启动开销。
import pytest
from utils.logger import setup_logger
from utils.testcase_support import finish_managed_page, start_managed_page

logger = setup_logger()


@pytest.fixture(scope="module")
def page(config):
    """
    浏览器页面 fixture（module 级）
    同一测试文件内所有用例共享同一个浏览器实例，文件执行结束后关闭。
    """
    browser_manager, page = start_managed_page(config)

    yield page

    finish_managed_page(browser_manager, page)
