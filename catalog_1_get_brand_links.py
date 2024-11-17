import subprocess
import json

# Set the name of the JSONL file
file_path = "data/catalog_method/brand_links.jsonl"

# Run the command
subprocess.run(["scrapy", "crawl", "brandlinks2", "-O", file_path])

with open(file_path, 'r') as file:
    lines = file.readlines()

with open(file_path, 'w') as file:
    for line in lines:
        entry = json.loads(line)
        entry["crawled"] = False
        file.write(json.dumps(entry) + '\n')