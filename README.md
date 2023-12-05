# ltlf2topl

# INTRODUCION

本项目是专门为了实现 cpachecker 与 meta 的 infer 的联动。
cpachecker 请使用 loopsummary 分支

- 使用 cpachecker(外部)作为循环抽象(因为 infer 不能识别循环)，将 while->if
- 自己处理了将 for 循环改为 while(cpachecker 的 LA 似乎不支持识别 for 循环)
- 使用 tree-sitter 解析代码并生成新的代码
- 使用 yaml 作为中间数据的输出格式
- 使用 ltlf2dfa 并基于 mona 将输入的 ltl 代码转换为 dfa
- 通过本项目自己实现的字符串操作，结合 tree-sitter 解析的语法树，将 dfa 转为 topl
- clang-format 进行 c 语言代码格式化

# TreeSitter

- 本项目扩展了 ts 的修改代码方法，只需传入被修改的结点和新的代码，即可修改更新整颗语法树。但是修改会导致不能继续遍历结点(似乎？还没测过)，于是选择收集每个结点的代码，只会最后一次修改结点，而不每次都修改。
- Tree-sitter 的 query 语法还算简单，就是用嵌套括号表示层次结构。而且有<a href="https://tree-sitter.github.io/tree-sitter/playground">playground</a>方便查看怎么遍历语法树。
- 美中不足的是他的 child 有的能用 key 找，有的不行，而且感觉有点混乱，可能是我理解不如大佬?但总体是好用的

# INSTALL

- 开发本项目的 OS 为` Ubuntu 22.04`
- python 版本`python==3.10`
- `cpachecker`的`loopsummary`分支
- 安装 infer 的`v1.1.0`

```shell
apt install mona=1.4-18-1
apt install clang-format
pip install ltlf2dfa==1.0.2
pip install tree-sitter==0.20.4
pip install pyyaml==6.0.1
```

> <a href="https://blog.csdn.net/sluck_0430/article/details/134194493?ops_request_misc=&request_id=&biz_id=102&utm_term=treesitter%E6%95%99%E7%A8%8B&utm_medium=distribute.pc_search_result.none-task-blog-2~all~sobaiduweb~default-0-134194493.142^v96^pc_search_result_base9&spm=1018.2226.3001.4187">tree-sitter 的初次使用教程</a>

# 运行方法

只要管 ~~main.sh~~ `run.sh` 就行

# Attention

代码能跑，但结构混乱，面向对象和面向过程齐用，数据流混乱，待整理......

# LIMIT 汇总

- cpachecker-la：不支持 for 循环/偶尔有些时候生成不出来
- infer：topl 语法及其苛刻，最后必须有个空行/只支持"=><!&"这些符号，不支持!(a&b)这种

# 套盾

学生开发，如果有破坏开源协议的地方，请联系我
