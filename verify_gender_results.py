import pandas as pd

# Read both sheets from the Excel file
males_df = pd.read_excel("100m Butterfly.xlsx", sheet_name='Male')
females_df = pd.read_excel("100m Butterfly.xlsx", sheet_name='Female')

print("=== MALE SWIMMERS (Top 10) ===")
print(f"Total male swimmers: {len(males_df)}")
print("\nTop 10 Male results:")
print(males_df[['Name', 'Tid', 'Poeng', 'Dato', 'Sted']])

print(f"\nMale statistics:")
print(f"Highest points: {males_df['Poeng'].max()}")
print(f"Lowest points: {males_df['Poeng'].min()}")
print(f"Average points: {males_df['Poeng'].mean():.2f}")

print("\n" + "="*50)

print("\n=== FEMALE SWIMMERS (Top 10) ===")
print(f"Total female swimmers: {len(females_df)}")
print("\nTop 10 Female results:")
print(females_df[['Name', 'Tid', 'Poeng', 'Dato', 'Sted']])

print(f"\nFemale statistics:")
print(f"Highest points: {females_df['Poeng'].max()}")
print(f"Lowest points: {females_df['Poeng'].min()}")
print(f"Average points: {females_df['Poeng'].mean():.2f}")

print("\n" + "="*50)

print(f"\n=== COMPARISON ===")
print(f"Best male: {males_df.iloc[0]['Name']} - {males_df.iloc[0]['Poeng']} points")
print(f"Best female: {females_df.iloc[0]['Name']} - {females_df.iloc[0]['Poeng']} points")
print(f"Male average: {males_df['Poeng'].mean():.2f} points")
print(f"Female average: {females_df['Poeng'].mean():.2f} points") 