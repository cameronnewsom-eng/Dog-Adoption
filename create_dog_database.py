import pandas as pd

# Create a DataFrame with dog data


available_dogs_df = pd.read_csv("dogs.csv")

# Save to SQLite database
available_dogs_df.to_sql('available_dogs', con='sqlite:///available_dogs.db', if_exists='replace', index=False)

print("Database created successfully!")
