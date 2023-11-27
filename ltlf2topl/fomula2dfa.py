import re
from typing import List, Tuple
from ltlf2dfa.parser.ltlf import LTLfParser
from ltlf2topl.my_implemention import change
import yaml

class Edge:
    def __init__(self,fro,to,val:str):
        self.fro = fro
        self.to = to
        self.val = val
    def __str__(self):
        return "{"+f"from:{self.fro}, to:{self.to}, val:{self.val}"+"}"

def get_params(params:str,all_params:list):
    res = []
    for p in all_params:
        if params.find(p) !=-1:
           res.append(p)
    return res 

def generate_trans_name(base_trans,params:List[Tuple])->str:
    return base_trans +''.join(params)
def is_subset(l1:list,l2:list):
    flag = True
    for i in l1:
        if i not in l2:
            flag = False
            break
    return flag

def replace_upper(s:str,params:List[str]):
    for p in params:
        while s.find(p) != -1:
            s = s.replace(p,p[0].upper()+p[1:])
    return s

def dfa2topl(graph:List[Edge],trans_functions: List[List],property:dict,infer_config:dict)->str:
    trans_funcs = [[param[1] for param in func] for func in trans_functions]
    relavant_variables = property['infer']['variables']
    prefix_blank = " "*2
    topl = "//"+property['origin']
    topl += "\nproperty Main"
    for edge in graph:
        if edge.fro == 'start':
            topl += f"\n{prefix_blank}start -> q{edge.to}: {infer_config['start']}(IgnoreRet)"
        elif edge.to == 'error':
            topl += f"\n{prefix_blank}q{edge.fro} -> error: {infer_config['error']}(IgnoreRet)"
        else:
            # 然后改大写
            # 校验是否可以包含
            need_params = get_params(edge.val,relavant_variables)
            for func in trans_funcs:
                if is_subset(need_params,func):
                    trans_suffix = f"({', '.join(func)}, IgnoreRet)"
                    if edge.val != 'true':
                        trans_suffix += f" when {edge.val}"
                    trans_func = generate_trans_name( infer_config['trans'],func) +  replace_upper(trans_suffix,func)
                    topl += f'\n{prefix_blank}q{edge.fro} -> q{edge.to}: {trans_func}'
    # 不知道为什么最后必须一行空行
    topl += "\n"
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
        if f.find("=") != -1 and f.find("==") == -1:
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

def formula2dfa(property)->list:
    # 获得公式
    s = property['infer']['fomula']
    # 替换原来的库函数，换为自己的实现
    change()
    parser = LTLfParser()
    formula = parser(s)
    dfa = formula.to_dfa()
    graph = handle_dfa(dfa,property["infer"]["map"])
    return graph