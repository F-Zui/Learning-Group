#include <bits/stdc++.h>
using namespace std;

const int MAXN = 100005;
int head[MAXN], nxt[MAXN << 1], to[MAXN << 1], wt[MAXN << 1], ecnt = 0;
int d[MAXN];                 // d[u] = 根到 u 的边权异或值
bool vis[MAXN];

void addEdge(int u, int v, int w) {
    to[++ecnt] = v; wt[ecnt] = w; nxt[ecnt] = head[u]; head[u] = ecnt;
}

// 01-Trie：每个数从第 30 位插到第 0 位，节点数 <= 31n + 1
const int MAXT = 3200005;
int ch[MAXT][2], tot = 0;

void insert(int x) {
    int u = 0;
    for (int i = 30; i >= 0; --i) {
        int b = (x >> i) & 1;
        if (!ch[u][b]) ch[u][b] = ++tot;      // 走不通才建新点，共享前缀
        u = ch[u][b];
    }
}

int query(int x) {
    int u = 0, res = 0;
    for (int i = 30; i >= 0; --i) {
        int b = (x >> i) & 1;
        if (ch[u][b ^ 1]) {                    // 反向位存在就先走它，这一位能拿到 1
            res |= 1 << i;
            u = ch[u][b ^ 1];
        } else {
            u = ch[u][b];
        }
    }
    return res;
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n;
    cin >> n;
    for (int i = 1; i < n; ++i) {
        int u, v, w;
        cin >> u >> v >> w;
        addEdge(u, v, w);
        addEdge(v, u, w);
    }
    // 迭代的 BFS 求前缀异或，避免 10^5 深度的递归爆栈
    queue<int> q;
    q.push(1);
    vis[1] = true;
    while (!q.empty()) {
        int u = q.front(); q.pop();
        insert(d[u]);
        for (int e = head[u]; e; e = nxt[e]) {
            int v = to[e];
            if (vis[v]) continue;
            vis[v] = true;
            d[v] = d[u] ^ wt[e];               // 异或是自己的逆运算，可沿路径累积
            q.push(v);
        }
    }
    int ans = 0;
    for (int i = 1; i <= n; ++i) ans = max(ans, query(d[i]));
    cout << ans << '\n';
    return 0;
}
