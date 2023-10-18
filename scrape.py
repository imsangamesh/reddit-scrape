import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import sys


url = "https://www.reddit.com/r/TwoXIndia/"

driver = webdriver.Chrome()
driver.get(url)


# - - - - - - - - - - - - - - - - - - - - - Scrape POSTS
def scrape_post_data(post_elm):
    # - - - - Title
    title_elm = post_elm.find(
        "div",
        class_="font-semibold text-neutral-content-strong text-16 xs:text-18 mb-2xs xs:mb-xs",
    )
    title = "" if title_elm is None else title_elm.text.strip()

    # - - - - Description
    description_elm = post_elm.find(
        "div",
        class_="text-neutral-content md max-h-[337px] overflow-hidden text-12 xs:text-14",
    )
    description = (
        ""
        if description_elm is None
        else [each for each in description_elm.stripped_strings]
    )

    # - - - - Extract score (votes)
    try:
        votes = int(post_elm["score"])
    except KeyError:
        votes = 0

    return {"title": title, "description": description, "votes": votes}


# ====================================================================================
# ======================================= START ======================================
# ====================================================================================

prev_scroll_position = 0
consecutive_same_position_count = 0  # variable which gets incremented
# when previous_scroll_pos is same as current_scroll_pos,
# and if it's incremented to 3times, means there is no change for 3times in a row,
# then we can be sure that, there are no posts left to scrape >> so we chip out of the loop

WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, "shreddit-post[permalink^='/r/']"))
)

while True:
    driver.find_element(By.TAG_NAME, "body").send_keys(Keys.END)
    current_scroll_position = driver.execute_script("return window.scrollY")

    # Checking if the scroll position hasn't changed
    if current_scroll_position == prev_scroll_position:
        consecutive_same_position_count += 1
        if consecutive_same_position_count >= 3:  # Threshold value
            break
    else:
        consecutive_same_position_count = 0  # Reset counter
        prev_scroll_position = current_scroll_position

    time.sleep(0.5)


soup = BeautifulSoup(driver.page_source, "html.parser")
scraped_data = []

post_elms = soup.select("shreddit-post[permalink^='/r/']")

for post_elm in post_elms:
    post_data = scrape_post_data(post_elm)
    scraped_data.append(post_data)


driver.quit()


# - - - - - - - - - - - - - - - - - - - - - PRINTING OUTPUT
original_stdout = sys.stdout  # saving the current standard o/p

with open("output.txt", "w", encoding="utf-8") as file:
    # Redirect the standard output to the file
    sys.stdout = file

    for item in scraped_data:
        print(item)

sys.stdout = original_stdout  # restoring the original standard o/p

print(f"{len(scraped_data)} posts output saved to 'output.txt'")
