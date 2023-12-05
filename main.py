import os
import yaml
from ltlf2topl.code_parser import MyParser
from ltlf2topl.fomula2dfa import dfa2topl
from ltlf2topl.infer_trans import Transformer
from ltlf2topl.preprocess_property import process as process_prop
from ltlf2topl.fomula2dfa import formula2dfa
import subprocess
import argparse

def main(code_path,property_path):
    file_name = os.path.basename(code_path).split(".")[0]
    # 配置topl里的三种辅助函数的名称
    config_path = "config.yaml"
    output_property_path = f"output/property/{file_name}.yaml"
    output_code_path =f"output/code/{file_name}.c"
    output_topl_path =f"output/topl/{file_name}.topl"
    if not os.path.exists(os.path.dirname(output_property_path)):
        os.makedirs(os.path.dirname(output_property_path))
    if not os.path.exists(os.path.dirname(output_code_path)):  
        os.makedirs(os.path.dirname(output_code_path))
    if not os.path.exists(os.path.dirname(output_topl_path)):  
        os.makedirs(os.path.dirname(output_topl_path))
    # 正式开始
    # 预先处理一下property
    process_prop(property_path,output_property_path)
    # 读取三个文件
    with open(code_path, 'r') as f:
        code = f.read()
    with open(config_path, 'r') as f:
        infer_config = yaml.safe_load(f)['infer']
    with open(output_property_path, 'r') as f:
        property = yaml.safe_load(f)['property']
    # ltl公式转dfa
    dfa = formula2dfa(property)
    # 预处理源码
    # 开始根据property改造源码
    parser = MyParser()
    parser.set_code(code)
    names = parser.function_names
    name = 'main'
    parser.for2while(name).havoc_abstraction(name)
    t = Transformer(parser,property,infer_config,dfa)
    t.trans(name,output_code_path)
    # 格式化一下c语言，好看一点
    parser.format_code(output_code_path)
    # 根据改造生成的trans，生成topl代码
    dfa2topl(dfa,t.trans_functions,property,infer_config,output_topl_path)
    # 验证
    run_res = subprocess.run(f"infer --topl --topl-properties  {output_topl_path} -- gcc -c {output_code_path}".split(), capture_output=True, text=True)
    output = run_res.stdout
    if output.find('reaches state error')!=-1:
        print("找到反例")
    else:
        print("无反例")
    
if __name__ == '__main__':
    # 1. 定义命令行解析器对象
    argparser = argparse.ArgumentParser(description='Demo of argparse')
    # 2. 添加命令行参数
    argparser.add_argument('-code', type=str)
    argparser.add_argument('-property', type=str)
    # 3. 从命令行中结构化解析参数
    args = argparser.parse_args()
    code_path = args.code
    property_path = args.property
    # 4.
    main(code_path,property_path)