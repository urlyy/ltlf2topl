# 得到性质感兴趣的变量名
import re
import yaml


def load_relavant_variables(self,property_file_path='property.yaml'):
    with open(property_file_path, 'r') as file:
        # 使用 PyYAML 加载 YAML 文件内容
        data = yaml.safe_load(file)
        property = data['property']
    fomula:str = property['origin']
    # c语言变量的命名规则，不已数字开头，后面可以数字字母下划线
    pattern = r"[a-zA-Z][a-zA-Z]*"
    variables = re.findall(pattern, fomula)
    variables = list(filter(lambda v: v not in ["X","WX","U","R","F","G"],variables))
    self.relavant_variables = variables