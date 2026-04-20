#!/bin/bash

# AI 模块适配执行脚本
# 用途：自动执行 AI 模块归档后的必要适配步骤

set -e

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 脚本所在目录（skill 根目录）
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_ROOT="$(dirname "$SCRIPT_DIR")"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}AI 模块适配脚本${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# 检查是否在正确的目录
if [ ! -f "$SKILL_ROOT/SKILL.md" ]; then
    echo -e "${RED}错误: 未找到 SKILL.md，请确认脚本在正确的 skill 根目录下执行${NC}"
    exit 1
fi

echo -e "${YELLOW}当前工作目录: $SKILL_ROOT${NC}"
echo ""

# 检查虚拟环境
if [ ! -d "$SKILL_ROOT/bundled/ok_autotest_ui_pc/venv" ]; then
    echo -e "${RED}错误: 虚拟环境不存在，请先创建虚拟环境${NC}"
    echo "执行: python3 -m venv bundled/ok_autotest_ui_pc/venv"
    exit 1
fi

# 激活虚拟环境
echo -e "${GREEN}[1/6] 激活虚拟环境...${NC}"
source "$SKILL_ROOT/bundled/ok_autotest_ui_pc/venv/bin/activate"
echo -e "${GREEN}✓ 虚拟环境已激活${NC}"
echo ""

# 运行 doctor 检查环境
echo -e "${GREEN}[2/6] 检查环境状态...${NC}"
python3 "$SKILL_ROOT/scripts/ok_test.py" doctor
echo ""

# 刷新 catalog
echo -e "${GREEN}[3/6] 刷新 catalog...${NC}"
python3 "$SKILL_ROOT/scripts/ok_test.py" ops catalog-build
echo -e "${GREEN}✓ Catalog 刷新完成${NC}"
echo ""

# 审计标识
echo -e "${GREEN}[4/6] 审计标识完整性...${NC}"
python3 "$SKILL_ROOT/scripts/ok_test.py" ops audit-identifiers
AUDIT_EXIT_CODE=$?

if [ $AUDIT_EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✓ 标识审计通过${NC}"
else
    echo -e "${YELLOW}⚠ 标识审计有警告或错误${NC}"
    echo -e "${YELLOW}请查看 catalog/identifier_audit.md 获取详细信息${NC}"
    echo ""
    echo -e "${YELLOW}是否应用审计建议? (y/n)${NC}"
    read -r APPLY_AUDIT
    if [ "$APPLY_AUDIT" = "y" ] || [ "$APPLY_AUDIT" = "Y" ]; then
        echo -e "${GREEN}应用审计建议...${NC}"
        python3 "$SKILL_ROOT/scripts/ok_test.py" ops audit-identifiers --apply
        echo -e "${GREEN}✓ 审计建议已应用${NC}"
        
        # 重新刷新 catalog
        echo -e "${GREEN}重新刷新 catalog...${NC}"
        python3 "$SKILL_ROOT/scripts/ok_test.py" ops catalog-build
        echo -e "${GREEN}✓ Catalog 重新刷新完成${NC}"
    fi
fi
echo ""

# 列出 AI 模块用例
echo -e "${GREEN}[5/6] 列出 AI 模块用例...${NC}"
python3 "$SKILL_ROOT/scripts/ok_test.py" list --module ai
echo ""

# Dry-run 验证
echo -e "${GREEN}[6/6] Dry-run 验证 AI 模块...${NC}"
python3 "$SKILL_ROOT/scripts/ok_test.py" run --module ai --dry-run
echo ""

# 完成提示
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}适配步骤执行完成！${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}后续建议操作：${NC}"
echo "1. 检查 catalog/identifier_audit.md 确认标识规范"
echo "2. 编辑 catalog/catalog.overrides.yaml 添加细粒度 feature 映射"
echo "3. 更新 references/module-map.md 添加 AI 模块 selector 指导"
echo "4. 归档文本用例到 bundled/knowledge_base/文本用例/ai/"
echo "5. 执行真实回归验证："
echo "   python3 scripts/ok_test.py run --module ai --feature ai_publish_job --site ae"
echo ""
echo -e "${YELLOW}查看完整适配指南：${NC}"
echo "cat $SKILL_ROOT/../../AI_MODULE_ARCHIVE_AND_ADAPTATION_GUIDE.md"
echo ""
