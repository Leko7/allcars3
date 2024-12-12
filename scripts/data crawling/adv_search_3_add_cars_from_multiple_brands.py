import subprocess
import argparse
import json

if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Crawl a chosen number of brands.")
    parser.add_argument(
        "--n",
        required=True,
        type=int,
        help="The number of brands to crawl."
    )
    args = parser.parse_args()

    # Load the dictionary from the JSONL file
    with open("data/crawled_brands.jsonl", "r") as file:
        crawled_brands = {}
        for line in file:
            crawled_brands.update(json.loads(line))

    # Create a list of uncrawled brands
    uncrawled_brands = [brand for brand, crawled in crawled_brands.items() if not crawled]

    # Crawl the specified number of brands
    for i in range(min(args.n, len(uncrawled_brands))):
        brand = uncrawled_brands[i]

        # Define the command to crawl a specific brand
        command_links = [
            "python",
            "adv_search_2_get_cars_from_brand.py",
            f"--brands={brand}"
        ]

        # Execute the command
        subprocess.run(command_links)

        # Update the crawled_brands dictionary
        crawled_brands[brand] = True

        # Write the updated dictionary back to the file
        with open("data/crawled_brands.jsonl", "w") as file:
            for key, value in crawled_brands.items():
                json.dump({key: value}, file)
                file.write("\n")