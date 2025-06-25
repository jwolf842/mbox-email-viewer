# src/core/exporter.py

import os
import csv
import pandas as pd
from pathlib import Path
from datetime import datetime
import re

class EmailExporter:
    """Handles various export formats"""
    
    def __init__(self):
        # No default export folder - will be specified per export
        pass
        
    def export_to_csv(self, emails, export_dir, filename="email_export.csv"):
        """Export emails to CSV format"""
        filepath = os.path.join(export_dir, filename)
        
        csv_data = []
        for email in emails:
            csv_data.append({
                'Date': email['date'].strftime('%Y-%m-%d %H:%M:%S') if email['date'] else '',
                'From': email['from'],
                'To': email['to'],
                'Subject': email['subject'],
                'Has Attachments': 'Yes' if email['attachments'] else 'No',
                'Attachment Count': len(email['attachments']),
                'Body Preview': email['body_plain'][:200] + '...' if len(email['body_plain']) > 200 else email['body_plain']
            })
            
        df = pd.DataFrame(csv_data)
        df.to_csv(filepath, index=False)
        
        return filepath
        
    def export_to_excel(self, emails, export_dir, filename="email_export.xlsx"):
        """Export emails to Excel format with multiple sheets"""
        filepath = os.path.join(export_dir, filename)
        
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            # Main email data
            email_df = pd.DataFrame([
                {
                    'Date': email['date'].strftime('%Y-%m-%d %H:%M:%S') if email['date'] else '',
                    'From': email['from'],
                    'To': email['to'],
                    'Subject': email['subject'],
                    'Body Length': len(email['body_plain']),
                    'Attachments': len(email['attachments'])
                }
                for email in emails
            ])
            email_df.to_excel(writer, sheet_name='Emails', index=False)
            
            # Attachment summary
            attachment_data = []
            for email in emails:
                for att in email['attachments']:
                    attachment_data.append({
                        'Email Date': email['date'].strftime('%Y-%m-%d') if email['date'] else '',
                        'From': email['from'],
                        'Subject': email['subject'],
                        'Filename': att['filename'],
                        'Type': att['type'],
                        'Size (bytes)': att['size']
                    })
                    
            if attachment_data:
                att_df = pd.DataFrame(attachment_data)
                att_df.to_excel(writer, sheet_name='Attachments', index=False)
                
        return filepath
        
    def export_individual_emails(self, emails, export_dir):
        """Export emails as individual text files"""
        # Create a subfolder for the individual email files
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        emails_folder = os.path.join(export_dir, f'exported_emails_{timestamp}')
        os.makedirs(emails_folder, exist_ok=True)
        
        count = 0
        for i, email in enumerate(emails):
            # Create safe filename
            date_str = email['date'].strftime('%Y%m%d_%H%M%S') if email['date'] else 'no_date'
            subject_safe = re.sub(r'[^\w\s-]', '', email['subject'])[:50]
            filename = f"{date_str}_{subject_safe}_{i}.txt"
            
            filepath = os.path.join(emails_folder, filename)
            
            # Write email content
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"From: {email['from']}\n")
                f.write(f"To: {email['to']}\n")
                f.write(f"Date: {email['date']}\n")
                f.write(f"Subject: {email['subject']}\n")
                f.write(f"Attachments: {len(email['attachments'])}\n")
                f.write("\n" + "="*50 + "\n\n")
                f.write(email['body_plain'])
                
            count += 1
            
        return emails_folder, count  # Return both folder path and count