import os
import subprocess
import shutil
import zipfile
import requests
from pathlib import Path

class WordlistManager:
    def __init__(self):
        # Create data directory if it doesn't exist
        self.data_dir = os.path.join(os.path.expanduser("~"), ".password_cracker")
        self.wordlists_dir = os.path.join(self.data_dir, "wordlists")
        
        os.makedirs(self.wordlists_dir, exist_ok=True)
        
        # Paths to common wordlists
        self.rockyou_path = os.path.join(self.wordlists_dir, "rockyou.txt")
        self.seclists_dir = os.path.join(self.wordlists_dir, "seclists")
        
    def get_rockyou_path(self):
        """Get path to rockyou.txt, downloading if necessary"""
        if not os.path.exists(self.rockyou_path):
            self._download_rockyou()
        return self.rockyou_path
    
    def get_seclists_path(self):
        """Get path to SecLists password directory, downloading if necessary"""
        seclists_passwords = os.path.join(self.seclists_dir, "Passwords")
        if not os.path.exists(seclists_passwords):
            self._download_seclists()
        return os.path.join(seclists_passwords, "Leaked-Databases")
    
    def _download_rockyou(self):
        """Download rockyou.txt wordlist"""
        rockyou_url = "https://github.com/praetorian-inc/Hob0Rules/raw/master/wordlists/rockyou.txt.gz"
        
        try:
            # Download compressed file
            print("Downloading rockyou.txt...")
            response = requests.get(rockyou_url, stream=True)
            response.raise_for_status()
            
            # Save to temporary file
            temp_gz = os.path.join(self.wordlists_dir, "rockyou.txt.gz")
            with open(temp_gz, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # Extract using gunzip
            print("Extracting rockyou.txt...")
            subprocess.run(["gunzip", "-f", temp_gz])
            
            print("rockyou.txt downloaded successfully.")
        except Exception as e:
            print(f"Error downloading rockyou.txt: {e}")
            
            # Create an empty file to prevent repeated download attempts
            with open(self.rockyou_path, 'w') as f:
                f.write("# Error downloading rockyou.txt - please download manually")
    
    def _download_seclists(self):
        """Download SecLists repository (passwords section only)"""
        seclists_url = "https://github.com/danielmiessler/SecLists/archive/master.zip"
        
        try:
            # Create directory
            os.makedirs(self.seclists_dir, exist_ok=True)
            
            # Download zip file
            print("Downloading SecLists...")
            response = requests.get(seclists_url, stream=True)
            response.raise_for_status()
            
            # Save to temporary file
            temp_zip = os.path.join(self.wordlists_dir, "seclists.zip")
            with open(temp_zip, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # Extract only the Passwords directory
            print("Extracting SecLists password files...")
            with zipfile.ZipFile(temp_zip, 'r') as zip_ref:
                for file in zip_ref.namelist():
                    if file.startswith('SecLists-master/Passwords/'):
                        # Extract with correct path structure
                        target_path = os.path.join(
                            self.seclists_dir, 
                            file.replace('SecLists-master/', '')
                        )
                        
                        # Create directories if needed
                        os.makedirs(os.path.dirname(target_path), exist_ok=True)
                        
                        # Don't extract directories
                        if not file.endswith('/'):
                            with zip_ref.open(file) as source, open(target_path, 'wb') as target:
                                shutil.copyfileobj(source, target)
            
            # Clean up
            os.remove(temp_zip)
            print("SecLists password files downloaded successfully.")
        except Exception as e:
            print(f"Error downloading SecLists: {e}")
            
            # Create a marker file
            os.makedirs(os.path.join(self.seclists_dir, "Passwords"), exist_ok=True)
            with open(os.path.join(self.seclists_dir, "Passwords", "README.txt"), 'w') as f:
                f.write("# Error downloading SecLists - please download manually")
