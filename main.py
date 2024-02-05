import json
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

# Load text_to_type values from config.json
with open('config.json', 'r') as f:
    config = json.load(f)
    locations = config.get('locations', [])

# Set options for headless mode
options = webdriver.ChromeOptions()
# options.add_argument("--headless")
options.add_argument("--window-size=1920,1200")
driver = webdriver.Chrome(options)
# Navigate to the URL
baseURL = 'https://member.dietitiansaustralia.org.au/Portal/Portal/Search-Directories/Find-a-Dietitian.aspx'
driver.get(baseURL)
# Iterate through each text_to_type value
for text_to_type in locations:


    # Locate the input field by its id using By.ID
    input_field = driver.find_element(By.ID, "txtLocationSearchField")

    # Clear existing text (if any)
    input_field.clear()

    # Type your desired text into the input field with a delay between characters
    for char in text_to_type:
        input_field.send_keys(char)
        time.sleep(0.01)  # Adjust the sleep duration as needed

    # Press the down arrow key
    input_field.send_keys(Keys.ARROW_DOWN)

    # Press Enter
    input_field.send_keys(Keys.ENTER)

    # Locate the mat-select element with id "mat-select-0"
    mat_select_element = driver.find_element(By.ID, "mat-select-0")

    # Click on the mat-select to open the dropdown
    mat_select_element.click()

    # Locate the option you want to select within the dropdown (e.g., option 5)
    option_5 = driver.find_element(By.ID, "mat-option-5")

    # Use ActionChains to move to the option and click on it
    action = ActionChains(driver)
    action.move_to_element(option_5).click().perform()

    time.sleep(4)

    # Locate and click the button with id "pseudoSearchbtn"
    search_button = driver.find_element(By.ID, "pseudoSearchbtn")
    search_button.click()

    time.sleep(14)

    # Extract the total number of items
    total_items_text = driver.find_element(By.CSS_SELECTOR, '.mat-paginator-range-label').text
    total_items = int(total_items_text.split('of')[-1].strip())

    # Calculate the number of pages
    pages = (total_items // 21) + (1 if total_items % 21 > 0 else 0)

    print(f"Processing {text_to_type}...")

    # Create lists to store data
    data = {'Name': [], 'Email': [], 'Phone': []}
    index = 0

    # Iterate through pages
    for page in range(pages):
        # Extract and print information from the initial content
        initial_soup = BeautifulSoup(driver.page_source, 'html.parser')
        initial_card_inner_elements = initial_soup.find_all('div', class_='card-inner')

        for card_inner in initial_card_inner_elements:
            name = card_inner.find('h4').text.strip()
            email = card_inner.find('a', href=lambda x: x and 'mailto' in x).text.strip() if card_inner.find('a', href=lambda x: x and 'mailto' in x) else "N/A"
            phone = card_inner.find('a', href=lambda x: x and 'tel' in x).text.strip() if card_inner.find('a', href=lambda x: x and 'tel' in x) else "N/A"

            # Append data to lists
            data['Name'].append(name)
            data['Email'].append(email)
            data['Phone'].append(phone)

            # Print information
            print(f"Page: {page + 1}, Index: {index + 1}")
            print(f"Name: {name} -- Email: {email} -- Phone: {phone}")
            print("------------------")
            index = index + 1

        # Locate the next page button by its CSS selector
        next_page_button = driver.find_element(By.CSS_SELECTOR, ".mat-paginator-navigation-next")

        # Click the next page button
        next_page_button.click()

        # Wait for the new content to load using WebDriverWait
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'card-inner')))
        time.sleep(3)

    # Create a DataFrame from the collected data
    df = pd.DataFrame(data)

    # Print DataFrame
    print(df)

    # Save the DataFrame to an Excel file
    output_filename = f"{text_to_type.replace(' ', '_')}_data.xlsx"
    df.to_excel(output_filename, index=False)

    print(f"Excel file saved as {output_filename}")
    time.sleep(5)

# Close the browser
driver.quit()
