CPA_CHECKER_DIR="/home/urlyy/桌面/cpachecker"
rm -rf output
CPA_CHECKER_LA="output/LA"
file="input/main.c"
property="property/test.yaml"

if [ -d "$output_dir" ]; then  
    echo "目录存在，开始删除..."S
    # 删除目录  
    rm -rf "$output_dir"
fi

$CPA_CHECKER_DIR/scripts/cpa.sh -generateLoopAbstractions $file
  
# 判断文件个数是否大于0  
if [ -d "$CPA_CHECKER_LA" ]; then  
    echo "成功"
    mv $CPA_CHECKER_LA tmp_output
    rm -rf output
    mv tmp_output output
    # 遍历目标文件夹
    count=1
    for file in "output"/*; do
        # 检查文件名是否包含 "HAVOC"
        if [[ "$file" == *HAVOC* ]]; then
            # 提取文件名和扩展名
            filename=$(echo "$file" | awk -F. '{print $1}')
            # 设置新的文件名为 "code.c"
            new_filename="${filename}_${count}.c"
            # 构建新的文件路径
            new_filepath="$new_filename"
            # 移动并重命名文件
            cp "$file" "$new_filepath"
            echo "已将文件 $file 移动到 $new_filepath"
            count=$((count + 1))
        fi
    done
    sh run.sh "output/main_1.c" "$property"
else  S
    echo "失败"
fi
rm -f *.o