# 得到性质感兴趣的变量名
import re
import yaml

with open('new_property.yaml', 'r') as file:
    # 使用 PyYAML 加载 YAML 文件内容
    data = yaml.safe_load(file)
fomula:str = data['property']['origin']

infer = dict()
data['property']['infer'] = infer
infer['map'] = dict()

ap_set = set()
tmp = ""
for idx,ch in enumerate(fomula):
    if ch == "(":
        tmp = ""
    elif ch == ")":
        ap_set.add(tmp)
    elif ch == "&" or ch == '|':
        if tmp != "":
            ap_set.add(tmp)
        tmp = ""
    else:
        tmp += ch
new_fomula = fomula
tmp_variables = set()
for idx,ap in enumerate(ap_set):
    identifier = f"p_{idx}"
    while new_fomula.find(ap) != -1:
        new_fomula = new_fomula.replace(ap,identifier)
    # 把转换存了
    infer['map'][identifier] = ap
    # 找到所有的变量
    pattern = r"[a-zA-Z_][a-zA-Z0-9_]*"
    variables = re.findall(pattern, ap)
    variables = list(filter(lambda v: v not in ["X","WX","U","R","F","G"],variables))
    for v in variables:
        tmp_variables.add(v)
infer['fomula'] = new_fomula
infer['variable'] = list(tmp_variables)
with open('output.yaml', 'w') as file:
    yaml.dump(data, file)
        

def load_relavant_variables(self,property_file_path='new_property.yaml'):
    with open(property_file_path, 'r') as file:
        # 使用 PyYAML 加载 YAML 文件内容
        data = yaml.safe_load(file)
        property = data['property']
    fomula:str = property['origin']
    # c语言变量的命名规则，不已数字开头，后面可以数字字母下划线
    pattern = r"[a-zA-Z][a-zA-Z_]*"
    variables = re.findall(pattern, fomula)
    variables = list(filter(lambda v: v not in ["X","WX","U","R","F","G"],variables))
    self.relavant_variables = variables
    # data = {'key': 'value'}
    # with open('output.yaml', 'w') as file:
    #     yaml.dump(data, file)