import datetime as dt
import time
import json
import os
import scrapy
import re

def convert_key_value(keys_dict, text_list):
    infos = dict()
    for index, key in enumerate(keys_dict):
        if key not in text_list:
            raise KeyError(f'{key} not in text_list')
        if index == len(keys_dict) -1:
            infos[key] = text_list[text_list.index(key)+1:]
        else:
            infos[key] = text_list[text_list.index(key)+1:text_list.index(keys_dict[index+1])]
    return infos

class VNWCrawler(scrapy.Spider):
    name = 'vnw_i4_crawler'

    listdirs = os.listdir('data')
    if('urls.json' in listdirs):
        listdirs.remove('urls.json')

    with open (f'data/{listdirs[-1]}', 'r') as f:
        urls = json.load(f)
 
    start_urls = [urls[0]]
    listdirs = os.listdir('json')
    if 'out.json' in listdirs:
        os.remove('json/out.json')
    CURRENT_URL = 0
    LIMIT = len(urls)
    ERRORS = []
        

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.FormRequest(url=url, callback=self.parse, dont_filter=True)

    def parse(self, response):
#####################################################################################################################################################  
        ''' JOB DESCRIPTION INFO
            1. Get selection of the header
            2. get all text in selection
            3. cleaning the space and '\n' in the text
            4. saving the job_name, company_name, salary, end_date
        '''
        # 1. get selection of the header
        try:
            job_header_info = response.xpath('/html/body/div[1]/main/div[2]/div/div/div/div[1]/div/div[1]/div/div[1]')
            # 2. get all text in selection
            text = job_header_info.css('::text').getall()
            # 3. cleaning the space and '\n' in the text
            text = [x.strip(' \n') for x in text]
            text = list(filter(None, text))
            # 4. saving the job_name, company_name, salary, end_date
            if len(text) > 3:
                job_name = text[0]
                company_name = text[1]
                salary = text[2]
                remaining_date = None
                for i in range(3, len(text), 1):
                    remaining_date = re.search(r"\d+", text[i])
                    if(remaining_date):
                        remaining_date = remaining_date.group()
                        break
                end_date = (dt.datetime.now() + dt.timedelta(days = int(remaining_date))).strftime("%Y-%m-%d")
            else:
                pass
            ''' JOB FOOTER INFO

            '''
            job_footer_info = response.xpath('/html/body/div[1]/main/div[2]/div/div/div/div[1]/div/div[1]/div/div[5]')
            keys = job_footer_info.css('label::text').getall()
            text_footer = job_footer_info.css('::text').getall()
            infos = convert_key_value(keys, text_footer)


            ''' JOB DESCRIPTION INFO

            '''
            job_requests = response.xpath('/html/body/div[1]/main/div[2]/div/div/div/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div')
            keys_content = job_requests.css('h2::text').getall()
            job_description = job_requests.css('::text').getall()        
            job_description_dict = convert_key_value(keys_content, job_description)
            for key, value in job_description_dict.items():
                new_value = []
                for text in value:
                    text = text.split('\n')
                    text = [x.strip(' \r\t') for x in text]
                    text = list(filter(None, text))
                    new_value.append(text)
                job_description_dict[key] = new_value
            try: 
                address = response.xpath('/html/body/div[1]/main/div[2]/div/div/div/div[2]/div/div[1]/div[3]/div/div[1]/div[2]/p/text()').getall()
                # address = address.css('::text').getall()
                # if (address != None or len(address) > 0):
                #     address = address[0]
                # else:
                #     address = None
            except:
                address = None
            
            job_infos = {
                'url': self.urls[self.CURRENT_URL],
                'job_name': job_name,
                'company_name': company_name,
                'salary': salary,
                'end_date': end_date,
                'address': address
            }
            job_infos.update(infos)
            job_infos.update(job_description_dict)


            yield job_infos
            self.CURRENT_URL += 1
            if self.CURRENT_URL < self.LIMIT:
                # time.sleep(5)
                yield scrapy.Request(url=self.urls[self.CURRENT_URL], callback=self.parse)
        except:
            # raise KeyError(f'Error in parsing the job info {self.CURRENT_URL}')
            self.ERRORS.append(self.urls[self.CURRENT_URL])
            self.CURRENT_URL += 1
            if self.CURRENT_URL < self.LIMIT:
                # time.sleep(5)
                yield scrapy.Request(url=self.urls[self.CURRENT_URL], callback=self.parse)
        
        if self.CURRENT_URL == self.LIMIT:
            print('ERRORS: ' + str(len(self.ERRORS)))
            print(self.ERRORS)
            

#####################################################################################################################################################
        # job_header_info = response.xpath('/html/body/div[1]/main/div[2]/div/div/div/div[1]/div/div[1]/div/div[1]')
        # # 2. get all text in selection
        # text = job_header_info.css('::text').getall()
        # # 3. cleaning the space and '\n' in the text
        # text = [x.strip(' \n') for x in text]
        # text = list(filter(None, text))
        # print(text)
        # # 4. saving the job_name, company_name, salary, end_date
        # job_name = text[0]
        # company_name = text[1]
        # salary = text[2]
        # remaining_date = re.search(r"\d+", text[3]).group()
        # end_date = (dt.datetime.now() + dt.timedelta(days = int(remaining_date))).strftime("%Y-%m-%d")

        # ''' JOB FOOTER INFO

        # '''
        # job_footer_info = response.xpath('/html/body/div[1]/main/div[2]/div/div/div/div[1]/div/div[1]/div/div[5]')
        # keys = job_footer_info.css('label::text').getall()
        # text_footer = job_footer_info.css('::text').getall()
        # infos = convert_key_value(keys, text_footer)


        # ''' JOB DESCRIPTION INFO

        # '''
        # job_requests = response.xpath('/html/body/div[1]/main/div[2]/div/div/div/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div')
        # keys_content = job_requests.css('h2::text').getall()
        # job_description = job_requests.css('::text').getall()        
        # job_description_dict = convert_key_value(keys_content, job_description)
        # for key, value in job_description_dict.items():
        #     new_value = []
        #     for text in value:
        #         text = text.split('\n')
        #         text = [x.strip(' \r') for x in text]
        #         text = list(filter(None, text))
        #         new_value.append(text)
        #     job_description_dict[key] = new_value
        
        
        # job_infos = {
        #     'job_name': job_name,
        #     'company_name': company_name,
        #     'salary': salary,
        #     'end_date': end_date,
        # }
        # job_infos.update(infos)
        # job_infos.update(job_description_dict)


        # yield job_infos