import argparse
import os
from tree_sitter import Node
from ltlf2topl.code_parser import MyParser
from ltlf2topl.my_enum import NodeName
# 将代码的for全部转为while，让cpachecker识别

def process(input_path,output_path):
    with open(input_path, 'r') as f:
        code = f.read()
    parser = MyParser()
    parser.set_code(code)
    
    def function_names(parser: MyParser):
        query_function_name_text = f'''
        (function_definition
            declarator: (function_declarator
                declarator: (identifier)@function_name
            )
        )
        '''
        function_name_nodes = parser.query(parser.root,query_function_name_text)
        return [parser.code(node) for node,_ in function_name_nodes]

    def find_function_body_by_name(parser:MyParser,name)->Node:
        query_function_body_text = f'''
        (function_definition
            declarator: (function_declarator
                declarator: (identifier)@function_name)(#eq? @function_name "{name}")
                body: (compound_statement)@body
        )
        ''' 
        res = parser.query(parser.root,query_function_body_text)
        body = [item for item,alias in res if alias == 'body'][0]
        return body

    names = function_names(parser)
    name = names[0]
    function_body = find_function_body_by_name(parser,name)
    def _process(body_node:Node):
        tmp_code = ""
        for child in body_node.named_children:
            if child.type == NodeName.FOR.value:
                init = child.child_by_field_name('initializer')
                condition = child.child_by_field_name('condition')
                update = child.child_by_field_name('update')
                for_body = child.named_children[-1]
                tmp_code += "\t" + parser.code(init) +"\n"
                tmp_code += "\t"+"while("+parser.code(condition)+")"
                # 去掉末尾的花括号和换行符
                tmp_code += _process(for_body).rstrip()[:-2]
                tmp_code += "\t"+parser.code(update) +";\n}\n"
            else:
                tmp_code += "\t"+parser.code(child) + "\n"
        return "{\n" + tmp_code + "\n}"
    
    new_code = _process(function_body)
    parser.update(function_body,new_code)
    with open(output_path,'w') as f:
        f.write(parser.code(parser.root))
        
if __name__ == '__main__':
    # 1. 定义命令行解析器对象
    parser = argparse.ArgumentParser(description='Demo of argparse')
    # 2. 添加命令行参数
    parser.add_argument('-input', type=str)
    parser.add_argument('-output', type=str)
    # 3. 从命令行中结构化解析参数
    args = parser.parse_args()
    input_path = args.input
    output_path = args.output
    process(input_path,output_path)