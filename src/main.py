import pandas as pd
import logging
from risk_engine import process_studemt
from datetime import datetime

#Configure logging
logging.basicConfig(
    level = logging.INFO,
    format ='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def load_data(filepath: str) ->pd.DataFrame:
    """Loads CSV and handles missing values gracefully."""
    try:
        df = pd.read_csv(filepath)
        logger.info(f"Successfully loaded {len(df)} records from {dilepath}")
        
        #Data Quality Check: fill missing values to prevent crashes
        df['attendance'] = df['attendance'].fillna(0)
        df['average_mark'] = df['average_mark'].fillna(0)
        df['failed_modules'] = df['failed_modules'].fillna(0)
        
        return df
    except FileNotFoundError:
        logger.error(f"File {filepath} not found. Please check the path.")
        raise
    
def main():
    #1.load
    df = load_data("data/student.csv")
    
    #2. Transform
    logger.info("Starrting risk assessment...")
    
    #Convert each row to dict, process, and convert back t DataFrame
    enriched_records = [process_studemt(row.to_dict()) for _, row in df.iterrows()]
    enriched_df = pd.DataFrame(enriched_records)
    
    #3. Load(save results for audit trail)
    output_path = f"data/risk_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    enriched_df.to_csv(output_path, index=False)
    logger.info(f"Risk report saved to {output_path}")
    
    #4. Executve summary
    print("\n" + "="*50)
    print("NSFAS RISK DASHBOARD (OFFLINE BATCH)")
    print("="*50)
    
    high_risk = enriched_df[enriched_df['risk_level'] == 'HIGH']
    medium_risk = enriched_df[enriched_df['risk_level'] == 'MEDIUM']
    
    print(f"Total Student: {len(enriched_df)}")
    print(f"High Risk: {len(high_risk)} ({len(high_risk)/len(enriched_df)*100:.1f}%)")
    
    #The Kill Switch  Alert
    if len(high_risk)> 10:
        print("\n ALERT: More than 10 high-risk students ditected!")
        print(" [SIMULATION] SNS Email sent to NSFAS Administrators.")
        
        print("\nTop 5 Highest Risk Students:")
        print(enriched_df.nlargest(5, 'risk_score')[['name', 'risk_score', 'risk_level']])
    
        return enriched_df

if __name__ == "__main__":
    main()

# df["risk_score"] = df.apply(calculate_risk, axis=1)
# df["risk_level"] = df["risk_score"].apply(get_risk_level)

# print("\nFirst 5 Records")
# print(df.head())

# print("\nDataset Info")
# print(df.info())

# print("\nSummary Statistics")
# print(df.describe())

# print("\nNumber of Students")
# print(len(df))

# print("\nAverage Mark")
# print(df["average_mark"].mean())

# print("\nStudents with Attendance Below 70%")

# at_risk = df[df["attendance"] < 70]
# print(at_risk["name"])


# print("\nStudents with Average Marks Below 50%")
# low_grade = df[df["average_mark"] < 50]

# #printing students with mark below 50
# for student in low_grade["name"]:
#     print(student)
    

# #counting high-risk students    
# print(df[["name", "risk_score", "risk_level"]])

# high_risk = df[df["risk_level"] == "HIGH"]

# print("\nNumber of High Risk Students")
# print(len(high_risk))

# #high risk students only
# print("\nHigh Risk Students")

# print(df[df["risk_level"] == "HIGH"]
#       [["name", "risk_score", "risk_level"]])

# #printing students with highest risk score
# highest_risk = df.sort_values(
#     by="risk_score",
#     ascending=False
# )
# print("\nHighest Risk Student")

# print(
#     highest_risk[["name", "risk_score", "risk_level"]].head(1)
# )


    
    


