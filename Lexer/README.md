## 需求

实现一个词法分析程序，输入一个句子，找出这个句子中各个单词构建符号表，并将符号表输出。

## 思路

第一步，读入输入的句子并保存起来供之后分析。

第二步，开始进行词法分析，顺序遍历这个句子字符串，**根据单词的第一个字符去找到整个单词**。需要注意的是维护每次循环开始的时候，i都指向新的需要识别的单词的第一个字符。
- 字符为空，那么直接跳过
- 字母字符
  - 继续读，直到遇到非字母数字字符的字符串，如a23b23+，那么我们读入a23b23
  - 考虑是关键字还是变量名，并且存入符号表
- 数字字符
  - 继续读，读到非数字字符为止
  - 然后将数字存入符号表
- 运算符
  - 对于长度可能为2的多字符运算符我们试着多读一个操作符看看能否组成合法操作符
  - 再去判断读入是否合法，若合法则加入符号表
- 如果判断运算符失败，不符合上面任意一种情况，我们认为是非法字符。
```c++
/**
 * @brief
 * 分析源代码并构建符号表,支持识别各种单词，不检测句子的正确性。当遇到不属于任何一种类型的单词时报错
 *
 * @param code 输入源代码
 */
void analyze(const std::string &code) {
    for (size_t i = 0; i < code.size(); i++) {
        if (isspace(code[i])) {
            continue;
        } else if (isalpha(code[i])) {
            handleAlpha(code, i);
        } else if (isdigit(code[i])) {
            handleDigit(code, i);
        } else {
            if (!handleSeparatorOrOperator(code, i)) {
                std::cerr << "错误： " << code[i] << " 不是有效的操作符！"
                          << std::endl;
            }
        }
        // 检测完成一个word后，i的位置将在当前识别word的最后一个字符的下标。
        // 当循环结束i++即可实现i指向新的需要识别的word。
    }
}
```

## 结果

![image-20231129164110999](https://jgox-image-1316409677.cos.ap-guangzhou.myqcloud.com/blog/image-20231129164110999.png)