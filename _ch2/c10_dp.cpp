#include <bits/stdc++.h>
using namespace std;

double x[19], y[19];
int line[19][19];            // line[i][j] = 过 i、j 的抛物线能打掉的猪的集合（位掩码）
int dp[1 << 18];

int main() {
    int T;
    scanf("%d", &T);
    while (T--) {
        int n, m;
        scanf("%d%d", &n, &m);   // m 只是指令类型，对答案没有影响
        for (int i = 0; i < n; ++i) scanf("%lf%lf", &x[i], &y[i]);

        for (int i = 0; i < n; ++i)
            for (int j = 0; j < n; ++j) line[i][j] = 1 << i;   // 默认只能单打 i

        for (int i = 0; i < n; ++i)
            for (int j = i + 1; j < n; ++j) {
                if (fabs(x[i] - x[j]) < 1e-8) continue;       // 两点同 x，没有合法抛物线
                double a = (y[i] / x[i] - y[j] / x[j]) / (x[i] - x[j]);
                if (a >= -1e-8) continue;                     // 必须开口向下
                double b = y[i] / x[i] - a * x[i];
                int mask = 0;
                for (int k = 0; k < n; ++k)
                    if (fabs(a * x[k] * x[k] + b * x[k] - y[k]) < 1e-6) mask |= 1 << k;
                line[i][j] = line[j][i] = mask;
            }

        int full = (1 << n) - 1;
        for (int s = 0; s <= full; ++s) dp[s] = 1e9;
        dp[0] = 0;
        for (int s = 0; s <= full; ++s) {
            if (dp[s] >= 1e9) continue;
            int low = -1;                                     // 第一个没被打掉的猪
            for (int k = 0; k < n; ++k) if (!(s >> k & 1)) { low = k; break; }
            if (low < 0) continue;
            dp[s | (1 << low)] = min(dp[s | (1 << low)], dp[s] + 1);
            for (int k = 0; k < n; ++k) {
                if (s >> k & 1) continue;
                int ns = s | line[low][k];
                dp[ns] = min(dp[ns], dp[s] + 1);
            }
        }
        printf("%d\n", dp[full]);
    }
    return 0;
}
