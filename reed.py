from selenium import webdriver
from time import sleep
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC  
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException


#set up drivers
driver = webdriver.Chrome(ChromeDriverManager().install())
driver.get('https://www.reed.co.uk')
sleep(2)

#close popup find search bar
try:
    element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID,"onetrust-accept-btn-handler")))
    element.click()
except:
    print("Error with popup.")

search = driver.find_element_by_id("main-keywords")
search.clear()
search.send_keys("machine learning engineer")
search.send_keys(Keys.RETURN)
  

#get links based on keywords
def get_links(exact_match, keywords):
    results = driver.find_element_by_id("server-results")
    if(not exact_match):
        links = results.find_elements_by_partial_link_text(keywords[0])
        for i in range(1, len(keywords)):
            links.extend(results.find_elements_by_partial_link_text(keywords[i]))
        return links
    else:
        links = results.find_elements_by_link_text(keywords[0])
        for i in range(1, len(keywords)):
            links.extend(results.find_elements_by_link_text(keywords[i]))
        return links



#setup and scrape
seen = set()
desc = []
salary = []
location = []
kws = ["Machine Learning Engineer", "Junior Machine Learning Engineer"]
exact_match = True

#go through all pages
while(True):
    
    #get all ads on given page
    for i in range(0, len(get_links(exact_match, kws))):
        
        #this needs to be done every iteration for some reason
        links = get_links(exact_match, kws)
        if links[i] not in seen:
            
            #scroll down to ad
            actions = ActionChains(driver)
            actions.move_to_element(links[i]).perform()
            
            #click and wait
            sleep(2)
            links[i].click()
            
            #get data from job
            desc.append(driver.find_element_by_class_name("description").text)
            try:
                salary.append(driver.find_element_by_xpath('//*[@id="content"]/div[1]/div[2]/article/div/div[2]/div/div[2]/div/div[1]/span/span[1]').text)
                location.append(driver.find_element_by_xpath('//*[@id="content"]/div[1]/div[2]/article/div/div[2]/div/div[2]/div/div[2]/span[2]/a/span/span').text)
            except:
                print("No salary or location")
                
            #go back and add visited to seen
            seen.add(links[i])
            driver.back()
            driver.implicitly_wait(5)
       
    #go to next page, if there is one  
    driver.find_element_by_id("nextPage").click()
    sleep(2)
    try:
        driver.find_element_by_id("nextPage")
    except NoSuchElementException:
        print("No more pages left, scrape finished, found", len(desc),"jobs.")
        break
    



