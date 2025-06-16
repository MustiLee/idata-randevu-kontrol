#!/usr/bin/env python3
"""Test script to debug website structure"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

def test_website():
    """Test website access and structure"""
    options = Options()
    # Run in visible mode for debugging
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    driver = webdriver.Chrome(options=options)
    
    try:
        print("Opening IDATA website...")
        driver.get("https://it-tr-appointment.idata.com.tr/tr")
        
        print("Waiting for page to load...")
        time.sleep(5)
        
        print("Page title:", driver.title)
        print("Current URL:", driver.current_url)
        
        # Try to find captcha elements
        print("\nSearching for captcha elements...")
        possible_selectors = [
            "img[alt*='captcha']",
            "img[src*='captcha']", 
            ".captcha-image",
            "#captcha-image",
            "img[class*='captcha']",
            "div[class*='captcha'] img",
            "img[alt*='güvenlik']",
            "img[alt*='security']"
        ]
        
        for selector in possible_selectors:
            try:
                element = driver.find_element(By.CSS_SELECTOR, selector)
                print(f"✓ Found element with selector: {selector}")
                print(f"  - Tag: {element.tag_name}")
                print(f"  - Alt: {element.get_attribute('alt')}")
                print(f"  - Src: {element.get_attribute('src')[:100]}...")
                break
            except:
                print(f"✗ Not found: {selector}")
        
        # Try to find input fields
        print("\nSearching for input fields...")
        input_selectors = [
            "input[name*='captcha']",
            "input[placeholder*='güvenlik']",
            ".captcha-input",
            "#captcha-input",
            "input[type='text']"
        ]
        
        for selector in input_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    print(f"✓ Found {len(elements)} input(s) with selector: {selector}")
                    for i, elem in enumerate(elements[:3]):
                        print(f"  Input {i+1}:")
                        print(f"    - Name: {elem.get_attribute('name')}")
                        print(f"    - Placeholder: {elem.get_attribute('placeholder')}")
                        print(f"    - Type: {elem.get_attribute('type')}")
            except:
                pass
        
        print("\nPress Enter to close browser...")
        input()
        
    finally:
        driver.quit()

if __name__ == "__main__":
    test_website()