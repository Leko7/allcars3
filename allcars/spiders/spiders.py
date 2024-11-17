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

class BrandLinksSpider2(scrapy.Spider):
    name = "brandlinks2"
    start_urls = ["https://www.auto-data.net/en/allbrands"]

    def parse(self, response):
        brands = response.css("a.marki_blok")
        for brand in brands:
            brand_name = brand.css("strong::text").get()
            brand_link = response.urljoin(brand.attrib["href"])
            yield {"brand": brand_name, "link": brand_link}

class FamilyLinksSpider(scrapy.Spider):
    name = "familinks"
    
    def start_requests(self):
        # Load the links from the JSONL file
        with open("data/catalog_method/brand_links.jsonl", "r") as f:
            for line in f:
                brand_data = json.loads(line)
                yield scrapy.Request(url=brand_data["link"], callback=self.parse)

    def parse(self, response):
        for family in response.css('a.modeli'):
            family_name = family.css('strong::text').get()
            family_link = response.urljoin(family.css('::attr(href)').get())
            yield {"family": family_name, "link": family_link}

# class FamilyLinksSpider(scrapy.Spider):
#     name = "familinks"
#     start_urls = ["https://www.auto-data.net/en/abarth-brand-200"]

#     def parse(self, response):
#         for family in response.css('a.modeli'):
#             family_name = family.css('strong::text').get()
#             family_link = response.urljoin(family.css('::attr(href)').get())
#             yield {"family": family_name, "link": family_link}

class GenLinksSpider(scrapy.Spider):
    name = "genlinks"
    start_urls = ["https://www.auto-data.net/en/abarth-124-spider-model-2152"]

    def parse(self, response):
        for generation in response.css('a.position'):
            gen_name = generation.css('strong.tit::text').get()
            gen_link = response.urljoin(generation.css('::attr(href)').get())
            
            # Ensure that gen_name and gen_link are valid and unique
            if gen_name and gen_link:
                yield {
                    "generation": gen_name.strip(),
                    "link": gen_link
                }

class ModelLinksSpider(scrapy.Spider):
    name = "modelinks"
    start_urls = ["https://www.auto-data.net/en/abarth-124-gt-generation-6774"]

    def parse(self, response):
        for model in response.xpath('//a[contains(@title, "Technical Specs")]'):
            model_name = model.xpath('./strong/span[@class="tit"]/text()').get()
            model_link = response.urljoin(model.xpath('./@href').get())
            yield {
                "model": model_name,
                "link": model_link
            }