# 自己实现havoc后，使用的shell
code="input/1/main.c"
property="input/1/p1.yml"
echo "代码:$code,性质:$property"
rm -rf output
python main.py -code $code -property $property
# # 删除无用文件
rm -f *.o