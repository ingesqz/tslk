import pandas as pd

# Read the newly created file
df = pd.read_excel("100m Butterfly.xlsx")

print("File contents summary:")
print(f"Total rows: {len(df)}")
print(f"Columns: {list(df.columns)}")
print("\nTop 10 results:")
print(df.head(10))

print(f"\nHighest points: {df['Poeng'].max()}")
print(f"Lowest points: {df['Poeng'].min()}")
print(f"Average points: {df['Poeng'].mean():.2f}")

# Check for any duplicate swimmers
duplicates = df['Name'].duplicated()
if duplicates.any():
    print(f"\nWarning: Found {duplicates.sum()} duplicate swimmer names")
else:
    print("\nNo duplicate swimmers found - each swimmer has only their best result")

# Show the ranking range
print(f"\nRanking range: 1st place ({df.iloc[0]['Poeng']} points) to 30th place ({df.iloc[-1]['Poeng']} points)") 