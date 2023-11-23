# 定义一个枚举类
from enum import Enum
    
class NodeName(Enum):
    PRIMITIVE_TYPE = "primitive_type"
    IDENTIFIER = "identifier"
    NUMBER_LITERAL = "number_literal"
    BINARY_EXPRESSION = "binary_expression"
    INIT_DECLARATOR="init_declarator"
    DECLARATION="declaration"
    COMPOUND_STATEMENT="compound_statement"
    EXPRESSION_STATEMENT="expression_statement"
    ASSIGNMENT_EXPRESSION="assignment_expression"
    UPDATE_EXPRESSION="update_expression"
    FOR = "for_statement"
    WHILE = "while_statement"
    FUNCTION_DEFINITION = 'function_definition'
    RETURN_STATEMENT = 'return_statement'
    COMMENT = 'comment'
    IF_STATEMENT = 'if_statement'