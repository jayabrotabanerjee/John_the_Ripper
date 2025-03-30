from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QPushButton, 
                            QLabel, QHBoxLayout, QSpacerItem, QSizePolicy)
from PyQt5.QtGui import QFont, QIcon, QPixmap
from PyQt5.QtCore import Qt

class HomePage(QMainWindow):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.init_ui()
        
    def init_ui(self):
        # Set window properties
        self.setWindowTitle("Password Cracking Tool")
        self.setMinimumSize(800, 600)
        
        # Create central widget and layout
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Header section
        header_layout = QVBoxLayout()
        
        # Title
        title_label = QLabel("Password Cracking Tool by Jayabrota Banerjee")
        title_font = QFont("Arial", 24, QFont.Bold)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        
        # Subtitle
        subtitle_label = QLabel("Using John the Ripper")
        subtitle_font = QFont("Arial", 16)
        subtitle_label.setFont(subtitle_font)
        subtitle_label.setAlignment(Qt.AlignCenter)
        
        header_layout.addWidget(title_label)
        header_layout.addWidget(subtitle_label)
        header_layout.addSpacing(20)
        
        # Button section
        button_layout = QVBoxLayout()
        
        # Start button
        start_button = QPushButton("Start Password Cracking")
        start_button.setMinimumHeight(50)
        start_button.setFont(QFont("Arial", 14))
        start_button.clicked.connect(self.controller.show_cracking_ui)
        
        # Quit button
        quit_button = QPushButton("Quit")
        quit_button.setMinimumHeight(50)
        quit_button.setFont(QFont("Arial", 14))
        quit_button.clicked.connect(self.controller.quit_application)
        
        button_layout.addWidget(start_button)
        button_layout.addSpacing(10)
        button_layout.addWidget(quit_button)
        
        # Add visualization section
        visualization_label = QLabel("How John the Ripper Works:")
        visualization_label.setFont(QFont("Arial", 16, QFont.Bold))
        
        # Create visualization widget
        visualization_widget = self.create_visualization()
        
        # Combine layouts
        main_layout.addLayout(header_layout)
        main_layout.addSpacing(30)
        main_layout.addLayout(button_layout)
        main_layout.addSpacing(30)
        main_layout.addWidget(visualization_label)
        main_layout.addWidget(visualization_widget)
        
        # Set central widget
        self.setCentralWidget(central_widget)
        
    def create_visualization(self):
        """Create a widget that visually explains how John the Ripper works"""
        vis_widget = QWidget()
        vis_layout = QVBoxLayout(vis_widget)
        
        # Explanation steps with arrows
        steps = [
            "1. Input Password Hash",
            "↓",
            "2. Apply Cracking Rules and Wordlists",
            "↓",
            "3. Generate Password Candidates",
            "↓",
            "4. Hash Each Candidate",
            "↓",
            "5. Compare with Target Hash",
            "↓",
            "6. Output Password if Match Found"
        ]
        
        # Add each step with appropriate styling
        for i, step in enumerate(steps):
            step_label = QLabel(step)
            
            if "↓" not in step:  # This is a text step
                step_label.setFont(QFont("Arial", 12))
                step_label.setStyleSheet("background-color: #f0f0f0; padding: 10px; border-radius: 5px;")
                step_label.setAlignment(Qt.AlignCenter)
            else:  # This is an arrow
                step_label.setAlignment(Qt.AlignCenter)
            
            vis_layout.addWidget(step_label)
            
            # Add small spacing between steps
            if i < len(steps) - 1:
                vis_layout.addSpacing(5)
        
        # Add a more detailed explanation
        details_label = QLabel(
            "John the Ripper takes password hashes and attempts to crack them by:\n"
            "• Using wordlists (like rockyou.txt) as a source of potential passwords\n"
            "• Applying rule-based mangling (adding numbers, special chars, etc.)\n"
            "• Supporting multiple hash types (MD5, SHA1, NTLM, etc.)\n"
            "• Optimizing with specialized algorithms for different hash formats"
        )
        details_label.setFont(QFont("Arial", 11))
        details_label.setWordWrap(True)
        details_label.setStyleSheet("background-color: #e6f7ff; padding: 15px; border-radius: 5px;")
        
        vis_layout.addSpacing(20)
        vis_layout.addWidget(details_label)
        
        # Add space at the bottom
        vis_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
        return vis_widget
