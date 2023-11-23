

from fomula2dfa import dfa2topl
from infer_trans import Transformer


if __name__ == '__main__':
    with open('input/code.c', 'r') as f:
        code = f.read()
    t = Transformer(code)
    names = t.function_names
    name = names[1]
    t.trans(name)
    dfa2topl