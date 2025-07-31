# CSE Trade Summary Automation

This project automatically downloads the daily trade summary from the Colombo Stock Exchange (CSE) website and commits it to the repository.

## Features

- **Automated Download**: Downloads CSV data from CSE trade summary page
- **Smart Naming**: Files are named with the timestamp from the page (e.g., `cse_trade_summary_2025-07-31_14-47-42.csv`)
- **Daily Scheduling**: Runs automatically every day at 4:00 PM Sri Lankan Time
- **Git Integration**: Automatically commits and pushes downloaded files
- **Headless Operation**: Runs without UI for GitHub Actions compatibility

## How it works

1. **Navigate** to the CSE trade summary page
2. **Select "All"** from the records dropdown to get complete data
3. **Wait** for the table to load all records
4. **Extract** the timestamp from the page header
5. **Download** the CSV file
6. **Rename** the file with the extracted timestamp
7. **Commit and push** to the git repository

## Setup Instructions

### Local Setup

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd cse-automate
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run manually (optional)**
   ```bash
   python cse_automation.py
   ```

### GitHub Actions Setup

The automation is configured to run automatically via GitHub Actions:

- **Schedule**: Every day at 4:00 PM Sri Lankan Time (10:30 AM UTC)
- **Manual Trigger**: Can be triggered manually from the Actions tab

#### Prerequisites

1. **Enable GitHub Actions** in your repository settings
2. **Ensure repository permissions** allow Actions to write to the repository
3. **Push this code** to your GitHub repository

The workflow will automatically:
- Set up Python environment
- Install Chrome browser
- Install dependencies
- Run the automation script
- Commit and push any new files

## File Structure

```
.
├── .github/
│   └── workflows/
│       └── daily-download.yml    # GitHub Actions workflow
├── downloads/                    # Directory for downloaded files
├── cse_automation.py            # Main automation script
├── requirements.txt             # Python dependencies
└── README.md                   # This file
```

## Downloaded Files

Files are saved with the following naming convention:
```
cse_trade_summary_YYYY-MM-DD_HH-MM-SS.csv
```

Example: `cse_trade_summary_2025-07-31_14-47-42.csv`

## Troubleshooting

### Common Issues

1. **Chrome Driver Issues**: The script uses `webdriver-manager` to automatically download and manage Chrome drivers
2. **Download Timeouts**: Increase the timeout in `wait_for_download()` if downloads are slow
3. **Git Push Failures**: Ensure the repository has proper permissions for GitHub Actions

### Manual Testing

To test the automation locally:

```bash
python cse_automation.py
```

Check the `downloads/` directory for the downloaded file.

## Configuration

### Changing the Schedule

To modify the daily run time, edit the cron expression in `.github/workflows/daily-download.yml`:

```yaml
schedule:
  - cron: '30 10 * * *'  # Current: 4:00 PM LKT (10:30 AM UTC)
```

Use [crontab.guru](https://crontab.guru/) to generate different schedules.

### Download Directory

By default, files are downloaded to the `downloads/` directory. To change this, modify the `download_dir` variable in `cse_automation.py`.

## Dependencies

- **selenium**: Web automation
- **webdriver-manager**: Automatic Chrome driver management
- **requests**: HTTP requests (if needed)
- **python-dateutil**: Date parsing utilities

## License

This project is for educational and personal use. Please respect the CSE website's terms of service and rate limits.
