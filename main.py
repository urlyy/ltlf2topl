import os
import yaml
from ltlf2topl.fomula2dfa import dfa2topl
from ltlf2topl.infer_trans import Transformer
from ltlf2topl.fomula2yml import prehandle
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
    with open(code_path, 'r') as f:
        code = f.read()
    with open(config_path, 'r') as f:
        # 使用 PyYAML 加载 YAML 文件内容
        infer_config = yaml.safe_load(f)['infer']
    # 转property
    prehandle(property_path,output_property_path)
    with open(output_property_path, 'r') as f:
        # 使用 PyYAML 加载 YAML 文件内容
        property = yaml.safe_load(f)['property']
    t = Transformer(code,property,infer_config)
    names = t.function_names
    name = names[0]
    t.trans(name,output_code_path)
    topl = dfa2topl(t.dfa,t.trans_functions,property,infer_config)
    with open(output_topl_path,"w") as f:
        f.write(topl)
    res = subprocess.run(f"infer --topl --topl-properties  {output_topl_path} -- gcc -c {output_code_path}".split(), capture_output=True, text=True)
    output = res.stdout
    if output.find('reaches state error')!=-1:
        print("找到反例")
    else:
        print("无反例")
    
if __name__ == '__main__':
    # 1. 定义命令行解析器对象
    parser = argparse.ArgumentParser(description='Demo of argparse')
    # 2. 添加命令行参数
    parser.add_argument('-code', type=str)
    parser.add_argument('-property', type=str)
    # 3. 从命令行中结构化解析参数
    args = parser.parse_args()
    code_path = args.code
    property_path = args.property
    # 4.
    main(code_path,property_path)