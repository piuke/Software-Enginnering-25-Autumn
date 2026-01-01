#!/bin/bash

# 快速启动5小时+ 模糊测试脚本

VENV="/home/fujisawa/Software-Enginnering-25-Autumn/.venv/bin/python"
PROJECT_DIR="/home/fujisawa/Software-Enginnering-25-Autumn/exp3"
CORPUS="$PROJECT_DIR/fuzz_corpus_extended"

echo "╔════════════════════════════════════════════════════════════╗"
echo "║  🧪 启动长时间模糊测试 (5小时+)                           ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

mkdir -p "$CORPUS"

echo "📊 测试配置:"
echo "  • 运行时间: 5 小时 (18000 秒)"
echo "  • 工具: Atheris + libFuzzer"
echo "  • 覆盖模块: 所有"
echo "  • 语料库: $CORPUS"
echo ""

echo "⏱️  开始时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# 运行5小时的模糊测试
timeout 18000 $VENV "$PROJECT_DIR/fuzz_tests/fuzz_long_run.py" \
    -timeout=2 \
    -max_total_time=18000 \
    -rss_limit_mb=2048 \
    -max_len=500000 \
    "$CORPUS"

EXIT_CODE=$?

echo ""
echo "📊 测试完成!"
echo "  • 结束时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "  • 退出代码: $EXIT_CODE"
echo ""

if [ -d "$CORPUS" ]; then
    SAMPLE_COUNT=$(find "$CORPUS" -type f | wc -l)
    CRASH_COUNT=$(find "$CORPUS" -name "crash-*" 2>/dev/null | wc -l)
    echo "📈 统计数据:"
    echo "  • 生成样本: $SAMPLE_COUNT 个"
    echo "  • 发现崩溃: $CRASH_COUNT 个"
    echo ""
fi

if [ $CRASH_COUNT -gt 0 ]; then
    echo "💥 发现问题! 请检查崩溃文件:"
    find "$CORPUS" -name "crash-*" -exec echo "  • {}" \;
else
    echo "✅ 未发现崩溃 - 代码质量良好"
fi

echo ""
echo "📝 详细信息请查看: LONG_RUN_FUZZING.md"
echo ""

exit $EXIT_CODE
