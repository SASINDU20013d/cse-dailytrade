# CSE Trade Data Automation

This project automatically downloads trade summary data from the Colombo Stock Exchange (CSE) website and stores it with timestamped filenames.

## Features

- **Automated Download**: Downloads CSV files from CSE trade summary page
- **Smart Naming**: Renames files using the timestamp from the webpage
- **Daily Automation**: GitHub Actions workflow runs daily at 4:00 PM Sri Lankan time
- **All Data**: Automatically selects "All" option to download complete dataset

## Setup

### Local Development

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd cse-automate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run manually**
   ```bash
   python cse_downloader.py
   ```

### GitHub Actions Setup

The project includes a GitHub Actions workflow that:
- Runs daily at 4:00 PM Sri Lankan Time (10:30 AM UTC)
- Downloads the latest trade data
- Commits and pushes the files to the repository

No additional setup is required - the workflow will run automatically once you push this code to GitHub.

## How it Works

1. **Navigate to CSE Website**: Opens the trade summary page
2. **Change Display Settings**: Changes dropdown from "25" to "All" items
3. **Extract Timestamp**: Gets the current timestamp from the page
4. **Download CSV**: Clicks the download button and saves CSV file
5. **Rename File**: Renames the downloaded file with the extracted timestamp
6. **Store Data**: Saves file in the `downloads/` directory

## File Structure

```
├── .github/
│   └── workflows/
│       └── download-cse-data.yml  # GitHub Actions workflow
├── downloads/                      # Downloaded CSV files (auto-created)
├── cse_downloader.py              # Main automation script
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

## Downloaded File Format

Files are saved with the format: `CSE_Trade_Summary_{timestamp}.csv`

Example: `CSE_Trade_Summary_Jul_31__2025__2_47_42_PM.csv`

## Manual Trigger

You can manually trigger the GitHub Actions workflow:
1. Go to the "Actions" tab in your GitHub repository
2. Select "CSE Trade Data Download"
3. Click "Run workflow"

## Requirements

- Python 3.11+
- Chrome browser (for Selenium)
- Internet connection
- GitHub repository (for automated runs)

## Troubleshooting

If the script fails:
1. Check if the CSE website structure has changed
2. Verify Chrome browser is installed
3. Check internet connectivity
4. Review the GitHub Actions logs for detailed error messages

## Contributing

Feel free to submit issues or pull requests to improve the automation.
