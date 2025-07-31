import time
import os
import re
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

class CSEDownloader:
    def __init__(self, download_path="downloads"):
        self.download_path = os.path.abspath(download_path)
        self.driver = None
        self.setup_driver()
    
    def setup_driver(self):
        """Setup Chrome driver with download preferences"""
        chrome_options = Options()
        
        # Create download directory if it doesn't exist
        os.makedirs(self.download_path, exist_ok=True)
        
        # Chrome preferences for downloads
        prefs = {
            "download.default_directory": self.download_path,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        }
        
        chrome_options.add_experimental_option("prefs", prefs)
        
        # Uncomment the next line if you want to run headless
        # chrome_options.add_argument("--headless")
        
        # Setup driver with automatic ChromeDriver management
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        
    def get_timestamp_from_page(self):
        """Extract timestamp from the updated-time span element"""
        if not self.driver:
            return "driver_not_initialized"
            
        try:
            # Wait for the timestamp element to be present
            timestamp_element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "updated-time"))
            )
            
            timestamp_text = timestamp_element.text
            print(f"Found timestamp: {timestamp_text}")
            
            # Extract the date and time from the text
            # Expected format: "MARKET STATISTICS AS OF Jul 31, 2025, 2:47:42 PM"
            match = re.search(r'AS OF (.+)', timestamp_text)
            if match:
                date_time_str = match.group(1).strip()
                # Convert to a filename-safe format
                safe_filename = re.sub(r'[^\w\s-]', '_', date_time_str)
                safe_filename = re.sub(r'\s+', '_', safe_filename)
                return safe_filename
            
            return "unknown_timestamp"
            
        except Exception as e:
            print(f"Error extracting timestamp: {e}")
            return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def download_csv(self):
        """Main method to download CSV file"""
        if not self.driver:
            print("Driver not initialized")
            return
            
        try:
            # Navigate to the CSE trade summary page
            url = "https://www.cse.lk/pages/trade-summary/trade-summary.component.html"
            print(f"Navigating to: {url}")
            self.driver.get(url)
            
            # Wait for the page to load
            time.sleep(5)
            
            # Get timestamp before making changes
            timestamp = self.get_timestamp_from_page()
            
            # Find and change the dropdown to "All"
            try:
                dropdown = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.NAME, "DataTables_Table_0_length"))
                )
                
                select = Select(dropdown)
                select.select_by_value("-1")  # Select "All"
                print("Changed dropdown to 'All'")
                
                # Wait for the table to reload with all data
                time.sleep(10)
                
            except Exception as e:
                print(f"Error changing dropdown: {e}")
            
            # Find and click the download button
            try:
                download_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.ID, "dropdownMenu2"))
                )
                
                download_button.click()
                print("Clicked download button")
                
                # Wait for dropdown menu to appear and click CSV option
                time.sleep(2)
                
                # Look for CSV download option (you might need to adjust this selector)
                csv_option = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'CSV') or contains(text(), 'csv')]"))
                )
                
                csv_option.click()
                print("Clicked CSV download option")
                
                # Wait for download to complete
                time.sleep(10)
                
                # Rename the downloaded file
                self.rename_downloaded_file(timestamp)
                
            except Exception as e:
                print(f"Error downloading CSV: {e}")
            
        except Exception as e:
            print(f"Error in download process: {e}")
        
        finally:
            if self.driver:
                self.driver.quit()
    
    def rename_downloaded_file(self, timestamp):
        """Rename the most recently downloaded CSV file"""
        try:
            # Find the most recent CSV file in the download directory
            csv_files = [f for f in os.listdir(self.download_path) if f.endswith('.csv')]
            
            if not csv_files:
                print("No CSV files found in download directory")
                return
            
            # Sort by modification time to get the most recent
            csv_files.sort(key=lambda x: os.path.getmtime(os.path.join(self.download_path, x)), reverse=True)
            latest_file = csv_files[0]
            
            # Create new filename with timestamp
            new_filename = f"CSE_Trade_Summary_{timestamp}.csv"
            
            old_path = os.path.join(self.download_path, latest_file)
            new_path = os.path.join(self.download_path, new_filename)
            
            os.rename(old_path, new_path)
            print(f"Renamed '{latest_file}' to '{new_filename}'")
            
        except Exception as e:
            print(f"Error renaming file: {e}")

def main():
    """Main function to run the CSE downloader"""
    downloader = CSEDownloader()
    downloader.download_csv()

if __name__ == "__main__":
    main()
