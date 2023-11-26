from ltlf2dfa.ltlf2dfa import get_value,ter2symb,simplify_guard
from sympy import symbols
import ltlf2dfa
from ltlf2dfa.ltlf2dfa import parse_mona


# 替换原先的parse过程，改为自己自定义的
# 只返回邻接表
def __parse_mona(mona_output):
    """Parse mona output and construct a dot."""
    free_variables = get_value(
        mona_output, r".*DFA for formula with free variables:[\s]*(.*?)\n.*", str
    )
    if "state" in free_variables:
        free_variables = None
    else:
        free_variables = symbols(
            " ".join(
                x.strip().lower() for x in free_variables.split() if len(x.strip()) > 0
            )
        )
    accepting_states = get_value(mona_output, r".*Accepting states:[\s]*(.*?)\n.*", str)
    termiante = [
        str(x.strip()) for x in accepting_states.split() if len(x.strip()) > 0
    ]
    dot_trans = dict()  # maps each couple (src, dst) to a list of guards
    for line in mona_output.splitlines():
        if line.startswith("State "):
            orig_state = get_value(line, r".*State[\s]*(\d+):\s.*", int)
            guard = get_value(line, r".*:[\s](.*?)[\s]->.*", str)
            if free_variables:
                guard = ter2symb(free_variables, guard)
            else:
                guard = ter2symb(free_variables, "X")
            dest_state = get_value(line, r".*state[\s]*(\d+)[\s]*.*", int)
            if orig_state:
                if (orig_state, dest_state) in dot_trans.keys():
                    dot_trans[(orig_state, dest_state)].append(guard)
                else:
                    dot_trans[(orig_state, dest_state)] = [guard]
    # for c, guards in dot_trans.items():
    #     simplified_guard = simplify_guard(guards)
    #     dot += ' {} -> {} [label="{}"];\n'.format(
    #         c[0], c[1], str(simplified_guard).lower()
    #     )
    for c, guards in dot_trans.items():
        simplified_guard = simplify_guard(guards)
        # print(simplified_guard)
        # <class 'sympy.logic.boolalg.BooleanTrue'>
        # print(type(simplified_guard))
        dot_trans[c] = str(simplified_guard).lower()
        # dot_trans[c] = simplified_guard
    # return dot
    return {"trans":dot_trans,"terminate":termiante,"begin":1,}


def change():
    # 替换原库中的parse过程，改为自己自定义的
    ltlf2dfa.ltlf2dfa.parse_mona = __parse_mona