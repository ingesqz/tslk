import pandas as pd
import os

def verify_event_file(file_path):
    """
    Verify the contents of a single event file.
    """
    print(f"\n{'='*60}")
    print(f"VERIFYING: {os.path.basename(file_path)}")
    print(f"{'='*60}")
    
    try:
        # Read all four sheets from the Excel file
        males_25m = pd.read_excel(file_path, sheet_name='Male_25m')
        males_50m = pd.read_excel(file_path, sheet_name='Male_50m')
        females_25m = pd.read_excel(file_path, sheet_name='Female_25m')
        females_50m = pd.read_excel(file_path, sheet_name='Female_50m')
        
        print(f"\n📊 MALE 25m SWIMMERS: {len(males_25m)}")
        if len(males_25m) > 0:
            print(f"Best: {males_25m.iloc[0]['Name']} - {males_25m.iloc[0]['Poeng']} points")
            print(f"Average: {males_25m['Poeng'].mean():.1f} points")
        
        print(f"\n🏊‍♂️ MALE 50m SWIMMERS: {len(males_50m)}")
        if len(males_50m) > 0:
            print(f"Best: {males_50m.iloc[0]['Name']} - {males_50m.iloc[0]['Poeng']} points")
            print(f"Average: {males_50m['Poeng'].mean():.1f} points")
        
        print(f"\n🏊‍♀️ FEMALE 25m SWIMMERS: {len(females_25m)}")
        if len(females_25m) > 0:
            print(f"Best: {females_25m.iloc[0]['Name']} - {females_25m.iloc[0]['Poeng']} points")
            print(f"Average: {females_25m['Poeng'].mean():.1f} points")
        
        print(f"\n🏊‍♀️ FEMALE 50m SWIMMERS: {len(females_50m)}")
        if len(females_50m) > 0:
            print(f"Best: {females_50m.iloc[0]['Name']} - {females_50m.iloc[0]['Poeng']} points")
            print(f"Average: {females_50m['Poeng'].mean():.1f} points")
        
        total_swimmers = len(males_25m) + len(males_50m) + len(females_25m) + len(females_50m)
        print(f"\n📈 TOTAL SWIMMERS: {total_swimmers}")
        
        return True
        
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return False

def main():
    """
    Verify all files in the EndResult folder.
    """
    endresult_folder = "EndResult"
    
    if not os.path.exists(endresult_folder):
        print(f"EndResult folder not found!")
        return
    
    # Get all Excel files in the EndResult folder
    excel_files = []
    for file in os.listdir(endresult_folder):
        if file.endswith(".xlsx") and not file.startswith("~$"):
            excel_files.append(os.path.join(endresult_folder, file))
    
    if not excel_files:
        print("No Excel files found in EndResult folder!")
        return
    
    print(f"Found {len(excel_files)} files to verify:")
    for file in excel_files:
        print(f"  - {os.path.basename(file)}")
    
    # Verify each file
    successful_verifications = 0
    for file_path in excel_files:
        if verify_event_file(file_path):
            successful_verifications += 1
    
    print(f"\n{'='*60}")
    print(f"VERIFICATION SUMMARY")
    print(f"{'='*60}")
    print(f"Successfully verified: {successful_verifications}/{len(excel_files)} files")
    
    if successful_verifications == len(excel_files):
        print("✅ All files processed successfully!")
    else:
        print("❌ Some files had issues during verification.")

if __name__ == "__main__":
    main() 