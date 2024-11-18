import subprocess
import json

# Set the name of the JSONL file
file_path = "data/catalog_method/generation_links.jsonl"

# Run the command
subprocess.run(["scrapy", "crawl", "genlinks", "-o", file_path])