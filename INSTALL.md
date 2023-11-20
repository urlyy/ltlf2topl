```shell
apt install mona
pip install ltlf2dfa
```

```python
from ltlf2dfa.parser.ltlf import LTLfParser

parser = LTLfParser()
formula_str = "G(a -> X b)"
# returns an LTLfFormula
formula = parser(formula_str)
# "G(a -> X (b))"
print(formula)
dfa = formula.to_dfa()
print(dfa)
```
