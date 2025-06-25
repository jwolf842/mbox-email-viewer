# src/core/email_processor.py
# Replace the entire file with this version

import email
from email.utils import parsedate_to_datetime
from datetime import datetime
import re
import os

class EmailProcessor:
    """Processes individual emails into structured data"""
    
    def __init__(self):
        self.processed_emails = []
        self.processing_errors = []
        
    def extract_email_data(self, msg, index):
        """Extract all relevant data from an email message"""
        try:
            email_data = {
                'index': index,
                'message_id': msg.get('Message-ID', ''),
                'from': self._clean_email_field(msg.get('From', '')),
                'to': self._clean_email_field(msg.get('To', '')),
                'cc': self._clean_email_field(msg.get('Cc', '')),
                'subject': msg.get('Subject', ''),
                'date': self._parse_date(msg.get('Date', '')),
                'body_plain': '',
                'body_html': '',
                'attachments': [],
                'size': len(str(msg)),
                'thread_id': msg.get('Thread-Index', ''),
                'in_reply_to': msg.get('In-Reply-To', ''),
                'labels': self._extract_labels(msg),
                'raw_message': msg  # Store the raw message for attachment extraction
            }
            
            self._extract_body_and_attachments(msg, email_data)
            return email_data
            
        except Exception as e:
            self.processing_errors.append({
                'index': index,
                'error': str(e)
            })
            return None
            
    def _clean_email_field(self, field):
        """Clean email fields for better display"""
        if not field:
            return ''
        return ' '.join(field.split())
        
    def _parse_date(self, date_str):
        """Parse email date string to datetime object"""
        try:
            return parsedate_to_datetime(date_str)
        except:
            return None
            
    def _extract_labels(self, msg):
        """Extract Gmail labels if present"""
        labels = msg.get('X-Gmail-Labels', '')
        if labels:
            return [label.strip() for label in labels.split(',')]
        return []
        
    def _extract_body_and_attachments(self, msg, email_data):
        """Extract email body and attachment information"""
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition", ""))
                
                if part.is_multipart():
                    continue
                    
                if "attachment" in content_disposition:
                    filename = part.get_filename()
                    if filename:
                        # Store attachment info including the part reference
                        email_data['attachments'].append({
                            'filename': filename,
                            'type': content_type,
                            'size': len(part.get_payload(decode=True) or b''),
                            'part': part  # Store the part for later extraction
                        })
                elif content_type == "text/plain":
                    body = part.get_payload(decode=True)
                    if body:
                        email_data['body_plain'] = body.decode('utf-8', errors='ignore')
                elif content_type == "text/html":
                    body = part.get_payload(decode=True)
                    if body:
                        email_data['body_html'] = body.decode('utf-8', errors='ignore')
        else:
            body = msg.get_payload(decode=True)
            if body:
                email_data['body_plain'] = body.decode('utf-8', errors='ignore')
                
    def process_mbox(self, mbox_loader, progress_callback=None, limit=None):
        """Process all emails in the MBOX file"""
        mbox = mbox_loader.mbox
        total = limit if limit else mbox_loader.email_count
        
        for i, msg in enumerate(mbox):
            if limit and i >= limit:
                break
                
            email_data = self.extract_email_data(msg, i)
            if email_data:
                self.processed_emails.append(email_data)
                
            if progress_callback:
                progress_callback(i + 1, total)
                
        return len(self.processed_emails), len(self.processing_errors)
    
    def extract_attachment(self, email_data, attachment_index, save_path):
        """Extract a specific attachment from an email"""
        try:
            if attachment_index >= len(email_data['attachments']):
                return False, "Invalid attachment index"
                
            attachment = email_data['attachments'][attachment_index]
            part = attachment.get('part')
            
            if not part:
                return False, "Attachment data not available"
                
            # Get the payload
            payload = part.get_payload(decode=True)
            if not payload:
                return False, "Empty attachment"
                
            # Save the file
            with open(save_path, 'wb') as f:
                f.write(payload)
                
            return True, f"Saved to {save_path}"
            
        except Exception as e:
            return False, f"Error extracting attachment: {str(e)}"
    
    def extract_all_attachments(self, email_data, save_directory):
        """Extract all attachments from an email to a directory"""
        try:
            if not email_data['attachments']:
                return False, "No attachments in this email"
                
            os.makedirs(save_directory, exist_ok=True)
            extracted_files = []
            
            for i, attachment in enumerate(email_data['attachments']):
                filename = attachment['filename']
                # Make filename safe for filesystem
                safe_filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
                
                # Handle duplicate filenames
                save_path = os.path.join(save_directory, safe_filename)
                if os.path.exists(save_path):
                    name, ext = os.path.splitext(safe_filename)
                    counter = 1
                    while os.path.exists(save_path):
                        safe_filename = f"{name}_{counter}{ext}"
                        save_path = os.path.join(save_directory, safe_filename)
                        counter += 1
                
                success, message = self.extract_attachment(email_data, i, save_path)
                if success:
                    extracted_files.append(safe_filename)
                    
            return True, extracted_files
            
        except Exception as e:
            return False, f"Error extracting attachments: {str(e)}"