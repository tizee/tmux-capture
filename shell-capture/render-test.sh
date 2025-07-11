#!/bin/bash

# ==============================================================================
# Terminal Rendering Performance Test
#
# This script bombards the terminal with random character placements and color
# changes to measure rendering throughput and identify performance bottlenecks.
#
# Usage:
# 1. Save as render-test.sh
# 2. chmod +x render-test.sh
# 3. Run with: time ./render-test.sh
# ==============================================================================

# --- Configuration ---
# 總共要渲染的字元數量。增加此值會讓測試時間更長、壓力更大。
# 50000 在現代終端中大約需要 5-15 秒。
ITERATIONS=50000

# 用於產生隨機字元的字元集
CHARS="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#%^&*()-_=+"

# --- Terminal Setup ---
# 獲取終端的行數和列數
ROWS=$(tput lines)
COLS=$(tput cols)

# 檢查是否成功獲取到終端尺寸
if [[ -z "$ROWS" || -z "$COLS" ]]; then
    echo "無法獲取終端尺寸。請在一個互動式終端中執行。"
    exit 1
fi

echo "開始渲染性能測試..."
echo "終端尺寸: ${ROWS}x${COLS}"
echo "總渲染次數: ${ITERATIONS}"
sleep 1

# 隱藏游標，避免閃爍
tput civis
# 清除螢幕
tput clear

# --- Main Test Loop ---
# 將所有輸出組合在一起，然後用一個 `printf` 輸出，這樣可以稍微減少 shell 自身的開銷，
# 讓測試更專注於終端本身的處理能力。
output_buffer=""
for ((i = 1; i <= ITERATIONS; i++)); do
    # 產生隨機位置
    RAND_ROW=$((RANDOM % ROWS + 1))
    RAND_COL=$((RANDOM % COLS + 1))

    # 產生隨機的 256 色彩
    RAND_COLOR=$((RANDOM % 256))

    # 隨機選擇一個字元
    RAND_CHAR_INDEX=$((RANDOM % ${#CHARS}))
    RAND_CHAR=${CHARS:$RAND_CHAR_INDEX:1}

    # 建立 ANSI 跳脫序列:
    # 1. \x1b[${RAND_ROW};${RAND_COL}H  -> 移動游標到指定位置
    # 2. \x1b[38;5;${RAND_COLOR}m      -> 設定前景色 (256色模式)
    # 3. ${RAND_CHAR}                   -> 打印字元
    #
    # 我們將所有指令累積在一個緩衝區中，每 200 次迭代刷新一次，以模擬 TUI 應用的刷新行為。
    output_buffer+="\x1b[${RAND_ROW};${RAND_COL}H\x1b[38;5;${RAND_COLOR}m${RAND_CHAR}"

    # 為了避免 shell 緩衝區無限增長，定期刷新到螢幕
    if (( i % 200 == 0 )); then
        printf "%s" "$output_buffer"
        output_buffer="" # 清空緩衝區

        # 在左上角顯示進度，並清除到行尾
        printf "\x1b[1;1H\x1b[KProgress: %d / %d" "$i" "$ITERATIONS"
    fi
done

# 確保最後一批緩衝區的內容也被打印出來
if [[ -n "$output_buffer" ]]; then
    printf "%s" "$output_buffer"
fi


# --- Cleanup ---
# 將游標移動到左下角
printf "\x1b[${ROWS};1H"
# 重置所有圖形屬性 (顏色等)
tput sgr0
# 清除從游標到螢幕結尾的所有內容
tput ed
# 顯示游標
tput cnorm

echo "測試完成！"
