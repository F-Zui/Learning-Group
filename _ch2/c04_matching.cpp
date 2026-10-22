#include <bits/stdc++.h>
using namespace std;

const int MAXN = 205;
vector<int> g[MAXN];
int matchR[MAXN], vis[MAXN], stamp = 0;

bool dfs(int u) {
    for (int v : g[u]) {
        if (vis[v] == stamp) continue;        // 本轮增广中已经试过的右点
        vis[v] = stamp;
        if (!matchR[v] || dfs(matchR[v])) {   // 空着，或者它的主人能让位
            matchR[v] = u;
            return true;
        }
    }
    return false;
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int T;
    cin >> T;
    while (T--) {
        int n;
        cin >> n;
        for (int i = 1; i <= n; ++i) {
            g[i].clear();
            for (int j = 1; j <= n; ++j) {
                int x;
                cin >> x;
                if (x == 1) g[i].push_back(j);   // 第 i 行必须在第 j 列有一个黑格
            }
        }
        memset(matchR, 0, sizeof(matchR));
        memset(vis, 0, sizeof(vis));
        stamp = 0;
        int cnt = 0;
        for (int i = 1; i <= n; ++i) {
            ++stamp;                             // 时间戳代替 memset
            if (dfs(i)) ++cnt;
            else break;                          // 有一行配不上，不可能满匹配
        }
        cout << (cnt == n ? "Yes" : "No") << '\n';
    }
    return 0;
}
