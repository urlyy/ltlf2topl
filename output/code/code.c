void begin(){}
void terminate(){}
void trans_y_x(int y,int x){}
extern int __VERIFIER_nondet_int();

void main()
{
	begin();
	int x,y;
	x = __VERIFIER_nondet_int();
	trans_y_x(y,x);
	y = 1;
	trans_y_x(y,x);
	// START HAVOCSTRATEGY;
	if(x > (0)){
	y = __VERIFIER_nondet_int();
	trans_y_x(y,x);
	x = __VERIFIER_nondet_int();
	trans_y_x(y,x);
	}
	if(x > (0)){
	abort();
	}
	// END HAVOCSTRATEGY;
	
}
