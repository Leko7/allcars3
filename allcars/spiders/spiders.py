import json
import scrapy

class CarsSpider(scrapy.Spider):
    name = "cars"
    custom_settings = {
        'DOWNLOAD_DELAY': 3,  # Wait 3 seconds between requests to avoid overloading the server
    }

    def start_requests(self):
        # Load URLs from the JSONL file
        cars_links_path = "data/car_links.jsonl"
        with open(cars_links_path, "r") as f:
            for line in f:
                data = json.loads(line)
                url = data.get("link")
                if url:
                    yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        car_data = {}
        for row in response.css("table tr"):
            header = row.css("th::text").get()
            value = row.css("td::text").get()
            
            # Check for links or additional text in the <td>
            if not value:
                value = row.css("td a::text").get()
            
            if value is None:
                # If still None, try to get entire contents in case of mixed text types
                value = row.css("td *::text").getall()
                value = " ".join(value).strip() if value else None
            
            # Add header-value pair to the dictionary if header exists
            if header:
                car_data[header.strip()] = value.strip() if value else None
        
        yield car_data

class CarLinkSpider(scrapy.Spider):
    name = "carlinks"
    # start_urls = [
    #     "https://www.auto-data.net/en/results?brand=41&model=0&power1=0&power2=0&page=1"  # Audi
    #     "https://www.auto-data.net/en/results?brand=301&model=0&power1=&power2=", # Aiways
    #      "https://www.auto-data.net/en/results?brand=200&model=0&power1=&power2=" # Abarth
    # ]

    def __init__(self, start_url=None, *args, **kwargs):
        super(CarLinkSpider, self).__init__(*args, **kwargs)
        if not start_url:
            raise ValueError("A start URL must be provided.")
        self.start_urls = [start_url]

    custom_settings = {
        'DOWNLOAD_DELAY': 3,  # Wait 3 seconds between requests to avoid overloading the server
    }

    def parse(self, response):
        # Extract all links within divs with class "down down2"
        links = response.css("div.down.down2 a::attr(href)").getall()
        for link in links:
            yield {"link": response.urljoin(link)}
        
        # Find the next page link with the ">" symbol in the text
        next_page = response.css("a.pagination").xpath("//*[text()='>']/@href").get()

        if next_page:
            yield response.follow(next_page, self.parse)

class BrandLinksSpider(scrapy.Spider):
    name = "brandlinks"
    start_urls = ["https://www.auto-data.net/en/search"]

    def parse(self, response):
        brand_options = response.css('select[name="brand"] option')
        brand_dict = {
            option.css('::text').get().lower().replace('.', '_').replace('-', '_').replace(' ', '_'): option.attrib.get('value')
            for option in brand_options if option.attrib.get('value')
        }
        for brand, value in brand_dict.items():
            yield {"brand": brand, "value": value}