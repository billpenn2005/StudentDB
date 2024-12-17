#include <algorithm>
#include <bits/stdc++.h>
#include <functional>
#include <iostream>
#include <queue>
#include <set>
#include <stack>
#include <utility>
#include <vector>
#define int long long
void solve( ) {
    int n;
    std::cin >> n;
    std::vector< int > a(n + 2);
    for (int i = 1; i <= n; i++)
        std::cin >> a[i];
    std::vector< std::vector< int > > dp(n + 2, std::vector< int >(n + 2));
    std::vector<int> mxdp(n + 2),exmxdp(n + 2);
    for (int i = 1; i <= n; i++) {
        for (int j = 0; j < i; j++) {
            int res0 = 0;
            int l0st = -1;

            for (int k = j + 1; k < i; k++) {
                if (a[k] != l0st) {
                    l0st = a[k];
                } else
                    res0 += a[k];
            }
            if (a[j] == a[i])
                res0 += a[i];
            dp[i][j]      = std::max(dp[i][j], res0 + exmxdp[j + 1]);
        }
        for(int j = 0;j < i;j++){
            mxdp[i] = std::max(mxdp[i], dp[i][j]);
            if(j != i - 1)exmxdp[i] = std::max(exmxdp[i], dp[i][j]);
        }
    }

    std::cout << mxdp[n] << '\n';
}
signed main( ) {
    std::ios::sync_with_stdio(0);
    std::cin.tie(0);
    int T = 1;
    std::cin >> T;
    while (T--)
        solve( );
    return 0;
}