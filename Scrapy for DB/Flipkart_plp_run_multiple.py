import scrapy as sp
import pandas as pd
import numpy as np
from scrapy.crawler import CrawlerProcess
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from datetime import date
import time
import random
import smtplib
import ssl
from email.message import EmailMessage
from xlsxwriter import workbook
import re
import requests
# from urllib.parse import urlparse, parse_qs
import os
import glob
import shutil
from pathlib import Path
# from google.cloud import storage
import datetime

from random_text import generate_descrb


########################################## To get the filename as Global ###########################################
glob_file=''

class FlipkartpdpSpider(sp.Spider):

    name = 'flipkartplp'
    main_url = "https://www.flipkart.com/search?q="
    input_folder='D:/Dhiomics/Scrapy for DB/input'
    all_urls = []
    filename = ""

    main_xpaths_df = pd.read_excel(r"xpath_flipkart_plp.xlsx")
    xpaths_df = dict(zip(main_xpaths_df['KPI'], main_xpaths_df['xpaths']))
    main_div_xpath = '('+xpaths_df['MAIN_DIV']+')'
    del xpaths_df['MAIN_DIV']
    output_data = []


    def start_requests(self):
        try:
            if (len(self.output_data) > 0):
                self.output_data = []
        except:
            pass
        for filename in os.listdir(self.input_folder):
            if filename.endswith(".xlsx"):
                input_path = os.path.join(self.input_folder, filename)  
                df = pd.read_excel(input_path,sheet_name="Sheet1")
                listings = list(df["Product_list"])
                all_urls = []  
                for categorys in listings:
                     all_urls.append(self.main_url+str(categorys)+'&page=')
                for url in all_urls:
                    for pages in range(1, 6):
                        yield sp.Request(url+str(pages), callback=self.parse,meta={'KeyName': url.split(self.main_url)[1].split("&")[0], 'filename': filename})
                        self.filename = filename

    def parse(self, response):
        global glob_file
        glob_file=response.meta['filename']
        print("FFFFFFFFFFFFFFFFFFF",glob_file)
        # page_num = re.search(r'\bpage=(\d+)\b', response.url).group(1)
        len_main_div = len(response.xpath(self.main_div_xpath).getall())
        data_lis = []
        response_url=[]

        Product_descrb = generate_descrb()

        for i in range(1, len_main_div+1):
            temp_dict = {}
            for key in self.xpaths_df:
                temp_dict.update({"category":response.meta['KeyName']})
                temp_dict.update({"productdescrb":Product_descrb})
                temp_dict.update({"productprice":random.randint(500, 900)})
                

                try:
                    product_xpath = self.main_div_xpath + str([i]) + self.xpaths_df[key]
                    # if (key == 'productprice'):
                    #     val = response.xpath(product_xpath+'/text()').getall()
                    #     productprice = ''
                    #     for v in val:
                    #         productprice += v
                    #     temp_dict.update({key: productprice if productprice != '' else ''})

                    if (key == 'imgurl'):
                        val = response.xpath(product_xpath).get()
                        temp_dict.update(
                            {key: val if val != None and val != '' else ''})

                    elif (key == 'productname'):
                        product_xpath = '('+self.main_div_xpath + str([i])+')'+self.xpaths_df[key]
                        val = response.xpath(product_xpath+'/text()').get()
                        if (val == 'None' or val == '' or val == None):
                            product_xpath = '('+self.main_div_xpath + str([i])+')'+'//*[@class="IRpwTa _2-ICcC"]'
                            val = response.xpath(product_xpath+'/text()').get()
                        temp_dict.update({key: val})

                    # elif (key == 'Platform Sponsored'):
                    #     val = response.xpath(product_xpath).get()
                    #     temp_dict.update(
                    #         {key: 'f_assured' if val != None and val != '' else ''})

                    # elif (key == 'Product URL'):
                    #     Base_URL = 'https://www.flipkart.com'
                    #     val = response.xpath(product_xpath).get()
                    #     temp_dict.update(
                    #         {key: Base_URL+val if val != None and val != '' else ''})
                        
                    # elif(key=='Product Id'):
                    #     val=response.xpath(product_xpath).get()
                    #     val=val.split("pid=")[1].split("&lid")[0]
                    #     temp_dict.update({key:val if val!=None and val != '' else ''})

                    else:
                        val = response.xpath(product_xpath + '/text()').get()
                        temp_dict.update(
                            {key: val if val != None and val != '' else ''})
                except:
                    temp_dict.update({key: "***"})
            data_lis.append(temp_dict)
        self.output_data += data_lis
        
        return data_lis


process = CrawlerProcess(settings={'LOG_LEVEL': 'DEBUG',
                                   'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
                                   'FEEDS': {"Flipkart_OutputData.csv": {'format': 'csv', 'overwrite': True}}
                                   })
process.crawl(FlipkartpdpSpider)
process.start()

print(f'The value of my_key is {glob_file}')

df = pd.read_csv('Flipkart_OutputData.csv')
writer = pd.ExcelWriter('FlipkartPLP_OutputData.xlsx',options={'strings_to_urls': False})
df.to_excel(writer,index=False)
writer.close()
# df.to_excel("D:/Scraping/FlipkartPLP_OutputData.xlsx", index=False)


########################### Filtering a data and removing of unneccesary rows(Post Processing) ####################################
output_df = pd.read_excel("FlipkartPLP_OutputData.xlsx")
# output_df['Price'] = output_df['Price'].str.replace("₹", '')
output_df['productprice'] = output_df['productprice'].str.replace("₹", '')
# output_df['Discount'] = output_df['Discount'].str.replace(
#     '%', '').str.replace('off', '')
# output_df['Deal Text'] = output_df['Deal Text'].str.replace('\d+', '').str.replace('₹,','').str.replace('₹','')


output_df.sort_values(by='category', inplace=True)
output_df['Rank'] = 1
prev_category = None

# logic to add rank for specific category
for index, row in output_df.iterrows():
    if row['category'] != prev_category:
        count = 1
    else:
        count += 1
    # output_df.at[index, 'Rank'] = count
    prev_category = row['category']

# output_df = output_df.to_excel(
#     "FlipkartPLP_Filtered_Batch_400-600.xlsx", index=False)
writer = pd.ExcelWriter(f'FlipkartPLP_Filtered_{glob_file}',options={'strings_to_urls': False})
output_df.to_excel(writer,index=False)
writer.close()

df = pd.read_excel(f"FlipkartPLP_Filtered_{glob_file}")
df1 = pd.read_excel(f"input/{glob_file}",sheet_name="Sheet1")
df2 = df.drop_duplicates(subset=['category'])
set1= set(df1['Product_list'])
set2= set(df2['category'])
missing_in_df = set1 - set2
missing_in_df = list(missing_in_df)

pd.DataFrame({"Product_list":missing_in_df}).to_excel(f"Flipkart_Exception_Product_{glob_file}",index=False)


############################## Saving All exception in a single excel file ###########################################
