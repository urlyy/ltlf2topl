int sum(a,b){
  return a+b;
}

int fun(int a,int b){
    int res = 0 ,res1=0;
    int tmp;
    if(res == 0){
      res ++ ;
      if(res == 1){
        res = 1;
      }
    }
    int lyy;
    res += 1 + 2;
    res += 1 - 2;
    res ++;
    res = 2+3;
    res = sum(2,3);
    // 循环的注释
    for(int i = 0,j=0,k=0;i <10 && j<10 && j<20 && res<200 ;i++,j++,res++){
      int lyy;
      res += a + b;
      res += a-b;
      res ++;
      a += b;
    }
    if(res <0)res = 0;
    return res;
}

int main(){
  int a = 2,b = 3;
  int sum = fun(a,b);
  return 0;
}