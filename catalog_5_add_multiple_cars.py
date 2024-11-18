import subprocess
import json

# Set the name of the JSONL file
file_path = "data/catalog_method/cars.jsonl"

# Run the command
subprocess.run(["scrapy", "crawl", "cars2", "-o", file_path])