#include <cctype>
#include <fstream>
#include <iostream>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <vector>

enum TokenType {
    KEYWORD = 1,
    IDENTIFIER = 2,
    CONSTANT = 3,
    OPERATOR = 4,
    SEPARATOR = 5,
};

const std::unordered_set<std::string> KEYWORDS = {
    "if", "int", "for", "while", "do", "return", "break", "continue"};

const std::unordered_set<std::string> SEPARATORS = {",", ";", "(",
                                                    ")", "{", "}"};

std::unordered_map<std::string_view, TokenType> operatorSeparatorMap = {
    {"+", OPERATOR},  {"-", OPERATOR},  {"*", OPERATOR},  {"/", OPERATOR},
    {"=", OPERATOR},  {":=", OPERATOR}, {"<", OPERATOR},  {"<=", OPERATOR},
    {">", OPERATOR},  {">=", OPERATOR}, {"<>", OPERATOR}, {",", SEPARATOR},
    {";", SEPARATOR}, {"(", SEPARATOR}, {")", SEPARATOR}, {"{", SEPARATOR},
    {"}", SEPARATOR}};

class SymbolTableEntry {
public:
    SymbolTableEntry(int tokenType, const std::string &symbol)
        : symbol(symbol), tokenType(tokenType) {}

    std::string symbol; /**< 符号字符串 */
    int tokenType;      /**< 标记类型 */
};

class SymbolTable {
public:
    void insertSymbol(const std::string &symbol, int tokenType) {
        entries.emplace_back(tokenType, symbol);
    }

    void printTable() {
        for (const auto &entry : entries) {
            std::cout << "(" << entry.tokenType << ", \"" << entry.symbol
                      << "\")\n";
        }
    }

private:
    std::vector<SymbolTableEntry> entries;
};

SymbolTable symbolTable;

bool isKeyword(const std::string &word) {
    return KEYWORDS.find(word) != KEYWORDS.end();
}

bool isSeparator(const std::string &charStr) {
    return SEPARATORS.find(charStr) != SEPARATORS.end();
}

void handleAlpha(const std::string &code, size_t &index) {
    size_t end = index + 1;
    while (end < code.size() && isalnum(code[end])) {
        end++;
    }
    std::string word = code.substr(index, end - index);
    index = end - 1;
    symbolTable.insertSymbol(word, isKeyword(word) ? KEYWORD : IDENTIFIER);
}

void handleDigit(const std::string &code, size_t &index) {
    size_t end = index + 1;
    while (end < code.size() && isdigit(code[end])) {
        end++;
    }
    std::string num = code.substr(index, end - index);
    symbolTable.insertSymbol(num, CONSTANT);
    index = end - 1;
}

bool handleSeparatorOrOperator(const std::string &code, size_t &index) {
    std::string currentChar(&code[index], 1);

    if (currentChar == "<" || currentChar == ">" || currentChar == ":") {
        // 检查多字符操作符
        if (index + 1 < code.size()) {
            std::string nextChar(&code[index + 1], 1);
            std::string combined = currentChar + nextChar;
            if (operatorSeparatorMap.find(combined) !=
                operatorSeparatorMap.end()) {
                currentChar = combined;
                index++;
            }
        }
    }

    if (operatorSeparatorMap.find(currentChar) != operatorSeparatorMap.end()) {
        symbolTable.insertSymbol(currentChar,
                                 operatorSeparatorMap[currentChar]);
    } else {
        return false;
    }
    return true;
}

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

std::string readInput(const std::string &path) {
    std::ifstream inputFile(path);
    if (!inputFile.is_open()) {
        std::cerr << "错误：无法打开文件！" << std::endl;
        return "";
    }
    return std::string((std::istreambuf_iterator<char>(inputFile)),
                       std::istreambuf_iterator<char>());
}

int main() {
    const std::string codePath = "./input.txt";
    const std::string code = readInput(codePath);

    if (!code.empty()) {
        analyze(code);
        symbolTable.printTable();
    }
    return 0;
}
