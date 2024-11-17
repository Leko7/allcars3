import json
import scrapy
import os

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

class CarsSpiderImage(scrapy.Spider):
    name = "cars_image"
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

        # Extract the Brand name
        car_data['Brand'] = response.xpath('//tr[th[contains(text(), "Brand")]]/td/a/text()').get()

        # Extract the Model name
        car_data['Model'] = response.xpath('//tr[th[contains(text(), "Model")]]/td/a/text()').get()
        
        # Extract the generation name
        car_data['Generation'] = response.xpath('//tr[th[contains(text(), "Generation")]]/td/a/text()').get()

        # list of all images in the page
        lst = response.css('img::attr(src)').getall()

        if lst:
            # list of cars images
            car_images = [x.replace('_thumb', '') for x in lst if 'images' in x]
            car_images = [x.replace('small', 'big') for x in car_images if 'images' in x]

            # Extract the car model name from the URL
            subdir_name = car_data['Brand'] + '_' + car_data['Model'] + '_' + car_data['Generation']

            car_data['image_path'] = 'temp_images/' + subdir_name

            for num,img_url in enumerate(car_images):

                full_url = response.urljoin(img_url)
                
                yield scrapy.Request(
                        url=full_url,
                        callback=self.save_image,
                        cb_kwargs={'dir_name': subdir_name + '/' + str(num)}  # Pass directory path
                    )
        else:
            car_data['image_path'] = None
        
        
        yield car_data
    
    def save_image(self, response, dir_name):
        # Extract image name from URL
        file_name = response.url.split('/')[-2:]
        ext = file_name[-1].split('.')[1]
        # Save the file to a temporary folder
        save_path = f'temp_images/{dir_name}' + '.' + ext
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, 'wb') as f:
            f.write(response.body)

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