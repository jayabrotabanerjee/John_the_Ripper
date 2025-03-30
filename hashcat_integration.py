import os
import subprocess
import platform
import shutil

class HashcatIntegration:
    def __init__(self):
        # Check for hashcat installation
        self.hashcat_path = self._find_hashcat()
        
    def _find_hashcat(self):
        """Try to find hashcat executable"""
        # Check if hashcat is in PATH
        hashcat_cmd = "hashcat.exe" if platform.system() == "Windows" else "hashcat"
        
        if shutil.which(hashcat_cmd):
            return hashcat_cmd
        
        # Common install locations
        possible_paths = []
        
        if platform.system() == "Windows":
            possible_paths = [
                r"C:\Program Files\hashcat\hashcat.exe",
                r"C:\hashcat\hashcat.exe",
                os.path.expanduser(r"~\hashcat\hashcat.exe")
            ]
        else:  # Linux/Mac
            possible_paths = [
                "/usr/bin/hashcat",
                "/usr/local/bin/hashcat",
                "/opt/hashcat/hashcat",
                os.path.expanduser("~/hashcat/hashcat")
            ]
            
        for path in possible_paths:
            if os.path.isfile(path):
                return path
                
        # Not found
        return None
        
    def is_available(self):
        """Check if hashcat is available"""
        return self.hashcat_path is not None
        
    def supported_hashes(self):
        """Return list of hash types supported by hashcat"""
        # Common hash types and their hashcat mode numbers
        return {
            "MD5": 0,
            "SHA1": 100, 
            "SHA256": 1400,
            "SHA512": 1700,
            "NTLM": 1000,
            "NetNTLMv2": 5600,
            "WPA/WPA2": 2500,
            "MySQL": 300
        }
        
    def crack_password(self, hash_file, hash_type, wordlist, custom_rules=None):
        """Use hashcat to crack passwords"""
        if not self.is_available():
            # Fall back to John if hashcat not available
            return self._fallback_to_john(hash_file, wordlist, custom_rules)
            
        # Get hashcat mode number for this hash type
        hash_modes = self.supported_hashes()
        mode = hash_modes.get(hash_type)
        
        if not mode:
            # Fall back to John if hash type not supported
            return self._fallback_to_john(hash_file, wordlist, custom_rules)
            
        # Build hashcat command
        cmd = [
            self.hashcat_path,
            "-m", str(mode),
            "-a", "0",  # Dictionary attack
            hash_file,
            wordlist
        ]
        
        # Add rules if specified
        if custom_rules and custom_rules.lower() != "none":
            cmd.extend(["-r", custom_rules])
            
        # Run hashcat
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        
        return process
        
    def _fallback_to_john(self, hash_file, wordlist, custom_rules=None):
        """Fall back to John the Ripper if hashcat is not available or hash type not supported"""
        cmd = ["john", f"--wordlist={wordlist}"]
        
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
        
        return process
