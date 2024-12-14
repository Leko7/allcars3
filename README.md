# CARS Engineering -- Data Acquisition Project for the IASD Master 2

For a detailed summary of the process, look at `journal.pdf`.

For some quick data exploration, look at `data_exploration.ipynb`.

The slides or the presentation can be found in `slides.pdf`.

To <mark>reproduce the full data set crawling/transformation/storage<mark>, run scripts in the following order :

- I. Crawling :
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
