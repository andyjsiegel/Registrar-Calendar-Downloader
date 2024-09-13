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

def handle_options(options: list):
    print("Available options:")
    try: 
        options.pop(0)
    except IndexError:
        print("Selenium encountered an error. Please try running the program again.\n\nINFO: Sometimes the elements list is an empty list [] when Selenium picks them up and then the program will crash.\nI tried to mitigate this with the time.sleep() but it works inconsistently.")
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

def clean_text(text: str):
    text1 = re.sub(r'\s+', ' ', text).strip()
    spaced_text = re.sub(r'(?<!^)(?<!\s)([A-Z]+)([A-Z][a-z])', r'\1\n\2', text1)
    spaced_text = re.sub(r'([a-z])([A-Z])', r'\1\n\2', spaced_text)
    return spaced_text

def select_element(element_name: str):
    select = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.NAME, element_name))
    )
    select = Select(select)
    options = select.options
    chosen_option = handle_options(options)
    select.select_by_visible_text(chosen_option.text)
    return chosen_option.text

options = webdriver.ChromeOptions()
options.add_argument('headless')  # Run in headless mode
driver = webdriver.Chrome(options=options)

driver.get('https://registrar.arizona.edu/dates-and-deadlines')

try:
    file_name = ""
    class_dates = select_element("dates_dropdown_0")
    file_name += class_dates.replace(' ', '_').replace('-','_').lower()  + '_'
    
    time.sleep(1) 

    selected_element = select_element("dates_dropdown_1")
    file_name += selected_element.replace(' ', '_').lower()  + '_' 
    
    time.sleep(1)

    selected_element = select_element("dates_dropdown_2")
    file_name += selected_element.replace(' ', '_').lower()  + '_'

    time.sleep(1)

    selected_element = select_element("dates_dropdown_3")

    if class_dates == 'Standard Class Dates':
        file_name += selected_element.replace(' ', '_').lower()
    else:
        file_name += selected_element.split('-')[1].strip().replace(',', '').replace(' ','_').lower()

        time.sleep(1)

        selected_element = select_element("dates_dropdown_4")
        file_name += '_' + selected_element.split('-')[1].strip().replace(' ', '_').lower()  + '_'

        time.sleep(1)

        selected_element = select_element("dates_dropdown_5")
        file_name += selected_element.replace(' ', '_').lower()

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
        event.make_all_day()
        
        # Add the event to the calendar
        calendar.events.add(event)

    # Write the calendar to an .ics file
    with open(f'{file_name}.ics', 'w') as f:
        f.writelines(calendar.serialize_iter())


    print(f'\n{file_name}.ics file generated.\n\nyou can now import it to your calendar app of choice!')


except TimeoutException:
    print('Timed out waiting for the select elements to be clickable')

