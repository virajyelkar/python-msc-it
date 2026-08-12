n = int(input("Enter number of students: "))

students = []

for i in range(n):
    roll = input("Enter Roll No: ")
    name = input("Enter Name: ")

    marks = []
    for j in range(5):
        marks.append(int(input("Enter marks: ")))

    total = sum(marks)
    percentage = total / 5

    if percentage >= 90:
        grade = "A+"
    elif percentage >= 80:
        grade = "A"
    elif percentage >= 70:
        grade = "B"
    elif percentage >= 60:
        grade = "C"
    elif percentage >= 50:
        grade = "D"
    else:
        grade = "F"

    students.append([roll, name, total, percentage, grade])

# Sort by total marks
students.sort(key=lambda x: x[2], reverse=True)

# Rank
for i in range(n):
    if i > 0 and students[i][2] == students[i-1][2]:
        students[i].append(students[i-1][5])
    else:
        students[i].append(i + 1)

# Display
print("\nRank  Roll  Name  Total  Percentage  Grade")

for s in students:
    print(s[5], s[0], s[1], s[2], s[3], s[4])
