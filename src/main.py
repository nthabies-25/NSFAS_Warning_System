import pandas as pd
from risk_engine import calculate_risk, get_risk_level

df = pd.read_csv("data/students.csv")

df["risk_score"] = df.apply(calculate_risk, axis=1)
df["risk_level"] = df["risk_score"].apply(get_risk_level)

print("\nFirst 5 Records")
print(df.head())

print("\nDataset Info")
print(df.info())

print("\nSummary Statistics")
print(df.describe())

print("\nNumber of Students")
print(len(df))

print("\nAverage Mark")
print(df["average_mark"].mean())

print("\nStudents with Attendance Below 70%")

at_risk = df[df["attendance"] < 70]
print(at_risk["name"])


print("\nStudents with Average Marks Below 50%")
low_grade = df[df["average_mark"] < 50]

#printing students with mark below 50
for student in low_grade["name"]:
    print(student)
    

#counting high-risk students    
print(df[["name", "risk_score", "risk_level"]])

high_risk = df[df["risk_level"] == "HIGH"]

print("\nNumber of High Risk Students")
print(len(high_risk))

#high risk students only
print("\nHigh Risk Students")

print(df[df["risk_level"] == "HIGH"]
      [["name", "risk_score", "risk_level"]])

#printing students with highest risk score
highest_risk = df.sort_values(
    by="risk_score",
    ascending=False
)
print("\nHighest Risk Student")

print(
    highest_risk[["name", "risk_score", "risk_level"]].head(1)
)


    
    


