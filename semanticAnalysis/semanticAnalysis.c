#include "stdio.h"
#include "stdlib.h"
#include "string.h"
char prog[100], token[8], ch;
char *rwtab[6] = {"begin", "if", "then", "while", "do", "end"};
int syn, p, m, n, sum, q;
int kk;
struct {
    char result1[8];
    char ag11[8];
    char op1[8];
    char ag21[8];
} quad[20];
char *factor();
char *expression();
int yucu();
char *term();
int statement();
int lrparser();
char *newtemp();
void scaner();
void emit(char *result, char *ag1, char *op, char *ag2);

int main() {
    int j;
    q = p = kk = 0;
    printf("\nplease input a string (end with '#'): ");
    do {
        scanf("%c", &ch);
        prog[p++] = ch;
    } while (ch != '#');
    p = 0;
    scaner();
    lrparser();
    if (q > 19)
        printf(" to long sentense!\n");
    else
        for (j = 0; j < q; j++)
            printf("%s=%s%s%s\n\n", quad[j].result1, quad[j].ag11, quad[j].op1,
                   quad[j].ag21);
    // getch();
}

int lrparser() {
    int schain = 0;
    kk = 0;
    if (syn == 1) {
        scaner();         // 读下一个单词符号
        schain = yucu();  // 调用语句串分析函数进行分析
        if (syn == 6) {
            scaner();  // 读下一个单词符号
            if ((syn == 0) && (kk == 0))
                printf("Success!\n");  // 输出（“success”）
        } else {
            if (kk != 1)
                printf("short of 'end' !\n");  // 输出 ‘缺end’ 错误
            kk = 1;
            //        getch();
            exit(0);
        }
    } else {
        printf("short of 'begin' !\n");  // 输出’begin’错误
        kk = 1;
        //    getch();
        exit(0);
    }
    return (schain);
}
int yucu() {
    int schain = 0;
    schain = statement();  // 调用语句分析函数进行分析
    while (syn == 26) {
        scaner();              // 读下一个单词符号
        schain = statement();  // 调用语句分析函数进行分析
    }
    return (schain);
}
int statement() {
    char tt[8], eplace[8];
    int schain = 0;
    if (syn == 10) {
        strcpy(tt, token);
        scaner();
        if (syn == 18) {
            scaner();  // 读下一个单词符号
            strcpy(eplace, expression());
            emit(tt, eplace, "", "");
            schain = 0;
        } else {
            printf("short of sign ':=' !\n");  // 输出’缺少赋值号’的错误
            kk = 1;
            //   getch();
            exit(0);
        }
        return (schain);
    }
}
char *expression() {
    char *tp, *ep2, *eplace, *tt;
    tp = (char *)malloc(12);  // 分配空间
    ep2 = (char *)malloc(12);
    eplace = (char *)malloc(12);
    tt = (char *)malloc(12);
    strcpy(eplace, term());  // 调用term分析产生表达式计算的第一项eplace
    while ((syn == 13) || (syn == 14)) {
        if (syn == 13)
            strcpy(tt, "+");  // 操作符 tt= ‘+’或者‘—’
        else
            strcpy(tt, "-");
        scaner();             // 读下一个单词符号
        strcpy(ep2, term());  // 调用term分析产生表达式计算的第二项ep2
        strcpy(tp, newtemp());  // 调用newtemp产生临时变量tp存储计算结果
        emit(tp, eplace, tt, ep2);  // 生成四元式送入四元式表
        strcpy(eplace, tp);
    }
    return (eplace);
}
char *term()  // 仿照函数expression编写
{
    char *tp, *ep2, *eplace, *tt;
    tp = (char *)malloc(12);
    ep2 = (char *)malloc(12);
    eplace = (char *)malloc(12);
    tt = (char *)malloc(12);
    strcpy(eplace, factor());
    while ((syn == 15) || (syn == 16)) {
        if (syn == 15)
            strcpy(tt, "*");
        else
            strcpy(tt, "/");
        scaner();  // 读下一个单词符号
        strcpy(ep2, factor());
        strcpy(tp, newtemp());
        emit(tp, eplace, tt, ep2);
        strcpy(eplace, tp);
    }
    return (eplace);
}
char *factor() {
    char *fplace;
    fplace = (char *)malloc(12);
    strcpy(fplace, "");
    if (syn == 10) {
        strcpy(fplace, token);
        scaner();  // 读下一个单词符号
    } else if (syn == 11) {
        // itoa(sum, fplace, 10);
        sprintf(fplace, "%d", sum);
        scaner();  // 读下一个单词符号
    } else if (syn == 27) {
        scaner();               // 读下一个单词符号
        fplace = expression();  // 调用expression分析返回表达式的值
        if (syn == 28)
            scaner();  // 读下一个单词符号
        else {
            printf("error on ')' !\n");
            kk = 1;
            //   getch();
            exit(0);
        }
    } else {
        printf("error on '(' !\n");
        kk = 1;
        // getch();
        exit(0);
    }
    return (fplace);
}
char *newtemp() {
    char *p;
    char m[8];
    p = (char *)malloc(8);
    kk++;
    // itoa(kk, m, 10);
    sprintf(m, "%d", kk);
    strcpy(p + 1, m);
    p[0] = 't';
    return (p);
}
void scaner() {
    sum = 0;
    for (m = 0; m < 8; m++) token[m++] = ' ';
    m = 0;
    ch = prog[p++];
    while (ch == ' ') ch = prog[p++];
    if (((ch <= 'z') && (ch >= 'a')) || ((ch <= 'Z') && (ch >= 'A'))) {
        while (((ch <= 'z') && (ch >= 'a')) || ((ch <= 'Z') && (ch >= 'A')) ||
               ((ch >= '0') && (ch <= '9'))) {
            token[m++] = ch;
            ch = prog[p++];
        }
        p--;
        syn = 10;
        token[m++] = '\0';
        for (n = 0; n < 6; n++)
            if (strcmp(token, rwtab[n]) == 0) {
                syn = n + 1;
                break;
            }
    } else if ((ch >= '0') && (ch <= '9')) {
        while ((ch >= '0') && (ch <= '9')) {
            sum = sum * 10 + ch - '0';
            ch = prog[p++];
        }
        p--;
        syn = 11;
    } else
        switch (ch) {
        case '<':
            m = 0;
            ch = prog[p++];
            if (ch == '>') {
                syn = 21;
            } else if (ch == '=') {
                syn = 22;
            } else {
                syn = 20;
                p--;
            }
            break;
        case '>':
            m = 0;
            ch = prog[p++];
            if (ch == '=') {
                syn = 24;
            } else {
                syn = 23;
                p--;
            }
            break;
        case ':':
            m = 0;
            ch = prog[p++];
            if (ch == '=') {
                syn = 18;
            } else {
                syn = 17;
                p--;
            }
            break;
        case '+':
            syn = 13;
            break;
        case '-':
            syn = 14;
            break;
        case '*':
            syn = 15;
            break;
        case '/':
            syn = 16;
            break;
        case '(':
            syn = 27;
            break;
        case ')':
            syn = 28;
            break;
        case '=':
            syn = 25;
            break;
        case ';':
            syn = 26;
            break;
        case '#':
            syn = 0;
            break;
        default:
            syn = -1;
            break;
        }
}
void emit(char *result, char *ag1, char *op, char *ag2) {
    strcpy(quad[q].result1, result);
    strcpy(quad[q].ag11, ag1);
    strcpy(quad[q].op1, op);
    strcpy(quad[q].ag21, ag2);
    q++;
}
