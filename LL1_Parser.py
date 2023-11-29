def read_grammar(file_path):
    grammar = {'terminals': set(), 'non_terminals': set()}
    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            if line:
                parts = line.split('->')
                non_terminal = parts[0].strip()
                grammar['non_terminals'].add(non_terminal)
                productions = [prod.strip() for prod in parts[1].split('|')]
                for production in productions:
                    for symbol in production:
                        if symbol.isupper():
                            grammar['non_terminals'].add(symbol)
                        else:
                            grammar['terminals'].add(symbol)
                grammar[non_terminal] = productions
    grammar['terminals'].add('#')
    return grammar


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

def calculate_first_of_string(string, first_sets):
    first_set = set()

    for symbol in string:
        first_set |= first_sets[symbol]

        if 'ε' not in first_sets[symbol]:
            break

    return first_set



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

def format_ll1_table(ll1_table):
    for non_terminal, row in ll1_table.items():
        print(f"{non_terminal}:", end=" ")
        for terminal, productions in row.items():
            print(f"{terminal}: {productions}", end=", ")
        print()


file_path = 'grammar.txt'
grammar_data = read_grammar(file_path)
print("输入文法：\n", grammar_data)

first_sets = calculate_first_sets(grammar_data)
follow_sets = calculate_follow_sets(grammar_data, first_sets)
print("FIRST集: \n",first_sets)
print("FOLLOW集: \n",follow_sets)
ll1_table = build_ll1_table(grammar_data, first_sets, follow_sets)

print("LL1_table:")
format_ll1_table(ll1_table)

print(parse_input_string("i+i*i", ll1_table))