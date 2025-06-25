Changelog
All notable changes to MBOX Email Viewer will be documented in this file.

The format is based on Keep a Changelog, and this project adheres to Semantic Versioning.

1.0.0 - 2025-6-25
Added
Initial release of MBOX Email Viewer
Load and parse MBOX files from Google Takeout
Search emails by content, sender, and subject
Filter emails by date range
Filter emails by attachment presence
View email details with formatted display
Extract individual attachments in original formats
Extract all attachments from search results
Export emails to CSV format
Export emails to Excel with multiple sheets
Export emails as individual text files
Dark theme UI for comfortable viewing
Progress bar for email processing
Keyboard shortcuts (Enter to search)
Installer for easy Windows deployment
Technical Details
Built with Python 3.10 and PyQt5
Uses pandas for data export
Supports large MBOX files (tested up to 2GB)
Multi-threaded processing to keep UI responsive
Known Issues
Large MBOX files (>2GB) may take several minutes to initially load
Some special characters in email subjects may not display correctly in exports
Email count estimation during initial load may be inaccurate for very large files
