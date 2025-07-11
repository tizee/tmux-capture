#!/bin/bash

echo "测试不同的ANSI转义序列写法："
echo "================================"

echo -n "1. 使用 \\x1b (双引号): "
echo "\x1b[31mRED\x1b[0m"

echo -n "2. 使用 \\033 (双引号): "
echo "\033[32mGREEN\033[0m"

echo -n "3. 使用 \$'\\x1b' (ANSI-C引用): "
echo $'\x1b[33mYELLOW\x1b[0m'

echo -n "4. 使用 \$'\\033' (ANSI-C引用): "
echo $'\033[34mBLUE\033[0m'

echo -n "5. 使用 printf \\x1b: "
printf "\x1b[35mMAGENTA\x1b[0m\n"

echo -n "6. 使用 printf \\033: "
printf "\033[36mCYAN\033[0m\n"

echo -n "7. 使用 printf \\e: "
printf "\e[91mBRIGHT RED\e[0m\n"

echo -n "8. 使用 echo -e \\x1b: "
echo -e "\x1b[92mBRIGHT GREEN\x1b[0m"

echo -n "9. 使用 echo -e \\033: "
echo -e "\033[93mBRIGHT YELLOW\033[0m"

echo -n "10. 使用 echo -e \\e: "
echo -e "\e[94mBRIGHT BLUE\e[0m"

echo "================================"
echo "如果你看到了颜色，说明该方法在你的环境中有效！"