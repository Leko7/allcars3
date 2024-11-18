import subprocess
import json

# Set the name of the JSONL file
file_path = "data/catalog_method/brand_links.jsonl"

# Run the command
subprocess.run(["scrapy", "crawl", "brandlinks2", "-o", file_path])