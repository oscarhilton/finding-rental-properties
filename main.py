from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urlparse, parse_qs
import csv

CSV_FILE = "spareroom_listings.csv"

def handle_reg_popup(driver):
    try:
        print("[INFO] Checking for registration pop-up...")

        # Wait up to 3 seconds for the popup (don't wait if it's not there)
        reg_popup = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.ID, "reg_popup"))
        )

        if reg_popup.is_displayed():
            print("[INFO] Registration pop-up found, clicking 'Remind me later'...")

            remind_me_button = driver.find_element(By.ID, "reg_remind_me_later")
            remind_me_button.click()

            # Ensure the pop-up disappears before proceeding
            WebDriverWait(driver, 2).until(
                EC.invisibility_of_element_located((By.ID, "reg_popup"))
            )
            print("[INFO] Registration pop-up dismissed.")

    except Exception:
        print("[INFO] No registration pop-up detected, continuing...")


def handle_cookies(driver):
    try:
        print("[INFO] Checking for cookie pop-up...")

        # Quickly check if the button is already present
        cookie_button = WebDriverWait(driver, 2).until(
            EC.presence_of_element_located((By.ID, "onetrust-accept-btn-handler"))
        )

        if cookie_button.is_displayed():
            print("[INFO] Cookie button found, clicking now...")
            cookie_button.click()

            # Ensure it disappears
            WebDriverWait(driver, 2).until(
                EC.invisibility_of_element_located((By.ID, "onetrust-accept-btn-handler"))
            )
            print("[INFO] Cookie pop-up dismissed.")
        else:
            print("[INFO] Cookie button not visible, continuing...")

    except Exception:
        print("[INFO] No cookie pop-up detected, moving on...")

def already_recorded(listing_id):
    try:
        with open(CSV_FILE, "r", newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            for row in reader:
                if listing_id in row:
                    return True
    except FileNotFoundError:
        pass  # No existing file means nothing is recorded yet
    return False

def write_to_csv(data):
    with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(data)

def main():
    print("[INFO] Starting browser...")
    driver = webdriver.Chrome()
    
    print("[INFO] Navigating to SpareRoom advanced search...")
    driver.get("https://www.spareroom.co.uk/flatshare/search.pl?searchtype=advanced")

    # Handle cookies
    handle_cookies(driver)

    print("[INFO] Entering search criteria...")
    
    try:
        # Enter location
        location_box = driver.find_element(By.ID, "search_by_location_field")
        location_box.send_keys("London")
        print("  - Set location to London")

        # Example: Set max price
        max_price = driver.find_element(By.NAME, "max_rent")
        max_price.send_keys("700")
        print("  - Set max rent to £700")

        # Click the search button
        search_button = driver.find_element(By.ID, "search-button")
        search_button.click()
        print("[INFO] Search submitted, waiting for results...")
        
    except Exception as e:
        print(f"[ERROR] Problem filling search form: {e}")
        driver.quit()
        return
    
    handle_reg_popup(driver)
    
    # Loop through pages
    page_number = 1
    while True:
        try:
            print(f"[INFO] Scraping page {page_number}...")

            # Wait for listings to load
            WebDriverWait(driver, 2).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".listing-result"))
            )

            # Get all listing elements directly with Selenium
            listings = driver.find_elements(By.CSS_SELECTOR, ".listing-result")

            for listing in listings:
                try:
                    link_element = listing.find_element(By.CSS_SELECTOR, "a")
                    link = link_element.get_attribute("href")

                    # Parse the URL and extract query parameters
                    parsed_url = urlparse(link)
                    query_params = parse_qs(parsed_url.query)

                    # Extract the search_id
                    listing_id = query_params.get("flatshare_id", [""])[0]

                    if already_recorded(listing_id):
                        print(f"  - Skipping already recorded listing: {listing_id}")
                        continue

                    title = listing.find_element(By.CSS_SELECTOR, ".listing-card__title").text.strip()
                    price = listing.find_element(By.CSS_SELECTOR, ".listing-card__price").text.strip()

                    # Save data
                    write_to_csv([listing_id, title, price, link])
                    print(f"  - Saved new listing: {title} ({price})")

                except Exception as e:
                    print(f"[WARNING] Skipping listing due to error: {e}")

        except Exception as e:
            print(f"[WARNING] Skipping listing due to error: {e}")

        # Check if there's a 'Next' button and move to the next page
        try:
            next_button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "paginationNextPageLink")))
            next_page_url = next_button.get_attribute("href")

            if next_page_url:
                print(f"[INFO] Moving to next page ({page_number + 1})... Navigating to: {next_page_url}")
                driver.get(next_page_url)
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".listing-result"))
                )  
                page_number += 1
            else:
                print("[INFO] No more pages to scrape. Exiting...")
                break  # Break only if no next page

        except Exception as e:
            print(f"[INFO] No 'Next' button found. Exiting... Error: {e}")
            break  # Break if there's an error finding the next button

    print("[INFO] Scraping complete. Closing browser.")
    driver.quit()

if __name__ == "__main__":
    main()
