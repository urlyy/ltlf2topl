CPA_CHECKER_DIR="/home/urlyy/桌面/cpachecker"
output_dir="output/LA"
input_dir="input"
filename="code2.c"
if [ -d "$output_dir" ]; then  
    echo "目录存在，开始删除..."S
    # 删除目录  
    rm -rf "$output_dir"
fi

$CPA_CHECKER_DIR/scripts/cpa.sh -generateLoopAbstractions $input_dir/$filename
  
# 判断文件个数是否大于0  
if [ -d "$output_dir" ]; then  
    echo "成功"
    # 遍历目标文件夹
    for file in "$output_dir"/*; do
        # 检查文件名是否包含 "HAVOC"
        if [[ "$file" == *HAVOC* ]]; then
            # 提取文件名和扩展名
            filename=$(basename "$file")
            extension="${filename##*.}"
            # 设置新的文件名为 "code.c"
            new_filename="new_code.c"
            # 构建新的文件路径
            new_filepath="$input_dir/$new_filename"
            # 移动并重命名文件
            cp "$file" "$new_filepath"
            echo "已将文件 $file 重命名为 $new_filename 并移动到 $new_filepath"
        fi
    done
else  S
    echo "失败"
fi