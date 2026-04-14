#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通用Markdown格式测试用例生成器
支持任何项目，格式标准化便于阅读、编辑和版本管理
"""

from datetime import datetime
from typing import List, Dict


class TestCase:
    """测试用例数据结构"""
    
    def __init__(self, tc_id: str, title: str, preconditions: List[str],
                 steps: List[str], expected: List[str], priority: str, 
                 test_type: str, ui_automation: bool = True, group: str = ""):
        self.tc_id = tc_id
        self.title = title
        self.preconditions = preconditions
        self.steps = steps
        self.expected = expected
        self.priority = priority
        self.test_type = test_type
        self.ui_automation = ui_automation
        self.group = group


class MarkdownTestCaseGenerator:
    """Markdown测试用例生成器"""
    
    def __init__(self, project_name: str, test_scope: str = ""):
        self.project_name = project_name
        self.test_scope = test_scope or "全功能测试"
        self.test_cases: List[TestCase] = []
        self.groups: Dict[str, List[TestCase]] = {}
        
    def add_test_case(self, test_case: TestCase):
        """添加测试用例"""
        self.test_cases.append(test_case)
        
        # 按分组归类
        if test_case.group not in self.groups:
            self.groups[test_case.group] = []
        self.groups[test_case.group].append(test_case)
    
    def generate_markdown(self, output_path: str = None):
        """生成Markdown文件"""
        
        content = self._generate_header()
        content += self._generate_toc()
        content += self._generate_overview()
        content += self._generate_test_cases()
        content += self._generate_statistics()
        
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Markdown测试用例已生成: {output_path}")
        
        return content
    
    def _generate_header(self) -> str:
        """生成文件头部"""
        date = datetime.now().strftime("%Y-%m-%d")
        
        # 统计自动化用例
        automatable = sum(1 for tc in self.test_cases if tc.ui_automation)
        auto_rate = f"{automatable/len(self.test_cases)*100:.0f}%" if self.test_cases else "0%"
        
        return f"""# {self.project_name} - 测试用例文档

> **生成时间**: {date}  
> **测试范围**: {self.test_scope}  
> **总用例数**: {len(self.test_cases)}条  
> **可自动化**: {automatable}条 ({auto_rate})

---

"""
    
    def _generate_toc(self) -> str:
        """生成目录"""
        toc = "## 📑 目录\n\n"
        toc += "- [测试概述](#测试概述)\n"
        toc += "- [测试用例](#测试用例)\n"
        
        for group_name in self.groups.keys():
            # 转换为锚点格式
            anchor = group_name.lower().replace(' ', '-').replace('(', '').replace(')', '')
            toc += f"  - [{group_name}](#{anchor})\n"
        
        toc += "- [测试统计](#测试统计)\n\n"
        toc += "---\n\n"
        return toc
    
    def _generate_overview(self) -> str:
        """生成测试概述"""
        return f"""## 测试概述

### 测试目标
验证{self.project_name}的功能完整性、稳定性和安全性。

### 测试环境
- **浏览器**: Chrome 120+, Safari 17+, Firefox 120+
- **操作系统**: macOS, Windows
- **测试账号**: 需准备不同权限的测试账号

### 全局前置条件
- 测试环境已部署
- 测试数据已准备
- 测试账号已创建

---

"""
    
    def _generate_test_cases(self) -> str:
        """生成所有测试用例"""
        content = "## 测试用例\n\n"
        
        for group_name, cases in self.groups.items():
            content += f"### {group_name}\n\n"
            
            for case in cases:
                content += self._format_test_case(case)
        
        return content
    
    def _format_test_case(self, case: TestCase) -> str:
        """格式化单条测试用例"""
        tc = f"#### {case.tc_id}: {case.title}\n\n"
        
        # 前置条件
        tc += "**前置条件**:\n"
        if case.preconditions:
            for pre in case.preconditions:
                tc += f"- {pre}\n"
        else:
            tc += "- 无\n"
        tc += "\n"
        
        # 执行步骤
        tc += "**执行步骤**:\n"
        for i, step in enumerate(case.steps, 1):
            tc += f"{i}. {step}\n"
        tc += "\n"
        
        # 预期结果
        tc += "**预期结果**:\n"
        for expected in case.expected:
            tc += f"- {expected}\n"
        tc += "\n"
        
        # 元数据
        tc += f"**优先级**: {case.priority}\n\n"
        tc += f"**测试类型**: {case.test_type}\n\n"
        
        # UI自动化标记
        automation_mark = "✅ 可自动化" if case.ui_automation else "❌ 不可自动化"
        tc += f"**UI自动化**: {automation_mark}\n\n"
        
        tc += "---\n\n"
        
        return tc
    
    def _generate_statistics(self) -> str:
        """生成统计信息"""
        stats = "## 测试统计\n\n"
        
        total = len(self.test_cases)
        
        # 用例概览（包含自动化统计）
        automatable = sum(1 for tc in self.test_cases if tc.ui_automation)
        non_automatable = total - automatable
        auto_rate = f"{automatable/total*100:.0f}%" if total > 0 else "0%"
        non_auto_rate = f"{non_automatable/total*100:.0f}%" if total > 0 else "0%"
        
        stats += "### 用例概览\n\n"
        stats += f"- **总用例数**: {total}条\n"
        stats += f"- **可自动化**: {automatable}条 ({auto_rate})\n"
        stats += f"- **不可自动化**: {non_automatable}条 ({non_auto_rate})\n\n"
        
        # 按优先级统计（包含自动化率）
        priority_count = {'P0': 0, 'P1': 0, 'P2': 0, 'P3': 0}
        priority_auto = {'P0': 0, 'P1': 0, 'P2': 0, 'P3': 0}
        
        for case in self.test_cases:
            priority_count[case.priority] = priority_count.get(case.priority, 0) + 1
            if case.ui_automation:
                priority_auto[case.priority] = priority_auto.get(case.priority, 0) + 1
        
        stats += "### 按优先级分布\n\n"
        stats += "| 优先级 | 总数 | 可自动化 | 自动化率 |\n"
        stats += "|-------|------|---------|----------|\n"
        
        for priority in ['P0', 'P1', 'P2', 'P3']:
            count = priority_count.get(priority, 0)
            auto_count = priority_auto.get(priority, 0)
            auto_percent = f"{auto_count/count*100:.0f}%" if count > 0 else "0%"
            stats += f"| {priority} | {count}条 | {auto_count}条 | {auto_percent} |\n"
        
        stats += "\n"
        
        # 按分组统计
        stats += "### 按分组分布\n\n"
        stats += "| 分组 | 数量 |\n"
        stats += "|------|------|\n"
        
        for group_name, cases in self.groups.items():
            stats += f"| {group_name} | {len(cases)}条 |\n"
        
        stats += "\n---\n\n"
        stats += "**文档生成工具**: Senior QA Brain v2.1\n"
        stats += f"**最后更新**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        
        return stats


# ==================== 示例使用 ====================

def demo_usage():
    """演示如何使用"""
    
    # 1. 创建生成器
    generator = MarkdownTestCaseGenerator(
        project_name="示例项目",
        test_scope="登录与权限模块"
    )
    
    # 2. 添加测试用例
    generator.add_test_case(TestCase(
        tc_id="TC001",
        title="用户正常登录",
        preconditions=[
            "用户已注册",
            "用户账号状态正常"
        ],
        steps=[
            "打开登录页面",
            "输入正确的用户名和密码",
            "点击登录按钮"
        ],
        expected=[
            "登录成功",
            "跳转到首页",
            "显示用户名"
        ],
        priority="P0",
        test_type="功能测试",
        ui_automation=True,  # 可自动化
        group="登录功能"
    ))
    
    generator.add_test_case(TestCase(
        tc_id="TC002",
        title="用户名为空登录",
        preconditions=["打开登录页面"],
        steps=[
            "用户名输入框留空",
            "输入密码",
            "点击登录按钮"
        ],
        expected=[
            "显示错误提示'请输入用户名'",
            "登录失败",
            "停留在登录页面"
        ],
        priority="P0",
        test_type="表单校验",
        ui_automation=True,  # 可自动化
        group="登录功能"
    ))
    
    # 3. 生成Markdown文件
    output_path = "/tmp/test_cases_demo.md"
    generator.generate_markdown(output_path)
    print(f"✅ 示例文件已生成: {output_path}")


if __name__ == "__main__":
    demo_usage()
