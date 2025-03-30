import sys
import os
import tempfile
from PyQt5.QtWidgets import QApplication, QMessageBox
from homepage import HomePage
from cracking_ui import PasswordCrackingUI
from wordlist_manager import WordlistManager
from hashcat_integration import HashcatIntegration
import subprocess

class PasswordCrackingTool:
    def __init__(self):
        self.app = QApplication(sys.argv)
        
        # Initialize components
        self.wordlist_manager = WordlistManager()
        self.hashcat_integration = HashcatIntegration()
        
        # Initialize UI components
        self.homepage = HomePage(self)
        self.cracking_ui = PasswordCrackingUI(self)
        
        # Show homepage initially
        self.show_homepage()
        
        # Execute application
        sys.exit(self.app.exec_())
    
    def show_homepage(self):
        """Switch to homepage view"""
        self.homepage.show()
        if hasattr(self, 'cracking_ui') and self.cracking_ui.isVisible():
            self.cracking_ui.hide()
    
    def show_cracking_ui(self):
        """Switch to password cracking UI view"""
        self.cracking_ui.show()
        self.homepage.hide()
    
    def quit_application(self):
        """Exit the application"""
        self.app.quit()
    
    def process_hash_file(self, original_hash_file):
        """
        Process a hash file that contains multiple hash types with labels
        and create separate files for each hash type.
        
        Returns a dictionary with hash types as keys and file paths as values.
        """
        hash_files = {}
        current_type = None
        temp_files = {}
        
        try:
            with open(original_hash_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                        
                    # Check if this is a header line
                    if line.startswith('#'):
                        # Extract hash type from header (e.g., "# MD5 Hashes" -> "MD5")
                        parts = line.split()
                        if len(parts) > 1:
                            current_type = parts[1]  # Get the hash type (MD5, SHA1, etc.)
                            
                            # Create temp file for this hash type if not already created
                            if current_type not in temp_files:
                                fd, temp_path = tempfile.mkstemp(suffix=f'_{current_type.lower()}.txt')
                                temp_files[current_type] = (os.fdopen(fd, 'w'), temp_path)
                    
                    # If not a header and we have a current type, write the hash
                    elif current_type and not line.startswith('#'):
                        temp_files[current_type][0].write(line + '\n')
        
            # Close all temp files
            for hash_type, (file_obj, file_path) in temp_files.items():
                file_obj.close()
                hash_files[hash_type] = file_path
                
            return hash_files
        except Exception as e:
            print(f"Error processing hash file: {e}")
            return {}
        
    def run_password_cracking(self, hash_file, hash_type, wordlist, custom_rules=None):
        """Coordinate the password cracking workflow"""
        # Prepare wordlist if needed
        if wordlist == "rockyou":
            wordlist_path = self.wordlist_manager.get_rockyou_path()
        elif wordlist == "seclists":
            wordlist_path = self.wordlist_manager.get_seclists_path()
        else:
            wordlist_path = wordlist
        
        # If no specific hash type is selected (Auto-detect) or file contains multiple hash types,
        # try to process the file to extract different hash types
        if not hash_type or hash_type == "Auto-detect":
            # Check if the file might contain multiple hash types
            with open(hash_file, 'r') as f:
                content = f.read()
                
            if '# MD5' in content or '# SHA' in content or '# NTLM' in content:
                # This appears to be a multi-hash type file
                self.cracking_ui.output_text.append("Detected a file with multiple hash types. Processing...")
                
                # Process the file to separate different hash types
                hash_files_by_type = self.process_hash_file(hash_file)
                
                if not hash_files_by_type:
                    # Error processing file
                    self.cracking_ui.output_text.append("ERROR: Could not process the hash file.")
                    return None
                
                # Display information about the separated files
                self.cracking_ui.output_text.append(f"Found {len(hash_files_by_type)} different hash types:")
                for h_type in hash_files_by_type.keys():
                    self.cracking_ui.output_text.append(f"  - {h_type}")
                
                # Choose the first hash type to start with
                first_type = list(hash_files_by_type.keys())[0]
                self.cracking_ui.output_text.append(f"\nStarting with {first_type} hashes...")
                
                # Convert hash type string to format option
                format_option = self.get_format_option(first_type)
                
                # Use the path for the first hash type
                hash_file_path = hash_files_by_type[first_type]
                
                # Use John the Ripper with explicit format
                cmd = ["john", f"--wordlist={wordlist_path}"]
                
                if format_option:
                    cmd.append(f"--format={format_option}")
                
                if custom_rules:
                    cmd.append(f"--rules={custom_rules}")
                    
                cmd.append(hash_file_path)
                
                # Run John the Ripper
                process = subprocess.Popen(
                    cmd, 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.PIPE,
                    universal_newlines=True
                )
                
                return process
            
        # For explicitly specified hash types or single-type files
        if hash_type in self.hashcat_integration.supported_hashes():
            # Use hashcat for supported hash types
            return self.hashcat_integration.crack_password(
                hash_file, hash_type, wordlist_path, custom_rules
            )
        else:
            # Use John the Ripper as default
            format_option = self.get_format_option(hash_type) if hash_type else None
            
            cmd = ["john", f"--wordlist={wordlist_path}"]
            
            if format_option:
                cmd.append(f"--format={format_option}")
                
            if custom_rules:
                cmd.append(f"--rules={custom_rules}")
                
            cmd.append(hash_file)
            
            # Run John the Ripper
            process = subprocess.Popen(
                cmd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            
            # Return process for UI to monitor
            return process
    
    def get_format_option(self, hash_type):
        """Convert hash type to John the Ripper format option"""
        if not hash_type:
            return None
            
        # Map hash types to John the Ripper format options
        format_mapping = {
            "MD5": "Raw-MD5",
            "SHA1": "Raw-SHA1",
            "SHA256": "Raw-SHA256",
            "SHA512": "Raw-SHA512",
            "NTLM": "NT",
            "NetNTLMv2": "NetNTLMv2",
            "MySQL": "mysql",
            "WPA/WPA2": "wpapsk"
        }
        
        return format_mapping.get(hash_type)

if __name__ == "__main__":
    PasswordCrackingTool()