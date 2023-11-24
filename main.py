import yaml
from fomula2dfa import dfa2topl
from infer_trans import Transformer


if __name__ == '__main__':
    with open('input/code.c', 'r') as f:
        code = f.read()
    with open("config.yaml", 'r') as f:
        # 使用 PyYAML 加载 YAML 文件内容
        infer_config = yaml.safe_load(f)['infer']
    with open("property.yaml", 'r') as f:
        # 使用 PyYAML 加载 YAML 文件内容
        property = yaml.safe_load(f)['property']
    t = Transformer(code,property,infer_config)
    names = t.function_names
    name = names[1]
    t.trans(name)
    topl = dfa2topl(t.dfa,t.trans_functions,property,infer_config)
    print(topl)