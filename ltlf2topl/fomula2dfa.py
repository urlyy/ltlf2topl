import re
from typing import List, Tuple
from ltlf2dfa.parser.ltlf import LTLfParser

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

def dfa2topl(graph:List[Edge],trans_functions: List[List],property:dict,infer_config:dict,output)->str:
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
    with open(output,"w") as f:
        f.write(topl)

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








from ltlf2dfa.ltlf2dfa import get_value,ter2symb,simplify_guard
from sympy import symbols
import ltlf2dfa


# 替换原先的parse过程，改为自己自定义的
# 只返回邻接表
def __parse_mona(mona_output):
    """Parse mona output and construct a dot."""
    free_variables = get_value(
        mona_output, r".*DFA for formula with free variables:[\s]*(.*?)\n.*", str
    )
    if "state" in free_variables:
        free_variables = None
    else:
        free_variables = symbols(
            " ".join(
                x.strip().lower() for x in free_variables.split() if len(x.strip()) > 0
            )
        )
    accepting_states = get_value(mona_output, r".*Accepting states:[\s]*(.*?)\n.*", str)
    termiante = [
        str(x.strip()) for x in accepting_states.split() if len(x.strip()) > 0
    ]
    dot_trans = dict()  # maps each couple (src, dst) to a list of guards
    for line in mona_output.splitlines():
        if line.startswith("State "):
            orig_state = get_value(line, r".*State[\s]*(\d+):\s.*", int)
            guard = get_value(line, r".*:[\s](.*?)[\s]->.*", str)
            if free_variables:
                guard = ter2symb(free_variables, guard)
            else:
                guard = ter2symb(free_variables, "X")
            dest_state = get_value(line, r".*state[\s]*(\d+)[\s]*.*", int)
            if orig_state:
                if (orig_state, dest_state) in dot_trans.keys():
                    dot_trans[(orig_state, dest_state)].append(guard)
                else:
                    dot_trans[(orig_state, dest_state)] = [guard]
    # for c, guards in dot_trans.items():
    #     simplified_guard = simplify_guard(guards)
    #     dot += ' {} -> {} [label="{}"];\n'.format(
    #         c[0], c[1], str(simplified_guard).lower()
    #     )
    for c, guards in dot_trans.items():
        simplified_guard = simplify_guard(guards)
        # print(simplified_guard)
        # <class 'sympy.logic.boolalg.BooleanTrue'>
        # print(type(simplified_guard))
        dot_trans[c] = str(simplified_guard).lower()
        # dot_trans[c] = simplified_guard
    # return dot
    return {"trans":dot_trans,"terminate":termiante,"begin":1,}


# 暴露出去的
def formula2dfa(property)->list:
    # 获得公式
    s = property['infer']['fomula']
    # 替换原库中的parse过程，改为自己自定义的
    ltlf2dfa.ltlf2dfa.parse_mona = __parse_mona
    parser = LTLfParser()
    formula = parser(s)
    dfa = formula.to_dfa()
    graph = handle_dfa(dfa,property["infer"]["map"])
    return graph