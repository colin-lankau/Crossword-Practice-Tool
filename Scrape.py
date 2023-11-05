from selenium import webdriver
from selenium.webdriver.common.by import By
import time
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.support.ui import WebDriverWait

def Scrape(date: str):

    # setup
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--mute-audio")
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(f"https://nytcrosswordanswers.org/nyt-crossword-answers-{date}/")
    print(driver.title)
    time.sleep(3)

    uls = driver.find_elements(By.TAG_NAME, "ul")
    across = uls[1].find_elements(By.TAG_NAME, "li")
    down = uls[2].find_elements(By.TAG_NAME, "li")

    across_clues = []
    across_answers = []
    for group in across:
        clue = group.find_element(By.TAG_NAME, "a").get_attribute('innerText')
        answer = group.find_element(By.TAG_NAME, "span").get_attribute('innerText')
        across_clues.append(clue)
        across_answers.append(answer)

    down_clues = []
    down_answers = []
    for group in down:
        clue = group.find_element(By.TAG_NAME, "a").get_attribute('innerText')
        answer = group.find_element(By.TAG_NAME, "span").get_attribute('innerText')
        down_clues.append(clue)
        down_answers.append(answer)

    driver.quit()
    
    return across_clues, across_answers, down_clues, down_answers