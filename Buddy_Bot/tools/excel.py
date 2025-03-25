import pandas as pd

# Load the CSV file
file_path = 'Z:\\Projects\\elasticsearch_dsl\\data\\temp.csv'  # Replace with your CSV file path
df = pd.read_csv(file_path)

# Specify the columns to merge
# skills = []  # Initialize empty list to hold column names
# for i in range(0, 37):
#     skills.append(f'skills.names[{i}]')  # Use f-string to properly format the column names

tags = []  # Initialize empty list to hold column names
for i in range(0, 4):
    tags.append(f'tags.match[{i}]')  # Use f-string to properly format the column names

experience = []  # Initialize empty list to hold column names
for i in range(0, 6):
    experience.append(f'experience.level[{i}]')  # Use f-string to properly format the column names

# Create a new merged column with data as arrays
# df['skills'] = df[skills].apply(lambda row: row.dropna().tolist(), axis=1)
df['tags'] = df[tags].apply(lambda row: row.dropna().tolist(), axis=1)
df['experience'] = df[tags].apply(lambda row: row.dropna().tolist(), axis=1)

# Drop the original columns
# df = df.drop(columns=skills)
df = df.drop(columns=tags)
df = df.drop(columns=experience)

# Save the updated DataFrame to a new CSV file
output_file = 'final_jobs.csv'  # You can keep the .csv extension here
df.to_csv(output_file, index=False)

print(f"Merged column added and saved to {output_file}")
