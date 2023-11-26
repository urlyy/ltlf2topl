import yaml
from fomula2dfa import dfa2topl
from infer_trans import Transformer
from property2yml import prehandle

if __name__ == '__main__':
    code_path = "input/new_code.c"
    property_path = "property/p.yaml"
    config_path = "config.yaml"
    output_property_path = "output/property/test.yaml"
    output_code_path ="output/code/code.c"
    output_topl_path ="output/topl/test.topl"
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