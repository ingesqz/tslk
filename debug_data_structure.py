import pandas as pd
import os

def examine_data_structure(file_path):
    """
    Examine the detailed data structure to understand how pool length relates to results.
    """
    print(f"\n{'='*60}")
    print(f"EXAMINING DATA STRUCTURE: {os.path.basename(file_path)}")
    print(f"{'='*60}")
    
    # Read the Excel file
    df = pd.read_excel(file_path, header=None)
    
    print(f"Total rows: {len(df)}")
    print(f"Total columns: {len(df.columns)}")
    
    # Find rows that have swimmer data
    swimmer_rows = []
    for idx, row in df.iterrows():
        if pd.notna(row[0]) and isinstance(row[0], str) and "Navn:" in row[0]:
            swimmer_rows.append(idx)
    
    print(f"Found {len(swimmer_rows)} swimmer name rows")
    
    # Examine the structure around a few swimmers
    for i, swimmer_row in enumerate(swimmer_rows[:3]):  # Look at first 3 swimmers
        print(f"\n--- Swimmer {i+1}: {df.iloc[swimmer_row, 0]} ---")
        
        # Look at the next few rows after swimmer name
        for j in range(swimmer_row + 1, min(swimmer_row + 10, len(df))):
            row_data = df.iloc[j]
            
            # Check if this row has time data (column 2)
            if pd.notna(row_data[2]):
                print(f"  Row {j}: Time={row_data[2]}, Points={row_data[3]}, Date={row_data[4]}, Location={row_data[5]}, Pool={row_data[6]}")
            elif pd.notna(row_data[0]) and isinstance(row_data[0], str) and "Navn:" in row_data[0]:
                # Found next swimmer, stop here
                break
    
    # Count pool lengths
    pool_counts = {}
    for idx, row in df.iterrows():
        if pd.notna(row[6]) and isinstance(row[6], str):
            pool_val = row[6]
            if pool_val in pool_counts:
                pool_counts[pool_val] += 1
            else:
                pool_counts[pool_val] = 1
    
    print(f"\nPool length counts:")
    for pool, count in pool_counts.items():
        print(f"  {pool}: {count} occurrences")

def main():
    """
    Examine data structure in all grdRanking files.
    """
    rawdata_folder = "Rawdata"
    
    # Get all files starting with "grdRanking" in the Rawdata folder
    grd_files = []
    for file in os.listdir(rawdata_folder):
        if file.startswith("grdRanking") and file.endswith(".xlsx"):
            grd_files.append(os.path.join(rawdata_folder, file))
    
    # Examine each file
    for file_path in grd_files:
        examine_data_structure(file_path)

if __name__ == "__main__":
    main() 