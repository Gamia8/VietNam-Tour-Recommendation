from Place_crawl import get_place_list
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup
import time
import csv
import random

def scrape_google_maps_reviews(place_name, location_type, max_reviews):
    driver = webdriver.Chrome()
    try:
        search_url = f"https://www.google.com/maps/search/{place_name.replace(' ', '+')}"
        driver.get(search_url)
        time.sleep(1)

        first_result = None
        try:
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "m6QErb")))
            xpath_options = [
                "//div[contains(@class, 'Nv2PK') and contains(@class, 'THOPZb')]/a[1]",
                "//button[contains(@class, 'wR3cXd') and @data-bundle-id][1]//a",
                "//li[contains(@class, 'ODXihb')]//a[1]"
            ]
            for xpath in xpath_options:
                try:
                    first_result = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, xpath)))
                    if first_result:
                        break
                except:
                    continue
            if first_result:
                first_result.click()
                time.sleep(3)
        except TimeoutException:
            pass

        try:
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "w6VYqd")))
        except TimeoutException:
            return []

        soup = BeautifulSoup(driver.page_source, "html.parser")
        address_element = soup.find(lambda tag: tag.name == "div" and "Io6YTe" in tag.get("class", []))
        address = address_element.text if address_element and address_element.text.strip() else ""

        try:
            tabs = driver.find_elements(By.CSS_SELECTOR, 'button.hh2c6')
            review_button = None
            for tab in tabs:
                if "Reviews" in tab.get_attribute("aria-label"):
                    review_button = tab
                    break
            if not review_button:
                raise NoSuchElementException
            review_button.click()
            time.sleep(1)
        except (TimeoutException, NoSuchElementException):
            return []

        reviews_section = driver.find_element(By.CLASS_NAME, "DxyBCb")

        scroll_pause_time = random.uniform(0.8, 1.5)
        scroll_increment = 1500
        max_attempts = 5
        attempts = 0

        while attempts < max_attempts:
            soup = BeautifulSoup(driver.page_source, "html.parser")
            reviews = soup.find_all("div", class_="jftiEf")
            if len(reviews) >= max_reviews:
                break

            current_height = driver.execute_script("return arguments[0].scrollTop + arguments[0].clientHeight", reviews_section)
            total_height = driver.execute_script("return arguments[0].scrollHeight", reviews_section)
            
            if current_height >= total_height:
                attempts += 1
                time.sleep(scroll_pause_time)
                continue
                
            driver.execute_script("arguments[0].scrollBy(0, arguments[1]);", reviews_section, scroll_increment)
            time.sleep(scroll_pause_time)
            
            new_height = driver.execute_script("return arguments[0].scrollTop + arguments[0].clientHeight", reviews_section)
            if new_height == current_height:
                attempts += 1
            else:
                attempts = 0

        soup = BeautifulSoup(driver.page_source, "html.parser")
        reviews = soup.find_all("div", class_="jftiEf")

        result = []
        for review in reviews[:max_reviews]:
            try:
                review_id = review.get("data-review-id")
                user_info = review.find("div", class_="d4r55").text if review.find("div", class_="d4r55") else "Unknown"
                rating = review.find("span", class_="kvMYJc")["aria-label"].split()[0] if review.find("span", class_="kvMYJc") else "0"
                date = review.find("span", class_="rsqaWe").text if review.find("span", class_="rsqaWe") else "No date"

                content_div = driver.find_element(By.ID, review_id) if review_id else None
                if content_div:
                    content_span = content_div.find_element(By.CLASS_NAME, "wiI7pd")
                    content = content_span.text if content_span else "No comment"
                    more_button = content_div.find_elements(By.CLASS_NAME, "w8nwRe")
                    if more_button:
                        driver.execute_script("arguments[0].click();", more_button[0])
                        time.sleep(0.5)
                        content_span = content_div.find_element(By.CLASS_NAME, "wiI7pd")
                        content = content_span.text if content_span else content
                else:
                    content = "No comment"

                result.append({
                    "place_name": place_name,
                    "user_info": user_info,
                    "rating": rating,
                    "content": content,
                    "date": date,
                    "address": address,
                    "location": location_type
                })
            except:
                continue

        return result

    finally:
        driver.quit()

def crawl_google_maps_data(output_file, max_reviews):
    places = get_place_list()  

    with open(output_file, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["place_name", "user_info", "rating", "content", "date", "address", "location"])
        if f.tell() == 0:
            writer.writeheader()

        for place_name, location_type in places:
            print(f"Start collecting reviews for {place_name}...")
            reviews = scrape_google_maps_reviews(place_name, location_type, max_reviews=max_reviews)
            if not reviews:
                print(f"Unable to collect reviews for {place_name}.")
                continue

            for review in reviews:
                writer.writerow({
                    "place_name": review["place_name"],
                    "user_info": review["user_info"],
                    "rating": f"{review['rating']} sao",
                    "content": review["content"],
                    "date": review["date"],
                    "address": review["address"],
                    "location": review["location"]
                })
            print(f"Collected {len(reviews)} Reviews for {place_name}.")

    print(f"Data has been saved to {output_file}")