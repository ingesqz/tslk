import pandas as pd
import re
from datetime import datetime

def identify_gender(name):
    """
    Identify gender based on the swimmer's name.
    This is a simple heuristic based on common Norwegian names.
    """
    # Remove "Navn: " prefix if present
    clean_name = name.replace("Navn: ", "").strip()
    
    # Split the name to get the first name
    name_parts = clean_name.split(',')
    if len(name_parts) > 1:
        # If it's "Last, First" format, get the first name
        first_name = name_parts[1].strip().split()[0]
    else:
        # If it's "First Last" format, get the first name
        first_name = clean_name.split()[0]
    
    first_name = first_name.lower()
    
    # Common Norwegian male names
    male_names = {
        'odin', 'adam', 'jon', 'albert', 'ole', 'aamund', 'johannes', 'tomas', 'paal',
        'sondre', 'andreas', 'ivan', 'tamer', 'bjarne'
    }
    
    # Common Norwegian female names
    female_names = {
        'sara', 'maria', 'silje', 'carina', 'eirill', 'henriette', 'elise', 'vilde', 
        'tove', 'amanda', 'silje', 'carina', 'sara', 'maria'
    }
    
    # Check if it's a known male name
    if first_name in male_names:
        return 'Male'
    # Check if it's a known female name
    elif first_name in female_names:
        return 'Female'
    else:
        # Try to guess based on name endings and patterns
        if first_name.endswith(('a', 'e', 'i', 'n', 'r')):
            # Common female name endings in Norwegian
            if first_name.endswith(('a', 'e')):
                return 'Female'
            else:
                return 'Male'
        else:
            # Default to male for unknown names (you can adjust this logic)
            return 'Male'

def clean_swimmer_name(name):
    """
    Clean swimmer name for comparison by removing prefixes and standardizing format.
    """
    # Remove "Navn: " prefix if present
    clean_name = name.replace("Navn: ", "").strip()
    
    # Standardize specific name variations
    clean_name = standardize_name_variations(clean_name)
    
    return clean_name

def standardize_name_variations(name):
    """
    Standardize known name variations to their correct format.
    """
    # Standardize "Solum Ole Peder Uthus" to "Ole Peder Uthus Solum"
    if name == "Solum Ole Peder Uthus":
        return "Ole Peder Uthus Solum"
    
    return name

def get_pool_length(pool_val):
    """
    Extract pool length from the pool value in column G.
    """
    if pd.isna(pool_val):
        return "Unknown"
    
    pool_str = str(pool_val).lower()
    if '25' in pool_str or '25m' in pool_str:
        return "25m"
    elif '50' in pool_str or '50m' in pool_str:
        return "50m"
    else:
        return "Unknown"

def process_swim_results(input_file):
    """
    Process swim results Excel file and create a new file with highest points for each swimmer.
    """
    # Read the Excel file
    df = pd.read_excel(input_file, header=None)
    
    # Find the event name from data rows (where times are shown)
    event_name = None
    for idx, row in df.iterrows():
        # Look for rows that have time data (usually in column 2 or 3)
        if pd.notna(row[1]) and isinstance(row[1], str):
            # Check if this looks like an event name (contains distance and stroke)
            if any(keyword in row[1].lower() for keyword in ['m', 'butterfly', 'freestyle', 'backstroke', 'breaststroke', 'medley']):
                event_name = row[1]
                break
    
    if not event_name:
        print("Could not find event name in the data rows")
        return
    
    print(f"Event name found: {event_name}")
    
    # Initialize lists to store data
    swimmers_data = []
    current_swimmer = None
    current_swimmer_data = []
    
    # Process each row
    for idx, row in df.iterrows():
        # Check if this is a swimmer name row (usually has a name in first column)
        if pd.notna(row[0]) and isinstance(row[0], str):
            # If we have data from previous swimmer, process it
            if current_swimmer and current_swimmer_data:
                swimmers_data.append((current_swimmer, current_swimmer_data))
            
            # Start new swimmer
            current_swimmer = row[0]
            current_swimmer_data = []
        else:
            # This is a result row for the current swimmer
            if current_swimmer:
                # Extract relevant data (adjust column indices based on your file structure)
                # Assuming: Time, Points, Date, Location, Pool Length are in specific columns
                try:
                    time_val = row[2] if pd.notna(row[2]) else None  # Time column
                    points_val = row[3] if pd.notna(row[3]) else None  # Points column
                    date_val = row[4] if pd.notna(row[4]) else None  # Date column
                    location_val = row[5] if pd.notna(row[5]) else None  # Location column
                    pool_val = row[6] if pd.notna(row[6]) else None  # Pool length column G
                    
                    # Only add if we have valid points
                    if points_val is not None and isinstance(points_val, (int, float)):
                        current_swimmer_data.append({
                            'Name': current_swimmer,
                            'Tid': time_val,
                            'Poeng': points_val,
                            'Dato': date_val,
                            'Sted': location_val,
                            'Pool': pool_val
                        })
                except:
                    continue
    
    # Add the last swimmer's data
    if current_swimmer and current_swimmer_data:
        swimmers_data.append((current_swimmer, current_swimmer_data))
    
    # Find the best result for each swimmer
    best_results = []
    for swimmer, results in swimmers_data:
        if results:
            # Find the result with highest points
            best_result = max(results, key=lambda x: x['Poeng'] if x['Poeng'] is not None else 0)
            best_results.append(best_result)
    
    # Create DataFrame
    if best_results:
        result_df = pd.DataFrame(best_results)
        
        # Add gender column
        result_df['Gender'] = result_df['Name'].apply(identify_gender)
        
        # Add pool length column
        result_df['PoolLength'] = result_df['Pool'].apply(get_pool_length)
        
        # Add cleaned name column for comparison
        result_df['CleanName'] = result_df['Name'].apply(clean_swimmer_name)
        
        # Check for duplicate names and merge them
        print(f"Total swimmers before duplicate check: {len(result_df)}")
        
        # Group by cleaned name and keep the best result for each unique swimmer
        merged_results = []
        seen_names = set()
        
        for _, group in result_df.groupby('CleanName'):
            if len(group) > 1:
                print(f"Found duplicate swimmer: {group.iloc[0]['CleanName']} ({len(group)} entries)")
                # Keep the one with highest points
                best_entry = group.loc[group['Poeng'].idxmax()]
                merged_results.append(best_entry)
                seen_names.add(best_entry['CleanName'])
            else:
                merged_results.append(group.iloc[0])
                seen_names.add(group.iloc[0]['CleanName'])
        
        # Create new DataFrame with merged results
        result_df = pd.DataFrame(merged_results)
        result_df = result_df.drop('CleanName', axis=1)  # Remove the temporary column
        
        print(f"Total swimmers after duplicate check: {len(result_df)}")
        
        # Clean the names by removing "Navn: " prefix
        result_df['Name'] = result_df['Name'].apply(clean_swimmer_name)
        
        # Sort by Poeng in descending order (highest on top)
        result_df = result_df.sort_values('Poeng', ascending=False)
        
        # Create separate DataFrames for each category
        males_25m = result_df[(result_df['Gender'] == 'Male') & (result_df['PoolLength'] == '25m')].head(10)
        males_50m = result_df[(result_df['Gender'] == 'Male') & (result_df['PoolLength'] == '50m')].head(10)
        females_25m = result_df[(result_df['Gender'] == 'Female') & (result_df['PoolLength'] == '25m')].head(10)
        females_50m = result_df[(result_df['Gender'] == 'Female') & (result_df['PoolLength'] == '50m')].head(10)
        
        # Clean the event name for filename
        clean_event_name = re.sub(r'[<>:"/\\|?*]', '_', event_name)
        clean_event_name = clean_event_name.strip()
        
        # Create output filename
        output_filename = f"{clean_event_name}.xlsx"
        
        # Save to Excel with four sheets
        with pd.ExcelWriter(output_filename, engine='openpyxl') as writer:
            males_25m.to_excel(writer, sheet_name='Male_25m', index=False)
            males_50m.to_excel(writer, sheet_name='Male_50m', index=False)
            females_25m.to_excel(writer, sheet_name='Female_25m', index=False)
            females_50m.to_excel(writer, sheet_name='Female_50m', index=False)
        
        print(f"Created file: {output_filename}")
        print(f"Total unique swimmers processed: {len(result_df)}")
        print(f"Male 25m swimmers: {len(males_25m)} (top 10)")
        print(f"Male 50m swimmers: {len(males_50m)} (top 10)")
        print(f"Female 25m swimmers: {len(females_25m)} (top 10)")
        print(f"Female 50m swimmers: {len(females_50m)} (top 10)")
        
        # Display top results for each category
        print("\nTop 5 Male 25m results:")
        print(males_25m.head(5)[['Name', 'Tid', 'Poeng', 'Dato', 'Sted', 'PoolLength']])
        
        print("\nTop 5 Male 50m results:")
        print(males_50m.head(5)[['Name', 'Tid', 'Poeng', 'Dato', 'Sted', 'PoolLength']])
        
        print("\nTop 5 Female 25m results:")
        print(females_25m.head(5)[['Name', 'Tid', 'Poeng', 'Dato', 'Sted', 'PoolLength']])
        
        print("\nTop 5 Female 50m results:")
        print(females_50m.head(5)[['Name', 'Tid', 'Poeng', 'Dato', 'Sted', 'PoolLength']])
        
    else:
        print("No valid results found")

if __name__ == "__main__":
    input_file = "grdRanking (35).xlsx"
    process_swim_results(input_file) 