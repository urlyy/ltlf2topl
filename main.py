from ltlf2dfa.parser.ltlf import LTLfParser
from my_implemention import change

def formula2dfa(formula_str)->dict:
    # 替换原来的库函数，换为自己的实现
    change()
    parser = LTLfParser()
    formula = parser(formula_str)
    d = formula.to_dfa()
    return d

if __name__ == "__main__":
    s = "G(a->F(b))"
    dfa = formula2dfa(s)
    print(dfa)


