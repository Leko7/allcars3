# CARS Engineering -- Data Acquisition Project for the IASD Master 2

For this course project, we built a cars dataset by crawling data from <href>auto-data.net</href> 
and we applied multiple transformations in order to build a version suitable for machine learning.

For a detailed summary of the process, look at `journal.pdf`.

For some quick data exploration, look at `data_exploration.ipynb`.

The slides or the presentation can be found in `slides.pdf`.

To <b>reproduce the full data set crawling/transformation/storage</b>, run scripts in the following order. 
Please note that with the current crawling delays (3 sec for links and 1 sec for car data), the crawling would take 5 full days.

- I. Crawling (Scrapy spiders can be found at `allcars/spiders/spiders.py`):
  - links 
    - `catalog_1_get_brand_links.py`
    - `catalog_2_get_model_links.py`
    - `catalog_3_get_generation_links.py`
    - `catalog_4_get_modification_links.py`
  - cars data
    - `catalog_5_add_multiple_cars.py`
- II. Transformations & cleaning :
  - `transformations.py`
- III. Storage
  - Create the data base
    - `create_db.py`
  - Visualize the data base/check data & images
    - `visualize_data_base.py`
