# https://tree-sitter.github.io/tree-sitter/playground
# query教学 https://blog.csdn.net/qq_38808667/article/details/128172301
from typing import Any, Callable, List, Tuple
from ltlf2topl.my_enum import NodeName
from tree_sitter import Parser,Language,Node,Tree

class MyParser:
  def __init__(self):
    # 配置
    Language.build_library(
      # so文件保存位置
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