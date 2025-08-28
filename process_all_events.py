import pandas as pd
import re
import os
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
        'sondre', 'andreas', 'ivan', 'tamer', 'bjarne', 'brage', 'ådne', 'sindre', 'vetle', 'terje'
    }
    
    # Common Norwegian female names
    female_names = {
        'sara', 'maria', 'silje', 'carina', 'eirill', 'henriette', 'elise', 'vilde', 
        'tove', 'amanda', 'silje', 'carina', 'sara', 'maria', 'kirsti',
        'guro', 'linn-mari', 'paulien', 'frøydis', 'mari', 'sissel', 'gudrun', 
        'torborg', 'solveig', 'elisabeth', 'malin', 'siv', 'sigrid', 'annelin', 
        'heidi', 'linn', 'maud', 'miriam', 'ingrid'
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

def format_name_for_display(name):
    """
    Format name as "Firstname Lastname" from various input formats.
    """
    # Remove "Navn: " prefix if present
    clean_name = name.replace("Navn: ", "").strip()
    
    # Standardize specific name variations
    clean_name = standardize_name_variations(clean_name)
    
    # Handle "Last, First" format
    if ',' in clean_name:
        parts = clean_name.split(',')
        if len(parts) >= 2:
            last_name = parts[0].strip()
            first_name = parts[1].strip()
            return f"{first_name} {last_name}"
    
    # Handle "First Last" format (already correct)
    return clean_name



def read_exceptions_file():
    """
    Read the Exceptions file and return a dictionary mapping event names to DataFrames.
    """
    exceptions_file = os.path.join("Rawdata", "Exceptions.xlsx")
    
    if not os.path.exists(exceptions_file):
        print("Exceptions file not found, skipping...")
        return {}
    
    try:
        # Read the exceptions file
        exceptions_df = pd.read_excel(exceptions_file)
        print(f"Found {len(exceptions_df)} exception entries")
        
        # Group by event name
        exceptions_by_event = {}
        for event_name, group in exceptions_df.groupby('Event'):
            if pd.notna(event_name):
                print(f"Exception event: {event_name} - {len(group)} entries")
                exceptions_by_event[event_name] = group.copy()
        
        return exceptions_by_event
        
    except Exception as e:
        print(f"Error reading exceptions file: {e}")
        return {}

def process_single_file(input_file):
    """
    Process a single swim results Excel file and return the processed data.
    """
    print(f"\nProcessing file: {input_file}")
    
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
        print(f"Could not find event name in {input_file}")
        return None, None
    
    print(f"Event name found: {event_name}")
    
    # Rename "Individuell Medley" to "Medley" (case insensitive)
    if "individuell medley" in event_name.lower():
        # Handle all possible case variations
        event_name = event_name.replace("Individuell Medley", "Medley")
        event_name = event_name.replace("Individuell medley", "Medley")
        event_name = event_name.replace("individuell medley", "Medley")
        print(f"Event name updated to: {event_name}")
    
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
    
    # Keep all results for each swimmer (we'll handle pool-specific best results later)
    all_results = []
    for swimmer, results in swimmers_data:
        if results:
            all_results.extend(results)
    
    # Create DataFrame
    if all_results:
        result_df = pd.DataFrame(all_results)
        
        # Add gender column
        result_df['Gender'] = result_df['Name'].apply(identify_gender)
        
        # Debug: Count pool lengths
        pool_counts = result_df['Pool'].value_counts()
        print(f"Pool length distribution: {dict(pool_counts)}")
        
        # Add cleaned name column for comparison
        result_df['CleanName'] = result_df['Name'].apply(clean_swimmer_name)
        
        # Check for duplicate names and merge them
        print(f"Total swimmers before duplicate check: {len(result_df)}")
        
        # Group by cleaned name and pool type, keep the best result for each unique swimmer per pool
        merged_results = []
        seen_combinations = set()
        
        for _, group in result_df.groupby(['CleanName', 'Pool']):
            if len(group) > 1:
                print(f"Found duplicate swimmer: {group.iloc[0]['CleanName']} in {group.iloc[0]['Pool']} pool ({len(group)} entries)")
                # Keep the one with highest points for this pool type
                best_entry = group.loc[group['Poeng'].idxmax()]
                merged_results.append(best_entry)
                seen_combinations.add((best_entry['CleanName'], best_entry['Pool']))
            else:
                merged_results.append(group.iloc[0])
                seen_combinations.add((group.iloc[0]['CleanName'], group.iloc[0]['Pool']))
        
        # Create new DataFrame with merged results
        result_df = pd.DataFrame(merged_results)
        result_df = result_df.drop('CleanName', axis=1)  # Remove the temporary column
        
        print(f"Total swimmers after duplicate check: {len(result_df)}")
        
        # Clean the names by removing "Navn: " prefix and format for display
        result_df['Name'] = result_df['Name'].apply(format_name_for_display)
        
        # Sort by Poeng in descending order (highest on top)
        result_df = result_df.sort_values('Poeng', ascending=False)
        
        return event_name, result_df
    else:
        print("No valid results found")
        return None, None

def process_all_files():
    """
    Process all grdRanking files in the Rawdata folder and create separate files for each event.
    """
    rawdata_folder = "Rawdata"
    endresult_folder = "EndResult"
    
    # Read exceptions file first
    exceptions_by_event = read_exceptions_file()
    
    # Get all files starting with "grdRanking" in the Rawdata folder
    grd_files = []
    for file in os.listdir(rawdata_folder):
        if file.startswith("grdRanking") and file.endswith(".xlsx"):
            grd_files.append(os.path.join(rawdata_folder, file))
    
    print(f"Found {len(grd_files)} grdRanking files to process:")
    for file in grd_files:
        print(f"  - {file}")
    
    # Process each file
    all_events = {}
    
    for file_path in grd_files:
        event_name, result_df = process_single_file(file_path)
        
        if event_name and result_df is not None:
            # If we already have this event, combine the data
            if event_name in all_events:
                print(f"Combining data for existing event: {event_name}")
                all_events[event_name] = pd.concat([all_events[event_name], result_df], ignore_index=True)
                # Remove duplicates again after combining, keeping best per pool type
                all_events[event_name] = all_events[event_name].drop_duplicates(subset=['Name', 'Pool'], keep='first')
            else:
                all_events[event_name] = result_df
    
    # Add exceptions data to the events
    for event_name, exceptions_df in exceptions_by_event.items():
        # Rename "Individuell Medley" to "Medley" in exceptions as well
        if "Individuell Medley" in event_name:
            event_name = event_name.replace("Individuell Medley", "Medley")
            print(f"Event name updated to: {event_name}")
        
        print(f"\nAdding exceptions for event: {event_name}")
        
        # Remove the Event column from exceptions data since it's redundant
        exceptions_df_clean = exceptions_df.drop('Event', axis=1)
        
        # Format names in exceptions data
        exceptions_df_clean['Name'] = exceptions_df_clean['Name'].apply(format_name_for_display)
        
        if event_name in all_events:
            print(f"Combining exceptions with existing data for {event_name}")
            # Add exceptions to existing event data
            all_events[event_name] = pd.concat([all_events[event_name], exceptions_df_clean], ignore_index=True)
            # Remove duplicates and keep best result for each swimmer per pool type
            all_events[event_name] = all_events[event_name].drop_duplicates(subset=['Name', 'Pool'], keep='first')
            # Re-sort by points
            all_events[event_name] = all_events[event_name].sort_values('Poeng', ascending=False)
        else:
            print(f"Creating new event from exceptions: {event_name}")
            # Create new event from exceptions only
            all_events[event_name] = exceptions_df_clean.sort_values('Poeng', ascending=False)
    
    # Create separate files for each event
    print(f"\nCreating separate files for {len(all_events)} events:")
    
    for event_name, result_df in all_events.items():
        # Create separate DataFrames for each category (top 10 for display, all data for statistics)
        males_25m_all = result_df[(result_df['Gender'] == 'Male') & (result_df['Pool'] == '25m')]
        males_50m_all = result_df[(result_df['Gender'] == 'Male') & (result_df['Pool'] == '50m')]
        females_25m_all = result_df[(result_df['Gender'] == 'Female') & (result_df['Pool'] == '25m')]
        females_50m_all = result_df[(result_df['Gender'] == 'Female') & (result_df['Pool'] == '50m')]
        
        # Top 10 for website display
        males_25m = males_25m_all.head(10)
        males_50m = males_50m_all.head(10)
        females_25m = females_25m_all.head(10)
        females_50m = females_50m_all.head(10)
        
        # Clean the event name for filename
        clean_event_name = re.sub(r'[<>:"/\\|?*]', '_', event_name)
        clean_event_name = clean_event_name.strip()
        
        # Create output filename for display (top 10)
        output_filename = os.path.join(endresult_folder, f"{clean_event_name}.xlsx")
        
        # Save to Excel with four sheets (top 10 for display)
        with pd.ExcelWriter(output_filename, engine='openpyxl') as writer:
            males_25m.to_excel(writer, sheet_name='Male_25m', index=False)
            males_50m.to_excel(writer, sheet_name='Male_50m', index=False)
            females_25m.to_excel(writer, sheet_name='Female_25m', index=False)
            females_50m.to_excel(writer, sheet_name='Female_50m', index=False)
        
        print(f"Created display file: {output_filename}")
        print(f"  - Male 25m swimmers: {len(males_25m)}")
        print(f"  - Male 50m swimmers: {len(males_50m)}")
        print(f"  - Female 25m swimmers: {len(females_25m)}")
        print(f"  - Female 50m swimmers: {len(females_50m)}")
        
        # Create statistics folder if it doesn't exist
        statistics_folder = "Statistics"
        if not os.path.exists(statistics_folder):
            os.makedirs(statistics_folder)
        
        # Create output filename for statistics (all data)
        statistics_filename = os.path.join(statistics_folder, f"{clean_event_name}_statistics.xlsx")
        
        # Save to Excel with four sheets (all data for statistics)
        with pd.ExcelWriter(statistics_filename, engine='openpyxl') as writer:
            males_25m_all.to_excel(writer, sheet_name='Male_25m', index=False)
            males_50m_all.to_excel(writer, sheet_name='Male_50m', index=False)
            females_25m_all.to_excel(writer, sheet_name='Female_25m', index=False)
            females_50m_all.to_excel(writer, sheet_name='Female_50m', index=False)
        
        print(f"Created statistics file: {statistics_filename}")
        print(f"  - Male 25m swimmers: {len(males_25m_all)}")
        print(f"  - Male 50m swimmers: {len(males_50m_all)}")
        print(f"  - Female 25m swimmers: {len(females_25m_all)}")
        print(f"  - Female 50m swimmers: {len(females_50m_all)}")
    
    print(f"\nProcessing complete! Created {len(all_events)} files in the EndResult folder.")

if __name__ == "__main__":
    process_all_files() 