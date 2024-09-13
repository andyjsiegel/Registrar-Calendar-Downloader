from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from ics import Calendar, Event
from datetime import datetime
import re
import time
import sys

def handle_options(options):
    print("Available options:")
    try: 
        options.pop(0)
    except IndexError:
        print("Selenium encountered an error. Please try running the program again.")
        sys.exit(1)
    for i, option in enumerate(options):
        print(f"{i+1}. {option.text}")

    # Ask the user to choose an option
    while True:
        choice = input("Enter the number of your chosen option: ")
        if choice.isdigit() and 1 <= int(choice) <= len(options):
            chosen_option = options[int(choice) - 1]
            break
        else:
            print("Invalid choice. Please try again.")

    # Print the chosen option
    print(f"You chose: {chosen_option.text}")
    return chosen_option

def clean_text(text):
    text1 = re.sub(r'\s+', ' ', text).strip()
    spaced_text = re.sub(r'(?<!^)(?<!\s)([A-Z]+)([A-Z][a-z])', r'\1\n\2', text1)
    spaced_text = re.sub(r'([a-z])([A-Z])', r'\1\n\2', spaced_text)
    return spaced_text

# Set up the webdriver
options = webdriver.ChromeOptions()
options.add_argument('headless')  # Run in headless mode
driver = webdriver.Chrome(options=options)

# Navigate to the website
driver.get('https://registrar.arizona.edu/dates-and-deadlines')

try:
    file_name = ""
    # Wait for the first select element to be clickable
    select1 = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.NAME, 'dates_dropdown_0'))
    )
    select1 = Select(select1)
    options = select1.options
    chosen_option = handle_options(options)
    class_dates = chosen_option.text
    select1.select_by_visible_text(class_dates)
    file_name += class_dates.replace(' ', '_').replace('-','_').lower()  + '_'
    
    time.sleep(1)
    select2 = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.NAME, 'dates_dropdown_1'))
    )
    select2 = Select(select2)
    options = select2.options
    chosen_option = handle_options(options)
    select2.select_by_visible_text(chosen_option.text)
    file_name += chosen_option.text.replace(' ', '_').lower()  + '_' 
    
    time.sleep(1)
    select3 = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.NAME, 'dates_dropdown_2'))
    )
    select3 = Select(select3)
    options = select3.options
    chosen_option = handle_options(options)
    select3.select_by_visible_text(chosen_option.text)
    file_name += chosen_option.text.replace(' ', '_').lower()  + '_'

    time.sleep(1)
    select4 = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.NAME, 'dates_dropdown_3'))
    )

    select4 = Select(select4)
    options = select4.options
    chosen_option = handle_options(options)
    select4.select_by_visible_text(chosen_option.text)
    if class_dates == 'Standard Class Dates':
        file_name += chosen_option.text.replace(' ', '_').lower()
    else:
        file_name += chosen_option.text.split('-')[1].strip().replace(',', '').replace(' ','_').lower()

    if class_dates == "Non-Standard Class Dates":
        time.sleep(1)
        select5 = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.NAME, 'dates_dropdown_4'))
        )
        select5 = Select(select5)
        options = select5.options
        chosen_option = handle_options(options)
        select5.select_by_visible_text(chosen_option.text)
        file_name += '_' + chosen_option.text.split('-')[1].strip().replace(' ', '_').lower()  + '_'

        time.sleep(1)
        select6 = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.NAME, 'dates_dropdown_5'))
        )
        select6 = Select(select6)
        options = select6.options
        chosen_option = handle_options(options)
        select6.select_by_visible_text(chosen_option.text)
        file_name += chosen_option.text.replace(' ', '_').lower()


    # keep driver open long enough to render all elements for bs4
    time.sleep(1)

    soup = BeautifulSoup(driver.page_source, 'html.parser')

    dates_table = soup.find('table', {'id': 'dates-table'})
 
    boxes = dates_table.find_all('td')

    td_texts = [td.get_text() for td in boxes]
    # print(td_texts)
    dates_dict = {td_texts[i]: clean_text(td_texts[i + 1]) for i in range(0, len(td_texts), 2)}

    calendar = Calendar()
    for date_str, event_description in dates_dict.items():
        # Parse the date string into a datetime object
        date = datetime.strptime(date_str, "%m/%d/%y")
        
        # Create a new event
        event = Event()
        event_parts = event_description.split('\n', 1)
        event.name = event_parts[0]
        event.description = event_parts[1] if len(event_parts) > 1 else ''
        event.begin = date
        event.make_all_day()  # Optional: set as all-day event
        
        # Add the event to the calendar
        calendar.events.add(event)

    # Write the calendar to an .ics file
    with open(f'{file_name}.ics', 'w') as f:
        f.writelines(calendar.serialize_iter())


    print(f'\n{file_name}.ics file generated.\n\nyou can now import it to your calendar app of choice!')


except TimeoutException:
    print('Timed out waiting for the select elements to be clickable')

