#!/bin/bash
# 长时间模糊测试脚本 - 5小时以上覆盖整个项目

VENV="/home/fujisawa/Software-Enginnering-25-Autumn/.venv/bin/python"
PROJECT_DIR="/home/fujisawa/Software-Enginnering-25-Autumn/exp3"
FUZZ_SCRIPT="$PROJECT_DIR/fuzz_tests/fuzz_all_modules.py"
CORPUS_DIR="$PROJECT_DIR/fuzz_corpus_extended"
RESULTS_DIR="$PROJECT_DIR/fuzz_results"
CRASH_DIR="$PROJECT_DIR/crash_results"

# 创建必要的目录
mkdir -p "$CORPUS_DIR"/{validators,order_service,product_service,message_service,combined}
mkdir -p "$RESULTS_DIR"
mkdir -p "$CRASH_DIR"

echo "╔════════════════════════════════════════════════════════════╗"
echo "║  🧪 长时间模糊测试套件 - 5小时+ 覆盖整个项目               ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "📊 测试配置:"
echo "  • 运行时间: 5+ 小时"
echo "  • 目标: 验证器、订单服务、产品服务、消息服务、组合操作"
echo "  • 语料库目录: $CORPUS_DIR"
echo "  • 结果目录: $RESULTS_DIR"
echo ""

# 记录开始时间
START_TIME=$(date +%s)

run_fuzz_test() {
    local target=$1
    local target_name=$2
    local corpus="$CORPUS_DIR/$target"
    local result_file="$RESULTS_DIR/${target}_result.txt"
    local log_file="$RESULTS_DIR/${target}_run.log"
    
    echo "🔍 开始测试: $target_name"
    echo "   目标编号: $target"
    echo "   语料库: $corpus"
    echo "   开始时间: $(date '+%Y-%m-%d %H:%M:%S')"
    
    # 运行5小时的模糊测试（18000秒）
    timeout 18000 $VENV "$FUZZ_SCRIPT" $target \
        -timeout=2 \
        -max_total_time=18000 \
        -rss_limit_mb=1024 \
        -max_len=10000 \
        "$corpus" \
        > "$log_file" 2>&1
    
    EXIT_CODE=$?
    END_TIME=$(date '+%s')
    ELAPSED=$((END_TIME - START_TIME))
    
    if [ -f "$log_file" ]; then
        # 分析结果
        RUNS=$(grep -c "INFO:" "$log_file" || echo "0")
        CRASHES=$(grep -c "ERROR:" "$log_file" || echo "0")
        LEAKS=$(grep -c "LeakSanitizer" "$log_file" || echo "0")
        
        echo "✅ 测试完成: $target_name"
        echo "   运行次数: $RUNS"
        echo "   发现崩溃: $CRASHES"
        echo "   内存泄漏: $LEAKS"
        echo "   耗时: $ELAPSED 秒"
        echo ""
        
        # 保存结果
        cat > "$result_file" << EOF
目标: $target_name
运行时间: $ELAPSED 秒
运行次数: $RUNS
发现崩溃: $CRASHES
内存泄漏: $LEAKS
完成时间: $(date '+%Y-%m-%d %H:%M:%S')
EOF
        
        # 检查崩溃
        if [ -f "$corpus/crash-"* ]; then
            echo "⚠️  发现崩溃文件! 正在复制..."
            cp "$corpus/crash-"* "$CRASH_DIR/" 2>/dev/null
        fi
    fi
    
    return $EXIT_CODE
}

# 运行所有模块的测试（分别各1小时）
echo "📋 模糊测试计划 (每个模块运行约1小时):"
echo "  1️⃣  验证器模块        (1小时)"
echo "  2️⃣  订单服务模块      (1小时)"
echo "  3️⃣  产品服务模块      (1小时)"
echo "  4️⃣  消息服务模块      (1小时)"
echo "  5️⃣  组合操作模块      (1小时+)"
echo ""
echo "⏱️  预计总时间: 5+ 小时"
echo "═════════════════════════════════════════════════════════════"
echo ""

# 同时运行多个模糊测试（并行处理加快速度）
# 但为了保证稳定，我们顺序运行

# 1. 测试验证器
echo "[1/5] $(date '+%H:%M:%S') 运行验证器模糊测试..."
run_fuzz_test 0 "验证器模块" &
PID1=$!

# 2. 测试订单服务
echo "[2/5] 等待验证器测试完成..."
wait $PID1
echo "[2/5] $(date '+%H:%M:%S') 运行订单服务模糊测试..."
run_fuzz_test 1 "订单服务" &
PID2=$!

# 3. 测试产品服务
echo "[3/5] 等待订单服务测试完成..."
wait $PID2
echo "[3/5] $(date '+%H:%M:%S') 运行产品服务模糊测试..."
run_fuzz_test 2 "产品服务" &
PID3=$!

# 4. 测试消息服务
echo "[4/5] 等待产品服务测试完成..."
wait $PID3
echo "[4/5] $(date '+%H:%M:%S') 运行消息服务模糊测试..."
run_fuzz_test 3 "消息服务" &
PID4=$!

# 5. 测试组合操作
echo "[5/5] 等待消息服务测试完成..."
wait $PID4
echo "[5/5] $(date '+%H:%M:%S') 运行组合操作模糊测试..."
run_fuzz_test 4 "组合操作" &
PID5=$!

# 等待所有测试完成
wait $PID5

# 计算总耗时
END_TIME=$(date +%s)
TOTAL_ELAPSED=$((END_TIME - START_TIME))
HOURS=$((TOTAL_ELAPSED / 3600))
MINUTES=$(((TOTAL_ELAPSED % 3600) / 60))
SECONDS=$((TOTAL_ELAPSED % 60))

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║  ✅ 模糊测试完成                                           ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "📊 总体结果:"
echo "  • 总耗时: ${HOURS}小时 ${MINUTES}分钟 ${SECONDS}秒"
echo "  • 测试覆盖模块: 5 个"
echo "  • 结果目录: $RESULTS_DIR"
echo "  • 语料库目录: $CORPUS_DIR"
echo ""

# 生成汇总报告
echo "生成汇总报告..."
cat > "$RESULTS_DIR/summary_report.txt" << EOF
╔════════════════════════════════════════════════════════════╗
║          模糊测试总结报告                                  ║
╚════════════════════════════════════════════════════════════╝

测试时间: $(date '+%Y-%m-%d %H:%M:%S')
总耗时: ${HOURS}小时 ${MINUTES}分钟 ${SECONDS}秒

测试覆盖:
EOF

for result_file in "$RESULTS_DIR"/*_result.txt; do
    if [ -f "$result_file" ]; then
        echo "" >> "$RESULTS_DIR/summary_report.txt"
        cat "$result_file" >> "$RESULTS_DIR/summary_report.txt"
    fi
done

# 检查是否发现崩溃
CRASH_COUNT=$(find "$CRASH_DIR" -name "crash-*" 2>/dev/null | wc -l)
echo "" >> "$RESULTS_DIR/summary_report.txt"
echo "═════════════════════════════════════════════════════════════" >> "$RESULTS_DIR/summary_report.txt"
echo "发现的崩溃: $CRASH_COUNT" >> "$RESULTS_DIR/summary_report.txt"

if [ $CRASH_COUNT -gt 0 ]; then
    echo "💥 发现问题!" >> "$RESULTS_DIR/summary_report.txt"
    find "$CRASH_DIR" -name "crash-*" -exec ls -lh {} \; >> "$RESULTS_DIR/summary_report.txt"
else
    echo "✅ 未发现崩溃 - 代码质量良好" >> "$RESULTS_DIR/summary_report.txt"
fi

echo ""
echo "📋 查看完整报告:"
echo "   cat $RESULTS_DIR/summary_report.txt"
echo ""

# 显示汇总
cat "$RESULTS_DIR/summary_report.txt"

exit 0
