from selenium import webdriver
from time import sleep
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC  
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException
import matplotlib.pyplot as plt
from collections import Counter
import numpy as np



POSITION = "Machine Learning Engineer"



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
search.send_keys(POSITION)
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
skills = []
salary = []
location = []
kws = [POSITION]
exact_match = False


#####TEST AREA


#####


#go through all pages
while(True):
    
    #get all ads on given page
    for i in range(0, len(get_links(exact_match, kws))):
        
        #this needs to be done every iteration for some reason
        links = get_links(exact_match, kws)
        
        #if anything bad happens, skip
        try:
            if links[i] not in seen:
       
                #scroll down to ad
                actions = ActionChains(driver)
                actions.move_to_element(links[i]).perform()
                
                #click and wait
                sleep(2)
                links[i].click()
                
                try:
                    #get skills and add them to list
                    skill_list = driver.find_element_by_class_name("skills").find_elements_by_tag_name("li")
                    for x in skill_list:
                        skills.append(x.text.lower())
                except:
                    print("Moving onto description.")
                    #if no skill list, get desciption
                    try:          
                        #get data from job
                        desc.append(driver.find_element_by_class_name("description").text)
                    except:
                        print("Promoted job or missing ad found.")
                    
                try:
                    salary.append(driver.find_element_by_xpath('//*[@id="content"]/div[1]/div[2]/article/div/div[2]/div/div[2]/div/div[1]/span/span[1]').text)
                    location.append(driver.find_element_by_xpath('//*[@id="content"]/div[1]/div[2]/article/div/div[2]/div/div[2]/div/div[2]/span[2]/a/span/span').text)
                except:
                    print("No salary or location")
                    
                #go back and add visited to seen
                seen.add(links[i])
                driver.back()
                driver.implicitly_wait(5)
        except:
            continue
        
    #go to next page, if there is one  
    driver.find_element_by_id("nextPage").click()
    sleep(2)
    
    try:
        driver.find_element_by_id("nextPage")
    except NoSuchElementException:
        print("No more pages left, scrape finished, found", len(desc),"jobs.")
        break



def plot_location(location):
    plt.style.use("ggplot")
    labels = list(set(location))
    loc_count = [location.count(x) for x in labels]

    #order them, and only get top 10
    d = dict(zip(labels, loc_count))
    d = dict(sorted(d.items(), key=lambda item: item[1], reverse = True))
    d = dict(Counter(d).most_common(20))
    
    plt.figure(figsize=(10,5))
    plt.bar(list(d.keys()), list(d.values()), align='center')
    
    plt.xticks(rotation=45)
    plt.title("Location of jobs")
    plt.show()
    
    
    
#add saalary and time frame (annum, hour, day)
def plot_salary(salary, time_frame):
    plt.style.use("ggplot")
    pay = [] 
    for s in salary:
        if time_frame in s:
            num_list = [x for x in s.split(" ")]
            c = 0
            pay_temp = 0
            for n in num_list:
                res = ''.join(e for e in n if e.isalnum())
                if res.isdigit():
                    pay_temp += int(res)
                    c+=1
                    
            #add the average - adds trailing 0s, needs to be divided by 100
            #is singleton value for hour add it to list/100 because stored as 9.00 -> 900
            if c < 2 and (time_frame == "hour" or time_frame == "day"):
                pay.append(pay_temp/100)
                
            elif time_frame == "hour" or time_frame == "day":
                pay.append(pay_temp/200)
            elif c < 2:
                pay.append(pay_temp)
            else:
                pay.append(pay_temp/2)
    
    #plot settings
    if len(pay) < 10:
        print("Not enough data for "+ time_frame)
        return

    #only keep rows in dataframe with all z-scores less than absolute value of 3 
    pay_clean = detect_outlier(pay)
    
    plt.figure(figsize=(10,5))
    plt.hist(pay_clean,bins = int(len(pay_clean)/5), color = "green")
    plt.title("Salary")
    plt.xlabel("Salary in GBP per " + time_frame)
    plt.show()
   
    
def detect_outlier(data):
    # find q1 and q3 values
    q1, q3 = np.percentile(sorted(data), [25, 75])
 
    # compute IRQ
    iqr = q3 - q1
 
    # find lower and upper bounds
    lower_bound = q1 - (1.5 * iqr)
    upper_bound = q3 + (1.5 * iqr)
  
    return [x for x in data if x >= lower_bound and x <= upper_bound] 



def plot_skills(skills, min_skill_count):
    #collect skills, clean and add it to complete_skills
    complete_skills = []
    for i in skills:
        unwrapped = i.split("|")
        for item in unwrapped:
            complete_skills.append(item.lower())
          
    #creating dictionary, setting min occurance of skills       
    d = {}
    for skill in set(complete_skills):
        d.update({skill : complete_skills.count(skill)})
    sorted_d = dict(sorted(d.items(), key=lambda x: x[1], reverse = True))
    sorted_d = {key:val for key, val in sorted_d.items() if val > min_skill_count}
    
    #if not enough data
    if len(sorted_d) < 3:
        print("Not enough data for skill graph.")
        return
    
    #plot results
    plt.figure(figsize=(10,5))
    plt.bar(sorted_d.keys(), sorted_d.values())
    plt.xticks(rotation = 45)
    plt.title("Required skills mentioned")
    plt.show()



plot_location(location)   
plot_salary(salary, "annum")
plot_salary(salary, "hour")
plot_salary(salary, "day")
plot_skills(skills, 3)












