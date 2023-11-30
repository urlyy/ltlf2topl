# TODO

1. 整合各工具,调整项目结构更加清晰
2. 将 cpachecker 的多个 havoc 处理为一个（不需要动 cpachecker 的源码，把那些 START HAVOC 作为括号，进行代码块的替换插入）
3. 有没有可能，自己写 havoc，看下面例子( 把所有的 while 变为 if，所有除了赋常量以外的操作全变为 variable=nodet() )
4. 测试 bug
5. 对于局部变量->全局变量的情况，增加不易重名的前缀

# 关于处理 havoc

```cpp
while(i<10){
    int j=0;
    // START HAVOCSTRATEGY
    while(j<i){
        j++;
        res += j;
    }
    if (j < i) abort();
    // END HAVOCSTRATEGY
    i++;
}
```

变为

```cpp
if(i<10){
    int j=0;
    // START HAVOCSTRATEGY
    if(j<i){
        j==rdm();
        res =rdm();
    }
    if (j < i) abort();
    // END HAVOCSTRATEGY
    i=rdm();
}
```
