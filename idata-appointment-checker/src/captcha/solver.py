import base64
import io
import logging
import re
from typing import Optional, Tuple

import cv2
import numpy as np
import pytesseract
import requests
from PIL import Image

logger = logging.getLogger(__name__)


class CaptchaSolver:
    """Solves image-based captchas from IDATA website."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
    
    def solve_captcha(self, image_data: bytes) -> Optional[str]:
        """
        Solve the captcha from image bytes.
        
        Args:
            image_data: Raw image bytes
            
        Returns:
            Solved captcha text or None if failed
        """
        try:
            # Convert bytes to PIL Image
            image = Image.open(io.BytesIO(image_data))
            
            # Preprocess image for better OCR
            processed_image = self._preprocess_image(image)
            
            # Extract text using OCR
            text = self._extract_text(processed_image)
            
            # Clean extracted text
            cleaned_text = self._clean_text(text)
            
            logger.info(f"Captcha solved: {cleaned_text}")
            return cleaned_text
            
        except Exception as e:
            logger.error(f"Failed to solve captcha: {e}")
            return None
    
    def _preprocess_image(self, image: Image.Image) -> np.ndarray:
        """
        Preprocess image for better OCR results.
        
        Args:
            image: PIL Image object
            
        Returns:
            Preprocessed image as numpy array
        """
        # Convert to OpenCV format
        img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Apply threshold to get binary image
        _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
        
        # Denoise
        denoised = cv2.medianBlur(thresh, 3)
        
        # Resize for better OCR
        scale_percent = 200
        width = int(denoised.shape[1] * scale_percent / 100)
        height = int(denoised.shape[0] * scale_percent / 100)
        resized = cv2.resize(denoised, (width, height), interpolation=cv2.INTER_CUBIC)
        
        return resized
    
    def _extract_text(self, image: np.ndarray) -> str:
        """
        Extract text from preprocessed image using OCR.
        
        Args:
            image: Preprocessed image as numpy array
            
        Returns:
            Extracted text
        """
        # Configure Tesseract for alphanumeric characters
        custom_config = r'--oem 3 --psm 8 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
        
        # Perform OCR
        text = pytesseract.image_to_string(image, config=custom_config)
        
        return text.strip()
    
    def _clean_text(self, text: str) -> str:
        """
        Clean extracted text by removing unwanted characters.
        
        Args:
            text: Raw extracted text
            
        Returns:
            Cleaned text
        """
        # Remove non-alphanumeric characters
        cleaned = re.sub(r'[^a-zA-Z0-9]', '', text)
        
        # Convert to uppercase (if needed based on captcha format)
        cleaned = cleaned.upper()
        
        return cleaned
    
    def download_captcha_image(self, url: str) -> Optional[bytes]:
        """
        Download captcha image from URL.
        
        Args:
            url: URL of the captcha image
            
        Returns:
            Image bytes or None if failed
        """
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.content
        except Exception as e:
            logger.error(f"Failed to download captcha image: {e}")
            return None
    
    def solve_from_base64(self, base64_string: str) -> Optional[str]:
        """
        Solve captcha from base64 encoded image.
        
        Args:
            base64_string: Base64 encoded image string
            
        Returns:
            Solved captcha text or None if failed
        """
        try:
            # Remove data URL prefix if present
            if ',' in base64_string:
                base64_string = base64_string.split(',')[1]
            
            # Decode base64
            image_data = base64.b64decode(base64_string)
            
            return self.solve_captcha(image_data)
        except Exception as e:
            logger.error(f"Failed to decode base64 image: {e}")
            return None