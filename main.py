import pandas as pd
from bs4 import BeautifulSoup
import requests
from requests import Session
import ast
import re
import time
import json

class Amazon:
    def __init__(self):
        self.sess= Session()
        self.headers= {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
			"accept-encoding": "gzip, deflate, br",
			"accept-language": "en",
			"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36"
        }
        self.sess.headers= self.headers

    def get(self, url):
        response= self.sess.get(url)
        output= {}
        # assert response.status_code ==200, f"URl not found: {url}"
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "lxml")
            # print(soup)
            product_title = self.get_product_title(soup)
            image_url = self.get_image_url(soup)
            price= self.get_price(soup)
            details = self.get_product_det(soup)
            output['Product title'] = product_title
            output['Image Url'] = image_url
            output['Price'] = price
            output['Product Details']= details
            print(output)
            # output_list.append(output)
            print("--------------------------------------------------------------------------------------------------")
        else:
            output[url]= "Not Found"
            print(output)
        return output

    def get_product_title(self,soup):
        title = soup.find("span", attrs={"id": "productTitle"})
        return title.string.strip()

    def get_price(self,soup):
        try:
            price = soup.find("span", attrs={"id": "price"})
            price_alternate = soup.find("span", attrs={"class": "a-offscreen"})
            if price is None:
                prod_price = price_alternate.string
            else:
                prod_price = price.string
        except:
            prod_price = 0
        return prod_price.string.strip()

    def get_product_det(self,soup):
        try:
            ### do this if product description is present
            prod_details_dict = {}
            prod_description_div = soup.find("div", attrs={"id": "productDescription"})
            if prod_description_div is not None:
                tagged_prod_desc = prod_description_div.findChild()
                clean = re.compile('<.*?>')
                prod_desc = re.sub(clean, '', str(tagged_prod_desc))
                # print(prod_desc)

            ### do this if product details is present
            tags_below_div = soup.find("div", attrs={"id": "detailBullets_feature_div"})
            if tags_below_div is not None:
                detail_tag_list = tags_below_div.find("ul", attrs={
                    "class": "a-unordered-list a-nostyle a-vertical a-spacing-none detail-bullet-list"})
                prod_details_list = []

                for next_tag in detail_tag_list.findChildren():
                    if next_tag.name == "span" and next_tag.string:
                        # print(str(next_tag.string).split("\n")[0])
                        prod_details_list.append(str(next_tag.string).split("\n")[0])
                        # print("+++++++++++++++++++++++++++++++++")

                prod_details_dict = {prod_details_list[i]: prod_details_list[i + 1] for i in
                                     range(0, len(prod_details_list), 2)}

            if tags_below_div is None:

                prod_details_dict["Product Description"] = prod_desc
                # print(prod_details_dict)
            else:
                prod_details_dict = prod_details_dict

        except AttributeError as e:
            prod_details_dict = {}
            print(e)
        # print(prod_details_dict)
        return prod_details_dict

    def get_image_url(self,soup):
        try:
            image_horizontal = soup.find("img", attrs={"class": "a-dynamic-image image-stretch-horizontal frontImage"})
            image_vertical = soup.find("img", attrs={"class": "a-dynamic-image image-stretch-vertical frontImage"})
            if image_horizontal is None:
                img_url_json = ast.literal_eval(image_vertical.get('data-a-dynamic-image'))
            else:
                img_url_json = ast.literal_eval(image_horizontal.get('data-a-dynamic-image'))
            image_url = list(img_url_json.keys())[0]
        except:
            image_url = ""

        return image_url

    def crawl(self):
        counter= 0
        output_list=[]
        start = time.time()
        df_url = pd.read_csv('urls.csv', usecols=['Asin', 'country'])
        total_time_seconds=0
        for ind, row in df_url.iterrows():
            counter= counter + 1
            # print(f"https://www.amazon.{row['country']}/dp/{row['Asin']}")
            output_list.append(self.get(f"https://www.amazon.{row['country']}/dp/{row['Asin']}"))
            if counter == 100:  #for every 100 rows
                end = time.time()
                time_for_100_rows= end-start
                total_time_seconds = time_for_100_rows + total_time_seconds
                start = time.time()
                counter= 0
        print(total_time_seconds,": time taken in seconds")
        print(output_list)
        with open("output.json", "w") as final:
            json.dump(output_list, final)

scraper = Amazon()
scraper.crawl()







def test():
    HEADERS = ({'User-Agent':
                    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36',
                'Accept-Language': 'en-US, en;q=0.5'})
    url= "https://www.amazon.de/dp/000102163X"
    response= requests.get(url, headers= HEADERS)
    soup= BeautifulSoup(response.content, "lxml")
    # print(soup)
    checkProductPage= product_exists(soup)
    if checkProductPage:
        # product_title= get_product_title(soup)
        # print(product_title)
        # image_url= get_image_url(soup)
        # print(image_url)
        # price= get_product_det(soup)
        print(soup)

def product_exists(soup):
    response_status= soup.find("a")
    response_text= response_status.get("href")
    if '404' in response_text:
        return False
    else:
        return True



# if __name__ == '__main__':
#     # crawl()
#     test()
