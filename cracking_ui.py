from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QPushButton, QLabel, QComboBox, QFileDialog, 
                            QTextEdit, QLineEdit, QGroupBox, QProgressBar, QMessageBox)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QTimer

class PasswordCrackingUI(QMainWindow):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.cracking_process = None
        self.output_timer = QTimer()
        self.output_timer.timeout.connect(self.update_output)
        self.init_ui()
        
    def init_ui(self):
        # Set window properties
        self.setWindowTitle("Password Cracking - John the Ripper")
        self.setMinimumSize(900, 700)
        
        # Create central widget and layout
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        title_label = QLabel("Password Cracking Tool")
        title_font = QFont("Arial", 18, QFont.Bold)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        
        # Input section
        input_group = QGroupBox("Input Settings")
        input_layout = QVBoxLayout()
        
        # Hash file selection
        hash_layout = QHBoxLayout()
        hash_label = QLabel("Hash File:")
        self.hash_path = QLineEdit()
        self.hash_path.setReadOnly(True)
        hash_button = QPushButton("Browse...")
        hash_button.clicked.connect(self.browse_hash_file)
        
        hash_layout.addWidget(hash_label)
        hash_layout.addWidget(self.hash_path)
        hash_layout.addWidget(hash_button)
        
        # Hash type selection
        hash_type_layout = QHBoxLayout()
        hash_type_label = QLabel("Hash Type:")
        self.hash_type_combo = QComboBox()
        self.hash_type_combo.addItems([
            "Auto-detect",
            "MD5", 
            "SHA1", 
            "SHA256", 
            "SHA512", 
            "NTLM", 
            "NetNTLMv2",
            "MySQL",
            "WPA/WPA2"
        ])
        
        hash_type_layout.addWidget(hash_type_label)
        hash_type_layout.addWidget(self.hash_type_combo)
        
        # Wordlist selection
        wordlist_layout = QHBoxLayout()
        wordlist_label = QLabel("Wordlist:")
        self.wordlist_combo = QComboBox()
        self.wordlist_combo.addItems([
            "rockyou",
            "seclists", 
            "Custom file..."
        ])
        self.wordlist_combo.currentTextChanged.connect(self.on_wordlist_changed)
        
        self.custom_wordlist_path = QLineEdit()
        self.custom_wordlist_path.setReadOnly(True)
        self.custom_wordlist_path.setVisible(False)
        
        wordlist_button = QPushButton("Browse...")
        wordlist_button.clicked.connect(self.browse_wordlist_file)
        wordlist_button.setVisible(False)
        
        self.wordlist_button = wordlist_button
        
        wordlist_layout.addWidget(wordlist_label)
        wordlist_layout.addWidget(self.wordlist_combo)
        wordlist_layout.addWidget(self.custom_wordlist_path)
        wordlist_layout.addWidget(wordlist_button)
        
        # Custom rules
        rules_layout = QHBoxLayout()
        rules_label = QLabel("Custom Rules:")
        self.rules_edit = QLineEdit()
        self.rules_edit.setPlaceholderText("Optional - e.g. jumbo, single, wordlist")
        
        rules_layout.addWidget(rules_label)
        rules_layout.addWidget(self.rules_edit)
        
        # Add layouts to input group
        input_layout.addLayout(hash_layout)
        input_layout.addLayout(hash_type_layout)
        input_layout.addLayout(wordlist_layout)
        input_layout.addLayout(rules_layout)
        input_group.setLayout(input_layout)
        
        # Action buttons
        action_layout = QHBoxLayout()
        
        self.start_button = QPushButton("Start Cracking")
        self.start_button.setMinimumHeight(40)
        self.start_button.clicked.connect(self.start_cracking)
        
        self.stop_button = QPushButton("Stop")
        self.stop_button.setMinimumHeight(40)
        self.stop_button.clicked.connect(self.stop_cracking)
        self.stop_button.setEnabled(False)
        
        back_button = QPushButton("Back to Home")
        back_button.setMinimumHeight(40)
        back_button.clicked.connect(self.controller.show_homepage)
        
        action_layout.addWidget(self.start_button)
        action_layout.addWidget(self.stop_button)
        action_layout.addWidget(back_button)
        
        # Progress tracking
        progress_layout = QVBoxLayout()
        progress_label = QLabel("Progress:")
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        
        progress_layout.addWidget(progress_label)
        progress_layout.addWidget(self.progress_bar)
        
        # Output section
        output_label = QLabel("Output:")
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setFont(QFont("Courier New", 10))
        
        # Assemble main layout
        main_layout.addWidget(title_label)
        main_layout.addSpacing(10)
        main_layout.addWidget(input_group)
        main_layout.addSpacing(10)
        main_layout.addLayout(action_layout)
        main_layout.addSpacing(10)
        main_layout.addLayout(progress_layout)
        main_layout.addSpacing(10)
        main_layout.addWidget(output_label)
        main_layout.addWidget(self.output_text)
        
        # Set central widget
        self.setCentralWidget(central_widget)
        
    def browse_hash_file(self):
        """Open file dialog to select hash file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Hash File", "", "All Files (*)"
        )
        if file_path:
            self.hash_path.setText(file_path)
            
    def browse_wordlist_file(self):
        """Open file dialog to select custom wordlist file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Wordlist File", "", "Text Files (*.txt);;All Files (*)"
        )
        if file_path:
            self.custom_wordlist_path.setText(file_path)
            
    def on_wordlist_changed(self, text):
        """Handle wordlist combo box changes"""
        if text == "Custom file...":
            self.custom_wordlist_path.setVisible(True)
            self.wordlist_button.setVisible(True)
        else:
            self.custom_wordlist_path.setVisible(False)
            self.wordlist_button.setVisible(False)
            
    def start_cracking(self):
        """Start the password cracking process"""
        # Validate inputs
        hash_file = self.hash_path.text()
        if not hash_file:
            QMessageBox.warning(self, "Input Error", "Please select a hash file.")
            return
            
        hash_type = self.hash_type_combo.currentText()
        if hash_type == "Auto-detect":
            hash_type = None
            
        # Get wordlist path
        wordlist = self.wordlist_combo.currentText()
        if wordlist == "Custom file...":
            wordlist = self.custom_wordlist_path.text()
            if not wordlist:
                QMessageBox.warning(self, "Input Error", "Please select a custom wordlist file.")
                return
                
        # Get custom rules
        custom_rules = self.rules_edit.text() if self.rules_edit.text() else None
        
        # Update UI state
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.output_text.clear()
        self.progress_bar.setValue(0)
        
        # Start cracking
        self.output_text.append("Starting password cracking process...\n")
        self.output_text.append(f"Hash File: {hash_file}")
        self.output_text.append(f"Hash Type: {hash_type if hash_type else 'Auto-detect'}")
        self.output_text.append(f"Wordlist: {wordlist}")
        if custom_rules:
            self.output_text.append(f"Custom Rules: {custom_rules}")
        self.output_text.append("\nRunning...\n")
        
        # Run the cracking process
        self.cracking_process = self.controller.run_password_cracking(
            hash_file, hash_type, wordlist, custom_rules
        )
        
        # Start timer to update output
        self.output_timer.start(100)
        
    def update_output(self):
        """Update the output text with process output"""
        if self.cracking_process is None:
            return
            
        # Check if process is still running
        if self.cracking_process.poll() is not None:
            # Process has finished
            self.output_timer.stop()
            
            # Get any remaining output
            stdout, stderr = self.cracking_process.communicate()
            
            if stdout:
                self.output_text.append(stdout)
            if stderr:
                self.output_text.append("ERROR: " + stderr)
                
            # Update UI state
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)
            self.progress_bar.setValue(100)
            
            # Show completion message
            self.output_text.append("\nPassword cracking process completed.")
            
            # Reset process
            self.cracking_process = None
            return
            
        # Process is still running, update output
        while True:
            line = self.cracking_process.stdout.readline()
            if line:
                self.output_text.append(line.strip())
                self.update_progress(line)
            else:
                break
                
    def update_progress(self, line):
        """Update progress bar based on John's output"""
        # Try to estimate progress from John's output
        # This is an approximation as John doesn't always provide clear progress info
        if "%" in line:
            try:
                percent = int(float(line.split("%")[0].split()[-1]))
                self.progress_bar.setValue(percent)
            except:
                pass
                
    def stop_cracking(self):
        """Stop the password cracking process"""
        if self.cracking_process:
            self.cracking_process.terminate()
            self.output_text.append("\nPassword cracking process stopped by user.")
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)
            self.output_timer.stop()
            self.cracking_process = None
