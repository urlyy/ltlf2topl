# https://tree-sitter.github.io/tree-sitter/playground
# query教学 https://blog.csdn.net/qq_38808667/article/details/128172301
import subprocess
from typing import Any, Callable, List, Tuple
from ltlf2topl.my_enum import NodeName
from tree_sitter import Parser,Language,Node,Tree

class MyParser:
  def __init__(self):
    # 配置
    Language.build_library(
      # so文件保存位置
      # 其实就是编译这个c之后的so文件要找个地方存取
      'build/my-languages.so',
      # 下git clone的仓库
      [
        'languages/tree-sitter-cpp',
      ]
    )
    # 加载cpp代码解析器
    self.language = Language('build/my-languages.so', 'cpp')
    parser = Parser()
    parser.set_language(self.language)
    self._parser = parser
  
  
  # 设置要解析的代码
  def set_code(self,code:str):
    self._tree:Tree = self._parser.parse(code.encode('utf-8'))
    return self
  
  
  # 返回语法树的root节点
  @property
  def root(self):
    return self._tree.root_node
  
  
  
  # 从结点获得的代码，默认为所有代码
  def code(self,node: Node):
    return self.code(node)
   
  
  
  # 返回结点的位置范围
  def range(self,node: Node = None)->Tuple:
    if node:
      return (node.start_byte,node.end_byte,node.start_point,node.end_point)
    else:
      return (self.root.start_byte,self.root.end_byte,self.root.start_point,self.root.end_point)
  
  # 被替换的结点和新的代码
  def update(self,replaced_node:Node,input_code:str):
    range = self.range(replaced_node)
    new_code = self.code(self.root).replace(self.code(replaced_node),input_code)
    lines = new_code.split('\n')
    # 修改语法树
    # 代码在字节时的偏移和在ide展示时的行列坐标
    # bytes: (start_byte,old_end_byte,new_end_byte)
    # points: ((start_row,start_column),(old_end_row,old_end_column),(new_end_row,new_end_column))
    bytes = (range[0],range[1],range[0]+len(new_code)-1)
    points = (range[2],range[3],(len(lines),len(lines[-1])))
    self._tree.edit(
      bytes[0],
      bytes[1],
      bytes[2],
      points[0],
      points[1],
      points[2],
    ) 
    self._tree = self._parser.parse(new_code.encode(),self._tree)
  
  
  # # 找循环
  # def find_loop_node(self):
  #   check = lambda node: node.type == NodeName.WHILE.value or node.type == NodeName.FOR.value
  #   return utils.find_node(self.root , check)
  
  
  def code(self,node: Node):
    return node.text.decode("utf-8")
        
  # 作为非递归遍历语法树方式的参考，dfs前序遍历
  def traverse(self,root: Node, operate: Callable[[Node], None]):
      stack = [root]
      while stack:
          current_node = stack.pop()
          operate(current_node)
          # 将子节点按逆序入栈，保持栈顶的节点是先进后出
          stack.extend(reversed(current_node.children))

  def find_node(self,root: Node, check: Callable[[Node], bool]):
      stack = [root]
      while stack:
          current_node = stack.pop()
          # 判断是否是符合条件的节点
          if check(current_node):
              return current_node
          # 将子节点按逆序入栈，保持栈顶的节点是先进后出
          stack.extend(reversed(current_node.children))
      # 如果遍历完整棵树都没有找到符合条件的节点，返回 None
      return None


  def find_nodes(self,root: Node, check: Callable[[Node], bool],exclude: Callable[[Node], bool] = None)->List[Node]:
      stack = [root]
      res = []
      while stack:
          current_node = stack.pop()
          if exclude and exclude(current_node):
              continue
          if check(current_node):
              res.append(current_node)
          # 将子节点按逆序入栈，保持栈顶的节点是先进后出
          stack.extend(reversed(current_node.children))
      return res


  def reduce_nodes(self,root: Node, reduce: Callable[[Any,Node],Any],init_val):
      stack = [root]
      res = init_val
      while stack:
          current_node = stack.pop()
          res = reduce(res,current_node)
          stack.extend(reversed(current_node.children))
      # 如果遍历完整棵树都没有找到符合条件的节点，返回 None
      return res


  def find_nodes_generator(self,root: Node, check: Callable[[Node], bool],exclude: Callable[[Node], bool] = None)->List[Node]:
      stack = [root]
      while stack:
          current_node = stack.pop()
          if exclude and exclude(current_node):
              continue
          if check(current_node):
              yield current_node
          # 将子节点按逆序入栈，保持栈顶的节点是先进后出
          stack.extend(reversed(current_node.children))
          
  def query(self,node:Node,query_text:str):
    query = self.language.query(query_text)
    capture = query.captures(node)
    # for node, alias in capture:
    #     print(alias,self.code(node))
    return capture
  
  @property
  def function_names(self):
      query_function_name_text = f'''
      (function_definition
          declarator: (function_declarator
              declarator: (identifier)@function_name
          )
      )
      '''
      function_name_nodes = self.query(self.root,query_function_name_text)
      return [self.code(node) for node,_ in function_name_nodes]
  
  def find_function_by_name(self,name)->Node:
      query_function_name_text = f'''
      (function_definition
          declarator: (function_declarator
              declarator: (identifier)@function_name)(#eq? @function_name "{name}")
      )
      '''
      function_name_nodes = self.query(self.root,query_function_name_text)
      if len(function_name_nodes) != 1:
          return None
      node = function_name_nodes[0][0]
      return node.parent.parent
  
  def find_function_body_by_name(self,name)->Node:
      query_function_body_text = f'''
      (function_definition
          declarator: (function_declarator
              declarator: (identifier)@function_name)(#eq? @function_name "{name}")
              body: (compound_statement)@body
      )
      ''' 
      res = self.query(self.root,query_function_body_text)
      body = [item for item,alias in res if alias == 'body'][0]
      return body
  
  def for2while(self,func_name):
    function_body = self.find_function_body_by_name(func_name)
    def _process(body_node:Node):
      tmp_code = ""
      for child in body_node.named_children:
          if child.type == NodeName.FOR.value:
              init = child.child_by_field_name('initializer')
              condition = child.child_by_field_name('condition')
              update = child.child_by_field_name('update')
              for_body = child.named_children[-1]
              tmp_code += "\t" + self.code(init) +"\n"
              tmp_code += "\t"+"while("+self.code(condition)+")"
              # 去掉末尾的花括号和换行符
              tmp_code += _process(for_body).rstrip()[:-2]
              tmp_code += "\t"+self.code(update) +";\n}\n"
          else:
              tmp_code += "\t"+self.code(child) + "\n"
      return "{\n" + tmp_code + "\n}"
    new_code = _process(function_body)
    self.update(function_body,new_code)
    return self
    
  def havoc_abstraction(self,func_name):
    func_body = self.find_function_body_by_name(func_name)
    # TODO 记录确定的值(字面值)
    # variable_value = dict()
    def _abstract(body_node:Node,in_while:bool):
        # modified_variables = set()
        tmp_code = ""
        for child in body_node.named_children:
            if child.type == NodeName.WHILE.value:
              tmp_code += "//===START_HAVOC===\n"
              condition = child.child_by_field_name('condition')
              tmp_code += "\tif" + self.code(condition)
              while_body = child.child_by_field_name('body')
              tmp_code += _abstract(while_body,True)
              tmp_code += "//===ENDDD_HAVOC===\n"
            else:
              if in_while and child.type == NodeName.EXPRESSION_STATEMENT.value:
                  tmp = child.children[0]
                  if tmp.type == NodeName.UPDATE_EXPRESSION.value:
                      variable = tmp.child_by_field_name('argument')
                  elif tmp.type == NodeName.ASSIGNMENT_EXPRESSION.value:
                      variable = tmp.child_by_field_name('left')
                  if variable is not None:
                      tmp_code += "\t"+self.code(variable) +"=nodet();\n"
              else:
                  tmp_code += "\t"+self.code(child) + "\n"
        return "{\n" + tmp_code + "}\n"
    
    new_code = _abstract(func_body,False)
    self.update(func_body,new_code)
    return self
  
  
  def format_code(self,path=None):
    def _format(code:str)->str:
      # 调用ClangFormat进行格式化
      proc = subprocess.Popen(['clang-format'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
      formatted_code, error = proc.communicate(input=code)
      if proc.returncode != 0:
          raise Exception(f'ClangFormat error: {error}')
      return formatted_code
    
    if path is None:
      code = self.code(self.root)
      new_code = _format(code)
      return new_code
    else:
      with open(path, 'r') as f:
        code = f.read()
      new_code = _format(code)
      with open(path, 'w') as f:
        f.write(new_code)
    