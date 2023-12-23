[TOC]

## 概要
这个仓库用来存放编译原理实验的源代码和思路总结以及实验报告。

## 目录
- 词法分析
- 自顶向下语法分析
- 自底向上语法分析
- 语义分析和中间代码生成

## 项目目录结构
```
.
├── Lexer
│   ├── 第一次实验 词法分析.docx
│   ├── input.txt
│   ├── lexer.cpp
│   ├── lexer.o
│   ├── README.md
│   └── res.png
├── LL1_Parser
│   ├── 编译原理实验报告自上而下语法分析指导.doc
│   ├── grammar.txt
│   ├── LL1_Parser.py
│   ├── README.md
│   └── res.png
├── LR0_Parser
│   ├── 编译原理实验报告LR(0)分析法指导书.doc
│   ├── grammar.txt
│   ├── LR0_Parser.py
│   ├── README.md
│   ├── res1.png
│   ├── res2.png
│   └── res3.png
├── README.md
├── semanticAnalysis
│   ├── 第四次：语义分析与中间代码生成实验指导书.docx
│   ├── grammar.txt
│   ├── res.png
│   └── semanticAnalysis.c
└── tree.md
```

# 语法分析

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

# 自顶向下语法分析

## 需求

构建一个语法分析器，使用LL1文法实现对句子的语法分析。

## 思路

第一步，读入需要分析的句子，我们需要保存文法中的产生式规则，终结符和非终结符。以下面这种数据结构保存下来。
```
输入文法：
 {'terminals': {')', 'ε', '*', '(', '#', 'i', '+'}, 'non_terminals': {'E', 'G', 'T', 'S', 'F'}, 'E': ['TG'], 'T': ['FS'], 'G': ['+TG', 'ε'], 'S': ['*FS', 'ε'], 'F': ['(E)', 'i']}
```

第二步，构建各文法符号的FIRST集。

在构建文法符号的 FIRST 集时，对于终结符，其 FIRST 集就是其自身。

对于非终结符，针对每个产生式：

- X -> a.. 如果产生式的第一个符号是终结符，将该终结符添加到当前非终结符的 FIRST 集中。
- X -> Y1Y2Y3..Ym..Yk 如果产生式的第一个符号是非终结符，将该非终结符的 FIRST 集中的所有符号（除空串 ε 外）添加到当前非终结符的 FIRST 集中。
  - 同时，检查Y1是否能推导出 ε。
    - 若可以推导出 ε，则按顺序寻找下一个不可推导出 ε 的文法符号，并将其 FIRST 集加入当前非终结符的 FIRST 集中。
    - 这个过程一直持续到找到一个不可推导出 ε 的符号，将其 FIRST 集加入。
    - 或者所有产生式都可以推导出 ε，则将 ε 加入该非终结符的 FIRST 集。

```python
def calculate_first_sets(grammar):
    first_sets = {symbol: set() for symbol in grammar['non_terminals'] | grammar['terminals']}

    for terminal in grammar['terminals']:
        first_sets[terminal].add(terminal)

    while True:
        original_first_sets = {key: value.copy() for key, value in first_sets.items()}

        # 对于每个非终结符的每个产生式：
        for non_terminal in grammar['non_terminals']:
            for production in grammar[non_terminal]:
                # X -> a.. 如果产生式的第一个符号是终结符，将该终结符添加到当前非终结符的 FIRST 集中。
                if production[0] in grammar['terminals']:
                    first_sets[non_terminal].add(production[0])
                else:
                    # X -> Y1Y2Y3 如果产生式的第一个符号是非终结符，将该非终结符的 FIRST 集中的所有符号（除空串 ε 外）添加到当前非终结符的 FIRST 集中。
                    first_sets[non_terminal] |= first_sets[production[0]].difference({'ε'})
                    # 找到一个不能推导出 ε 的符号
                    for symbol in production:
                        if 'ε' in first_sets[symbol]:
                            continue
                        first_sets[non_terminal] |= first_sets[symbol]
                        if 'ε' not in first_sets[symbol]:
                            break
                    else:
                        first_sets[non_terminal].add('ε')

        if original_first_sets == first_sets:
            break

    return first_sets
```

第三步，构建FOLLOW集，同FIRST集，代码中加入了注释。需要注意的是非终结符才有FOLLOW集合，我们要给开始符号的FOLLOW集合手动加入`#`

```python
def calculate_follow_sets(grammar, first_sets):
    follow_sets = {symbol: set() for symbol in grammar['non_terminals'] }

    follow_sets['E'].add('#')

    while True:
        # 只考虑非终结符
        original_follow_sets = {key: value.copy() for key, value in follow_sets.items()}

        for non_terminal in grammar['non_terminals']:
            for production in grammar[non_terminal]:
                for i, symbol in enumerate(production):
                    # 存在一个产生式A→αB
                    if i == len(production) - 1 and symbol.isupper():
                        follow_sets[symbol] |= follow_sets[non_terminal]
                        break
                    # 如果存在一个产生式A→αBβ
                    if symbol.isupper():
                        # 将后面的符号的 First 集（除去空串 ε）添加到当前非终结符的 Follow 集中。
                        follow_sets[symbol] |= first_sets[production[i+1]].difference({'ε'})
                        # 存在产生式A→αBβ且first（β）包含ε
                        if 'ε' in first_sets[production[i+1]]:
                            follow_sets[symbol] |= follow_sets[non_terminal]

        if original_follow_sets == follow_sets:
            break

    return follow_sets
```

第四步，构建LL1分析表

这里要会计算整个产生式右部`符号串的FIRST集`，当计算一个产生式右部的符号串的 FIRST 集时，按顺序遍历该符号串，依次将每个语法符号的 FIRST 集添加到结果集中。如果第一个语法符号的 FIRST 集包含空（ε），则将第二个符号的 FIRST 集加入；如果第二个符号的 FIRST 集也包含空，继续加入下一个符号的 FIRST 集，以此类推。

对于每个非终结符号，针对其每个产生式：

- 获取产生式右部符号串的 FIRST 集，并移除其中的空，得到一个终结符集合。
- 如果产生式右部符号串的 FIRST 集含有空，则需将当前文法符号的 FOLLOW 集加入得到的终结符集合。
- 最后，将当前产生式填入当前非终结符对应的终结符在分析表中的位置。


```python
def calculate_first_of_string(string, first_sets):
    first_set = set()

    for symbol in string:
        first_set |= first_sets[symbol]

        if 'ε' not in first_sets[symbol]:
            break

    return first_set

def build_ll1_table(grammar, first_sets, follow_sets):
    terminals = grammar['terminals']
    non_terminals = grammar['non_terminals']

    ll1_table = {non_terminal: {terminal: [] for terminal in terminals} for non_terminal in non_terminals}

    # 对于每个文法的每个产生式，去计算每个产生式右部符号串的first集，并判断有无空在里面，如果有，考虑follow集
    for non_terminal in non_terminals:
        for production in grammar[non_terminal]:
            first_set = calculate_first_of_string(production, first_sets)

            for terminal in first_set:
                if terminal != 'ε':
                    ll1_table[non_terminal][terminal].append(production)

            if 'ε' in first_set:
                for terminal in follow_sets[non_terminal]:
                    ll1_table[non_terminal][terminal].append(production)

    return ll1_table
```

第五步，实现分析器

记得初始化符号栈为`['#', 'E'] `，开始分析过程即可。

```python
def parse_input_string(input_string, ll1_table):
    stack = ['#', 'E'] 
    input_string += '#'  
    index = 0 

    while stack:
        top = stack[-1]
        current_input = input_string[index]

        # 对当前栈顶符号进行匹配
        # 终结符
        if top.isupper():
            if ll1_table[top][current_input]:
                popped = stack.pop()

                for symbol in reversed(ll1_table[top][current_input][0]):
                    if symbol != 'ε':
                        stack.append(symbol)

                print(f"Chose production: {popped} -> {ll1_table[top][current_input][0]}")
            else:
                # 分析表中没有对应的产生式
                return False
        # 非终结符并且匹配成功
        elif top == current_input:
            stack.pop()
            index += 1
        else:
            return False

    return True
```

## 结果

成功实现语法分析😊

![](./res.png)

# 自底向上语法分析

## 需求
构建一个语法分析器，要求使用自底向上LR0方法分析。

## 思路

第一步，依然是从文件中先读入文法，保存产生式，和之前实验几乎一样，这里不赘述了。

第二步，构建出项目集规范族，就是LR分析法中构造出来的DFA中各个状态集的集合。
- 需要先手动构造出0号状态集，并求其闭包。
- 执行goto操作以获取新的状态集，再求新的状态集的闭包
- 再对新的状态集执行goto操作
- ...
其实这就是一个递归的过程，我们只需要写一个函数处理需要goto的状态集即可，这个函数处理完需要goto的状态集会生成goto后的状态集，这些状态集当然也是需要goto的，那我们调用自己就好了，直到没有新的状态集生成。

构建项目规范族
```python
# 构造项目集规范族
def build_item_sets(productions):
    item_sets = []  # 存储所有的项目集

    # 构建初始状态，即 0 号状态
    initial_item_set = []  
    initial_item_set.append(Production("E'", "•E"))  

    # 为0号状态执行闭包操作
    closure(initial_item_set, productions)
    item_sets.append(initial_item_set)  # 将初始状态添加到项目集规范族中

    def recursive_build(item_set):
        # 对当前状态的每个符号进行扩展
        for symbol in get_symbols(item_set):  # 获取项目集中的所有符号（非终结符和终结符）
            new_item_set = goto(item_set, symbol, productions)  # 通过 Goto 操作生成新的项目集
            if new_item_set and new_item_set not in item_sets: 
                closure(new_item_set, productions)  # 对新的项目集执行闭包操作
                item_sets.append(new_item_set)  # 将新状态添加到项目集规范族中
                recursive_build(new_item_set)  # 递归构建新状态

    recursive_build(initial_item_set)  # 从初始状态开始递归构建状态

    return item_sets  # 返回构建完成的项目集规范族
```

闭包函数
```python
# 获取项目集的闭包
# 闭包可以理解为扩展，由一个项目扩展到一整个项目集，这个集合里的项目是在状态上是等价的。
# 等待的是一个非终结符那么就是可以扩展的
# 去遍历当前项目集每一个活前缀看看能否扩展即可。
# 需要多次遍历
def closure(item_set, productions):
    while True:
        new_items = []  # 存储新加入的项目
        added = False  # 标记是否有新项目被添加
        for item in item_set:
            dot_index = item.right.find('•')
            if dot_index != len(item.right) - 1:  # 如果点不在右部末尾
                next_symbol = item.right[dot_index + 1]  # 获取点后面的符号
                if next_symbol in productions:  # 如果是非终结符
                    # 添加非终结符的所有产生式到闭包中
                    for prod in productions[next_symbol]:
                        new_item = Production(next_symbol, '•' + prod.right)
                        if new_item not in item_set and new_item not in new_items:
                            new_items.append(new_item)
                            added = True 
        if not added:
            break
        item_set += new_items  # 将新产生的项目加入闭包
```


goto函数
```python
def goto(item_set, symbol, productions):
    """
    获取当前状态，来了一个symbol之后，将会转移到的状态

    Args:
        item_set: 当前状态集.
        symbol: 参数.
        productions: 产生式规则
    Returns:
        type: 一个状态集，为当前状态转移到的状态集
    """
    new_item_set = []  # 存储移进后的项目集
    for item in item_set:
        dot_index = item.right.find('•')
        if dot_index != len(item.right) - 1 and item.right[dot_index + 1] == symbol:
            new_right = item.right[:dot_index] + symbol + '•' + item.right[dot_index + 2:]
            new_item_set.append(Production(item.left, new_right))
    closure(new_item_set, productions)  # 对移进后的项目集执行闭包操作
    return new_item_set
```

第三步，根据构建好的项目规范集，构造出LR0分析表。
- 移进项目
  - 枚举每一个终结符和非终结符，并尝试在当前状态集下goto，看能否goto成功，能那么是移进项目
- 规约项目
  - 项目集第一个产生式以•结束就是规约项目。

构建分析表
```python
def fill_LR0_table(item_sets, productions, terminals, non_terminals):
    """
    构建LR0分析表
    """
    action_table = {}  # 初始化 Action 表
    goto_table = {}    # 初始化 Goto 表
    terminals.add('#') 
    # 遍历状态集
    for i, item_set in enumerate(item_sets):
        # 考虑移进项目
        # 思路是枚举每一个终结符和非终结符，并尝试在当前状态集下goto，看能否goto成功，能那么是移进项目
        for symbol in terminals | non_terminals:
            if symbol in terminals:
                next_state = goto(item_set, symbol, productions)
                if next_state:
                    action_table[i, symbol] = ('shift', item_sets.index(next_state))
            
            else:
                next_item_set = goto(item_set, symbol, productions)
                if next_item_set in item_sets:
                    goto_table[i, symbol] = item_sets.index(next_item_set)
        # 考虑每个状态集第一个产生式是否为归约项目
        prod = item_set[0]
        if prod.right.endswith('•'):
            # 找到规约产生式的编号
            ind = 1
            tar = None
            for left in productions:
                for item in productions[left]:
                    if item.right == prod.right.split('•')[0] and item.left == prod.left: 
                        tar = ind
                        break
                    ind += 1
            # 规约的时候，当前状态集遇到任意非终结符都进行规约！
            for symbol in terminals:
                if tar != None:
                    action_table[i, symbol] = ('reduce', tar)  

        if 'E' in item_set[0].left and item_set[0].right == 'E•':
            action_table[i, '#'] = 'accept'  
    
    return action_table, goto_table
```

第四步，实现解析函数。需要维护两个栈，和指向输入符号串的指针，之后不断查表实现分析即可。需要注意的是规约时候符号栈和状态栈都需要弹出相同数量的元素。并且规约之后需要解决符号栈状态栈数量不平衡的问题。

```python
def parse(input_string, action_table, goto_table, productions):
    """
    对输入的句子按照LR分析表开始语法分析。
    """
    stack_state = [0] 
    stack_symbol = ['#']
    input_symbols = input_string.split()[0] + '#'  # 输入符号串
    index = 0

    while True:
        current_state = stack_state[-1]
        current_symbol = input_symbols[index]

        print(f"当前状态: {current_state}, 当前符号: {current_symbol}")

        action = action_table.get((current_state, current_symbol))

        if action:
            
            if action== 'accept':
                print("解析成功！")
                return True
            
            action_type, action_value = action
            
            if action_type == 'shift':
                stack_symbol.append(current_symbol)
                stack_state.append(action_value)
                index += 1
                print(f"移进: 移动到状态 {action_value}")
            elif action_type == 'reduce':
                productions_for_reduce = None
                ind = 1
                for left in productions:
                    for proc in productions[left]:
                        if ind == action_value:
                            productions_for_reduce = proc
                        ind += 1
                
                # 规约时候符号栈和状态栈都需要弹出相同数量的元素
                for _ in range(len(productions_for_reduce.right)):
                    stack_symbol.pop()
                    stack_state.pop()
                stack_symbol.append(productions_for_reduce.left)
                print(stack_state)
                print(stack_symbol)
                # 解决符号栈状态栈数量不平衡的问题
                while stack_state.__len__() != stack_symbol.__len__():
                    print(goto_table.get((stack_state[-1], stack_symbol[-1])))
                    stack_state.append(goto_table.get((stack_state[-1], stack_symbol[-1])))
                
            else:
                print("解析失败：无效的操作")
                return False
        else:
            print("解析失败：未找到动作")
            return False
```

## 结果
分析成功😊
![](./res1.png)

![](./res2.png)

![](./res3.png)

# 语义分析和中间代码生成

TODO