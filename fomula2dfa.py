import re
from typing import List, Tuple
from ltlf2dfa.parser.ltlf import LTLfParser
from my_implemention import change
import yaml

class Edge:
    def __init__(self,fro,to,val:str):
        self.fro = fro
        self.to = to
        self.val = val
    def __str__(self):
        return "{"+f"from:{self.fro}, to:{self.to}, val:{self.val}"+"}"
        
def dfa2topl(graph:List[Edge],trans_param_num:int,condition_map:dict=None)->str:
    with open('property.yaml', 'r') as file:
        # 使用 PyYAML 加载 YAML 文件内容
        data = yaml.safe_load(file)
        infer = data['infer']
    # TODO
    # 然后改大写
    trans_func = f"{infer['trans']}({', '.join(['P'+str(i) for i in range(trans_param_num)])}, IgnoreRet)"
    topl = "property Main"
    for edge in graph:
        if edge.fro == 'start':
            topl += f"\n\tstart -> q{edge.to}: {infer['start']}(IgnoreRet)"
        elif edge.to == 'error':
            topl += f"\n\tq{edge.fro} -> error: {infer['error']}(IgnoreRet)"
        else:
            topl += f'\n\tq{edge.fro} -> q{edge.to}: {trans_func}'
            if edge.val != 'true':
                topl += f" when {edge.val}"
    return topl

def simplify(f:str)->str:
    if f.find("~") != -1:
        f = f.replace("~","")
        if f.find(">=") != -1:
            return f.replace(">=","<")
        if f.find("<=") != -1:
            return f.replace("<=",">")
        if f.find("<") != -1:
            return f.replace("<",">=")
        if f.find(">") != -1:
            return f.replace(">","<=")
        if f.find("=") != -1:
            return f.replace("=","!=")
    return f
        
def handle_dfa(dfa:dict,_map:dict):
    graph = []
    begin = dfa['begin']
    graph.append(Edge("start",begin,None))
    for e,v in dfa['trans'].items():
        edge = Edge(e[0],e[1],v)
        for k,v in _map.items():
            # 先把命题替换了
            pattern = r"\b" + re.escape(k) + r"\b"
            edge.val = re.sub(pattern, v, edge.val)
        # 有&的情况
        if edge.val.find("&") != -1:
            tmp = []
            for i in edge.val.split("&"):
                tmp.append(simplify(i.strip()))
            graph.append(Edge(edge.fro,edge.to," && ".join(tmp)))
            continue
        # 有|或没|的情况
        if edge.val.find('|')!=-1:
            # 分成两条
            lis = [Edge(edge.fro,edge.to,s.strip()) for s in edge.val.split("|")]
        else:
            lis = [edge]
        for ee in lis:
            ee.val = simplify(ee.val)
            graph.append(ee)
    for t in dfa['terminate']:
        graph.append(Edge(t,"error",None))
    return graph

def formula2dfa(property_path='property.yaml')->list:
    # 获得公式
    property = yaml.safe_load(open(property_path, 'r'))['property']
    s = property['infer']['fomula']
    # 替换原来的库函数，换为自己的实现
    change()
    parser = LTLfParser()
    formula = parser(s)
    dfa = formula.to_dfa()
    graph = handle_dfa(dfa,property["infer"]["map"])
    return graph

