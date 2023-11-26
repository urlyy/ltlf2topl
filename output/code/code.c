void begin(){}
void terminate(){}
void transx(int x){}
void main(){
	begin();
	int x,y;
	x = __VERIFIER_nondet_int();
	transx(x);
	y = __VERIFIER_nondet_int();
	transx(x);
	// START HAVOCSTRATEGY;
	if(x > (0)){
	x = __VERIFIER_nondet_int();
	transx(x);
	}
	if(x > (0)){
	abort();
	}
	// END HAVOCSTRATEGY;
	
}
