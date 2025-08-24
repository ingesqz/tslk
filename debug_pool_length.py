import pandas as pd
import os

def examine_pool_data(file_path):
    """
    Examine the pool length data in column G of a file.
    """
    print(f"\n{'='*60}")
    print(f"EXAMINING POOL DATA: {os.path.basename(file_path)}")
    print(f"{'='*60}")
    
    # Read the Excel file
    df = pd.read_excel(file_path, header=None)
    
    print(f"Total rows: {len(df)}")
    print(f"Total columns: {len(df.columns)}")
    
    # Look at column G (index 6) data
    print(f"\nColumn G (Pool Length) data samples:")
    
    # Find rows that have swimmer data (where column 0 has names)
    swimmer_rows = []
    for idx, row in df.iterrows():
        if pd.notna(row[0]) and isinstance(row[0], str) and "Navn:" in row[0]:
            swimmer_rows.append(idx)
    
    print(f"Found {len(swimmer_rows)} swimmer name rows")
    
    # Examine pool data around swimmer rows
    pool_samples = []
    for i, swimmer_row in enumerate(swimmer_rows[:5]):  # Look at first 5 swimmers
        print(f"\nSwimmer {i+1}: {df.iloc[swimmer_row, 0]}")
        
        # Look at the next few rows after swimmer name for pool data
        for j in range(swimmer_row + 1, min(swimmer_row + 5, len(df))):
            if pd.notna(df.iloc[j, 6]):  # Column G
                pool_val = df.iloc[j, 6]
                print(f"  Row {j}: Column G = '{pool_val}' (type: {type(pool_val)})")
                pool_samples.append(pool_val)
                break
    
    # Also look for any unique values in column G
    unique_pool_values = df[6].dropna().unique()
    print(f"\nUnique values in Column G:")
    for val in unique_pool_values:
        print(f"  '{val}' (type: {type(val)})")
    
    return pool_samples

def main():
    """
    Examine pool data in all grdRanking files.
    """
    rawdata_folder = "Rawdata"
    
    # Get all files starting with "grdRanking" in the Rawdata folder
    grd_files = []
    for file in os.listdir(rawdata_folder):
        if file.startswith("grdRanking") and file.endswith(".xlsx"):
            grd_files.append(os.path.join(rawdata_folder, file))
    
    print(f"Found {len(grd_files)} grdRanking files to examine:")
    for file in grd_files:
        print(f"  - {file}")
    
    # Examine each file
    for file_path in grd_files:
        examine_pool_data(file_path)

if __name__ == "__main__":
    main() 