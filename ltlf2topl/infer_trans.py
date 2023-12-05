from typing import List, Set, Tuple
from tree_sitter import Node
import yaml
from ltlf2topl.code_parser import MyParser
from ltlf2topl.my_enum import NodeName
from ltlf2topl.fomula2dfa import formula2dfa


class Transformer:
            
    def __init__(self,parser:MyParser,property:dict,infer_config:dict,dfa):
        self._parser = parser
        self.start_func = infer_config['start']
        self.trans_func = infer_config['trans']
        self.error_func = infer_config['error']
        self.relavant_variables = property['infer']['variables']
        # [[(int,a),(float,b)],[(float,b)]]
        self.trans_functions:List[List[Tuple[str,str]]] = list()
        self.param2type = dict()
        # 记录_insert_trans_terminate()是否insert了terminate语句，避免无return导致的无terminate
        self.terminated = False
        self.init_variables = set()
        self.dfa = dfa
        # 处理一下dfa，获得各trans函数的params
        self.dfa_trans_params:List[List] = []
        for e in self.dfa:
            if e.val and e.val != "true":
                tmp = []
                for var in self.relavant_variables:
                    if e.val.find(var) != -1:
                        tmp.append(var)
                # 又要有序又要去重
                if len(tmp) > 0 and tmp not in self.dfa_trans_params:
                    self.dfa_trans_params.append(tmp)
        # 如果存在[(x,y),(x),(y)]，优先选择(x,y)，不满足再看(x)
        self.dfa_trans_params.sort(key=lambda x:len(x),reverse=True)
    
    @property
    def root(self):
        return self._parser.root
    
    def code(self,node):
        return self._parser.code(node)
    
    def update(self,replaced_node: Node,new_code: str):
        self._parser.update(replaced_node,new_code)
    
    def insert_begin(self,name):
        body = self._parser.find_function_body_by_name(name)
        new_code = "{\n\t"+self.start_func+"();"+self.code(body)[1:-1]+"\n}"
        self.update(body,new_code)
        
    def output(self,path):
        with open(path, 'w') as f:
            f.write(self.code(self.root))
    
    # 统一生成trans名称
    def generate_trans_name(self,params:List[Tuple])->str:
        return self.trans_func + ''.join([f'{name}' for typ,name in params])
    
    
    # 根据当前已初始化的参数，生成真正trans的参数列表
    def true_params(self)->list:
        for p in self.dfa_trans_params:
            flag = True
            for element in p:
                # 有变量未初始化
                if element not in self.init_variables:
                    flag = False
                    break
            if flag:
                return [(self.param2type[var],var) for var in p]
        raise ValueError("property文件有问题!")

    def generate_trans_call(self,params:List[Tuple])->str:
        func_name = self.generate_trans_name(params)
        return f"{func_name}({','.join([name for typ,name in params])});"
    
    def generate_trans_declaration(self,params:List[Tuple])->str:
        func_name = self.generate_trans_name(params)
        return f"void {func_name}({','.join([f'{typ} {name}' for typ,name in params])}){{}}"
    
    def insert_infer_declarations(self):
        new_code = "void "+self.start_func+"(){}\nvoid "+self.error_func+"(){}\n"
        for params in self.trans_functions:
            new_code += self.generate_trans_declaration(params)+"\n"
        new_code += self.code(self.root)
        self.update(self.root,new_code)
    
    def _insert_trans_terminate(self,body_node:Node):
        tmp_code = ""
        for child in body_node.named_children:
            c = self.code(child)
            if child.type == NodeName.COMMENT.value:
                tmp_code += f"\t{c}\n"
                continue
            if child.type != NodeName.IF_STATEMENT.value:
                if c.find(";") == -1:
                    c += ";"
                if child.type == NodeName.RETURN_STATEMENT.value:
                    tmp_code += f"\t{self.error_func}();\n"
                    self.terminated = True
                tmp_code += f"\t{c}\n"
                if child.type == NodeName.COMMENT.value:
                    tmp_code += "\n"
                if child.type == NodeName.DECLARATION.value:
                    ds  = child.children_by_field_name('declarator')
                    type = self.code(child.child_by_field_name('type'))
                    # 只是定义语句
                    # int i; 或 int i=10;或int i=10,j=10;
                    # 有初始化值
                    for d in ds:
                        if d.child_by_field_name('value'):
                            variable = self.code(d.child_by_field_name('declarator'))
                            self.param2type[variable] = type
                            # 变量是性质关心的变量
                            if variable in self.relavant_variables:
                                # 额外的set记录已初始化的变量
                                self.init_variables.add(variable)
                                params = self.true_params()
                                # 只能存tuple
                                if params not in self.trans_functions:
                                    self.trans_functions.append(params) 
                                tmp_code += f"\t{self.generate_trans_call(params)}\n"
                        else:
                            # 无初始值的情况
                            variable = self.code(d)
                            self.param2type[variable] = type
                elif child.type == NodeName.EXPRESSION_STATEMENT.value:
                    # 额外的set记录已初始化的变量
                    exp = child.named_children[0]
                    if exp.type == NodeName.ASSIGNMENT_EXPRESSION.value:
                        variable = self.code(exp.child_by_field_name('left'))
                    elif exp.type == NodeName.UPDATE_EXPRESSION.value:
                        variable = self.code(exp.child_by_field_name('argument'))
                    # 变量是性质关心的变量
                    if variable in self.relavant_variables:
                        self.init_variables.add(variable)
                        params = self.true_params()
                        if params not in self.trans_functions:
                            self.trans_functions.append(params) 
                        tmp_code += f"\t{self.generate_trans_call(params)}\n"
            else:
                tmp_code += "\tif"+self.code(child.child_by_field_name("condition"))
                tmp_code += self._insert_trans_terminate(child.child_by_field_name('consequence'))
        return "{\n" + tmp_code +"\t}\n"
    
    
    
    def insert_trans_terminate(self,name):
        self.terminated = False
        self.param2type = dict()
        self.trans_functions = list()
        body = self._parser.find_function_body_by_name(name)
        new_code = self._insert_trans_terminate(body)
        if not self.terminated:
            new_code = new_code.rstrip()[:-1]
            new_code +=self.error_func+"();}\n"
        self.update(body,new_code)
    
    
    def trans(self,func_name,outpath_path=None):
        self.insert_trans_terminate(func_name)
        
        self.insert_infer_declarations()
        self.insert_begin(func_name)
        self.output(outpath_path)