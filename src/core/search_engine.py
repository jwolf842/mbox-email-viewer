from datetime import datetime
from collections import defaultdict

class EmailSearchEngine:
    """Search and filter capabilities for processed emails"""
    
    def __init__(self, processed_emails):
        self.emails = processed_emails
        self.current_results = processed_emails
        
    def search(self, query, fields=['subject', 'from', 'to', 'body_plain']):
        """Search emails across multiple fields"""
        if not query:
            self.current_results = self.emails
            return self.current_results
            
        query_lower = query.lower()
        results = []
        
        for email in self.emails:
            for field in fields:
                value = email.get(field, '')
                if isinstance(value, str) and query_lower in value.lower():
                    results.append(email)
                    break
                    
        self.current_results = results
        return results
        
    def filter_by_date_range(self, start_date=None, end_date=None):
        """Filter emails by date range"""
        filtered = []
        
        for email in self.current_results:
            email_date = email.get('date')
            if not email_date:
                continue
                
            if start_date and email_date < start_date:
                continue
            if end_date and email_date > end_date:
                continue
                
            filtered.append(email)
            
        self.current_results = filtered
        return filtered
        
    def filter_by_sender(self, sender):
        """Filter emails by sender"""
        if not sender:
            return self.current_results
            
        sender_lower = sender.lower()
        filtered = [
            email for email in self.current_results
            if sender_lower in email.get('from', '').lower()
        ]
        
        self.current_results = filtered
        return filtered
        
    def filter_by_has_attachments(self, has_attachments=True):
        """Filter emails by attachment presence"""
        if has_attachments:
            filtered = [
                email for email in self.current_results
                if email.get('attachments', [])
            ]
        else:
            filtered = [
                email for email in self.current_results
                if not email.get('attachments', [])
            ]
            
        self.current_results = filtered
        return filtered
        
    def get_statistics(self):
        """Get statistics about the current result set"""
        stats = {
            'total_emails': len(self.current_results),
            'unique_senders': len(set(email.get('from', '') for email in self.current_results)),
            'emails_with_attachments': sum(1 for email in self.current_results if email.get('attachments')),
            'total_attachments': sum(len(email.get('attachments', [])) for email in self.current_results),
            'date_range': self._get_date_range()
        }
        return stats
        
    def _get_date_range(self):
        """Get the date range of current results"""
        dates = [email.get('date') for email in self.current_results if email.get('date')]
        if dates:
            return {
                'earliest': min(dates),
                'latest': max(dates)
            }
        return None