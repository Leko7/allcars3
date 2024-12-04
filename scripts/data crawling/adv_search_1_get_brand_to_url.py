import subprocess
import json

# Run the Scrapy command to crawl and output to a JSON file
subprocess.run(["scrapy", "crawl", "brandlinks", "-o", "data/brand_to_option.jsonl"], check=True)

# Load the JSONL file into a list of dictionaries
brand_to_option_list = []
with open("data/brand_to_option.jsonl", "r") as file:
    for line in file:
        brand_to_option_list.append(json.loads(line.strip()))

# Convert the list of dictionaries to a single dictionary
brand_to_option = {item['brand']: item['value'] for item in brand_to_option_list}

# Create the JSONL file with URLs
with open("data/brand_to_url.jsonl", "w") as f:
    for brand, option in brand_to_option.items():
        url = f"https://www.auto-data.net/en/results?brand={option}"
        json.dump({brand: url}, f)
        f.write("\n")