# 定义文法规则的数据结构
class Production:
    def __init__(self, left, right):
        self.left = left
        self.right = right

    # 支持 not in 运算符需要实现这个方法
    def __eq__(self, other): 
        # 自定义对象相等性比较逻辑
        return self.left == other.left and self.right == other.right

def read_file(file_path):
    productions = {}
    terminals = set()
    non_terminals = set()

    with open(file_path, 'r') as file:
        lines = file.readlines()

        for line in lines:
            line = line.strip()
            left, right = line.split('->')
            left = left.strip()
            right = right.strip().split('|')

            non_terminals.add(left)  # 将左部视为非终结符

            if left not in productions:
                productions[left] = []

            for prod in right:
                productions[left].append(Production(left, prod))
                # 处理右部，确定终结符和非终结符
                symbols = prod.split()[0]
                for symbol in symbols:
                    if symbol.islower() or symbol.isnumeric():
                        terminals.add(symbol)
                    elif symbol.isupper() and symbol != 'ε':  # 大写字母视为非终结符
                        non_terminals.add(symbol)

    print('读入文法：')
    ind = 1
    for left in productions:
        for prod in productions[left]:
            print(f"{ind} {prod.left} -> {prod.right}")
            ind += 1

    return terminals, non_terminals, productions


# 定义闭包函数
# 闭包或许可以理解为扩展，由一个项目扩展到一整个项目集，这个集合里的项目是在状态上是等价的。去遍历当前项目集看看能否扩展即可。
# 需要多次遍历，因为加入后的
# 什么是项目呢，分为规约项目和移进项目，你懂的~
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
                            added = True  # 设置标记为有新项目被添加
        if not added:
            break
        item_set += new_items  # 将新产生的项目加入闭包
        


# 定义函数执行 Goto 操作
def goto(item_set, symbol, productions):
    new_item_set = []  # 存储移进后的项目集
    for item in item_set:
        dot_index = item.right.find('•')
        if dot_index != len(item.right) - 1 and item.right[dot_index + 1] == symbol:
            new_right = item.right[:dot_index] + symbol + '•' + item.right[dot_index + 2:]
            new_item_set.append(Production(item.left, new_right))
    closure(new_item_set, productions)  # 对移进后的项目集执行闭包操作
    return new_item_set


# 定义函数获取项目集中的所有符号
def get_symbols(item_set):
    symbols = set()
    for item in item_set:
        # 获取项目中的点后的符号
        if '•' in item.right:
            dot_index = item.right.index('•')
            if dot_index < len(item.right) - 1:
                symbol = item.right[dot_index + 1]  # 获取点后的符号
                symbols.add(symbol)
    return symbols


# 递归构造项目集规范族的函数
def build_item_sets(productions):
    item_sets = []  # 存储所有的项目集

    # 构建初始状态，即 0 号状态
    initial_item_set = []  # 初始状态的项目集
    initial_item_set.append(Production("E'", "•E"))  # 添加起始项目到初始项目集

    # 执行闭包操作
    closure(initial_item_set, productions)
    item_sets.append(initial_item_set)  # 将初始状态添加到项目集规范族中

    # 构造一个状态
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


# 定义函数打印项目规范族
def print_item_sets(item_sets):
    for i, item_set in enumerate(item_sets):
        print(f"State {i}:")
        for item in item_set:
            print(f"    {item.left} -> {item.right}")
        print()

def fill_LR0_table(item_sets, productions, terminals, non_terminals):
    action_table = {}  # 初始化 Action 表
    goto_table = {}    # 初始化 Goto 表
    terminals.add('#')
    for i, item_set in enumerate(item_sets):
        for symbol in terminals | non_terminals:
            # 填充 Action 表和 Goto 表

            # 对于终结符的移进操作
            if symbol in terminals:
                # 判断当前状态下该符号是否存在移进操作，然后填充 Action 表
                next_state = goto(item_set, symbol, productions)
                if next_state:
                    action_table[i, symbol] = ('shift', item_sets.index(next_state))
            
            # 对于非终结符的 Goto 操作
            else:
                # 判断当前状态下该符号是否存在 Goto 操作，然后填充 Goto 表
                next_item_set = goto(item_set, symbol, productions)
                if next_item_set in item_sets:
                    goto_table[i, symbol] = item_sets.index(next_item_set)
        
        # 对于规约动作和接受状态
        # 检查当前状态的项目集是否有规约动作或接受状态，并填充 Action 表
        for prod in item_set:
            # 判断是否有规约动作
            if prod.right.endswith('•'):
                # 找到规约的产生式并填充 Action 表
                for symbol in terminals:
                    ind = 1
                    tar = None
                    for left in productions:
                        for item in productions[left]:
                            if item.right == prod.right.split('•')[0] and item.left == prod.left: 
                                tar = ind
                                break
                            ind += 1
                    if tar != None:
                        action_table[i, symbol] = ('reduce', tar)  # 将规约动作填入 Action 表中

                # 检查是否为接受状态，将接受状态填入 Action 表
        if 'E' in item_set[0].left and item_set[0].right == 'E•':
            action_table[i, '#'] = 'accept'  # 假设开始符号为 'E'，结束标记为 '#'
    
    return action_table, goto_table


def parse(input_string, action_table, goto_table, productions):
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
            print(action)
            
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
                
                
                for _ in range(len(productions_for_reduce.right)):
                    stack_symbol.pop()
                    stack_state.pop()
                stack_symbol.append(productions_for_reduce.left)
                print(stack_state)
                print(stack_symbol)
                while stack_state.__len__() != stack_symbol.__len__():
                    print(goto_table.get((stack_state[-1], stack_symbol[-1])))
                    stack_state.append(goto_table.get((stack_state[-1], stack_symbol[-1])))
                
            else:
                print("解析失败：无效的操作")
                return False
        else:
            print("解析失败：未找到动作")
            return False

def print_goto_table(goto_table):
    print("Goto 表:")
    for key, value in goto_table.items():
        print(f"({key}): {value}")

def print_action_table(action_table):
    print("Action 表:")
    for key, value in action_table.items():
        print(f"({key}): {value}")
        
        
file_path = 'grammar.txt'
terminals, non_terminals, productions = read_file(file_path)
item_sets = build_item_sets(productions)
build_item_sets(productions)
print_item_sets(item_sets)
action_table, goto_table = fill_LR0_table(item_sets, productions, terminals, non_terminals)
print_action_table(action_table)
print_goto_table(goto_table)
parse("acccd", action_table, goto_table, productions)
