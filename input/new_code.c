extern int __VERIFIER_nondet_int();

void main()
{
    int x,y;
    x = __VERIFIER_nondet_int();
    y = 1;
    // START HAVOCSTRATEGY
    if (x > (0)) {
    y = __VERIFIER_nondet_int();
    x = __VERIFIER_nondet_int();
    }
    if (x > (0)) abort();
    // END HAVOCSTRATEGY
}