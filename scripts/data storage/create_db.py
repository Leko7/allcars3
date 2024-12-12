import sqlite3
import pandas as pd
import os

# Load CSV data
csv_path = "data/catalog_method/cars_filtered_ml.csv"
df = pd.read_csv(csv_path)

# Create SQLite database
db_path = "data/catalog_method/catalog.db"
conn = sqlite3.connect(db_path)

# Create first table with CSV data
df.to_sql("cars_data", conn, if_exists="replace", index=False)

# Prepare data for the second table
unique_gens = df["unique_gen"].unique()
image_data = []

images_folder = "data/catalog_method/images"
for unique_gen in unique_gens:
    gen_folder = os.path.join(images_folder, unique_gen)
    if os.path.exists(gen_folder):
        images = os.listdir(gen_folder)
        for img_name in images:
            image_path = os.path.join(gen_folder, img_name)
            with open(image_path, 'rb') as f:
                image_bytes = f.read()  # Read image as binary data
            image_data.append({"unique_gen": unique_gen, "image": image_bytes})

image_df = pd.DataFrame(image_data)

# Create second table with actual images
image_df.to_sql("unique_gen_images", conn, if_exists="replace", index=False, 
                dtype={"image": "BLOB"})  # Store images as BLOB

# Close connection
conn.close()
