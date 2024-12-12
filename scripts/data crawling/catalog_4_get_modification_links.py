import subprocess
import json

# Set the name of the JSONL file
file_path = "data/catalog_method/modification_links.jsonl"

# Run the command
subprocess.run(["scrapy", "crawl", "modiflinks", "-o", file_path])