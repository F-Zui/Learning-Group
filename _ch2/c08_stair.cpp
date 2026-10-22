#include <bits/stdc++.h>
using namespace std;

int main() {
    int T;
    scanf("%d", &T);
    while (T--) {
        int n;
        scanf("%d", &n);
        int xr = 0;
        for (int i = 0; i < n; ++i) {
            int m;
            scanf("%d", &m);
            bool occ[21] = {false};
            for (int k = 0; k < m; ++k) { int p; scanf("%d", &p); occ[p] = true; }
            int c[22], t = 0;
            c[0] = 0;
            for (int p = 1; p <= 20; ++p) if (!occ[p]) c[++t] = p;   // 空格位置升序
            for (int s = t; s >= 1; s -= 2) xr ^= (c[s] - c[s - 1] - 1);  // 从右往左两两配对
        }
        puts(xr ? "YES" : "NO");
    }
    return 0;
}
