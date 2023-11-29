def read_grammar(file_path):
    # grammar = {'terminals': set(), 'non_terminals': set()}
    grammar = []
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
    grammar['S\''] = 'S'
    return grammar
        
def make_item(grammar_data):
    item_set = []
    for grammar in grammar_data:
        if not grammar.isupper():
            continue
        
        for production in grammar_data[grammar]:
            print(production)
            
    print(item_set)
    return item_set

        
def make_closure(grammar_data):
    for grammar in grammar_data:
        if grammar.isupper():
            for production in grammar_data[grammar]:
                print(production)            
        

        
        
file_path = 'grammar_LR0.txt'
grammar_data = read_grammar(file_path)
print(grammar_data)


make_closure(grammar_data)
make_item(grammar_data)

