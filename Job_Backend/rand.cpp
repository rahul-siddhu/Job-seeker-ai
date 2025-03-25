#include<bits/stdc++.h>

long long nCr(int n, int r) {
    if (r > n - r) r = n - r;
    
    long long res = 1;
    for (int i = 0; i < r; i++) {
        res *= (n - i);
        res /= (i + 1);
    }

    return res;
}
long long Balanced(int A, int B, int C){
    long long ans = 0;
    if(A<4 || B<1)return 0;
    else{
        for(int i=4;i<=A-1;i++){
            if(C-i>B)continue;
            ans += nCr(A, i)*nCr(B, C-i);
        }
    }
    return ans;
}