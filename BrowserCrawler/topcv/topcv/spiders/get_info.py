import datetime as dt
import time
import json
import os
import scrapy
import re

'''
    liststr: list of string
    letters: string of all special letters that need to be removed. For example: '.,:;()[]{}' -> remove all .,:;()[]{}
'''
def remove_special_letter(liststr: list, letters: str) -> list:
    return [x.strip(letters) for x in liststr]

def filter_empty_string(liststr: list) -> list:
    return list(filter(None, liststr))

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

class TopCVCrawler(scrapy.Spider):

    name = 'topcv_i4_crawler'

    listdirs = os.listdir('data')
    if('urls.json' in listdirs):
        listdirs.remove('urls.json')

    with open (f'data/{listdirs[-1]}', 'r') as f:
        urls = json.load(f)
 
    start_urls = [urls[0]]
    # start_urls = ['https://www.topcv.vn/viec-lam/thuc-tap-sinh-lap-trinh-web-mobile-app-thu-nhap-3-7-trieu-thang/1160615.html?ta_source=ITJobs_LinkDetail']
    listdirs = os.listdir('json')
    if 'out.json' in listdirs:
        os.remove('json/out.json')
    CURRENT_URL = 0
    LIMIT = len(urls)
    CHUNK_SIZE = 15
    ERRORS = []


    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.FormRequest(url=url, callback=self.parse, dont_filter=True)
    def parse(self, response):

        try:
            job_header = response.xpath('/html/body/div[9]/div[3]/div[3]/div/div[1]/div[1]')
            job_header = job_header.css('::text').getall()
            job_header = filter_empty_string(remove_special_letter(job_header, ' \n'))
            print("---------------------------------")
            print(job_header)
            print("---------------------------------")
            if len(job_header) > 3:
                salary_index = job_header.index('Mức lương')
                address_index = job_header.index('Địa điểm')

                job_name = job_header[0:salary_index]
                salary = job_header[salary_index+1:address_index]
                exp = job_header[6]
                remaining = None
                for i in range(7,len(job_header),1):
                    reg = re.search(r'\d+/\d+/\d+',job_header[i])
                    if reg is not None:
                        remaining = reg.group()
                        break
            else:
                # raise ValueError('Job header is not enough information')
                raise ValueError('Job header is not enough information') # for next url
            
            job_description = response.xpath('/html/body/div[9]/div[3]/div[3]/div/div[1]/div[2]/div[1]/div[1]')
            job_description_text = job_description.css('::text').getall()
            key_job_description = job_description.css('h3::text').getall()
            job_description_text = filter_empty_string(remove_special_letter(job_description_text, ' \n'))
            job_description_info = convert_key_value(key_job_description, job_description_text)

            company_description = response.xpath('/html/body/div[9]/div[3]/div[3]/div/div[2]/div[1]')
            company_description_text = company_description.css('::text').getall()
            company_description_text = filter_empty_string(remove_special_letter(company_description_text, ' \n'))
            company_name = company_description_text[0]
            address = company_description_text[4:-1]
            
            candidate_requirement = response.xpath('/html/body/div[9]/div[3]/div[3]/div/div[2]/div[2]/div')
            candidate_requirement_text = candidate_requirement.css('::text').getall()
            candidate_requirement_text = filter_empty_string(remove_special_letter(candidate_requirement_text, ' \n'))[3:]
            candidate_requirement_info = dict(map(lambda i: (candidate_requirement_text[i], candidate_requirement_text[i+1]), range(len(candidate_requirement_text)-1)[::2]))

            job_infos = {
                'urls': self.urls[self.CURRENT_URL],
                'job_name': job_name,
                'company_name': company_name,
                'address': address,
                'salary': salary,
                'exp': exp,
                'remaining': remaining
            }

            job_infos.update(job_description_info)
            job_infos.update(candidate_requirement_info)


            yield job_infos
            time.sleep(2)
            self.CURRENT_URL += 1
            if self.CURRENT_URL % self.CHUNK_SIZE == 0 and self.CURRENT_URL != 0:
                time.sleep(5*60)
            if self.CURRENT_URL < self.LIMIT:
                yield scrapy.FormRequest(url=self.urls[self.CURRENT_URL], callback=self.parse, meta = {'dont_redirect': True, 'handle_httpstatus_list': [302, 429]})
        except:
            #  raise KeyError(f'Error in parsing the job info {self.CURRENT_URL}')
            self.ERRORS.append(self.urls[self.CURRENT_URL])
            time.sleep(2)
            self.CURRENT_URL += 1
            if self.CURRENT_URL % self.CHUNK_SIZE == 0 and self.CURRENT_URL != 0:
                time.sleep(5*60)
            if self.CURRENT_URL < self.LIMIT:
                yield scrapy.FormRequest(url=self.urls[self.CURRENT_URL], callback=self.parse, meta = {'dont_redirect': True, 'handle_httpstatus_list': [302, 429]})
