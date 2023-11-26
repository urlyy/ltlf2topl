//@ ltl invariant positive: ([] ( AP(x > 0) ==> <>AP(y==0)));

void begin(){}
void end(){}
void terminate(){}



void main()
{
    int x,y;
    x = __VERIFIER_nondet_int();
    
    y = 1;
    // START HAVOCSTRATEGY
    if (x > (0)) {
    x = __VERIFIER_nondet_int();
    y = __VERIFIER_nondet_int();
    }
    if (x > (0)) abort();
    // END HAVOCSTRATEGY
}