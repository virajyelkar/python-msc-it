# 2. Missing Roll Number

a = list(map(int, input().split()))

n = max(a)
s = n * (n + 1) // 2

print(s - sum(a))