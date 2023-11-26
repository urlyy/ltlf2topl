//#Unsafe
//@ ltl invariant positive: !([](AP(x > 0) ==> <>AP(y == 0)));
void main(){
  int x,y;
  x = 10;
  y = 1;
  while(x>0){
      x--;
      if(x<=1){
          y=0;
      }
  }
}
