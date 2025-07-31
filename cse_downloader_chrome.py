import time
import os
import re
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.select import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options as ChromeOptions
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService

class CSEDownloader:
    def __init__(self, download_path="downloads"):
        self.download_path = os.path.abspath(download_path)
        self.driver = None
        self.setup_driver()
    
    def setup_driver(self):
        """Setup Chrome driver with download preferences using webdriver-manager"""
        # Create download directory if it doesn't exist
        os.makedirs(self.download_path, exist_ok=True)
        
        chrome_options = ChromeOptions()
        
        # Chrome preferences for downloads
        prefs = {
            "download.default_directory": self.download_path,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        }
        
        chrome_options.add_experimental_option("prefs", prefs)
        chrome_options.add_argument("--window-size=1920,1080")
        
        # Check if we're in CI environment
        if os.environ.get('GITHUB_ACTIONS') or os.environ.get('CI'):
            print("Running in CI environment - adding headless mode")
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
        else:
            print("Running in local environment")
        
        try:
            # Use webdriver-manager to automatically handle ChromeDriver
            print("Setting up Chrome with webdriver-manager...")
            
            # In CI environment, try to use system ChromeDriver first
            if os.environ.get('GITHUB_ACTIONS') or os.environ.get('CI'):
                import shutil
                chromedriver_path = shutil.which('chromedriver')
                if chromedriver_path:
                    print(f"✅ Using system ChromeDriver in CI: {chromedriver_path}")
                    service = ChromeService(chromedriver_path)
                    self.driver = webdriver.Chrome(service=service, options=chrome_options)
                    print("✅ Chrome initialized successfully with system ChromeDriver")
                    return
            
            # For local development or if system ChromeDriver not found
            try:
                service = ChromeService(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
                print("✅ Chrome initialized successfully with WebDriver Manager")
            except Exception as cdm_error:
                print(f"⚠️ ChromeDriverManager failed: {cdm_error}")
                # Fall back to system ChromeDriver
                import shutil
                chromedriver_path = shutil.which('chromedriver')
                if chromedriver_path:
                    print(f"🔄 Falling back to system ChromeDriver: {chromedriver_path}")
                    service = ChromeService(chromedriver_path)
                    self.driver = webdriver.Chrome(service=service, options=chrome_options)
                    print("✅ Chrome initialized successfully with system ChromeDriver")
                else:
                    raise Exception("No ChromeDriver available")
            
        except Exception as e:
            print(f"❌ Error setting up Chrome: {e}")
            raise
    
    def wait_for_download(self, expected_filename_pattern=None, timeout=30):
        """Wait for download to complete"""
        print(f"Waiting for download to complete in: {self.download_path}")
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            # Check for downloaded files
            files = os.listdir(self.download_path)
            
            # Filter out temporary download files
            downloaded_files = [f for f in files if not f.endswith('.crdownload') and not f.endswith('.tmp')]
            
            if downloaded_files:
                latest_file = max(downloaded_files, key=lambda f: os.path.getctime(os.path.join(self.download_path, f)))
                
                if expected_filename_pattern:
                    if re.search(expected_filename_pattern, latest_file, re.IGNORECASE):
                        print(f"✅ Download complete: {latest_file}")
                        return latest_file
                else:
                    print(f"✅ Download complete: {latest_file}")
                    return latest_file
            
            time.sleep(1)
        
        print("❌ Download timeout reached")
        return None
    
    def download_trade_summary(self):
        """Download trade summary from CSE website"""
        if not self.driver:
            raise Exception("Driver not initialized")
            
        try:
            url = "https://www.cse.lk/pages/trade-information/trade-summary"
            print(f"🔗 Navigating to: {url}")
            
            self.driver.get(url)
            
            # Wait for page to load
            wait = WebDriverWait(self.driver, 20)
            
            # Wait for the Market dropdown to be present
            print("⏳ Waiting for Market dropdown...")
            market_dropdown = wait.until(
                EC.presence_of_element_located((By.NAME, "MarketType"))
            )
            
            # Select "All" from Market dropdown
            print("📋 Selecting 'All' from Market dropdown...")
            market_select = Select(market_dropdown)
            market_select.select_by_visible_text("All")
            
            # Wait a moment for the selection to take effect
            time.sleep(2)
            
            # Find and click the Export CSV button
            print("🔍 Looking for Export CSV button...")
            
            # Try different possible selectors for the CSV export button
            csv_button_selectors = [
                "//a[contains(text(), 'Export CSV')]",
                "//button[contains(text(), 'Export CSV')]",
                "//input[contains(@value, 'Export CSV')]",
                "//a[contains(@href, 'csv')]",
                "//button[contains(@class, 'csv')]",
                "//*[contains(text(), 'CSV')]"
            ]
            
            csv_button = None
            for selector in csv_button_selectors:
                try:
                    csv_button = wait.until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    print(f"✅ Found CSV button with selector: {selector}")
                    break
                except:
                    continue
            
            if not csv_button:
                # If we can't find the button, let's see what's available
                print("🔍 CSV button not found. Looking for all buttons and links...")
                all_buttons = self.driver.find_elements(By.TAG_NAME, "button")
                all_links = self.driver.find_elements(By.TAG_NAME, "a")
                all_inputs = self.driver.find_elements(By.TAG_NAME, "input")
                
                print(f"Found {len(all_buttons)} buttons, {len(all_links)} links, {len(all_inputs)} inputs")
                
                # Look for any element containing "csv" or "export"
                for element in all_buttons + all_links + all_inputs:
                    text = element.get_attribute('outerHTML')
                    if text and ('csv' in text.lower() or 'export' in text.lower()):
                        print(f"Potential CSV element: {text[:200]}...")
                        try:
                            if element.is_enabled() and element.is_displayed():
                                csv_button = element
                                break
                        except:
                            continue
            
            if csv_button:
                print("📥 Clicking Export CSV button...")
                
                # Store files before download
                files_before = set(os.listdir(self.download_path)) if os.path.exists(self.download_path) else set()
                
                # Click the button
                self.driver.execute_script("arguments[0].click();", csv_button)
                
                # Wait for download
                downloaded_file = self.wait_for_download(expected_filename_pattern=r'.*\.csv$')
                
                if downloaded_file:
                    # Rename file with timestamp
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    original_path = os.path.join(self.download_path, downloaded_file)
                    new_filename = f"cse_trade_summary_{timestamp}.csv"
                    new_path = os.path.join(self.download_path, new_filename)
                    
                    try:
                        os.rename(original_path, new_path)
                        print(f"✅ File renamed to: {new_filename}")
                        
                        # Verify file size
                        file_size = os.path.getsize(new_path)
                        print(f"📊 File size: {file_size} bytes")
                        
                        if file_size > 0:
                            print("✅ Download completed successfully!")
                            return new_path
                        else:
                            print("❌ Downloaded file is empty")
                            return None
                            
                    except Exception as rename_error:
                        print(f"⚠️ Could not rename file: {rename_error}")
                        print(f"✅ Download completed as: {downloaded_file}")
                        return original_path
                else:
                    print("❌ Download failed or timed out")
                    return None
            else:
                print("❌ Could not find Export CSV button")
                return None
                
        except Exception as e:
            print(f"❌ Error during download: {e}")
            return None
    
    def close(self):
        """Close the browser driver"""
        if self.driver:
            self.driver.quit()
            print("🔒 Browser closed")

def main():
    downloader = None
    try:
        print("🚀 Starting CSE Trade Summary Downloader...")
        downloader = CSEDownloader()
        
        result = downloader.download_trade_summary()
        
        if result:
            print(f"✅ Success! Downloaded file: {result}")
        else:
            print("❌ Download failed")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        if downloader:
            downloader.close()

if __name__ == "__main__":
    main()
