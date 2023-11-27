# 接收的参数
# 1.代码.c
# 2.性质.yaml，具体格式看例子
input_path="cpachecker_input/cpa.c"
property="cpachecker_input/p.yml"
# 1. 先将代码预处理
echo "===========1.开始将代码预处理==========="
code_name=$(basename "$input_path")  
# TODO后面记得改
# output_path="input/$code_name"
output_path="input/main.c"
python preprocessing.py -input $input_path -output $output_path
echo "===========1.处理后代码存放在$output_path==========="
# 2. 再使用cpachecker进行循环抽象
echo "===========2.调用cpachecker进行循环抽象==========="
CPA_CHECKER_DIR="/home/urlyy/桌面/cpachecker"
CPA_CHECKER_LA="output/LA"
if [ -d "output" ]; then  
    # 删除目录  
    rm -rf "output"
fi
if [ -d "infer-out" ]; then  
    # 删除目录  
    rm -rf "infer-out"
fi
$CPA_CHECKER_DIR/scripts/cpa.sh -generateLoopAbstractions $output_path
# 判断文件个数是否大于0  
if [ -d "$CPA_CHECKER_LA" ]; then  
    echo "===========2.循环抽象成功==========="
    mv $CPA_CHECKER_LA tmp_output
    rm -rf output
    mv tmp_output output
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
    echo "===========3.开始生成中间代码和topl,并进行校验==========="
    # TODO在这里之前整合所有的HAVOC抽象为一个文件
    code_path="output/main_1.c"
    # 在if里即循环抽象成功，进行代码的生成->TOPL的生成->infer的校验
    python main.py -code $code_path -property $property
else  S
    echo "失败"
fi
# 删除无用文件
rm -f *.o