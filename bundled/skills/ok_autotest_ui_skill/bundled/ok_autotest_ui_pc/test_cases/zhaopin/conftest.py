# test_cases/zhaopin/conftest.py
"""
招聘模块（zhaopin）专用配置
强制使用新加坡站（SITE=sg），确保 ConfigLoader 在首次加载时使用正确站点
Session 复用：仅第一次需要登录，后续用例加载已保存的 Cookie（见 sg_login_helper）
"""
import os

# 招聘模块测试必须使用新加坡站
os.environ["SITE"] = "sg"
os.environ["ROLE"] = "seller"
os.environ["USER_NAME"] = "dc_seller_sg"
