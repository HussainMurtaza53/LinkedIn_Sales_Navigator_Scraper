# Importing all Pre-requisites:
import pandas as pd
from tqdm import tqdm
import time
import json
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options


class Sales_Navigator_Scraper():

    # Constructor to save website which we will pass while calling Scraper class:
    def __init__(self):
        
        with open('credentials.json') as f:
            json_data = json.load(f)

        self.website = json_data['link']
        self.username = json_data['username']
        self.password = json_data['password']
        
        PROXY = "151.80.255.29:8001"

        options = Options()
        options.headless = True
        options.add_argument('--proxy-server=%s' % PROXY)
        options.add_argument('--no-sandbox')
        options.add_argument('--start-maximized')
        options.add_argument('--start-fullscreen')
        options.add_argument('--single-process')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument("--incognito")
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option('useAutomationExtension', False)
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_argument("disable-infobars")

        self.driver = webdriver.Chrome("/usr/lib/chromium-browser/chromedriver", chrome_options = options)

    # This function will open the website in new browser:
    def start_browser(self):
        
        self.driver.get(self.website)
        
        time.sleep(2)

        login_link = self.driver.find_element_by_tag_name('iframe').get_attribute('src')
        self.driver.get(login_link)

        self.enter_login_credentials()

        self.driver.get(self.website)
        try:
            self.driver.maximize_window()
        except:
            pass

        time.sleep(7)

    def enter_login_credentials(self):

        username = self.driver.find_element_by_id('username')
        username.send_keys(self.username)

        password = self.driver.find_element_by_id('password')
        password.send_keys(self.password)

        self.driver.find_element_by_class_name('from__button--floating').click()

    def get_page_data_by_scrolling(self):

        self.driver.find_element_by_xpath("//div[contains(@class, 'flex') and contains(@class, 'justify-space-between') and contains(@class, 'full-width')]").click()

        html = self.driver.find_element_by_tag_name('html')
        html.send_keys(Keys.END)

        for i in range(8):
            html.send_keys(Keys.PAGE_UP)
        
        time.sleep(2)
        html.send_keys(Keys.END)
        html.send_keys(Keys.END)
        html.send_keys(Keys.HOME)
        html.send_keys(Keys.END)
        
        page_data = self.driver.find_elements_by_class_name('artdeco-entity-lockup__title')

        return page_data

    def shift_tab(self, element):

        ActionChains(self.driver).key_down(Keys.CONTROL).click(element).key_up(Keys.CONTROL).perform()
        self.driver.switch_to.window(self.driver.window_handles[1])
        time.sleep(5)
    
    # This is the main function that will scrape all data:
    def scrape(self):
        
        condition = True
        all_details = []

        while condition:
            
            try:
                all_content = self.get_page_data_by_scrolling()
            except:
                time.sleep(8)
                all_content = self.get_page_data_by_scrolling()

            time.sleep(2)
            import pdb; pdb.set_trace()
            for l in tqdm(range(len(all_content))):
                
                try:
                    name_ls = self.driver.find_elements_by_class_name('artdeco-entity-lockup__title')[l].text.split()
            
                    if len(name_ls) > 1:

                        f_name = name_ls[0]
                        l_name = name_ls[1]

                    else:
                        f_name = name_ls[0]
                        l_name = None

                    try:
                        location = self.driver.find_elements_by_class_name('artdeco-entity-lockup__caption')[l].text
                    except:
                        location = None
                    
                    try:
                        job_title = self.driver.find_elements_by_class_name('artdeco-entity-lockup__subtitle')[l].find_element_by_tag_name('span').text
                        comp_info = self.driver.find_elements_by_class_name('artdeco-entity-lockup__subtitle')[l].find_element_by_tag_name('a')

                        company = comp_info.text

                        self.shift_tab(comp_info)

                        try:
                            company_url = self.driver.find_element_by_class_name('view-website-link').get_attribute('href')
                        except:
                            company_url = None

                        self.driver.close()

                        self.driver.switch_to.window(self.driver.window_handles[0])

                    except:
                        company = None
                        company_url = None
                        job_title = None

                    if company:
                        
                        dic = {
                            'First_Name': f_name,
                            'Last_Name': l_name,
                            'Company': company,
                            'Company_URL': company_url,
                            'Job_Title': job_title,
                            'Location': location
                        }
                        
                        all_details.append(dic)

                        self.save_data(all_details)
                
                except:
                    pass

            try:
                try:
                   button_class = self.driver.find_element_by_class_name('artdeco-pagination__button--next').get_attribute('class')
                except:
                   import pdb;pdb.set_trace()
                   time.sleep(5)
                   button_class = self.driver.find_element_by_class_name('artdeco-pagination__button--next').get_attribute('class')
                
                if 'artdeco-button--disabled' not in button_class:
                    self.driver.find_element_by_class_name('artdeco-pagination__button--next').click()
                    time.sleep(10)
                else:
                    import pdb; pdb.set_trace()
                    condition = False
            except:
                import pdb; pdb.set_trace()
                condition = False
        
        # Closing the browser after scraping all data:
        self.driver.close()

        print('-------------------- SCRAPING DONE --------------------')

    def save_data(self, data_ls):

        scraped_data = pd.DataFrame(data_ls)
        scraped_data.to_excel('LinkedIn_Sales_Navigator_Data.xlsx')


# Creating class object:
s_nav_scraper = Sales_Navigator_Scraper()

# Calling functions that are created above:
s_nav_scraper.start_browser()
s_nav_scraper.scrape()