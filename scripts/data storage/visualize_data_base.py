import sqlite3
from PIL import Image
import io
import pickle

# Connect to the existing database
connection = sqlite3.connect('data/catalog_method/catalog.db')

# Create a cursor object
cursor = connection.cursor()

# Function to get table schema
def get_table_schema(table_name):
    cursor.execute(f"PRAGMA table_info({table_name});")
    return cursor.fetchall()

# List of tables you want to display
tables = ["cars_data", "unique_gen_images"]

# Loop through tables and display structure
for table in tables:
    print(f"Table: {table}")
    schema = get_table_schema(table)
    print("+----------------------+----------------+-----------+")
    print("| Column Name          | Data Type      | Nullable  |")
    print("+----------------------+----------------+-----------+")
    for column in schema:
        name, data_type, notnull = column[1], column[2], "NO" if column[3] else "YES"
        print(f"| {name:<20} | {data_type:<14} | {notnull:<9} |")
    print("+----------------------+----------------+-----------+")
    print()

# Retrieve one image (BLOB data) from the "unique_gen_images" table
cursor.execute("SELECT image FROM unique_gen_images LIMIT 1")
image_data = cursor.fetchone()

# Save and display the image if it exists
if image_data and image_data[0]:
    try:
        # Treat the blob as raw image bytes
        image_bytes = image_data[0]
        image = Image.open(io.BytesIO(image_bytes))

        # Convert to JPG format if needed
        image = image.convert("RGB")
        
        # Save the image locally as a JPG file
        image.save("retrieved_image.jpg", format="JPEG")
        print("Image saved as 'retrieved_image.jpg'")
        
        # Display the image
        image.show()
    except Exception as e:
        print(f"Error reading image: {e}")
else:
    print("No image found or the image column is NULL.")

# Close the connection
connection.close()