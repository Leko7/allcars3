import subprocess
import json

# Set the name of the JSONL file
file_path = "data/catalog_method/model_links.jsonl"

# Run the command
subprocess.run(["scrapy", "crawl", "modelinks", "-o", file_path])