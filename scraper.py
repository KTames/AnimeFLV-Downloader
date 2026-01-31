from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import scrapy
import time
import regex


def scrapAnime(anime, browser, offset, limit=-1):
    if browser == "safari":
        driver = webdriver.Safari()
    elif browser == "chrome":
        driver = webdriver.Chrome()
    else:
        driver = browser

    driver.set_window_size(500, 500)
    driver.get("https://animeflv.net/anime/" + anime)

    scrollableUl = "document.getElementsByClassName('ListCaps')[0]"

    WebDriverWait(driver, 30).until(
        lambda d: d.execute_script(
            "return " + scrollableUl + " && " + scrollableUl + ".children.length > 0"
        )
    )

    last_height = driver.execute_script(
        "return " + scrollableUl + ".scrollTop")
    failed_count = 0

    driver.execute_script("window.scrollTo(0, 100000)")

    print("Scrolling down...")
    while True:

        # Scroll down to the bottom.
        driver.execute_script(scrollableUl +
                               ".scroll(0, 100000)",)

        # Wait to load the page.
        time.sleep(0.5)

        # Calculate new scroll height and compare with last scroll top.
        new_height = driver.execute_script(
            "return " + scrollableUl + ".scrollTop")

        if new_height == last_height:
            failed_count += 1
            if failed_count >= 5:
                break
        else:
            failed_count = 0

        last_height = new_height

    print("Finished scrolling")

    episodes = []
    for a in driver.find_elements(By.CSS_SELECTOR, "li.fa-play-circle>a"):
        url = a.get_attribute("href")
        if "#" in url:
            continue
        number = int(regex.findNumbers(url)[-1:][0].replace("-", ""))
        if number >= offset:
            episodes.append((number, url))

    # Oldest-first, then apply limit so "first N" means earliest episodes.
    episodes.sort(key=lambda item: item[0])
    if limit and limit > 0:
        episodes = episodes[:limit]

    links = [url for _, url in episodes]
    for url in links:
        print(url)
    driver.close()
    return links
