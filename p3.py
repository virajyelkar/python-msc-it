# 3. Password Strength Analyzer

p = input()

if not any(c.isupper() for c in p):
    print("No uppercase")

if not any(c.islower() for c in p):
    print("No lowercase")

if not any(c.isdigit() for c in p):
    print("No digit")

special = "!@#$%^&*"

if not any(c in special for c in p):
    print("No special character")

for i in range(len(p)-1):
    if p[i] == p[i+1]:
        print("Repeated consecutive characters")
        break