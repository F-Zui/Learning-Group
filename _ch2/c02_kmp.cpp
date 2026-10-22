#include <bits/stdc++.h>
using namespace std;

const int MAXN = 1000005;
int fail_[MAXN];              // fail_[i] = t[0..i] 的最长 border 长度
char stk[MAXN];               // 用栈当"当前字符串"
int len[MAXN];                // len[k] = 栈里前 k 个字符结尾处能与 t 匹配上的长度
int top = 0;

int main() {
    string s, t;
    cin >> s >> t;
    int n = s.size(), m = t.size();

    // 1) 只对模式串自身求 fail，O(m)
    fail_[0] = 0;
    for (int i = 1; i < m; ++i) {
        int j = fail_[i - 1];
        while (j && t[i] != t[j]) j = fail_[j - 1];
        if (t[i] == t[j]) ++j;
        fail_[i] = j;
    }

    // 2) 主串逐字符压栈，失配时沿 fail 跳
    for (int i = 0; i < n; ++i) {
        stk[++top] = s[i];
        int j = (top > 1) ? len[top - 1] : 0;   // 继承栈里前一个位置的匹配长度
        while (j && s[i] != t[j]) j = fail_[j - 1];
        if (s[i] == t[j]) ++j;
        len[top] = j;
        if (j == m) top -= m;                   // 凑满整个 t：整段弹出，指针自动前提
    }

    stk[top + 1] = '\0';
    cout << (stk + 1) << '\n';
    return 0;
}
