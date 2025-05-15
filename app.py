import csv
import json
import os
import sys
import time
import random
from datetime import datetime
from io import BytesIO
from string import Formatter

import openpyxl
import requests
from PIL import Image
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
import undetected_chromedriver as uc
from colorama import Fore, Style

# Logo and welcome message
def display_welcome():
    logo = """
███████╗██████╗     ███╗   ███╗ █████╗ ██████╗ ██╗  ██╗███████╗████████╗██████╗ ██╗      █████╗  ██████╗███████╗
██╔════╝██╔══██╗    ████╗ ████║██╔══██╗██╔══██╗██║ ██╔╝██╔════╝╚══██╔══╝██╔══██╗██║     ██╔══██╗██╔════╝██╔════╝
█████╗  ██████╔╝    ██╔████╔██║███████║██████╔╝█████╔╝ █████╗     ██║   ██████╔╝██║     ███████║██║     █████╗  
██╔══╝  ██╔══██╗    ██║╚██╔╝██║██╔══██║██╔══██╗██╔═██╗ ██╔══╝     ██║   ██╔═══╝ ██║     ██╔══██║██║     ██╔══╝  
██║     ██████╔╝    ██║ ╚═╝ ██║██║  ██║██║  ██║██║  ██╗███████╗   ██║   ██║     ███████╗██║  ██║╚██████╗███████╗
╚═╝     ╚═════╝     ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝   ╚═╝   ╚═╝     ╚══════╝╚═╝  ╚═╝ ╚═════╝╚══════╝
                                                                                                                 
    """
    print(f"{Fore.CYAN}{logo}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}=== Facebook Marketplace Auto Lister ==={Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Version: 1.0{Style.RESET_ALL}")
    
    # Features
    print(f"\n{Fore.BLUE}Key Features:{Style.RESET_ALL}")
    print(f"{Fore.WHITE}• Automated vehicle listing on Facebook Marketplace")
    print(f"• Anti-detection technology to bypass Facebook's bot detection")
    print(f"• Human-like interaction patterns")
    print(f"• Bulk listing from Excel spreadsheet")
    print(f"• Image upload support")
    print(f"• Automated form filling for vehicle details{Style.RESET_ALL}")
    
    # Process
    print(f"\n{Fore.BLUE}Process:{Style.RESET_ALL}")
    print(f"{Fore.WHITE}1. Login to Facebook (solve CAPTCHA if prompted)")
    print(f"2. Navigate to the specified Facebook group")
    print(f"3. Create vehicle listings for each row in Excel file")
    print(f"4. Fill in vehicle details (type, year, make, model, etc.)")
    print(f"5. Upload images and complete the listing{Style.RESET_ALL}")
    
    # Excel Instructions
    print(f"\n{Fore.BLUE}Excel File Instructions:{Style.RESET_ALL}")
    print(f"{Fore.WHITE}The script uses products.xlsx file with the following columns:")
    print(f"• images: Comma-separated image filenames from the 'images' folder")
    print(f"• vehicle_type: Type of vehicle (Car/Truck, Motorcycle, etc.)")
    print(f"• year: Vehicle year")
    print(f"• make: Vehicle make/brand")
    print(f"• model: Vehicle model")
    print(f"• mileage: Vehicle mileage")
    print(f"• price: Listing price")
    print(f"• fuel_type: Fuel type (Gasoline, Diesel, etc.)")
    print(f"• transmission: Transmission type")
    print(f"• body_style: Body style (Sedan, SUV, etc.)")
    print(f"• exterior_color: Exterior color")
    print(f"• interior_color: Interior color")
    print(f"• condition: Condition of the vehicle (New, Used, etc.)")
    print(f"• description: Detailed description of the vehicle{Style.RESET_ALL}")
    
    print(f"\n{Fore.YELLOW}To modify listings, simply edit the products.xlsx file.{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Make sure your images are in the 'images' folder.{Style.RESET_ALL}")
    
    print(f"\n{Fore.GREEN}Starting script...{Style.RESET_ALL}")
    print("-" * 80)

# Helper functions (from Helpers.py)
def read_json(file):
    file_name = file if file.endswith('.json') else file + '.json'
    with open(file_name, 'r') as f:
        return json.load(f)
    
def write_json(file, content):
    file_name = file if file.endswith('.json') else file + '.json'
    with open(file_name, 'w') as f:
        try:
            json.dump(content, f)
            return True
        except:
            return False
        
def fstring_keys(fstring):
    keys = [part[1] for part in Formatter().parse(fstring) if part[1] is not None]
    return keys

def format_xpath(fstring, vals):
    fstring_len = len(fstring_keys(fstring))
    if isinstance(vals, (str, list, tuple)):
        if isinstance(vals, str) or len(vals) < fstring_len:
            list_of_vals = [vals] if isinstance(vals, str) else [*vals]
            difference = fstring_len - len(list_of_vals)
            values = list_of_vals + ['' for _ in range(difference)]
        elif len(vals) > fstring_len:
            values = [*vals][:fstring_len]
        else:
            values = [*vals]
        return fstring.format(*values)
    else:
        raise TypeError('Must be a string, a list or a tuple')

def log(msg, type=None):
    if type == 'main':
        print(f"{Fore.BLUE}{msg}{Style.RESET_ALL}")
    elif type == 'sub':
        print(f"{Fore.CYAN}{msg}{Style.RESET_ALL}")
    elif type == 'success':
        print(f"{Fore.GREEN}{msg}{Style.RESET_ALL}")
    elif type == 'failure':
        print(f"{Fore.RED}{msg}{Style.RESET_ALL}")
    else:
        print(msg)

# Element class (from Element.py)
class Element:
    def __init__(self, driver, name, values=None):
        self.driver = driver
        self.name = name
        self.values = values
        self.pathes = read_json('elements')
    
    @property
    def xpath(self):
        xpath_format = self.pathes[self.name]['xpath']
        defaults = self.defaults
        return format_xpath(xpath_format, self.values) if self.values else format_xpath(xpath_format, defaults)
    
    @property
    def defaults(self):
        return self.pathes[self.name]['defaults']
    
    @property
    def element(self):
        xpath = self.xpath
        element_type = self.pathes[self.name]['type']
        if element_type == 'button':
            element = WebDriverWait(self.driver, 30).until(
                EC.element_to_be_clickable((By.XPATH, xpath))
            )
        else:
            element = self.driver.find_element(By.XPATH, xpath)
        return element

# Item class (from Lister.py)
class Item:
    def __init__(self, driver, item):
        self.driver = driver
        self.item = item
        
    def upload_images(self):
        try:
            log('Uploading Images', 'main')
            image_upload = Element(self.driver, 'post_image').element
            self.driver.execute_script("document.querySelector('%s').classList = []" % Element(self.driver, 'post_image_css').xpath)
            log('Showing image input ..', 'main')

            # for desktop images
            joined_images_path = ' \n '.join([os.path.abspath('images/%s' % image['file']) for image in self.item['images']][:10])

            print(f"Images Path : {joined_images_path}")
            log('sending images ..', 'main')
            image_upload.send_keys(joined_images_path)
            log('Uploaded Images Successfully .', 'success')
            return True
        except:
            log('FAILED TO UPLOAD IMAGE', 'failure')
            return False
            

    def enter_vehicle_make(self):
        try:
            log('Entering The Vehicle Make', 'main')
            title_input = Element(self.driver, 'vehicle_make').element
            title_input.click()
            values = self.item['vehicle_make'] if 'vehicle_make' in self.item.keys() and self.item['vehicle_make'] else None
            category_dropdown_option = Element(self.driver, 'vehicle_make_option', values).element
            print(Element(self.driver, 'vehicle_make_option', values).xpath)
            print(Element(self.driver, 'vehicle_make_option', values).xpath)
            print(Element(self.driver, 'vehicle_make_option', values).xpath)
            print(Element(self.driver, 'vehicle_make_option', values).xpath)
            print(Element(self.driver, 'vehicle_make_option', values).xpath)
            log('clicking The vehicle type Dropdown ..', 'sub')
            category_dropdown_option.click()
        except:
            log('FAILED TO ENTER THE Make', 'failure')
            return False

    def enter_vehicle_model(self):
        try:
            log('Entering The Vehicle Modal', 'main')
            title_input = Element(self.driver, 'vehicle_model').element
            title_input.clear()
            title_input.send_keys(self.item['model'])
            log('Entered vehicle modal Successfully .', 'success')
            return True
        except:
            log('FAILED TO ENTER THE vehicle_modal', 'failure')
            return False

    def enter_vehicle_mileage(self):
        try:
            log('Entering The Vehicle Mileage', 'main')
            title_input = Element(self.driver, 'vehicle_mileage').element
            title_input.clear()
            title_input.send_keys(self.item['mileage'])
            log('Entered vehicle mileage Successfully .', 'success')
            return True
        except Exception as e:
            log(f'FAILED TO ENTER THE vehicle mileage\n{e}', 'failure')
            return False
            
    def enter_price(self):
        try:
            log('Entering The Price', 'main')
            price_input = Element(self.driver, 'post_price').element
            price_input.clear()
            price_input.send_keys(self.item['price'])
            log('Entered Price Successfully .', 'success')
            return True
        except:
            log('FAILED TO ENTER THE PRICE', 'failure')
            return False

    
    def choose_condition(self):
        try:
            log('Choosing The Condition', 'main')
            condition_dropdown = Element(self.driver, 'post_condition').element
            condition_dropdown.click()
            log('clicking The Condition Dropdown ..', 'sub')
        
            values = self.item['condition'] if 'condition'in self.item.keys() and self.item['condition'] else None
            condition_dropdown_option = Element(self.driver, 'post_condition_option', values).element
            condition_dropdown_option.click()
            log('Condition Chosen Successfully .', 'success')
            return True
        except:
            log('FAILED TO CHOOSE THE CATEGORY', 'failure')
            return False

    def choose_vehicle_type(self):
        try:
            log('Choosing The Vehicle Type', 'main')
            category_dropdown = Element(self.driver, 'vehicle_type').element
            category_dropdown.click()

            values = self.item['vehicle_type'] if 'vehicle_type' in self.item.keys() and self.item['vehicle_type'] else None
            category_dropdown_option = Element(self.driver, 'vehicle_type_option', values).element
            print(Element(self.driver, 'vehicle_type_option', values).xpath)
            print(Element(self.driver, 'vehicle_type_option', values).xpath)
            print(Element(self.driver, 'vehicle_type_option', values).xpath)
            print(Element(self.driver, 'vehicle_type_option', values).xpath)
            print(Element(self.driver, 'vehicle_type_option', values).xpath)
            log('clicking The vehicle type Dropdown ..', 'sub')
            category_dropdown_option.click()

            log('vehicle type Chosen Successfully .', 'success')
            return True
        except:
            log('FAILED TO CHOOSE THE vehicle type', 'failure')
            return False
        

    def choose_vehicle_body_style(self):
        try:
            log('Choosing The Vehicle Body Style', 'main')
            category_dropdown = Element(self.driver, 'vehicle_body_style').element
            category_dropdown.click()

            values = self.item['body_style'] if 'body_style' in self.item.keys() and self.item['body_style'] else None
            category_dropdown_option = Element(self.driver, 'vehicle_body_style_option', values).element
            print(Element(self.driver, 'vehicle_body_style_option', values).xpath)
            print(Element(self.driver, 'vehicle_body_style_option', values).xpath)
            print(Element(self.driver, 'vehicle_body_style_option', values).xpath)
            print(Element(self.driver, 'vehicle_body_style_option', values).xpath)
            print(Element(self.driver, 'vehicle_body_style_option', values).xpath)
            log('clicking The vehicle Body Style Dropdown ..', 'sub')
            category_dropdown_option.click()

            log('vehicle body style Chosen Successfully .', 'success')
            return True
        except:
            log('FAILED TO CHOOSE THE vehicle body style', 'failure')
            return False
    
    def choose_exterior_color(self):
        try:
            log('Choosing The Exterior Color', 'main')
            category_dropdown = Element(self.driver, 'exterior_color').element
            category_dropdown.click()

            values = self.item['exterior_color'] if 'exterior_color' in self.item.keys() and self.item['exterior_color'] else None
            category_dropdown_option = Element(self.driver, 'exterior_color_option', values).element
            print(Element(self.driver, 'exterior_color_option', values).xpath)
            print(Element(self.driver, 'exterior_color_option', values).xpath)
            print(Element(self.driver, 'exterior_color_option', values).xpath)
            print(Element(self.driver, 'exterior_color_option', values).xpath)
            print(Element(self.driver, 'exterior_color_option', values).xpath)
            log('clicking The vehicle Exterior Color Dropdown ..', 'sub')
            category_dropdown_option.click()

            log('Vehicle Exterior Color Chosen Successfully .', 'success')
            return True
        except:
            log('FAILED TO CHOOSE The Exterior Color', 'failure')
            return False
        
    
    def choose_interior_color(self):
        try:
            log('Choosing The Interior Color', 'main')
            category_dropdown = Element(self.driver, 'interior_color').element
            category_dropdown.click()

            values = self.item['interior_color'] if 'interior_color' in self.item.keys() and self.item['interior_color'] else None
            category_dropdown_option = Element(self.driver, 'interior_color_option', values).element
            print(Element(self.driver, 'interior_color_option', values).xpath)
            print(Element(self.driver, 'interior_color_option', values).xpath)
            print(Element(self.driver, 'interior_color_option', values).xpath)
            print(Element(self.driver, 'interior_color_option', values).xpath)
            print(Element(self.driver, 'interior_color_option', values).xpath)  
            log('clicking The interior color Dropdown ..', 'sub')
            category_dropdown_option.click()

            log('Vehicle Interior Color Chosen Successfully .', 'success')
            return True
        except:
            log('FAILED TO CHOOSE The Vehicle Interior Color', 'failure')
            return False


    def choose_vehicle_year(self):
        try:
            log('Choosing The Vehicle Year', 'main')
            category_dropdown = Element(self.driver, 'year').element
            category_dropdown.click()

            values = str(self.item['year']) if 'year' in self.item.keys() and self.item['year'] else None
            category_dropdown_option = Element(self.driver, 'year_option', values).element
            print(Element(self.driver, 'year_option', values).xpath)
            print(Element(self.driver, 'year_option', values).xpath)
            print(Element(self.driver, 'year_option', values).xpath)
            print(Element(self.driver, 'year_option', values).xpath)
            print(Element(self.driver, 'year_option', values).xpath)
            log('clicking The Year Dropdown ..', 'sub')
            category_dropdown_option.click()

            log('Year Chosen Successfully .', 'success')
            return True
        except Exception as e:
            log(f'FAILED TO CHOOSE Year\n{e}', 'failure')
            return False

    def choose_vehicle_fuel_type(self):
        try:
            log('Choosing The Vehicle Fuel Type', 'main')
            category_dropdown = Element(self.driver, 'fuel_type').element
            category_dropdown.click()

            values = self.item['fuel_type'] if 'fuel_type' in self.item.keys() and self.item['fuel_type'] else None
            category_dropdown_option = Element(self.driver, 'fuel_type_option', values).element
            print(Element(self.driver, 'fuel_type_option', values).xpath)
            print(Element(self.driver, 'fuel_type_option', values).xpath)
            print(Element(self.driver, 'fuel_type_option', values).xpath)
            print(Element(self.driver, 'fuel_type_option', values).xpath)
            print(Element(self.driver, 'fuel_type_option', values).xpath)
            log('clicking The fuel type Dropdown ..', 'sub')
            category_dropdown_option.click()

            log('fuel type Chosen Successfully .', 'success')
            return True
        except:
            log('FAILED TO CHOOSE fuel type', 'failure')
            return False

    def choose_vehicle_transmission(self):
        try:
            log('Choosing The Vehicle Transmission', 'main')
            category_dropdown = Element(self.driver, 'transmission').element
            category_dropdown.click()

            values = self.item['transmission'] if 'transmission' in self.item.keys() and self.item['transmission'] else None
            category_dropdown_option = Element(self.driver, 'transmission_type_option', values).element
            print(Element(self.driver, 'transmission_option', values).xpath)
            print(Element(self.driver, 'transmission_option', values).xpath)
            print(Element(self.driver, 'transmission_option', values).xpath)
            print(Element(self.driver, 'transmission_option', values).xpath)
            print(Element(self.driver, 'transmission_option', values).xpath)
            log('clicking The transmission Dropdown ..', 'sub')
            category_dropdown_option.click()

            log('transmission Chosen Successfully .', 'success')
            return True
        except:
            log('FAILED TO CHOOSE transmission', 'failure')
            return False
            
    def enter_description(self):
        try:
            log('Entering The Description', 'main')
            description_input = Element(self.driver, 'post_description').element
            description_input.clear()
            description_input.send_keys(self.item['description'])
            log('Entered Description Successfully .', 'success')
            return True
        except:
            log('FAILED TO ENTER THE DESCRIPTION', 'failure')
            return False
            
            
    def choose_location(self):
        try:
            log('Choosing The Location', 'main')
            location_input = Element(self.driver, 'post_location').element
            location_input.clear()
            location_input.send_keys(self.item['location'])
            log('Entered Location Successfully .', 'sub')
            time.sleep(1)
            
            location_option = Element(self.driver, 'post_location_option', self.item['location']).element
            location_option.click()
            
            log('Location Chosen Successfully .', 'success')
            return True
        except:
            log('FAILED TO CHOOSE THE LOCATION', 'failure')
            return False
            
            
    def click_next(self):
        try:
            log('Clicking Next', 'main')
            next_button = Element(self.driver, 'post_next_button').element
            next_button.click()
            log('Clicked Next Successfully .', 'success')
            return True
        except:
            log('FAILED TO CLICK NEXT', 'failure')
            return False
            
    def click_publish(self):
        try:
            log('Clicking Publish', 'main')
            publish_button = Element(self.driver, 'post_publish_button').element
            publish_button.click()
            log('Clicked Publish Successfully .', 'success')
            return True
        except:
            log('FAILED TO CLICK PUBLISH', 'failure')
            return False
            
    def click_button(self, button):
        button.click()

# Lister class (from Lister.py)
class Lister:
    def __init__(self):
        self.sleep_time = random.uniform(0.5, 2.5)
        self.driver = self.get_driver_uc()  # Changed to use undetected_chromedriver by default

    def get_driver(self):
        ops = webdriver.ChromeOptions()
        # ops.add_argument('--headless')
        # ops.add_argument(f"--proxy-server={proxy}")

        ops.add_experimental_option("detach", True)

        prefs = {"credentials_enable_service": False,
                 "profile.password_manager_enabled": False}
        ops.add_experimental_option("prefs", prefs)
        # Adding argument to disable the AutomationControlled flag
        ops.add_argument("--disable-blink-features=AutomationControlled")

        # to open specific profile
        # ops.add_argument("--user-data-dir=/Users/apple/Library/Application Support/Google/Chrome")
        # ops.add_argument("--profile-directory=Profile 18")

        # Exclude the collection of enable-automation switches
        # to remove chrome is being controlled by automated software
        ops.add_experimental_option("excludeSwitches", ["enable-automation"])

        # Turn-off userAutomationExtension
        ops.add_experimental_option("useAutomationExtension", False)

        headers = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 " \
                  "(KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
        ops.add_argument('--disable-notifications')
        ops.add_argument("user-agent=" + headers)
        # service = Service(executable_path='/Users/apple/Desktop/chromedriver')
        service = Service()
        driver = webdriver.Chrome(service=service, options=ops)
        driver.maximize_window()
        driver.implicitly_wait(3)
        return driver

    def get_driver_uc(self):
        # Configure undetected_chromedriver for maximum stealth
        ops = uc.ChromeOptions()
        
        # Set a realistic user agent
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        ops.add_argument(f"--user-agent={user_agent}")
        
        # Disable automation flags
        ops.add_argument("--disable-blink-features=AutomationControlled")
        
        # Disable notifications
        ops.add_argument("--disable-notifications")
        
        # Disable password saving prompts
        prefs = {
            "credentials_enable_service": False,
            "profile.password_manager_enabled": False,
            "profile.default_content_setting_values.notifications": 2
        }
        ops.add_experimental_option("prefs", prefs)
        
        # Create a new undetected Chrome instance
        driver = uc.Chrome(
            options=ops,
            use_subprocess=True,
            driver_executable_path=None,  # Let it find the driver automatically
            version_main=None,  # Auto-detect Chrome version
        )
        
        # Additional stealth settings
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        # Set window size to a common resolution
        driver.set_window_size(1366, 768)
        
        # Set normal page load strategy
        driver.implicitly_wait(10)
        
        return driver

    def read_accounts(self):
        return read_json('accounts')['accounts']

    def login_with_cookies(self, file):
        with open(file, "r") as f:
            dict_reader = csv.DictReader(f)
            cookies = list(dict_reader)
            for c in cookies:
                self.driver.add_cookie(c)
            print("cookies are added...")
            self.driver.refresh()
            print("bot refreshed the page...")
            
    def login(self, account_id=""):
        registered_accounts = self.read_accounts()
        print(f"Reg Account : {registered_accounts}")

        account_info = registered_accounts

        # Clear cookies and cache before login attempt
        self.driver.execute_script('window.localStorage.clear();')
        self.driver.execute_script('window.sessionStorage.clear();')
        self.driver.delete_all_cookies()
        
        # Random delay before navigating to login page (2-5 seconds)
        time.sleep(random.uniform(2, 5))
        
        # Navigate to Facebook with randomized timing
        self.driver.get('https://www.facebook.com/')
        
        # Wait for page to load with some randomness
        time.sleep(random.uniform(3, 6))
        
        # Try to find login elements on the main page first
        try:
            # Random delay before starting to type (1-3 seconds)
            time.sleep(random.uniform(1, 3))

            # entering email with human-like typing
            log('Entering email...', 'main')
            email_input = self.driver.find_element(By.ID, "email")
            email_input.clear()
            email = account_info[0]['email']
            for char in email:
                email_input.send_keys(char)
                # Random delay between keystrokes (50-200ms)
                time.sleep(random.uniform(0.05, 0.2))
            
            # Random pause between email and password (0.5-2 seconds)
            time.sleep(random.uniform(0.5, 2))

            # entering password with human-like typing
            log('Entering password...', 'main')
            password_input = self.driver.find_element(By.ID, "pass")
            password_input.clear()
            password = account_info[0]['password']
            for char in password:
                password_input.send_keys(char)
                # Random delay between keystrokes (50-200ms)
                time.sleep(random.uniform(0.05, 0.2))
            
            # Random pause before clicking login button (0.7-2.5 seconds)
            time.sleep(random.uniform(0.7, 2.5))

            # Submitting - find login button by XPath to be more reliable
            log('Clicking login button...', 'main')
            login_button = self.driver.find_element(By.XPATH, "//button[@name='login']")
            
            # Move mouse to button with random offset before clicking
            action = webdriver.ActionChains(self.driver)
            action.move_to_element_with_offset(login_button, 
                                             random.randint(5, 10), 
                                             random.randint(5, 10)).pause(0.5).click().perform()
            
        except Exception as e:
            log(f"Error during login attempt: {e}", 'failure')
            # If main page login fails, try the dedicated login page
            self.driver.get('https://www.facebook.com/login')
            time.sleep(random.uniform(2, 4))
            
            # Try using the Element class as fallback
            email_input = Element(self.driver, 'login_email').element
            email_input.clear()
            email = account_info[0]['email']
            for char in email:
                email_input.send_keys(char)
                time.sleep(random.uniform(0.05, 0.2))
            
            time.sleep(random.uniform(0.5, 2))
            
            password_input = Element(self.driver, 'login_password').element
            password_input.clear()
            password = account_info[0]['password']
            for char in password:
                password_input.send_keys(char)
                time.sleep(random.uniform(0.05, 0.2))
            
            time.sleep(random.uniform(0.7, 2.5))
            
            password_button = Element(self.driver, 'login_button').element
            password_button.click()

        input("\n\n----------------------- solve captcha if any and press enter: ")
        
        # After captcha is solved, check for additional security prompts
        try:
            # Check for "This is You?" prompt
            security_buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'Continue') or contains(text(), 'This is Me') or contains(text(), 'Yes')]")
            if security_buttons:
                log('Detected security confirmation prompt, clicking continue...', 'main')
                security_buttons[0].click()
                time.sleep(random.uniform(1, 2))
        except:
            pass

        # Confirm Logged In with longer timeout
        try:
            logged = WebDriverWait(self.driver, 90).until(
                lambda driver: "login" not in driver.current_url and len(driver.find_elements(By.XPATH, "//div[@aria-label='Your profile' or @aria-label='Account']")) > 0
            )
        except:
            logged = "login" not in self.driver.current_url

        if logged:
            log('Logged in Successfully.', 'success')
            # Save cookies for future use
            cookies = self.driver.get_cookies()
            with open('facebook_cookies.json', 'w') as f:
                json.dump(cookies, f)
        else:
            log('Failed To Login.', 'failure')

        return logged

    def login_cookies(self, account_id="", login_cookies_file=""):
        registered_accounts = self.read_accounts()
        # account_info = list(filter(lambda acc: acc['id'] == account_id, registered_accounts))
        # print(f"Account Info : {account_info}")
        # log('Logging in as "%s" ..' % account_info['name'], 'main')

        self.driver.get('https://www.facebook.com/login')

        self.login_with_cookies(login_cookies_file)

        # Confirm Logged In
        logged = WebDriverWait(self.driver, 60).until(
            lambda driver: "login" not in driver.current_url 
        )
        
        if logged:
            log('Logged in Successfully.', 'success')
        else:
            log('Failed To Login.', 'failure')
        
        return logged
    
    def list(self, item):
        # self.driver.get('https://www.facebook.com/marketplace/create/item')

        # vehicle category
        self.driver.get('https://www.facebook.com/groups/haddockequipment')

        time.sleep(5)

        # clicking sell something
        self.driver.find_element(By.XPATH, '//div[@aria-label="Sell Something"]').click()

        time.sleep(5)

        self.driver.find_element(By.XPATH, '//div[@aria-label="Create new listing"]'
                                           '//span[normalize-space()="Vehicle for sale"]').click()

        time.sleep(5)
        
        listing_item = Item(self.driver, item)
        
        listing_item.upload_images()
        time.sleep(self.sleep_time)


        listing_item.choose_vehicle_type()
        time.sleep(self.sleep_time)

        listing_item.choose_vehicle_year()
        time.sleep(self.sleep_time)
        

        listing_item.enter_vehicle_make()
        time.sleep(self.sleep_time)
        
        listing_item.enter_vehicle_model()
        time.sleep(self.sleep_time)
        
        listing_item.enter_vehicle_mileage()
        time.sleep(self.sleep_time)
        
        listing_item.enter_price()
        time.sleep(self.sleep_time)

        listing_item.choose_vehicle_body_style()
        time.sleep(self.sleep_time)

        listing_item.choose_exterior_color()
        time.sleep(self.sleep_time)

        listing_item.choose_interior_color()
        time.sleep(self.sleep_time)
        
        listing_item.choose_vehicle_fuel_type()
        time.sleep(self.sleep_time)
        
        listing_item.choose_vehicle_transmission()
        time.sleep(self.sleep_time)
        
        listing_item.enter_description()
        time.sleep(self.sleep_time)
        
        
        listing_item.click_next()
        time.sleep(self.sleep_time)
        
        listing_item.click_publish()
        time.sleep(10)

    def save_as_draft(self):
        self.driver.get('https://www.facebook.com/marketplace/create/item')
        time.sleep(5)

# Main class (from main.py)
class Main:
    def __init__(self):
        self.products = self.read_excel("products.xlsx")
        self.lister = Lister()

    def read_excel(self, file_path):
        workbook = openpyxl.load_workbook(file_path)
        sheet = workbook.active

        header = [cell.value for cell in sheet[1]]

        data = []
        for row in sheet.iter_rows(min_row=2, values_only=True):
            row_dict = dict(zip(header, row))
            data.append(row_dict)

        workbook.close()
        return data

    def upload_products(self):
        if self.lister.login():
            for product in self.products:
                # self.download_images(product["images"])
                try:
                    images = product["images"].split(",")
                except:
                    print("For more than one images separate the name of each image with comma(,) in excel")
                    sys.exit(0)
                product["images"] = [{"file": image} for image in images if image]
                self.lister.list(product)
                # self.remove_images()
                time.sleep(1)

    def download_images(self, image_url):
        # Download the image from the URL
        response = requests.get(image_url)
        img = Image.open(BytesIO(response.content))

        # Save the image to a local file
        img_path = os.path.join("images", "image1.jpg")
        img.save(img_path)

    def remove_images(self):
        # deleting images
        for image in os.listdir("images"):
            os.remove(os.path.join("images", image))



if __name__ == "__main__":
    display_welcome()
    upload = Main()
    upload.upload_products() 