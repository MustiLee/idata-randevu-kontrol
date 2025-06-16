#!/usr/bin/env python3
"""Test script to understand the verification page structure"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import re

def test_verification_page():
    """Test and analyze the verification page"""
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
        
        # Save screenshot
        driver.save_screenshot("verification_page.png")
        print("\nScreenshot saved as verification_page.png")
        
        # Look for any 6-digit numbers on the page
        print("\nSearching for 6-digit numbers in page text...")
        page_text = driver.find_element(By.TAG_NAME, "body").text
        six_digit_pattern = re.findall(r'\b\d{6}\b', page_text)
        if six_digit_pattern:
            print(f"Found 6-digit numbers: {six_digit_pattern}")
        else:
            print("No 6-digit numbers found in visible text")
        
        # Check page source for 6-digit numbers
        print("\nSearching for 6-digit numbers in page source...")
        page_source = driver.page_source
        source_patterns = re.findall(r'>(\d{6})<', page_source)
        if source_patterns:
            print(f"Found 6-digit numbers in HTML: {source_patterns}")
        
        # Look for specific elements that might contain the code
        print("\nSearching for elements that might contain verification code...")
        possible_containers = [
            "div", "span", "p", "strong", "b", "label", "h1", "h2", "h3", "h4", "h5", "h6"
        ]
        
        for tag in possible_containers:
            elements = driver.find_elements(By.TAG_NAME, tag)
            for elem in elements:
                text = elem.text.strip()
                if re.search(r'\d{6}', text):
                    print(f"\nFound in <{tag}>: {text}")
                    print(f"  - Class: {elem.get_attribute('class')}")
                    print(f"  - ID: {elem.get_attribute('id')}")
        
        # Check for images that might contain the code
        print("\nChecking for images...")
        images = driver.find_elements(By.TAG_NAME, "img")
        for i, img in enumerate(images):
            alt = img.get_attribute('alt')
            src = img.get_attribute('src')
            if alt or 'captcha' in str(src).lower() or 'code' in str(src).lower():
                print(f"\nImage {i+1}:")
                print(f"  - Alt: {alt}")
                print(f"  - Src: {src[:100]}...")
        
        # Check the input field
        print("\nChecking input fields...")
        inputs = driver.find_elements(By.TAG_NAME, "input")
        for inp in inputs:
            if inp.get_attribute('type') != 'hidden':
                print(f"\nInput field:")
                print(f"  - Name: {inp.get_attribute('name')}")
                print(f"  - Placeholder: {inp.get_attribute('placeholder')}")
                print(f"  - Type: {inp.get_attribute('type')}")
                print(f"  - Value: {inp.get_attribute('value')}")
        
        # Save page source for analysis
        with open("page_source.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print("\nPage source saved as page_source.html")
        
        print("\nPress Enter to close browser...")
        input()
        
    finally:
        driver.quit()

if __name__ == "__main__":
    test_verification_page()