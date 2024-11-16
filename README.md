# Data Acquisition Project for the IASD Master 2

### To crawl the cars from a brand (example : ac)
```bash
python get_cars_from_brand.py --brand ac
```
The name of the brand has to be written in lower case, with space as separator between brands. If the brand name is composed of multiple words, use '_' as separator.

The output will be under data/cars.jsonl

You can find the available brands in data/brand_to_url.jsonl
