# src/core/mbox_loader.py

import mailbox
import os
from pathlib import Path

class MBOXLoader:
    """Handles loading and initial parsing of MBOX files"""
    
    def __init__(self):
        self.mbox = None
        self.mbox_path = None
        self.email_count = 0
        
    def load_mbox(self, file_path):
        """Load MBOX file without counting emails (faster initial load)"""
        try:
            # Just open the file, don't count yet
            self.mbox = mailbox.mbox(file_path)
            self.mbox_path = file_path
            # Don't count emails here - it will be done in the processing thread
            self.email_count = 0  # Will be updated during processing
            return True, "MBOX file loaded successfully"
        except Exception as e:
            return False, f"Error loading file: {str(e)}"
            
    def get_file_size(self):
        """Get the size of the MBOX file in MB"""
        if self.mbox_path:
            size_bytes = os.path.getsize(self.mbox_path)
            size_mb = size_bytes / (1024 * 1024)
            return f"{size_mb:.2f} MB"
        return "Unknown"
        
    def estimate_email_count(self):
        """Quick estimate of email count (optional - for progress bar)"""
        if self.mbox_path:
            # Estimate based on file size (rough estimate)
            size_bytes = os.path.getsize(self.mbox_path)
            # Assume average email size of 10KB
            estimated_count = size_bytes // 10240
            return max(100, estimated_count)  # Minimum 100 for progress bar
        return 100