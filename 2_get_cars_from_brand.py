import subprocess
import argparse
import json

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Crawl all cars from the corresponding brands.")
    parser.add_argument(
        "--brands", 
        required=True, 
        nargs='+', 
        help="The names of the brands in lower case, separated by spaces."
    )
    args = parser.parse_args()

    # Load the dict that converts a brand name to the corresponding URL
    with open("data/brand_to_url.jsonl", 'r') as file:
        brand_to_url = {list(json.loads(line).keys())[0]: list(json.loads(line).values())[0] for line in file}

    for brand_name in args.brands:
        # Get the URL from the name of the brand
        if brand_name not in brand_to_url:
            print(f"Brand '{brand_name}' not found in the mapping.")
            continue
        
        brand_link = brand_to_url[brand_name]

        # Define the Scrapy command as a list for car links
        command_links = [
            "scrapy",
            "crawl",
            "carlinks",
            "-a",
            f"start_url={brand_link}",
            "-O",
            "data/car_links.jsonl"
        ]

        # Run the command to get all links of cars from the brand
        subprocess.run(command_links)

        # Define the Scrapy command for cars with append mode
        command_cars = [
            "scrapy",
            "crawl",
            "cars",
            "-o",
            f"data/cars.jsonl"
        ]

        # Run the command to get all cars from the brand
        subprocess.run(command_cars)