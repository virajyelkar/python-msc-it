# Course Registration Conflict Detector 


class Course:
    def __init__(self, code, day, start_time, end_time):
        self.code = code
        self.day = day
        self.start_time = start_time    # stored as "HH:MM"
        self.end_time = end_time

        # Convert times to minutes so they are easy to compare
        self.start_minutes = self.to_minutes(start_time)
        self.end_minutes = self.to_minutes(end_time)

        if self.start_minutes >= self.end_minutes:
            raise ValueError("Start time must be before end time.")

    def to_minutes(self, time_text):
        # "09:30" -> 9 * 60 + 30 = 570
        parts = time_text.split(":")
        if len(parts) != 2:
            raise ValueError("Time must be in HH:MM format, e.g. 09:30")
        hour = int(parts[0])
        minute = int(parts[1])
        if hour < 0 or hour > 23 or minute < 0 or minute > 59:
            raise ValueError("Invalid time. Hour must be 0-23 and minute 0-59.")
        return hour * 60 + minute

    def overlaps(self, other):
        # Conflict only if same day AND the times overlap
        if self.day != other.day:
            return False
        return self.start_minutes < other.end_minutes and other.start_minutes < self.end_minutes

    def __str__(self):
        return self.code + " | " + self.day + " | " + self.start_time + " - " + self.end_time


class Student:
    def __init__(self, student_id, name):
        self.student_id = student_id
        self.name = name
        self.courses = []               # list of registered courses

    def add_course(self, course):
        self.courses.append(course)

    def find_conflicts(self):
        conflicts = []
        # Compare every course with every course after it
        for i in range(len(self.courses)):
            for j in range(i + 1, len(self.courses)):
                if self.courses[i].overlaps(self.courses[j]):
                    conflicts.append((self.courses[i], self.courses[j]))
        return conflicts

    def __str__(self):
        text = "Student ID: " + self.student_id + "\n"
        text += "Name      : " + self.name + "\n"
        text += "Courses   :\n"
        for course in self.courses:
            text += "   " + str(course) + "\n"
        return text


def main():
    students = []

    # Ask for number of students
    while True:
        try:
            n = int(input("Enter number of students: "))
            if n <= 0:
                print("Enter a number greater than 0.")
                continue
            break
        except ValueError:
            print("Please enter a valid number.")

    # Take student details
    for i in range(n):
        print("\n--- Student", i + 1, "---")
        student_id = input("Student ID: ")
        name = input("Student Name: ")
        student = Student(student_id, name)

        while True:
            try:
                count = int(input("How many courses? "))
                if count <= 0:
                    print("Enter a number greater than 0.")
                    continue
                break
            except ValueError:
                print("Please enter a valid number.")

        # Take course details
        for j in range(count):
            print("Course", j + 1)
            while True:
                try:
                    code = input("  Course Code: ")
                    day = input("  Day (e.g. Monday): ").capitalize()
                    start = input("  Start Time (HH:MM): ")
                    end = input("  End Time (HH:MM): ")
                    course = Course(code, day, start, end)
                    student.add_course(course)
                    break
                except ValueError as error:
                    print("  Error:", error)
                    print("  Please enter this course again.")

        students.append(student)

    # Show results
    print("\n========== RESULTS ==========")
    for student in students:
        print()
        print(student)

        conflicts = student.find_conflicts()
        if len(conflicts) > 0:
            print("Conflicting courses:")
            for first, second in conflicts:
                print("   ", first.code, "<-->", second.code, "on", first.day)
        else:
            print("No conflicts. Timetable:")
            for course in student.courses:
                print("   ", course)

        print("Total registered courses:", len(student.courses))
        print("-----------------------------")


main()