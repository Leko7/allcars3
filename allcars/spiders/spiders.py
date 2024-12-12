import json
import scrapy
import os

#### 1 - Search Method

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

#### 2 - Catalog Method

class BrandLinksSpider2(scrapy.Spider):
    name = "brandlinks2"
    start_urls = ["https://www.auto-data.net/en/allbrands"]

    custom_settings = {
        'DOWNLOAD_DELAY': 3,  # Wait 3 seconds between requests to avoid overloading the server
    }

    def parse(self, response):
        brands = response.css("a.marki_blok")
        for brand in brands:
            brand_name = brand.css("strong::text").get()
            brand_link = response.urljoin(brand.attrib["href"])
            yield {"brand": brand_name, "link": brand_link}

class ModelLinksSpider(scrapy.Spider):
    name = "modelinks"

    custom_settings = {
        'DOWNLOAD_DELAY': 3,  # Wait 3 seconds between requests to avoid overloading the server
    }
    
    def start_requests(self):
        # Load the links from the JSONL file
        with open("data/catalog_method/brand_links.jsonl", "r") as f:
            for line in f:
                brand_data = json.loads(line)
                yield scrapy.Request(url=brand_data["link"], callback=self.parse)

    def parse(self, response):
        for model in response.css('a.modeli'):
            model_name = model.css('strong::text').get()
            model_link = response.urljoin(model.css('::attr(href)').get())
            yield {"model": model_name, "link": model_link}

class GenLinksSpider(scrapy.Spider):
    name = "genlinks"

    custom_settings = {
        'DOWNLOAD_DELAY': 3,  # Wait 3 seconds between requests to avoid overloading the server
    }

    def start_requests(self):
        # Load the links from the JSONL file
        with open("data/catalog_method/model_links.jsonl", "r") as f:
            for line in f:
                brand_data = json.loads(line)
                yield scrapy.Request(url=brand_data["link"], callback=self.parse)

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

class ModifLinksSpider(scrapy.Spider):
    name = "modiflinks"

    custom_settings = {
        'DOWNLOAD_DELAY': 3,  # Wait 3 seconds between requests to avoid overloading the server
    }

    def start_requests(self):
        # Load the links from the JSONL file
        with open("data/catalog_method/generation_links.jsonl", "r") as f:
            for line in f:
                brand_data = json.loads(line)
                yield scrapy.Request(url=brand_data["link"], callback=self.parse)

    def parse(self, response):
        for modif in response.xpath('//a[contains(@title, "Technical Specs")]'):
            modif_name = modif.xpath('./strong/span[@class="tit"]/text()').get()
            modif_link = response.urljoin(modif.xpath('./@href').get())
            yield {
                "modif": modif_name,
                "link": modif_link
            }

class CarsSpider2(scrapy.Spider):
    name = "cars2"
    custom_settings = {
        'DOWNLOAD_DELAY': 1,  # Wait 1 seconds between requests to avoid overloading the server
    }

    def start_requests(self):
        # Load URLs from the JSONL file
        cars_links_path = "data/catalog_method/modification_links.jsonl"
        with open(cars_links_path, "r", encoding='utf-8') as f:
            for line in f:
                data = json.loads(line)
                url = data.get("link")
                modif = data.get("modif")
                if url and modif:
                    yield scrapy.Request(url=url, callback=self.parse, cb_kwargs={'modif': modif})

    def parse(self, response, modif):
        car_data = {'Modification': modif}
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

        # Extract the car model name from the URL
        subdir_name = car_data['Brand'] + '/' + car_data['Model'] + '/' + car_data['Generation']
        images_path = 'data/catalog_method/images/' + subdir_name

        # Check if the folder images_path doesn't exist already
        if not os.path.exists(images_path):

            big_images = response.xpath('//*[contains(text(), \"bigs\")]').get()
            prov = big_images.split(';')
            prov = [it for it in prov if 'bigs' in it]
            prov = prov[1:] # in the first element there is the inizialization

            lst = []
            for s in prov:
                t = s.split('"')
                lst.append('/images/' + t[1])

            if lst:
                # list of cars images
                car_images = lst

                car_data['images_path'] = images_path

                for num,img_url in enumerate(car_images):

                    full_url = response.urljoin(img_url)
                    
                    yield scrapy.Request(
                            url=full_url,
                            callback=self.save_image,
                            cb_kwargs={'dir_name': subdir_name + '/'  + str(num)}  # Pass directory path
                        )
            else:
                car_data['image_path'] = None
        
        yield car_data

    def save_image(self, response, dir_name):
        # Extract image name from URL
        file_name = response.url.split('/')[-2:]
        ext = file_name[-1].split('.')[1]
        # Save the file to a temporary folder
        save_path = f'data/catalog_method/images/{dir_name}' + '.' + ext

        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, 'wb') as f:
            f.write(response.body)