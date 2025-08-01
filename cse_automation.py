import os
import time
import re
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.select import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import subprocess
import glob

class CSETradeAutomation:
    def __init__(self):
        self.download_dir = os.path.join(os.getcwd(), "downloads")
        os.makedirs(self.download_dir, exist_ok=True)
        self.setup_chrome_options()
        
    def setup_chrome_options(self):
        """Setup Chrome options for headless operation and downloads"""
        self.chrome_options = Options()
        
        # Only add headless in production/CI environment
        if os.environ.get('CI') or os.environ.get('GITHUB_ACTIONS'):
            self.chrome_options.add_argument("--headless")
            print("Running in headless mode (CI/GitHub Actions)")
        else:
            self.chrome_options.add_argument("--headless")
            print("Running in headless mode (local)")
        
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--disable-dev-shm-usage")
        self.chrome_options.add_argument("--disable-gpu")
        self.chrome_options.add_argument("--window-size=1920,1080")
        self.chrome_options.add_argument("--disable-extensions")
        self.chrome_options.add_argument("--disable-plugins")
        self.chrome_options.add_argument("--disable-images")
        self.chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        self.chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Download preferences
        prefs = {
            "download.default_directory": self.download_dir,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        }
        self.chrome_options.add_experimental_option("prefs", prefs)
        
    def get_driver(self):
        """Initialize and return Chrome driver"""
        try:
            # Check if running in GitHub Actions or CI
            if os.environ.get('CI') or os.environ.get('GITHUB_ACTIONS'):
                print("Setting up Chrome driver for GitHub Actions...")
                # In GitHub Actions, use webdriver-manager
                service = Service(ChromeDriverManager().install())
                driver = webdriver.Chrome(service=service, options=self.chrome_options)
            else:
                # For local Windows environment, try system Chrome first
                print("Setting up Chrome driver with system Chrome...")
                
                # Set Chrome binary location for Windows
                chrome_paths = [
                    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
                ]
                
                chrome_path = None
                for path in chrome_paths:
                    if os.path.exists(path):
                        chrome_path = path
                        break
                
                if chrome_path:
                    self.chrome_options.binary_location = chrome_path
                    print(f"Found Chrome at: {chrome_path}")
                
                # Try with system Chrome first
                try:
                    driver = webdriver.Chrome(options=self.chrome_options)
                except Exception:
                    # Fallback to webdriver-manager
                    print("System Chrome failed, trying webdriver-manager...")
                    service = Service(ChromeDriverManager().install())
                    driver = webdriver.Chrome(service=service, options=self.chrome_options)
            
            # Add stealth settings
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            driver.execute_cdp_cmd('Network.setUserAgentOverride', {
                "userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            })
            
            print("Chrome driver setup successful!")
            return driver
            
        except Exception as e:
            print(f"Chrome driver setup failed: {e}")
            print("\nTroubleshooting suggestions:")
            print("1. Make sure Google Chrome is installed and up to date")
            print("2. Try running: pip install --upgrade selenium webdriver-manager")
            print("3. Clear webdriver cache: Remove ~/.wdm folder")
            raise
    
    def wait_for_download(self, timeout=60):
        """Wait for download to complete"""
        # Get list of files before download starts
        initial_files = set(glob.glob(os.path.join(self.download_dir, "*")))
        
        end_time = time.time() + timeout
        while time.time() < end_time:
            # Check for completed downloads (files without .crdownload extension)
            current_files = set(glob.glob(os.path.join(self.download_dir, "*")))
            
            # Look for new files that weren't there before
            new_files = current_files - initial_files
            completed_files = [f for f in new_files if not f.endswith('.crdownload') and not f.endswith('.tmp')]
            
            if completed_files:
                # Return the most recently created file among new files
                latest_file = max(completed_files, key=os.path.getctime)
                print(f"New download detected: {os.path.basename(latest_file)}")
                return latest_file
                
            # Also check if any .crdownload files have completed
            all_files = glob.glob(os.path.join(self.download_dir, "*"))
            download_in_progress = [f for f in all_files if f.endswith('.crdownload')]
            
            if not download_in_progress and len(current_files) > len(initial_files):
                # No downloads in progress and we have more files than before
                new_files_list = list(new_files)
                if new_files_list:
                    latest_file = max(new_files_list, key=os.path.getctime)
                    return latest_file
                    
            time.sleep(1)
            
        raise TimeoutError("Download did not complete within timeout period")
    
    def get_unique_filename(self, base_filename, directory):
        """Generate a unique filename by adding a counter if file exists"""
        filepath = os.path.join(directory, base_filename)
        
        if not os.path.exists(filepath):
            return filepath
        
        # Extract name and extension
        name, ext = os.path.splitext(base_filename)
        counter = 1
        
        while True:
            new_filename = f"{name}_{counter:03d}{ext}"
            new_filepath = os.path.join(directory, new_filename)
            if not os.path.exists(new_filepath):
                return new_filepath
            counter += 1
            
            # Safety check to avoid infinite loop
            if counter > 999:
                # Use timestamp as final fallback
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                new_filename = f"{name}_{timestamp}{ext}"
                return os.path.join(directory, new_filename)
    
    def extract_timestamp_from_text(self, text):
        """Extract timestamp from the span text and format it for filename"""
        # Example: "MARKET STATISTICS AS OF Jul 31, 2025, 2:47:42 PM"
        match = re.search(r'AS OF (.+)$', text)
        if match:
            date_str = match.group(1).strip()
            try:
                # Parse the date string
                dt = datetime.strptime(date_str, "%b %d, %Y, %I:%M:%S %p")
                # Format for filename (safe characters only)
                return dt.strftime("%Y-%m-%d_%H-%M-%S")
            except ValueError as e:
                print(f"Error parsing date: {e}")
                # Fallback to current timestamp
                return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        else:
            # Fallback to current timestamp
            return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    
    def download_trade_summary(self):
        """Main function to download CSE trade summary"""
        driver = None
        try:
            print("Starting CSE Trade Summary download...")
            driver = self.get_driver()
            
            # Navigate to the website
            url = "https://www.cse.lk/pages/trade-summary/trade-summary.component.html"
            print(f"Navigating to: {url}")
            driver.get(url)
            
            # Wait for page to load
            wait = WebDriverWait(driver, 30)
            
            # Wait for the dropdown to be present and select "All"
            print("Waiting for page elements to load...")
            dropdown = wait.until(EC.presence_of_element_located(
                (By.NAME, "DataTables_Table_0_length")
            ))
            
            print("Selecting 'All' from dropdown...")
            select = Select(dropdown)
            select.select_by_value("-1")  # Select "All"
            
            # Wait for table to reload with all data
            print("Waiting for table to load all data...")
            time.sleep(10)  # Give time for the table to load all records
            
            # Get the timestamp text before downloading
            timestamp_element = wait.until(EC.presence_of_element_located(
                (By.CLASS_NAME, "updated-time")
            ))
            timestamp_text = timestamp_element.text
            print(f"Found timestamp: {timestamp_text}")
            
            # Extract timestamp for filename
            file_timestamp = self.extract_timestamp_from_text(timestamp_text)
            print(f"Extracted timestamp for filename: {file_timestamp}")
            
            # Don't clear download directory - keep old files
            
            # Click the download button
            print("Clicking download button...")
            download_button = wait.until(EC.element_to_be_clickable(
                (By.ID, "dropdownMenu2")
            ))
            download_button.click()
            
            # Wait for dropdown menu to appear and click CSV option
            print("Looking for CSV download option...")
            time.sleep(3)
            
            # Try multiple selectors for CSV option
            csv_selectors = [
                "//a[contains(text(), 'CSV')]",
                "//a[contains(text(), 'csv')]",
                "//a[contains(@class, 'csv')]",
                "//button[contains(text(), 'CSV')]",
                "//button[contains(text(), 'csv')]",
                "//li[contains(text(), 'CSV')]//a",
                "//div[contains(@class, 'dropdown-menu')]//a[contains(text(), 'CSV')]"
            ]
            
            csv_option = None
            for selector in csv_selectors:
                try:
                    csv_option = driver.find_element(By.XPATH, selector)
                    if csv_option.is_displayed():
                        break
                except:
                    continue
            
            if csv_option is None:
                # Fallback: try to find any download option
                print("CSV option not found, looking for any download option...")
                csv_option = wait.until(EC.element_to_be_clickable(
                    (By.XPATH, "//div[contains(@class, 'dropdown-menu')]//a")
                ))
            
            print("Clicking CSV download option...")
            driver.execute_script("arguments[0].click();", csv_option)
            
            print("Waiting for download to complete...")
            downloaded_file = self.wait_for_download()
            print(f"Downloaded file: {downloaded_file}")
            
            # Create new filename with timestamp
            new_filename = f"cse_trade_summary_{file_timestamp}.csv"
            
            # Get unique filepath to avoid conflicts
            unique_filepath = self.get_unique_filename(new_filename, os.path.dirname(downloaded_file))
            unique_filename = os.path.basename(unique_filepath)
            
            try:
                os.rename(downloaded_file, unique_filepath)
                print(f"File renamed to: {unique_filename}")
                
                if unique_filename != new_filename:
                    print(f"Note: File was renamed to avoid conflict with existing file")
                    
            except Exception as e:
                print(f"Warning: Could not rename file: {e}")
                print(f"File remains as: {os.path.basename(downloaded_file)}")
                unique_filepath = downloaded_file
            
            return unique_filepath
            
        except Exception as e:
            print(f"Error during download: {e}")
            raise
        finally:
            if driver:
                driver.quit()

def main():
    """Main execution function"""
    try:
        print("=" * 60)
        print("CSE Trade Summary Automation Starting...")
        print(f"Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        automation = CSETradeAutomation()
        downloaded_file = automation.download_trade_summary()
        
        print("=" * 60)
        print("SUCCESS: CSE Trade Summary automation completed!")
        print(f"Downloaded file: {os.path.basename(downloaded_file)}")
        print(f"Full path: {downloaded_file}")
        print(f"File size: {os.path.getsize(downloaded_file)} bytes")
        print("=" * 60)
        
        return downloaded_file
        
    except Exception as e:
        print("=" * 60)
        print("ERROR: Automation failed!")
        print(f"Error details: {e}")
        print("=" * 60)
        print("\nTroubleshooting tips:")
        print("1. Check your internet connection")
        print("2. Verify the CSE website is accessible")
        print("3. Make sure Chrome browser is installed and updated")
        print("4. Check if downloads folder has write permissions")
        print("5. Try running the script again after a few minutes")
        return None

if __name__ == "__main__":
    main()
