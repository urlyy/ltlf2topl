from ltlf2dfa.parser.ltlf import LTLfParser
from ltlf2topl.my_implemention import change

change()
parser = LTLfParser()
formula_str = "a=>b"
formula = parser(formula_str)
dfa = formula.to_dfa()
print(dfa)