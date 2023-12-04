from tree_sitter import Node
from ltlf2topl.code_parser import MyParser
from ltlf2topl.my_enum import NodeName

def havoc():
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

    input_path = "./test.c"    
    with open(input_path, 'r') as f:
        code = f.read()
    parser = MyParser()
    parser.set_code(code)
    names = function_names(parser)
    print(names)
    name = names[1]
    func_body = find_function_body_by_name(parser,name)
    
    # TODO 记录确定的值(字面值)
    # variable_value = dict()
    
    
    def _abstract(body_node:Node,in_while:bool):
        # modified_variables = set()
        tmp_code = ""
        for child in body_node.named_children:
            if child.type == NodeName.WHILE.value:
                condition = child.child_by_field_name('condition')
                tmp_code += "\tif" + parser.code(condition)
                while_body = child.child_by_field_name('body')
                tmp_code += _abstract(while_body,True)
            else:
                if in_while and child.type == NodeName.EXPRESSION_STATEMENT.value:
                    tmp = child.children[0]
                    if tmp.type == NodeName.UPDATE_EXPRESSION.value:
                        variable = tmp.child_by_field_name('argument')
                    elif tmp.type == NodeName.ASSIGNMENT_EXPRESSION.value:
                        variable = tmp.child_by_field_name('left')
                    if variable is not None:
                        tmp_code += "\t"+parser.code(variable) +"=nodet()\n"
                else:
                    tmp_code += "\t"+parser.code(child) + "\n"
        return "{\n" + tmp_code + "\n}"
    
    new_code = _abstract(func_body,False)
    parser.update(func_body,new_code)
    print(parser.code(parser.root))
havoc()