# src/ui/main_window.py

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys
import os
from datetime import datetime
import re

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import all core modules at the top
from core.mbox_loader import MBOXLoader
from core.email_processor import EmailProcessor
from core.search_engine import EmailSearchEngine
from core.exporter import EmailExporter

class EmailTableModel(QAbstractTableModel):
    """Model for displaying emails in a table"""
    
    def __init__(self, emails=[]):
        super().__init__()
        self.emails = emails
        self.headers = ['Date', 'From', 'Subject', 'Attachments']
        
    def rowCount(self, parent=None):
        return len(self.emails)
        
    def columnCount(self, parent=None):
        return len(self.headers)
        
    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
            
        email = self.emails[index.row()]
        col = index.column()
        
        if role == Qt.DisplayRole:
            if col == 0:  # Date
                date = email.get('date')
                return date.strftime('%Y-%m-%d %H:%M') if date else 'No date'
            elif col == 1:  # From
                return email.get('from', '')[:50]
            elif col == 2:  # Subject
                return email.get('subject', '')[:100]
            elif col == 3:  # Attachments
                att_count = len(email.get('attachments', []))
                return str(att_count) if att_count > 0 else ''
                
        return None
        
    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.headers[section]
        return None

class ProcessingThread(QThread):
    """Thread for processing MBOX files without freezing UI"""
    
    progress = pyqtSignal(int, int)
    finished = pyqtSignal(int, int)
    error = pyqtSignal(str)
    status = pyqtSignal(str)  # Add this new signal
    
    def __init__(self, loader, processor):
        super().__init__()
        self.loader = loader
        self.processor = processor
        
    def run(self):
        try:
            # Count emails in the thread (not main thread)
            self.status.emit("Counting emails...")
            email_count = len(self.loader.mbox)
            self.loader.email_count = email_count
            self.status.emit(f"Found {email_count:,} emails. Processing...")
            
            # Process emails
            processed, errors = self.processor.process_mbox(
                self.loader,
                progress_callback=self.emit_progress
            )
            self.finished.emit(processed, errors)
        except Exception as e:
            self.error.emit(str(e))
            
    def emit_progress(self, current, total):
        """Emit progress signal - this was missing!"""
        self.progress.emit(current, total)

class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.loader = None
        self.processor = None
        self.search_engine = None
        self.exporter = None
        
        self.init_ui()
        self.setWindowTitle('MBOX Email Viewer')
        self.setGeometry(100, 100, 1200, 800)
        
        # Apply dark theme
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2b2b2b;
            }
            QWidget {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QPushButton {
                background-color: #3c3c3c;
                border: 1px solid #555555;
                padding: 5px 15px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #4c4c4c;
            }
            QPushButton:pressed {
                background-color: #1c1c1c;
            }
            QLineEdit, QTextEdit, QDateEdit {
                background-color: #3c3c3c;
                border: 1px solid #555555;
                padding: 5px;
                border-radius: 3px;
            }
            QTableView {
                background-color: #3c3c3c;
                alternate-background-color: #2c2c2c;
                gridline-color: #555555;
            }
            QHeaderView::section {
                background-color: #4c4c4c;
                padding: 5px;
                border: 1px solid #555555;
            }
            QProgressBar {
                border: 1px solid #555555;
                border-radius: 3px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #0d7377;
                border-radius: 3px;
            }
        """)
        
    def init_ui(self):
        """Initialize the UI components"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # File selection
        file_group = QGroupBox("1. Select MBOX File")
        file_layout = QHBoxLayout()
        
        self.file_path_edit = QLineEdit()
        self.file_path_edit.setPlaceholderText("Select an MBOX file...")
        
        self.browse_btn = QPushButton("Browse")
        self.browse_btn.clicked.connect(self.browse_file)
        
        self.load_btn = QPushButton("Load File")
        self.load_btn.clicked.connect(self.load_file)
        self.load_btn.setEnabled(False)
        
        file_layout.addWidget(self.file_path_edit)
        file_layout.addWidget(self.browse_btn)
        file_layout.addWidget(self.load_btn)
        file_group.setLayout(file_layout)
        layout.addWidget(file_group)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Search and filters
        search_group = QGroupBox("2. Search and Filter")
        search_layout = QGridLayout()
        
        # Search box
        search_layout.addWidget(QLabel("Search:"), 0, 0)
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search in emails...")
        self.search_edit.returnPressed.connect(self.perform_search)
        search_layout.addWidget(self.search_edit, 0, 1, 1, 3)
        
        # Sender filter
        search_layout.addWidget(QLabel("Sender:"), 1, 0)
        self.sender_edit = QLineEdit()
        self.sender_edit.setPlaceholderText("Filter by sender...")
        self.sender_edit.returnPressed.connect(self.perform_search)
        search_layout.addWidget(self.sender_edit, 1, 1, 1, 3)
        
        # Date range
        search_layout.addWidget(QLabel("From Date:"), 2, 0)
        self.date_from = QDateEdit()
        self.date_from.setCalendarPopup(True)
        self.date_from.setDate(QDate.currentDate().addYears(-1))
        search_layout.addWidget(self.date_from, 2, 1)
        
        search_layout.addWidget(QLabel("To Date:"), 2, 2)
        self.date_to = QDateEdit()
        self.date_to.setCalendarPopup(True)
        self.date_to.setDate(QDate.currentDate())
        search_layout.addWidget(self.date_to, 2, 3)
        
        # Attachment filter
        search_layout.addWidget(QLabel("Attachments:"), 3, 0)
        self.attachment_combo = QComboBox()
        self.attachment_combo.addItems(['All Emails', 'With Attachments', 'Without Attachments'])
        search_layout.addWidget(self.attachment_combo, 3, 1, 1, 3)
        
        # Search button
        self.search_btn = QPushButton("Search")
        self.search_btn.clicked.connect(self.perform_search)
        self.search_btn.setEnabled(False)
        search_layout.addWidget(self.search_btn, 4, 0, 1, 4)
        
        search_group.setLayout(search_layout)
        layout.addWidget(search_group)
        
        # Results table
        self.results_table = QTableView()
        self.results_table.setAlternatingRowColors(True)
        self.results_table.setSelectionBehavior(QTableView.SelectRows)
        self.results_table.doubleClicked.connect(self.view_email)
        layout.addWidget(self.results_table)
        
        # Export buttons
        export_group = QGroupBox("3. Export Options")
        export_layout = QHBoxLayout()

        self.export_csv_btn = QPushButton("Export to CSV")
        self.export_csv_btn.clicked.connect(lambda: self.export_data('csv'))
        self.export_csv_btn.setEnabled(False)

        self.export_excel_btn = QPushButton("Export to Excel")
        self.export_excel_btn.clicked.connect(lambda: self.export_data('excel'))
        self.export_excel_btn.setEnabled(False)

        self.export_txt_btn = QPushButton("Export as Text Files")
        self.export_txt_btn.clicked.connect(lambda: self.export_data('text'))
        self.export_txt_btn.setEnabled(False)

        # NEW: Export All Attachments button
        self.export_attachments_btn = QPushButton("Export All Attachments")
        self.export_attachments_btn.clicked.connect(lambda: self.export_data('attachments'))
        self.export_attachments_btn.setEnabled(False)
        self.export_attachments_btn.setToolTip("Extract all attachments from current search results")

        export_layout.addWidget(self.export_csv_btn)
        export_layout.addWidget(self.export_excel_btn)
        export_layout.addWidget(self.export_txt_btn)
        export_layout.addWidget(self.export_attachments_btn)  # Add the new button
        export_layout.addStretch()

        export_group.setLayout(export_layout)
        layout.addWidget(export_group)
        
        # Status bar
        self.status_bar = self.statusBar()
        self.status_bar.showMessage('Ready')
        
    def browse_file(self):
        """Open file dialog to select MBOX file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select MBOX File",
            "",
            "MBOX Files (*.mbox);;All Files (*.*)"
        )
        
        if file_path:
            self.file_path_edit.setText(file_path)
            self.load_btn.setEnabled(True)
            
    def load_file(self):
        """Load the selected MBOX file"""
        file_path = self.file_path_edit.text()
        
        if not file_path:
            QMessageBox.warning(self, "Warning", "Please select a file first")
            return
            
        # Show progress bar immediately
        self.progress_bar.setVisible(True)
        self.progress_bar.setMaximum(0)  # Indeterminate progress
        self.progress_bar.setMinimum(0)
        self.status_bar.showMessage("Loading MBOX file...")
        
        # Initialize components
        self.loader = MBOXLoader()
        success, message = self.loader.load_mbox(file_path)
        
        if not success:
            self.progress_bar.setVisible(False)
            QMessageBox.critical(self, "Error", message)
            return
            
        # Update status
        file_size = self.loader.get_file_size()
        self.status_bar.showMessage(f"File loaded ({file_size}). Preparing to process...")
        
        # Process emails in background thread
        self.processor = EmailProcessor()
        self.processing_thread = ProcessingThread(self.loader, self.processor)
        self.processing_thread.progress.connect(self.update_progress)
        self.processing_thread.finished.connect(self.processing_finished)
        self.processing_thread.error.connect(self.processing_error)
        self.processing_thread.status.connect(self.update_status)  # Connect new signal
        
        # Disable load button
        self.load_btn.setEnabled(False)
        
        # Start processing
        self.processing_thread.start()
               
    def update_status(self, status_message):
        """Update status bar with processing status"""
        self.status_bar.showMessage(status_message)
        # Set progress bar to determinate mode when we start actual processing
        if "Processing..." in status_message:
            self.progress_bar.setMaximum(100)  # Will be updated by update_progress
    
    def update_progress(self, current, total):
        """Update progress bar"""
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(current)
        self.status_bar.showMessage(f"Processing email {current} of {total}...")
        
    def processing_finished(self, processed, errors):
        """Handle processing completion"""
        self.progress_bar.setVisible(False)
        self.load_btn.setEnabled(True)
        
        # Initialize search engine and exporter
        self.search_engine = EmailSearchEngine(self.processor.processed_emails)
        self.exporter = EmailExporter()
        
        # Enable controls
        self.search_btn.setEnabled(True)
        self.export_csv_btn.setEnabled(True)
        self.export_excel_btn.setEnabled(True)
        self.export_txt_btn.setEnabled(True)
        self.export_attachments_btn.setEnabled(True)
        
        # Show all emails initially
        self.display_results(self.processor.processed_emails)
        
        message = f"Successfully processed {processed} emails"
        if errors > 0:
            message += f" ({errors} errors)"
        self.status_bar.showMessage(message)
        
    def processing_error(self, error_msg):
        """Handle processing error"""
        self.progress_bar.setVisible(False)
        self.load_btn.setEnabled(True)
        QMessageBox.critical(self, "Processing Error", error_msg)
        
    def perform_search(self):
        """Perform search with current filters"""
        if not self.search_engine or not self.search_btn.isEnabled():
            return
            
        # Reset to all emails
        self.search_engine.current_results = self.search_engine.emails
        
        # Apply search query
        query = self.search_edit.text()
        if query:
            self.search_engine.search(query)
            
        # Apply sender filter
        sender = self.sender_edit.text()
        if sender:
            self.search_engine.filter_by_sender(sender)
            
        # Apply date range
        start_date = self.date_from.date().toPyDate()
        end_date = self.date_to.date().toPyDate()
        
        # Convert to datetime
        from datetime import datetime, timezone
        start_dt = datetime.combine(start_date, datetime.min.time()).replace(tzinfo=timezone.utc)
        end_dt = datetime.combine(end_date, datetime.max.time()).replace(tzinfo=timezone.utc)
        
        self.search_engine.filter_by_date_range(start_dt, end_dt)
        
        # Apply attachment filter
        attachment_filter = self.attachment_combo.currentText()
        if attachment_filter == 'With Attachments':
            self.search_engine.filter_by_has_attachments(True)
        elif attachment_filter == 'Without Attachments':
            self.search_engine.filter_by_has_attachments(False)
            
        # Display results
        self.display_results(self.search_engine.current_results)
        
        stats = self.search_engine.get_statistics()
        self.status_bar.showMessage(
            f"Found {stats['total_emails']} emails | "
            f"{stats['unique_senders']} unique senders | "
            f"{stats['emails_with_attachments']} with attachments"
        )
        
    def display_results(self, emails):
        """Display emails in the table"""
        model = EmailTableModel(emails)
        self.results_table.setModel(model)
        self.results_table.resizeColumnsToContents()
        
    def view_email(self, index):
        """View selected email details with attachment extraction"""
        model = self.results_table.model()
        if not model:
            return
            
        email = model.emails[index.row()]
        
        # Create email viewer dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Email Details")
        dialog.setGeometry(200, 200, 900, 700)
        
        # Apply dark theme to dialog
        dialog.setStyleSheet(self.styleSheet())
        
        layout = QVBoxLayout(dialog)
        
        # Header info
        header_html = f"""
        <style>
            table {{ width: 100%; }}
            td {{ padding: 5px; }}
            .label {{ font-weight: bold; width: 100px; }}
        </style>
        <table>
            <tr><td class="label">From:</td><td>{email['from']}</td></tr>
            <tr><td class="label">To:</td><td>{email['to']}</td></tr>
            <tr><td class="label">Date:</td><td>{email['date']}</td></tr>
            <tr><td class="label">Subject:</td><td>{email['subject']}</td></tr>
            <tr><td class="label">Attachments:</td><td>{len(email['attachments'])}</td></tr>
        </table>
        """
        
        header_label = QLabel(header_html)
        header_label.setWordWrap(True)
        header_label.setStyleSheet("background-color: #3c3c3c; padding: 10px; border-radius: 5px;")
        layout.addWidget(header_label)
        
        # Email body
        body_group = QGroupBox("Message Content")
        body_layout = QVBoxLayout()
        body_text = QTextEdit()
        body_text.setPlainText(email['body_plain'])
        body_text.setReadOnly(True)
        body_layout.addWidget(body_text)
        body_group.setLayout(body_layout)
        layout.addWidget(body_group)
        
        # Attachments section
        if email['attachments']:
            att_group = QGroupBox(f"Attachments ({len(email['attachments'])})")
            att_layout = QVBoxLayout()
            
            # Attachments list with double-click to extract
            att_list = QListWidget()
            att_list.setStyleSheet("""
                QListWidget {
                    background-color: #3c3c3c;
                    border: 1px solid #555555;
                    padding: 5px;
                }
                QListWidget::item {
                    padding: 5px;
                    border-bottom: 1px solid #555555;
                }
                QListWidget::item:hover {
                    background-color: #4c4c4c;
                }
                QListWidget::item:selected {
                    background-color: #0d7377;
                }
            """)
            
            for i, att in enumerate(email['attachments']):
                size_kb = att['size'] / 1024
                if size_kb < 1024:
                    size_str = f"{size_kb:.1f} KB"
                else:
                    size_mb = size_kb / 1024
                    size_str = f"{size_mb:.1f} MB"
                
                item_text = f"{att['filename']} ({size_str}) - {att['type']}"
                att_list.addItem(item_text)
                
            att_list.setToolTip("Double-click to extract individual attachment")
            att_layout.addWidget(att_list)
            
            # Buttons for attachment actions
            button_layout = QHBoxLayout()
            
            extract_selected_btn = QPushButton("Extract Selected")
            extract_selected_btn.setIcon(self.style().standardIcon(QStyle.SP_DialogSaveButton))
            extract_selected_btn.clicked.connect(
                lambda: self._extract_selected_attachment(email, att_list.currentRow())
            )
            
            extract_all_btn = QPushButton("Extract All Attachments")
            extract_all_btn.setIcon(self.style().standardIcon(QStyle.SP_DirOpenIcon))
            extract_all_btn.clicked.connect(
                lambda: self._extract_all_attachments(email)
            )
            
            button_layout.addWidget(extract_selected_btn)
            button_layout.addWidget(extract_all_btn)
            button_layout.addStretch()
            
            att_layout.addLayout(button_layout)
            att_group.setLayout(att_layout)
            layout.addWidget(att_group)
            
            # Connect double-click to extract
            att_list.itemDoubleClicked.connect(
                lambda: self._extract_selected_attachment(email, att_list.currentRow())
            )
        
        # Dialog buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Close)
        button_box.rejected.connect(dialog.close)
        layout.addWidget(button_box)
        
        dialog.exec_()

    def _extract_selected_attachment(self, email, attachment_index):
        """Extract a single selected attachment"""
        if attachment_index < 0:
            QMessageBox.warning(self, "Warning", "Please select an attachment first")
            return
            
        attachment = email['attachments'][attachment_index]
        
        # Get save location
        suggested_filename = attachment['filename']
        save_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Attachment As",
            suggested_filename,
            "All Files (*.*)"
        )
        
        if not save_path:
            return
            
        # Extract the attachment
        success, message = self.processor.extract_attachment(email, attachment_index, save_path)
        
        if success:
            QMessageBox.information(self, "Success", f"Attachment saved to:\n{save_path}")
        else:
            QMessageBox.critical(self, "Error", message)

    def _extract_all_attachments(self, email):
        """Extract all attachments from an email"""
        if not email['attachments']:
            return
            
        # Get directory to save attachments
        save_dir = QFileDialog.getExistingDirectory(
            self,
            "Select Directory to Save All Attachments",
            "",
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        )
        
        if not save_dir:
            return
            
        # Create a subdirectory for this email's attachments
        email_date = email['date'].strftime('%Y%m%d_%H%M%S') if email['date'] else 'no_date'
        subject_safe = re.sub(r'[^\w\s-]', '', email['subject'])[:30]
        attachment_dir = os.path.join(save_dir, f"{email_date}_{subject_safe}_attachments")
        
        # Extract all attachments
        success, result = self.processor.extract_all_attachments(email, attachment_dir)
        
        if success:
            extracted_files = result
            file_list = '\n'.join(f"  • {f}" for f in extracted_files)
            QMessageBox.information(
                self, 
                "Success", 
                f"Extracted {len(extracted_files)} attachments to:\n{attachment_dir}\n\nFiles:\n{file_list}"
            )
        else:
            QMessageBox.critical(self, "Error", result)

    def export_data(self, export_type):
        """Export current search results"""
        if not self.search_engine or not self.exporter:
            return
            
        emails = self.search_engine.current_results
        
        if not emails:
            QMessageBox.warning(self, "Warning", "No emails to export")
            return
        
        # Prompt user to select export directory
        export_dir = QFileDialog.getExistingDirectory(
            self, 
            "Select Export Directory",
            "",
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        )
        
        if not export_dir:
            # User cancelled
            return
            
        try:
            if export_type == 'csv':
                # Generate filename with timestamp
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"email_export_{timestamp}.csv"
                filepath = self.exporter.export_to_csv(emails, export_dir, filename)
                QMessageBox.information(
                    self, 
                    "Export Successful", 
                    f"Exported {len(emails)} emails to:\n{filepath}"
                )
                
            elif export_type == 'excel':
                # Generate filename with timestamp
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"email_export_{timestamp}.xlsx"
                filepath = self.exporter.export_to_excel(emails, export_dir, filename)
                QMessageBox.information(
                    self, 
                    "Export Successful", 
                    f"Exported {len(emails)} emails to:\n{filepath}"
                )
                
            elif export_type == 'text':
                # Export individual emails
                folder_path, count = self.exporter.export_individual_emails(emails, export_dir)
                QMessageBox.information(
                    self, 
                    "Export Successful", 
                    f"Exported {count} individual email files to:\n{folder_path}"
                )
                
            elif export_type == 'attachments':
                # Count total attachments
                total_attachments = sum(len(email.get('attachments', [])) for email in emails)
                
                if total_attachments == 0:
                    QMessageBox.information(self, "No Attachments", "No attachments found in the current search results.")
                    return
                    
                # Confirm with user
                reply = QMessageBox.question(
                    self,
                    "Extract Attachments",
                    f"Found {total_attachments} attachments in {len(emails)} emails.\n\nExtract all attachments?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.Yes
                )
                
                if reply != QMessageBox.Yes:
                    return
                    
                # Create main directory for all attachments
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                attachments_dir = os.path.join(export_dir, f'all_attachments_{timestamp}')
                os.makedirs(attachments_dir, exist_ok=True)
                
                extracted_count = 0
                error_count = 0
                
                # Progress dialog
                progress = QProgressDialog("Extracting attachments...", "Cancel", 0, len(emails), self)
                progress.setWindowModality(Qt.WindowModal)
                progress.setWindowTitle("Extracting Attachments")
                
                for i, email in enumerate(emails):
                    if progress.wasCanceled():
                        break
                        
                    progress.setValue(i)
                    progress.setLabelText(f"Processing email {i+1} of {len(emails)}...")
                    
                    if email['attachments']:
                        # Create subdirectory for this email
                        email_date = email['date'].strftime('%Y%m%d_%H%M%S') if email['date'] else 'no_date'
                        from_safe = re.sub(r'[^\w\s-]', '', email['from'])[:30]
                        email_dir = os.path.join(attachments_dir, f"{email_date}_{from_safe}")
                        
                        success, result = self.processor.extract_all_attachments(email, email_dir)
                        if success:
                            extracted_count += len(result)
                        else:
                            error_count += 1
                
                progress.setValue(len(emails))
                
                # Show results
                message = f"Extraction complete!\n\n"
                message += f"Extracted {extracted_count} attachments\n"
                if error_count > 0:
                    message += f"Failed to extract from {error_count} emails\n"
                message += f"\nSaved to: {attachments_dir}"
                
                QMessageBox.information(self, "Attachment Extraction Complete", message)
                
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export: {str(e)}")