import logging
import time
from typing import Dict, Optional, Tuple
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

from src.captcha.solver import CaptchaSolver

logger = logging.getLogger(__name__)


class AppointmentChecker:
    """Checks for appointment availability on IDATA Turkey website."""
    
    BASE_URL = "https://it-tr-appointment.idata.com.tr"
    MAIN_PAGE = "/tr"
    APPOINTMENT_FORM = "/tr/appointment-form"
    NO_APPOINTMENT_TEXT = "Uygun randevu tarihi bulunmamaktadır"
    
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.driver = None
        self.captcha_solver = CaptchaSolver()
        self.form_data = {
            'residence_city': 'İstanbul',
            'idata_offices': ['Altunizade', 'Gayrettepe'],
            'travel_purpose': 'Tourism',
            'service_type': 'Standard',
            'num_persons': '3'
        }
    
    def _init_driver(self):
        """Initialize Selenium WebDriver."""
        options = Options()
        if self.headless:
            options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        self.driver = webdriver.Chrome(options=options)
        self.driver.implicitly_wait(10)
    
    def _close_driver(self):
        """Close Selenium WebDriver."""
        if self.driver:
            self.driver.quit()
            self.driver = None
    
    def check_appointments(self) -> Tuple[bool, Optional[str]]:
        """
        Check for appointment availability for all configured offices.
        
        Returns:
            Tuple of (is_available, message)
        """
        all_results = []
        available_offices = []
        
        logger.info("=" * 60)
        logger.info("STARTING APPOINTMENT CHECK SESSION")
        logger.info("=" * 60)
        
        for office in self.form_data['idata_offices']:
            logger.info(f"\n🏢 CHECKING OFFICE: {office}")
            logger.info("-" * 40)
            
            try:
                result = self._check_single_office(office)
                all_results.append(result)
                
                if result['available']:
                    available_offices.append(office)
                    logger.info(f"✅ APPOINTMENTS AVAILABLE at {office}!")
                else:
                    logger.info(f"❌ No appointments at {office}")
                    
            except Exception as e:
                logger.error(f"❌ Error checking {office}: {e}")
                all_results.append({
                    'office': office,
                    'available': False,
                    'message': f"Error: {str(e)}",
                    'details': {}
                })
        
        # Summary
        logger.info("\n" + "=" * 60)
        logger.info("SESSION SUMMARY")
        logger.info("=" * 60)
        
        for result in all_results:
            office = result['office']
            status = "✅ AVAILABLE" if result['available'] else "❌ NOT AVAILABLE"
            logger.info(f"{office}: {status}")
            if result['available']:
                logger.info(f"  └─ Details: {result['message']}")
        
        if available_offices:
            return True, f"Appointments available at: {', '.join(available_offices)}"
        else:
            return False, "No appointments available at any office"
    
    def _check_single_office(self, office_name: str) -> dict:
        """
        Check appointments for a single office.
        
        Args:
            office_name: Name of the IDATA office to check
            
        Returns:
            Dictionary with check results
        """
        try:
            self._init_driver()
            
            # Log the inputs for this attempt
            logger.info(f"📋 INPUT PARAMETERS:")
            logger.info(f"   • Residence City: {self.form_data['residence_city']}")
            logger.info(f"   • IDATA Office: {office_name}")
            logger.info(f"   • Travel Purpose: {self.form_data['travel_purpose']}")
            logger.info(f"   • Service Type: {self.form_data['service_type']}")
            logger.info(f"   • Number of Persons: {self.form_data['num_persons']}")
            
            # Navigate to main page
            logger.info("🌐 Navigating to main page...")
            main_url = urljoin(self.BASE_URL, self.MAIN_PAGE)
            self.driver.get(main_url)
            time.sleep(3)
            
            # Solve captcha
            logger.info("🔐 Solving CAPTCHA...")
            if not self._solve_captcha():
                return {
                    'office': office_name,
                    'available': False,
                    'message': "Failed to solve CAPTCHA",
                    'details': {'error': 'CAPTCHA solving failed'}
                }
            
            # Navigate to appointment form
            logger.info("📝 Navigating to appointment form...")
            form_url = urljoin(self.BASE_URL, self.APPOINTMENT_FORM)
            self.driver.get(form_url)
            time.sleep(3)
            
            # Fill appointment form for this specific office
            logger.info(f"✏️  Filling appointment form for {office_name}...")
            if not self._fill_appointment_form_for_office(office_name):
                return {
                    'office': office_name,
                    'available': False,
                    'message': "Failed to fill appointment form",
                    'details': {'error': 'Form filling failed'}
                }
            
            # Check availability
            logger.info("🔍 Checking appointment availability...")
            is_available, message, details = self._check_availability_detailed()
            
            # Log the result
            logger.info(f"📊 RESULT FOR {office_name}:")
            logger.info(f"   • Status: {'AVAILABLE' if is_available else 'NOT AVAILABLE'}")
            logger.info(f"   • Message: {message}")
            if details:
                for key, value in details.items():
                    logger.info(f"   • {key}: {value}")
            
            return {
                'office': office_name,
                'available': is_available,
                'message': message,
                'details': details
            }
            
        except Exception as e:
            logger.error(f"Error checking {office_name}: {e}", exc_info=True)
            return {
                'office': office_name,
                'available': False,
                'message': f"Error: {str(e)}",
                'details': {'error': str(e)}
            }
        finally:
            self._close_driver()
    
    def _solve_captcha(self) -> bool:
        """
        Find and solve CAPTCHA on the page.
        
        Returns:
            True if solved successfully, False otherwise
        """
        try:
            wait = WebDriverWait(self.driver, 10)
            
            # Find CAPTCHA image - it has alt="CAPTCHA Resmi"
            captcha_img = None
            try:
                captcha_img = self.driver.find_element(By.CSS_SELECTOR, "img[alt='CAPTCHA Resmi']")
                logger.info("Found CAPTCHA image with alt='CAPTCHA Resmi'")
            except:
                # Try other selectors
                captcha_selectors = [
                    "img[alt*='CAPTCHA']",
                    "img[alt*='captcha']",
                    "img[src*='captcha']",
                    ".captcha-image",
                    "#captcha-image"
                ]
                
                for selector in captcha_selectors:
                    try:
                        captcha_img = self.driver.find_element(By.CSS_SELECTOR, selector)
                        logger.info(f"Found CAPTCHA image with selector: {selector}")
                        break
                    except:
                        continue
            
            if not captcha_img:
                logger.error("No CAPTCHA image found on page")
                self.driver.save_screenshot("no_captcha_debug.png")
                return False
            
            # Get CAPTCHA image source
            img_src = captcha_img.get_attribute('src')
            logger.info(f"CAPTCHA image source type: {'base64' if img_src.startswith('data:') else 'URL'}")
            
            if img_src.startswith('data:'):
                # Base64 encoded image
                base64_data = img_src.split(',')[1]
                captcha_text = self.captcha_solver.solve_from_base64(base64_data)
            else:
                # Download image
                img_data = self.captcha_solver.download_captcha_image(img_src)
                if img_data:
                    captcha_text = self.captcha_solver.solve_captcha(img_data)
                else:
                    return False
            
            if not captcha_text:
                logger.error("Failed to solve CAPTCHA")
                return False
            
            logger.info(f"CAPTCHA solved: {captcha_text}")
            
            # Find the input field - it's named "mailConfirmCode"
            try:
                code_input = self.driver.find_element(By.NAME, "mailConfirmCode")
                logger.info("Found CAPTCHA input field (mailConfirmCode)")
            except:
                # Fallback to placeholder
                try:
                    code_input = self.driver.find_element(By.CSS_SELECTOR, "input[placeholder='Doğrulama kodu']")
                    logger.info("Found CAPTCHA input field by placeholder")
                except:
                    logger.error("No CAPTCHA input field found")
                    return False
            
            # Enter the CAPTCHA code
            code_input.clear()
            code_input.send_keys(captcha_text)
            logger.info(f"Entered CAPTCHA code: {captcha_text}")
            
            # Find and click the submit button - it's an <a> tag that says "RANDEVU AL"
            submit_btn = None
            
            # Try multiple methods to find the button
            button_selectors = [
                ("id", "confirmationbtn"),  # It has id="confirmationbtn"
                ("xpath", "//a[@id='confirmationbtn']"),
                ("xpath", "//a[text()='RANDEVU AL']"),
                ("xpath", "//a[contains(., 'RANDEVU AL')]"),
                ("css", "a.btn-danger"),  # The button appears to be red
                ("css", "a#confirmationbtn"),
                ("css", "a[name='confirmationbtn']")
            ]
            
            for method, selector in button_selectors:
                try:
                    if method == "xpath":
                        submit_btn = self.driver.find_element(By.XPATH, selector)
                    elif method == "id":
                        submit_btn = self.driver.find_element(By.ID, selector)
                    else:
                        submit_btn = self.driver.find_element(By.CSS_SELECTOR, selector)
                    logger.info(f"Found submit button using {method}: {selector}")
                    break
                except:
                    continue
            
            if not submit_btn:
                logger.error("No submit button found")
                self.driver.save_screenshot("no_button_debug.png")
                return False
            
            submit_btn.click()
            logger.info("Clicked submit button")
            
            time.sleep(5)  # Wait for page to load
            
            # Check if we successfully moved to the appointment form
            current_url = self.driver.current_url
            if "appointment-form" in current_url:
                logger.info("Successfully moved to appointment form page")
                return True
            
            # Check for error messages
            page_source = self.driver.page_source.lower()
            if "hatalı" in page_source or "yanlış" in page_source or "geçersiz" in page_source:
                logger.warning("CAPTCHA might be incorrect, will retry")
                return False
            
            logger.info("CAPTCHA submitted successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to solve CAPTCHA: {e}")
            try:
                self.driver.save_screenshot("captcha_error_debug.png")
                logger.info("Error screenshot saved as captcha_error_debug.png")
            except:
                pass
            return False
    
    def _fill_appointment_form_for_office(self, office_name: str) -> bool:
        """
        Fill the appointment form with predefined data for a specific office.
        
        Args:
            office_name: Name of the IDATA office to select
            
        Returns:
            True if filled successfully, False otherwise
        """
        try:
            wait = WebDriverWait(self.driver, 10)
            
            logger.info(f"🔧 Filling form fields...")
            
            # Select residence city
            logger.info(f"   └─ Setting residence city: {self.form_data['residence_city']}")
            city_select = Select(wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "select[name*='city'], select[name*='sehir'], #residence-city"))
            ))
            city_select.select_by_visible_text(self.form_data['residence_city'])
            time.sleep(1)
            
            # Select IDATA office
            logger.info(f"   └─ Setting IDATA office: {office_name}")
            office_select = Select(self.driver.find_element(By.CSS_SELECTOR, "select[name*='office'], select[name*='ofis'], #idata-office"))
            try:
                office_select.select_by_visible_text(office_name)
                logger.info(f"   ✅ Successfully selected office: {office_name}")
            except Exception as e:
                logger.error(f"   ❌ Failed to select office {office_name}: {e}")
                return False
            time.sleep(1)
            
            # Select travel purpose
            logger.info(f"   └─ Setting travel purpose: {self.form_data['travel_purpose']}")
            purpose_select = Select(self.driver.find_element(By.CSS_SELECTOR, "select[name*='purpose'], select[name*='amac'], #travel-purpose"))
            purpose_select.select_by_visible_text(self.form_data['travel_purpose'])
            time.sleep(1)
            
            # Select service type
            logger.info(f"   └─ Setting service type: {self.form_data['service_type']}")
            service_select = Select(self.driver.find_element(By.CSS_SELECTOR, "select[name*='service'], select[name*='hizmet'], #service-type"))
            service_select.select_by_visible_text(self.form_data['service_type'])
            time.sleep(1)
            
            # Enter number of persons
            logger.info(f"   └─ Setting number of persons: {self.form_data['num_persons']}")
            persons_input = self.driver.find_element(By.CSS_SELECTOR, "input[name*='person'], input[name*='kisi'], #num-persons")
            persons_input.clear()
            persons_input.send_keys(self.form_data['num_persons'])
            time.sleep(1)
            
            # Submit form
            logger.info("   └─ Submitting form...")
            submit_btn = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit'], input[type='submit'], .btn-submit, .btn-check")
            submit_btn.click()
            
            logger.info("✅ Appointment form submitted successfully")
            time.sleep(5)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to fill appointment form: {e}")
            return False
    
    def _check_availability_detailed(self) -> Tuple[bool, str, dict]:
        """
        Check if appointments are available based on page content with detailed results.
        
        Returns:
            Tuple of (is_available, message, details)
        """
        try:
            # Wait for results to load
            time.sleep(5)
            
            # Get page source
            page_content = self.driver.page_source
            soup = BeautifulSoup(page_content, 'html.parser')
            
            details = {
                'page_url': self.driver.current_url,
                'page_title': self.driver.title,
                'response_time': '5 seconds',
                'slots_found': 0,
                'error_messages': []
            }
            
            logger.info(f"   └─ Analyzing response page...")
            logger.info(f"   └─ Current URL: {details['page_url']}")
            logger.info(f"   └─ Page title: {details['page_title']}")
            
            # Check for no appointment message
            if self.NO_APPOINTMENT_TEXT in page_content:
                logger.info(f"   └─ Found 'no appointments' message")
                # Try to find the full message
                no_appt_element = soup.find(text=lambda text: text and self.NO_APPOINTMENT_TEXT in text)
                if no_appt_element:
                    full_message = no_appt_element.strip()
                    details['no_appointment_message'] = full_message
                    return False, full_message, details
                return False, "No appointments available", details
            
            # Check for error messages
            error_keywords = ['hata', 'error', 'başarısız', 'failed', 'geçersiz', 'invalid']
            for keyword in error_keywords:
                if keyword in page_content.lower():
                    error_elements = soup.find_all(text=lambda text: text and keyword.lower() in text.lower())
                    for error in error_elements[:3]:  # Get first 3 error messages
                        details['error_messages'].append(error.strip())
            
            if details['error_messages']:
                logger.info(f"   └─ Found error messages: {details['error_messages']}")
            
            # Check for time slots
            time_slot_selectors = [
                ['div', 'button', 'a'],  # Tags to search
                ['slot', 'time', 'saat', 'randevu', 'tarih', 'date']  # Keywords in classes
            ]
            
            time_slots = []
            for tags in [time_slot_selectors[0]]:
                for tag in tags:
                    elements = soup.find_all(tag)
                    for elem in elements:
                        class_attr = elem.get('class', [])
                        if any(keyword in str(class_attr).lower() for keyword in time_slot_selectors[1]):
                            slot_text = elem.get_text(strip=True)
                            if slot_text and len(slot_text) > 3:  # Filter out empty or very short texts
                                time_slots.append(slot_text)
            
            # Also check for calendar-like structures
            calendar_slots = soup.find_all(['td', 'div'], class_=lambda x: x and any(
                word in str(x).lower() for word in ['available', 'mevcut', 'uygun', 'calendar']
            ))
            
            for slot in calendar_slots:
                slot_text = slot.get_text(strip=True)
                if slot_text and len(slot_text) > 3:
                    time_slots.append(slot_text)
            
            # Remove duplicates and filter
            time_slots = list(set(time_slots))
            details['slots_found'] = len(time_slots)
            
            if time_slots:
                logger.info(f"   └─ Found {len(time_slots)} potential time slots!")
                available_times = time_slots[:5]  # Get first 5 slots
                details['available_slots'] = available_times
                
                message = f"Appointments available! Found {len(time_slots)} slots"
                if available_times:
                    message += f". Available times: {', '.join(available_times)}"
                
                logger.info(f"   └─ Available slots: {available_times}")
                return True, message, details
            
            # Check if we're on the right page
            if 'appointment' not in details['page_url'].lower():
                details['page_issue'] = 'Not on appointment page'
                logger.info(f"   └─ Warning: May not be on appointment results page")
            
            # If no clear indication, assume no availability
            logger.info(f"   └─ No appointment slots detected")
            return False, "No appointment slots found", details
            
        except Exception as e:
            logger.error(f"Failed to check availability: {e}")
            details['error'] = str(e)
            return False, f"Error checking availability: {str(e)}", details
    
    def _check_availability(self) -> Tuple[bool, str]:
        """
        Legacy method for backward compatibility.
        """
        is_available, message, _ = self._check_availability_detailed()
        return is_available, message