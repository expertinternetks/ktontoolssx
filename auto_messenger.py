"""
Facebook Auto Messenger - Fully Automated
Përdor sesionin e ruajtur - nuk duhet login!
"""

import os
import sys
import time
import random
import json
import logging
from datetime import datetime
from pathlib import Path
# import tkinter as tk
# from tkinter import ttk, scrolledtext, messagebox
import threading
import pyperclip

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
except ImportError:
    print("Error: Selenium not installed. Run: pip install selenium")
    sys.exit(1)


class FacebookAutoMessenger:
    """Main automation class - fully automated"""
    
    def __init__(self, config_file="config.json"):
        self.config_file = config_file
        self.driver = None
        self.is_running = False
        self.should_stop = False
        self.visited_profiles = set()  # Track visited profiles
        self.visited_profiles_file = "visited_profiles_history.json"  # File to save visited profiles
        self.message_count = 0  # Track how many messages sent
        self.post_count = 0  # Track how many posts made
        self.posted_groups = set()  # Track groups where we posted
        self.posted_groups_file = "posted_groups_history.json"  # File to save posted groups
        self.commented_groups = set()  # Track groups where we commented
        self.commented_groups_file = "commented_groups_history.json"  # File to save commented groups
        
        # Statistics tracking
        self.stats_file = "statistics.json"
        self.stats = {
            'total_posts': 0,
            'total_comments': 0,
            'total_messages': 0,
            'total_friend_requests': 0,
            'total_groups_contacted': 0,
            'last_updated': None
        }
        
        # HARDCODED list of German job/work from home groups - NO SEARCH!
        self.german_job_groups = [
            "https://www.facebook.com/groups/homeofficejobs.deutschland",
            "https://www.facebook.com/groups/jobsingermany",
            "https://www.facebook.com/groups/onlinejobsgermany",
            "https://www.facebook.com/groups/werbungprofessional",
            "https://www.facebook.com/groups/JobsAusStuttgart",
            "https://www.facebook.com/groups/StellenangeboteBerlin",
            "https://www.facebook.com/groups/jobsinmunich",
            "https://www.facebook.com/groups/jobsinhamburg",
            "https://www.facebook.com/groups/jobsberlin",
            "https://www.facebook.com/groups/freelancersgermany",
            "https://www.facebook.com/groups/remoteworkgermany",
            "https://www.facebook.com/groups/deutschlandjobs",
            "https://www.facebook.com/groups/jobsimauslandjobsquad",
            "https://www.facebook.com/groups/germany.mlm",
            "https://www.facebook.com/groups/jobsdigital",
        ]
        
        # Post template for groups
        self.group_post_text = """Hallo! 😊
Wir haben eine neue Bewertungsplattform ins Leben gerufen.
🏠 Flexibel von zu Hause aus arbeiten
✅ Kostenlose Anmeldung ohne Verpflichtung
💶 1 € Vergütung pro abgegebener Bewertung
👉 Jetzt registrieren: https://www.global-feedback.com/"""
        
        # Comment template for posts - SAME AS POST TEMPLATE!
        self.comment_template = """Hallo! 😊
Wir haben eine neue Bewertungsplattform ins Leben gerufen.
🏠 Flexibel von zu Hause aus arbeiten
✅ Kostenlose Anmeldung ohne Verpflichtung
💶 1 € Vergütung pro abgegebener Bewertung
👉 Jetzt registrieren: https://www.global-feedback.com/"""
        
        # Multiple message templates for variation (anti-spam)
        self.message_templates = [
            # Template 1
            """Hallo!

Mochtest du nebenbei etwas Geld verdienen?

Bei Global Feedback kannst du Produkte testen und Bewertungen schreiben.

Vorteile:
- Flexible Arbeitszeiten von zu Hause
- 1 Euro pro Bewertung
- Kostenlose Registrierung

Mehr Infos hier:
www.global-feedback.com""",
            
            # Template 2
            """Guten Tag!

Ich wollte dir eine interessante Moglichkeit vorstellen:

Global Feedback ist eine Plattform wo du fur Produktbewertungen bezahlt wirst.

Das bieten wir:
- Arbeit von zu Hause aus
- 1 Euro pro Bewertung
- Keine Verpflichtungen

Schau mal rein:
www.global-feedback.com""",
            
            # Template 3
            """Hey!

Kennst du schon Global Feedback?

Du kannst dort Produkte testen und fur deine Meinung bezahlt werden.

Einfach:
- Online von zu Hause arbeiten
- 1 Euro fur jede Bewertung
- Kostenlos anmelden

Hier anmelden:
www.global-feedback.com""",
            
            # Template 4
            """Hallo!

Suchst du nach einer flexiblen Nebenbeschäftigung?

Bei Global Feedback bezahlen wir dich fur ehrliche Produktbewertungen.

Details:
- Flexibel von zu Hause
- 1 Euro Vergutung pro Bewertung
- Gratis Registration

Mehr erfahren:
www.global-feedback.com""",
            
            # Template 5
            """Hi!

Ich habe etwas Interessantes gefunden:

Global Feedback zahlt fur Produkttests und Bewertungen.

Warum mitmachen:
- Arbeite wann und wo du willst
- 1 Euro pro abgegebener Bewertung
- Keine Kosten

Jetzt starten:
www.global-feedback.com"""
        ]
        
        self._setup_logging()
        self._load_posted_groups()  # Load history AFTER logging setup
        self._load_visited_profiles()  # Load visited profiles history
        self._load_commented_groups()  # Load commented groups history
        self._load_stats()  # Load statistics
    
    def _load_posted_groups(self):
        """Load posted groups history from file"""
        try:
            if os.path.exists(self.posted_groups_file):
                with open(self.posted_groups_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.posted_groups = set(data.get('posted_groups', []))
                    self.logger.info(f"📂 Loaded {len(self.posted_groups)} groups from history")
        except Exception as e:
            self.logger.warning(f"Could not load posted groups history: {e}")
            self.posted_groups = set()
    
    def _save_posted_groups(self):
        """Save posted groups history to file"""
        try:
            with open(self.posted_groups_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'posted_groups': list(self.posted_groups),
                    'last_updated': datetime.now().isoformat()
                }, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.warning(f"Could not save posted groups history: {e}")
    
    def _load_visited_profiles(self):
        """Load visited profiles history from file"""
        try:
            if os.path.exists(self.visited_profiles_file):
                with open(self.visited_profiles_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.visited_profiles = set(data.get('visited_profiles', []))
                    self.logger.info(f"📂 Loaded {len(self.visited_profiles)} visited profiles from history")
        except Exception as e:
            self.logger.warning(f"Could not load visited profiles history: {e}")
            self.visited_profiles = set()
    
    def _save_visited_profiles(self):
        """Save visited profiles history to file"""
        try:
            with open(self.visited_profiles_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'visited_profiles': list(self.visited_profiles),
                    'last_updated': datetime.now().isoformat()
                }, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.warning(f"Could not save visited profiles history: {e}")
    
    def _load_commented_groups(self):
        """Load commented groups history from file"""
        try:
            if os.path.exists(self.commented_groups_file):
                with open(self.commented_groups_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.commented_groups = set(data.get('commented_groups', []))
                    self.logger.info(f"📂 Loaded {len(self.commented_groups)} commented groups from history")
        except Exception as e:
            self.logger.warning(f"Could not load commented groups history: {e}")
            self.commented_groups = set()
    
    def _save_commented_groups(self):
        """Save commented groups history to file"""
        try:
            with open(self.commented_groups_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'commented_groups': list(self.commented_groups),
                    'last_updated': datetime.now().isoformat()
                }, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.warning(f"Could not save commented groups history: {e}")
    
    def _load_stats(self):
        """Load statistics from file"""
        try:
            if os.path.exists(self.stats_file):
                with open(self.stats_file, 'r', encoding='utf-8') as f:
                    self.stats = json.load(f)
                    self.logger.info(f"📊 Statistikat: {self.stats['total_posts']} postime, {self.stats['total_comments']} komente, {self.stats['total_messages']} mesazhe, {self.stats['total_friend_requests']} shokë")
        except Exception as e:
            self.logger.warning(f"Could not load stats: {e}")
    
    def _save_stats(self):
        """Save statistics to file"""
        try:
            self.stats['last_updated'] = datetime.now().isoformat()
            self.stats['total_groups_contacted'] = len(self.posted_groups) + len(self.commented_groups)
            with open(self.stats_file, 'w', encoding='utf-8') as f:
                json.dump(self.stats, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.warning(f"Could not save stats: {e}")
        
    def _setup_logging(self):
        """Setup logging"""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        log_file = log_dir / f"automation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def init_driver(self):
        """Initialize driver with saved session"""
        try:
            chrome_options = Options()
            
            user_data_dir = os.path.join(os.getcwd(), "chrome_profile")
            chrome_options.add_argument(f"user-data-dir={user_data_dir}")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            chrome_options.add_argument("--disable-notifications")
            chrome_options.add_argument("--lang=de-DE")
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.maximize_window()
            self.logger.info("✅ WebDriver initialized - Duke përdorur sesionin e ruajtur")
            return True
            
        except Exception as e:
            self.logger.error(f"Error initializing WebDriver: {e}")
            return False
    
    def check_login(self):
        """Check if already logged in"""
        try:
            self.driver.get("https://www.facebook.com")
            time.sleep(3)
            
            if "login" in self.driver.current_url.lower():
                self.logger.error("❌ Not logged in! Please login first manually.")
                return False
            
            self.logger.info("✅ Already logged in - Duke filluar automatizimin!")
            return True
            
        except Exception as e:
            self.logger.error(f"Login check error: {e}")
            return False
    
    def get_group_members(self, group_url):
        """Get clickable member elements - ONLY new members, NOT admins"""
        try:
            clean_url = group_url.rstrip('/')
            members_url = f"{clean_url}/members"
            self.logger.info(f"📋 Duke hapur faqen e members: {members_url}")
            
            self.driver.get(members_url)
            time.sleep(random.uniform(3, 5))
            
            member_profiles = []  # Store profile URLs, not elements (to avoid stale)
            scroll_attempts = 15
            
            for i in range(scroll_attempts):
                if self.should_stop:
                    break
                    
                # Scroll down
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(random.uniform(1, 2))
                
                current_count = len(member_profiles)
                
                # Find all list items with "Joined" text (NEW members, NOT admins)
                try:
                    list_items = self.driver.find_elements(By.XPATH, "//div[@role='listitem']")
                    
                    for item in list_items:
                        try:
                            item_text = item.text.lower()
                            
                            # SKIP admins and moderators
                            if 'admin' in item_text or 'moderator' in item_text:
                                continue
                            
                            # ONLY take members with "Joined" (new members)
                            if 'joined' not in item_text:
                                continue
                            
                            # Get profile link (NOT image link)
                            profile_links = item.find_elements(By.XPATH, ".//a[@role='link']")
                            for link in profile_links:
                                try:
                                    href = link.get_attribute('href')
                                    if href and ('/user/' in href or '/profile.php' in href):
                                        # Make sure it's not a duplicate and not visited
                                        if href not in member_profiles and href not in self.visited_profiles:
                                            member_profiles.append(href)
                                            break  # Only first profile link
                                except:
                                    continue
                        except:
                            continue
                except Exception as e:
                    self.logger.error(f"Error finding members: {e}")
                
                new_count = len(member_profiles)
                self.logger.info(f"Scroll {i+1}/{scroll_attempts}: U gjetën {new_count} members të rinj (PA ADMIN)")
                
                if new_count >= 100:
                    self.logger.info("✅ U gjetën mjaftueshëm members, duke ndaluar scroll")
                    break
                    
                if new_count == current_count and i > 5:
                    self.logger.info("✅ Nuk ka më members të rinj")
                    break
            
            self.logger.info(f"✅ Total members të rinj (pa admin): {len(member_profiles)}")
            return member_profiles
            
        except Exception as e:
            self.logger.error(f"Error getting members: {e}")
            return []
    
    def add_friend_from_list(self, member_element):
        """Add friend directly from members list - Target yellow buttons"""
        try:
            # Scroll element into view
            try:
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", member_element)
                time.sleep(random.uniform(0.3, 0.7))
            except:
                pass
            
            # Find "Add friend" button - MANY strategies
            add_friend_button = None
            
            # Strategy 1: Find by exact text "Add friend"
            try:
                buttons = member_element.find_elements(By.XPATH, ".//span[contains(text(), 'Add friend')]/ancestor::div[@role='button']")
                if buttons:
                    for btn in buttons:
                        if btn.is_displayed():
                            add_friend_button = btn
                            break
            except:
                pass
            
            # Strategy 2: Find by aria-label
            if not add_friend_button:
                try:
                    buttons = member_element.find_elements(By.XPATH, ".//div[@aria-label='Add friend'][@role='button']")
                    if buttons:
                        for btn in buttons:
                            if btn.is_displayed():
                                add_friend_button = btn
                                break
                except:
                    pass
            
            # Strategy 3: Find any button with "friend" in aria-label
            if not add_friend_button:
                try:
                    buttons = member_element.find_elements(By.XPATH, ".//div[@role='button'][contains(@aria-label, 'friend')]")
                    if buttons:
                        for btn in buttons:
                            if btn.is_displayed() and 'add' in btn.get_attribute('aria-label').lower():
                                add_friend_button = btn
                                break
                except:
                    pass
            
            # Strategy 4: Find button that contains span with "Add friend" text (more flexible)
            if not add_friend_button:
                try:
                    buttons = member_element.find_elements(By.XPATH, ".//div[@role='button']")
                    for btn in buttons:
                        try:
                            if btn.is_displayed():
                                btn_text = btn.text.lower()
                                if 'add friend' in btn_text or 'freund' in btn_text:
                                    add_friend_button = btn
                                    break
                        except:
                            continue
                except:
                    pass
            
            if not add_friend_button:
                return False
            
            # Click Add Friend button
            try:
                # Try JavaScript click first (most reliable)
                self.driver.execute_script("arguments[0].click();", add_friend_button)
                time.sleep(random.uniform(0.5, 1))
                return True
            except:
                try:
                    # Fallback to regular click
                    add_friend_button.click()
                    time.sleep(random.uniform(0.5, 1))
                    return True
                except:
                    return False
            
        except Exception as e:
            return False
    
    def send_message(self, profile_url):
        """Send message to user - Using PASTE for text"""
        try:
            # Check if already visited (CRITICAL - no duplicates!)
            if profile_url in self.visited_profiles:
                self.logger.warning(f"⚠️ Profili tashmë i vizituar - SKIP: {profile_url}")
                return False
            
            self.logger.info(f"📧 Duke hapur profilin: {profile_url}")
            self.driver.get(profile_url)
            time.sleep(random.uniform(4, 7))  # Më i gjatë për të duket human
            
            # Mark as visited IMMEDIATELY after opening
            self.visited_profiles.add(profile_url)
            self._save_visited_profiles()  # Save to file immediately
            
            # Find message button
            message_button_xpaths = [
                "//div[@aria-label='Message'][@role='button']",
                "//div[@aria-label='Nachricht senden'][@role='button']",
                "//span[text()='Message']/ancestor::div[@role='button']",
            ]
            
            message_button = None
            for xpath in message_button_xpaths:
                try:
                    message_button = WebDriverWait(self.driver, 3).until(
                        EC.presence_of_element_located((By.XPATH, xpath))
                    )
                    if message_button.is_displayed():
                        break
                except:
                    continue
            
            if not message_button:
                self.logger.warning("❌ Message button not found - skipping")
                return False
            
            # Click message button
            try:
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", message_button)
                time.sleep(random.uniform(0.5, 1.5))  # Më human-like
                self.driver.execute_script("arguments[0].click();", message_button)
            except:
                message_button.click()
            
            time.sleep(random.uniform(4, 6))  # Më i gjatë për të loading-uar chat
            
            # Find message input
            message_input_xpaths = [
                "//div[@contenteditable='true'][@role='textbox']",
                "//div[@contenteditable='true'][@aria-label]",
                "//textarea[@placeholder]",
            ]
            
            message_input = None
            for xpath in message_input_xpaths:
                try:
                    message_input = WebDriverWait(self.driver, 3).until(
                        EC.presence_of_element_located((By.XPATH, xpath))
                    )
                    if message_input.is_displayed():
                        break
                except:
                    continue
            
            if not message_input:
                self.logger.warning("❌ Message input not found")
                return False
            
            # PASTE message (më i shpejtë dhe pa probleme me emoji)
            message_input.click()
            time.sleep(random.uniform(0.8, 1.5))  # Më human-like
            
            # SELECT MESSAGE TEMPLATE - rotate through templates for variation
            template_index = self.message_count % len(self.message_templates)
            selected_message = self.message_templates[template_index]
            
            # Copy to clipboard
            pyperclip.copy(selected_message)
            time.sleep(0.3)  # Small pause
            
            # Paste using CTRL+V
            message_input.send_keys(Keys.CONTROL, 'v')
            time.sleep(random.uniform(1.5, 2.5))  # Më i gjatë për të duket real
            
            # Increment message counter
            self.message_count += 1
            
            # Send
            message_input.send_keys(Keys.ENTER)
            
            # Update statistics
            self.stats['total_messages'] += 1
            self._save_stats()
            
            self.logger.info(f"✅ Mesazhi u dërgua me sukses! | 📊 Total: {self.stats['total_messages']} mesazhe")
            time.sleep(1)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error sending message: {e}")
            return False
    
    def run_add_friends(self, max_requests=20, group_url="https://www.facebook.com/groups/werbungprofessional/"):
        """Add friends automation - DIRECTLY from members list (FAST)"""
        try:
            self.is_running = True
            self.should_stop = False
            
            if not self.init_driver():
                return False
            
            if not self.check_login():
                return False
            
            requests_sent = 0
            
            self.logger.info(f"\n=== Duke filluar ADD FRIEND automation (FAST MODE) ===")
            self.logger.info(f"Grupi: {group_url}")
            self.logger.info(f"Max requests: {max_requests}\n")
            
            # Navigate to members page
            clean_url = group_url.rstrip('/')
            members_url = f"{clean_url}/members"
            self.logger.info(f"📋 Duke hapur faqen e members: {members_url}")
            
            self.driver.get(members_url)
            time.sleep(random.uniform(3, 5))
            
            # Process members SLOWLY - check each one before scrolling
            processed_members = set()  # Track which members we've already checked
            scroll_attempts = 0
            max_scrolls = 100
            consecutive_no_new = 0
            
            while requests_sent < max_requests and scroll_attempts < max_scrolls:
                if self.should_stop:
                    break
                
                scroll_attempts += 1
                self.logger.info(f"\n--- Scroll #{scroll_attempts} - Checking visible members ---")
                
                # Find all CURRENTLY VISIBLE list items
                try:
                    list_items = self.driver.find_elements(By.XPATH, "//div[@role='listitem']")
                    self.logger.info(f"Found {len(list_items)} list items on screen")
                    
                    found_new_members = False
                    
                    for item in list_items:
                        if self.should_stop or requests_sent >= max_requests:
                            break
                        
                        try:
                            # Get unique identifier for this member
                            try:
                                member_link = item.find_element(By.XPATH, ".//a[@role='link']")
                                member_id = member_link.get_attribute('href')
                            except:
                                continue
                            
                            # Skip if already processed
                            if member_id in processed_members:
                                continue
                            
                            # Mark as processed
                            processed_members.add(member_id)
                            found_new_members = True
                            
                            item_text = item.text.lower()
                            
                            # SKIP admins
                            if 'admin' in item_text or 'moderator' in item_text:
                                self.logger.info(f"  ⚠️ Skipping admin/moderator")
                                continue
                            
                            # ONLY new members with "Joined"
                            if 'joined' not in item_text:
                                continue
                            
                            # Try to add friend directly from list
                            self.logger.info(f"  👤 Duke kontrolluar member: {member_id}")
                            success = self.add_friend_from_list(item)
                            
                            if success:
                                requests_sent += 1
                                # Update statistics
                                self.stats['total_friend_requests'] += 1
                                self._save_stats()
                                self.logger.info(f"  ✅ Friend request #{requests_sent}/{max_requests} u dërgua! | 📊 Total: {self.stats['total_friend_requests']} shokë")
                                
                                if requests_sent < max_requests:
                                    # Short delay
                                    delay = random.uniform(5, 10)
                                    self.logger.info(f"  ⏳ Pritje {delay:.1f}s...")
                                    time.sleep(delay)
                            else:
                                self.logger.info(f"  ❌ Nuk ka Add Friend button për këtë member")
                        
                        except Exception as e:
                            continue
                    
                    # If no new members found, track it
                    if not found_new_members:
                        consecutive_no_new += 1
                        self.logger.info(f"⚠️ Nuk u gjetën members të rinj ({consecutive_no_new}/3)")
                        
                        if consecutive_no_new >= 3:
                            self.logger.info("✅ Arrived at end of list")
                            break
                    else:
                        consecutive_no_new = 0
                    
                except Exception as e:
                    self.logger.error(f"Error processing list: {e}")
                
                # Scroll down SLOWLY (200-300 pixels) to load more
                if requests_sent < max_requests:
                    self.driver.execute_script("window.scrollBy(0, 250);")
                    time.sleep(random.uniform(2, 4))  # Wait for new members to load
                    self.logger.info(f"Totali dëri tani: {requests_sent}/{max_requests} friend requests")
            
            self.logger.info(f"\n=== ✅ PERFUNDOI! Totali: {requests_sent}/{max_requests} friend requests ===")
            return True
            
        except Exception as e:
            self.logger.error(f"Automation error: {e}")
            return False
        finally:
            self.is_running = False
    
    def run_automation(self, max_messages=50, group_url="https://www.facebook.com/groups/werbungprofessional/"):
        """Main automation loop - SEND MESSAGES"""
        try:
            self.is_running = True
            self.should_stop = False
            
            if not self.init_driver():
                return False
            
            if not self.check_login():
                return False
            
            messages_sent = 0
            
            self.logger.info(f"\n=== Duke filluar automatizimin ===")
            self.logger.info(f"Grupi: {group_url}")
            self.logger.info(f"Max mesazhe: {max_messages}\n")
            
            # Get ALL members once at the beginning
            self.logger.info(f"\n🔄 Duke gjetur members...")
            member_profiles = self.get_group_members(group_url)
            
            if not member_profiles:
                self.logger.error("❌ Nuk u gjetën members!")
                return False
            
            self.logger.info(f"✅ Gjeti {len(member_profiles)} members. Duke filluar dërgimin...\n")
            
            # Process members ONE BY ONE in order (1, 2, 3...)
            for index, profile_url in enumerate(member_profiles, start=1):
                if self.should_stop or messages_sent >= max_messages:
                    break
                
                self.logger.info(f"\n👤 Personi {index}/{len(member_profiles)}")
                self.logger.info(f"   URL: {profile_url}")
                
                message_sent_success = self.send_message(profile_url)
                
                if message_sent_success:
                    messages_sent += 1
                    self.logger.info(f"📊 Totali: {messages_sent}/{max_messages} mesazhe")
                    
                    if messages_sent < max_messages:
                        # Delays më të gjata për të shmangur bllokim
                        # Randomize 2-4 minuta për të duket human
                        delay = random.uniform(120, 240)  # 2-4 minuta
                        self.logger.info(f"⏳ Pritje {delay/60:.1f} minuta...")
                        time.sleep(delay)
                else:
                    small_delay = random.uniform(5, 10)  # Më i gjatë nëse nuk dërgohet
                    self.logger.info(f"➡️ Duke vazhduar tek personi tjetër ({small_delay:.1f}s)")
                    time.sleep(small_delay)
            
            self.logger.info(f"\n=== ✅ PERFUNDOI! Totali: {messages_sent}/{max_messages} ===")
            return True
            
        except Exception as e:
            self.logger.error(f"Automation error: {e}")
            return False
        finally:
            self.is_running = False
    
    def search_german_groups(self, city_name, max_groups=10):
        """Search for public German groups in a city"""
        try:
            # Construct search URL for groups in German
            search_query = f"{city_name} Germany jobs home office"
            search_url = f"https://www.facebook.com/search/groups/?q={search_query.replace(' ', '%20')}"
            
            self.logger.info(f"🔍 Duke kërkuar grupe për: {city_name}")
            self.driver.get(search_url)
            time.sleep(random.uniform(4, 7))
            
            # Scroll to load groups
            for _ in range(5):
                self.driver.execute_script("window.scrollBy(0, 500);")
                time.sleep(random.uniform(1, 2))
            
            # Find group links - FILTER PROPERLY
            group_links = []
            seen_group_ids = set()  # Track unique group IDs
            
            try:
                # Find all links that contain /groups/
                links = self.driver.find_elements(By.XPATH, "//a[contains(@href, '/groups/')]")
                
                for link in links:
                    try:
                        href = link.get_attribute('href')
                        if not href or '/groups/' not in href:
                            continue
                        
                        # Clean URL - remove query params and trailing slash
                        clean_href = href.split('?')[0].split('#')[0].rstrip('/')
                        
                        # FILTER: Only accept direct group URLs, NOT search or posts
                        # Valid: https://www.facebook.com/groups/GROUPNAME or /groups/123456
                        # Invalid: /groups/search/, /groups/123/posts/, /groups/123/permalink/
                        if '/search' in clean_href or '/posts/' in clean_href or '/permalink/' in clean_href:
                            continue
                        
                        # Extract group ID (name or number)
                        parts = clean_href.split('/groups/')
                        if len(parts) < 2:
                            continue
                        
                        group_id = parts[1].split('/')[0]  # Get first part after /groups/
                        
                        # Skip if we've seen this group already
                        if group_id in seen_group_ids:
                            continue
                        
                        # Add to list
                        seen_group_ids.add(group_id)
                        group_links.append(clean_href)
                        
                        if len(group_links) >= max_groups:
                            break
                            
                    except:
                        continue
            except Exception as e:
                self.logger.error(f"Error finding groups: {e}")
            
            self.logger.info(f"✅ Gjeti {len(group_links)} grupe UNIQUE për {city_name}")
            return group_links
            
        except Exception as e:
            self.logger.error(f"Error searching groups for {city_name}: {e}")
            return []
    
    def post_to_group(self, group_url, image_path=None):
        """Post text + all 4 images to a Facebook group"""
        try:
            # Check if already posted to this group
            if group_url in self.posted_groups:
                self.logger.warning(f"⚠️ Tashmë kemi postuar në këtë grup - SKIP: {group_url}")
                return False
            
            self.logger.info(f"📝 Duke postuar në grupin: {group_url}")
            
            # Navigate to group
            self.driver.get(group_url)
            time.sleep(random.uniform(5, 8))
            
            # Check for "Participation review" popup and accept group rules
            try:
                time.sleep(2)  # Wait for popup to appear
                
                # Look for "I agree to the group rules" checkbox - MORE AGGRESSIVE
                self.logger.info("🔍 Duke kërkuar group rules checkbox...")
                
                agree_checkbox_xpaths = [
                    # Direct checkbox with text nearby
                    "//span[contains(text(), 'I agree to the group rules')]/..//input[@type='checkbox']",
                    "//span[contains(text(), 'I agree to the group rules')]/preceding-sibling::input[@type='checkbox']",
                    "//label[contains(., 'I agree to the group rules')]//input[@type='checkbox']",
                    # Checkbox by role
                    "//div[@role='checkbox'][contains(@aria-label, 'agree')]",
                    "//input[@type='checkbox'][contains(@aria-label, 'agree')]",
                    # Any checkbox near "group rules" text
                    "//*[contains(text(), 'group rules')]/ancestor::div[3]//input[@type='checkbox']",
                ]
                
                checkbox_found = False
                for xpath in agree_checkbox_xpaths:
                    try:
                        checkboxes = self.driver.find_elements(By.XPATH, xpath)
                        for checkbox in checkboxes:
                            try:
                                if checkbox.is_displayed():
                                    # Scroll to checkbox
                                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", checkbox)
                                    time.sleep(0.5)
                                    
                                    # Click checkbox with multiple methods
                                    try:
                                        self.driver.execute_script("arguments[0].click();", checkbox)
                                    except:
                                        try:
                                            checkbox.click()
                                        except:
                                            # Click parent element
                                            parent = checkbox.find_element(By.XPATH, "..")
                                            self.driver.execute_script("arguments[0].click();", parent)
                                    
                                    self.logger.info("✅ Checkbox u klikua!")
                                    checkbox_found = True
                                    time.sleep(1)
                                    break
                            except Exception as e:
                                continue
                        if checkbox_found:
                            break
                    except:
                        continue
                
                if checkbox_found:
                    # Find and click Submit button
                    self.logger.info("🔍 Duke kërkuar Submit button...")
                    submit_button_xpaths = [
                        "//div[@aria-label='Submit'][@role='button']",
                        "//button[contains(text(), 'Submit')]",
                        "//div[@role='button'][contains(., 'Submit')]",
                    ]
                    
                    for xpath in submit_button_xpaths:
                        try:
                            buttons = self.driver.find_elements(By.XPATH, xpath)
                            for btn in buttons:
                                if btn.is_displayed():
                                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
                                    time.sleep(0.5)
                                    try:
                                        self.driver.execute_script("arguments[0].click();", btn)
                                    except:
                                        btn.click()
                                    self.logger.info("✅ Submit button clicked!")
                                    time.sleep(random.uniform(2, 3))
                                    break
                            break
                        except:
                            continue
                else:
                    self.logger.info("ℹ️ No checkbox found - group rules më parë të pranuar ose s'ka")
            except Exception as e:
                self.logger.info(f"Group rules: {e}")
            
            # SKIP private check - try posting anyway!
            self.logger.info("✅ Duke vazhduar me posting (no private check)...")
            
            # SCROLL TO FIND WRITE SOMETHING
            self.logger.info("📜 Duke bërë scroll për të gjetur Write something...")
            for _ in range(3):
                self.driver.execute_script("window.scrollBy(0, 400);")
                time.sleep(1)
            
            # DIREKT gjen YELLOW "Write something" box!
            self.logger.info("📝 Duke kërkuar YELLOW Write something box...")
            text_input_xpaths = [
                # Most specific - the yellow "Write something" in German
                "//span[contains(text(), 'Schreibe etwas')]",
                "//span[contains(text(), 'Write something')]",
                "//div[contains(@aria-label, 'Schreibe etwas')]",
                "//div[contains(@aria-label, 'Write something')]",
                # Contenteditable as fallback
                "//div[@contenteditable='true'][@role='textbox']",
                "//div[contains(@aria-placeholder, 'Create a public post')]",
            ]
            
            text_input = None
            for xpath in text_input_xpaths:
                try:
                    inputs = self.driver.find_elements(By.XPATH, xpath)
                    for inp in inputs:
                        try:
                            if inp.is_displayed():
                                text_input = inp
                                self.logger.info(f"✅ U gjet text input: {xpath}")
                                break
                        except:
                            continue
                    if text_input:
                        break
                except:
                    continue
            
            if not text_input:
                self.logger.warning("❌ Nuk u gjet text input")
                return False
            
            # CLICK on the "Write something" to open modal
            try:
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", text_input)
                time.sleep(0.5)
                # Try multiple click methods
                try:
                    text_input.click()
                except:
                    self.driver.execute_script("arguments[0].click();", text_input)
                
                self.logger.info("✅ Write something u klikua - modal po hapet")
                time.sleep(random.uniform(3, 5))  # WAIT for modal to open
            except Exception as e:
                self.logger.error(f"Error clicking Write something: {e}")
                return False
            
            # NOW find input INSIDE the modal
            self.logger.info("🔍 Duke kërkuar input BRENDA modalit...")
            modal_input_xpaths = [
                "//div[contains(@aria-label, 'Create a public post')]",
                "//div[contains(@aria-placeholder, 'Create a public post')]",
                "//div[@contenteditable='true'][@role='textbox']",
                "//div[contains(text(), 'Create a public post')]/ancestor::div[@contenteditable='true']",
            ]
            
            modal_input = None
            for xpath in modal_input_xpaths:
                try:
                    inputs = self.driver.find_elements(By.XPATH, xpath)
                    for inp in inputs:
                        try:
                            if inp.is_displayed() and inp.is_enabled():
                                modal_input = inp
                                self.logger.info(f"✅ U gjet modal input: {xpath}")
                                break
                        except:
                            continue
                    if modal_input:
                        break
                except:
                    continue
            
            if not modal_input:
                self.logger.warning("❌ Nuk u gjet modal input")
                return False
            
            # Click inside modal input to focus it
            try:
                modal_input.click()
                self.logger.info("✅ Modal input u klikua")
                time.sleep(1)
            except Exception as e:
                self.logger.error(f"Error clicking modal input: {e}")
                return False
            
            # PASTE text in modal input
            self.logger.info("✍️ Duke bërë paste tekstin në modal...")
            text_entered = False
            
            # Method 1: Use clipboard paste (most reliable for Facebook)
            try:
                pyperclip.copy(self.group_post_text)
                time.sleep(0.3)
                modal_input.send_keys(Keys.CONTROL, 'v')
                time.sleep(1)
                text_entered = True
                self.logger.info("✅ Teksti u fut me paste")
            except Exception as e:
                self.logger.warning(f"Paste failed: {e}")
            
            # Method 2: Send keys directly (fallback)
            if not text_entered:
                try:
                    modal_input.send_keys(self.group_post_text)
                    time.sleep(1)
                    text_entered = True
                    self.logger.info("✅ Teksti u fut me send_keys")
                except Exception as e:
                    self.logger.warning(f"Send keys failed: {e}")
            
            # Method 3: JavaScript (last resort)
            if not text_entered:
                try:
                    self.driver.execute_script(
                        "arguments[0].textContent = arguments[1]; arguments[0].innerText = arguments[1];",
                        text_input,
                        self.group_post_text
                    )
                    time.sleep(0.5)
                    # Trigger events
                    self.driver.execute_script(
                        "arguments[0].dispatchEvent(new Event('input', { bubbles: true })); arguments[0].dispatchEvent(new Event('change', { bubbles: true }));",
                        text_input
                    )
                    time.sleep(1)
                    text_entered = True
                    self.logger.info("✅ Teksti u fut me JavaScript")
                except Exception as e:
                    self.logger.error(f"All text entry methods failed: {e}")
                    return False
            
            time.sleep(random.uniform(1, 2))
            
            # STEP 3: Find and click photo/video button IN MODAL
            self.logger.info("📸 Duke kërkuar Photo button në modal...")
            
            # Look for photo button in modal - more specific
            photo_button_xpaths = [
                # German version
                "//div[@aria-label='Foto/Video'][@role='button']",
                "//span[contains(text(), 'Foto/Video')]/parent::div[@role='button']",
                # English version
                "//div[@aria-label='Photo/video'][@role='button']",
                "//span[contains(text(), 'Photo/video')]/parent::div[@role='button']",
                # Generic - find button with image icon
                "//div[contains(text(), 'Add to your post')]/..//div[@role='button']",
            ]
            
            photo_button = None
            for xpath in photo_button_xpaths:
                try:
                    buttons = self.driver.find_elements(By.XPATH, xpath)
                    for btn in buttons:
                        try:
                            if btn.is_displayed():
                                # Check if it looks like a photo button (has icon or svg)
                                btn_html = btn.get_attribute('innerHTML')
                                if 'svg' in btn_html or 'image' in btn.get_attribute('aria-label').lower():
                                    photo_button = btn
                                    self.logger.info(f"✅ U gjet photo button: {xpath}")
                                    break
                        except:
                            continue
                    if photo_button:
                        break
                except:
                    continue
            
            if not photo_button:
                self.logger.warning("⚠️ Nuk u gjet photo button - duke postuar vetëm tekst")
            else:
                try:
                    # Scroll and click photo button
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", photo_button)
                    time.sleep(0.5)
                    self.driver.execute_script("arguments[0].click();", photo_button)
                    self.logger.info("✅ Photo button u klikua")
                    time.sleep(random.uniform(2, 3))
                    
                    # STEP 4: Find file input and upload
                    self.logger.info("📂 Duke kërkuar file input...")
                    file_input = None
                    
                    # Wait for file input to appear
                    for attempt in range(3):
                        try:
                            file_inputs = self.driver.find_elements(By.XPATH, "//input[@type='file']")
                            for fi in file_inputs:
                                # Find the one that accepts images
                                accept = fi.get_attribute('accept')
                                if accept and 'image' in accept:
                                    file_input = fi
                                    break
                            
                            if file_input:
                                break
                            
                            if attempt < 2:
                                time.sleep(1)
                        except:
                            if attempt < 2:
                                time.sleep(1)
                    
                    if file_input:
                        # Upload ONLY 1.png
                        image_file = '1.png'
                        abs_path = os.path.abspath(image_file)
                        
                        if os.path.exists(abs_path):
                            file_input.send_keys(abs_path)
                            self.logger.info(f"✅ U ngarkua fotoja: {image_file}")
                            
                            # Wait for image to upload
                            self.logger.info("⏳ Duke pritur upload të fotos...")
                            time.sleep(random.uniform(4, 6))
                        else:
                            self.logger.warning(f"⚠️ Fotoja nuk ekziston: {abs_path}")
                    else:
                        self.logger.warning("❌ Nuk u gjet file input")
                        
                except Exception as e:
                    self.logger.error(f"Error uploading photo: {e}")
            
            # Find and click Post button - wait a bit for upload if image was added
            time.sleep(2)
            
            post_button_xpaths = [
                "//div[@aria-label='Post'][@role='button']",
                "//span[text()='Post']/ancestor::div[@role='button']",
                "//div[@aria-label='Posten'][@role='button']",
                "//div[contains(@aria-label, 'Post')][not(contains(@aria-label, 'anonymously'))][@role='button']",
            ]
            
            post_button = None
            for xpath in post_button_xpaths:
                try:
                    buttons = self.driver.find_elements(By.XPATH, xpath)
                    for btn in buttons:
                        try:
                            # Check if button is enabled (not disabled)
                            if btn.is_displayed() and btn.is_enabled():
                                btn_aria = btn.get_attribute('aria-disabled')
                                if btn_aria != 'true':  # Not disabled
                                    post_button = btn
                                    break
                        except:
                            continue
                    if post_button:
                        break
                except:
                    continue
            
            if not post_button:
                self.logger.warning("❌ Nuk u gjet Post button ose është disabled")
                # Try to take screenshot for debugging
                try:
                    self.driver.save_screenshot("debug_no_post_button.png")
                    self.logger.info("📸 Screenshot saved: debug_no_post_button.png")
                except:
                    pass
                return False
            
            # Click Post with retry
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", post_button)
                    time.sleep(0.5)
                    self.driver.execute_script("arguments[0].click();", post_button)
                    self.logger.info("✅ Post button clicked!")
                    break
                except Exception as e:
                    if attempt < max_retries - 1:
                        self.logger.warning(f"Retry {attempt+1}/{max_retries} to click Post...")
                        time.sleep(1)
                    else:
                        self.logger.error(f"Failed to click Post after {max_retries} attempts: {e}")
                        return False
            
            time.sleep(random.uniform(3, 5))
            
            self.logger.info("✅ Postimi u bë me sukses!")
            
            # Add to posted groups and save
            self.posted_groups.add(group_url)
            self._save_posted_groups()
            
            # Update statistics
            self.stats['total_posts'] += 1
            self._save_stats()
            
            self.logger.info(f"💾 Grupi u ruajt në historik: {len(self.posted_groups)} grupe | 📊 Total: {self.stats['total_posts']} postime")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error posting to group: {e}")
            return False
    
    def run_group_posting(self, cities_list, max_posts=50):
        """Post to groups automation - INFINITE LOOP until user stops"""
        try:
            self.is_running = True
            self.should_stop = False
            
            if not self.init_driver():
                return False
            
            if not self.check_login():
                return False
            
            posts_made = 0
            
            self.logger.info(f"\n=== Duke filluar GROUP POSTING automation ===")
            self.logger.info(f"Qytete: {cities_list}")
            self.logger.info(f"♾️ INFINITE MODE - Do të vazhdojë deri sa të ndalosh!\n")
            
            # INFINITE LOOP - SEARCH for NEW groups every cycle!
            while not self.should_stop:
                # Shuffle cities for variety
                shuffled_cities = cities_list.copy()
                random.shuffle(shuffled_cities)
                
                for city in shuffled_cities:
                    if self.should_stop:
                        break
                    
                    # SEARCH for groups - find NEW ones!
                    self.logger.info(f"🔍 Kërko grupe të REJA për: {city}")
                    groups = self.search_german_groups(city, max_groups=50)  # Get MANY groups
                    
                    # Shuffle for variety
                    random.shuffle(groups)
                    
                    self.logger.info(f"✅ Gjeti {len(groups)} grupe për {city}")
                    
                    for group_url in groups:
                        if self.should_stop:
                            break
                        
                        # Skip if already posted to this group
                        if group_url in self.posted_groups:
                            self.logger.info(f"⏭️ Grup i postuar më parë - skip: {group_url}")
                            continue
                        
                        # Post to group (will upload all 4 images)
                        success = self.post_to_group(group_url, None)
                        
                        if success:
                            posts_made += 1
                            self.logger.info(f"📊 Totali: {posts_made} postime (INFINITE MODE)")
                            
                            # Delay between posts (30 seconds - 2 minutes)
                            delay = random.uniform(30, 120)
                            self.logger.info(f"⏳ Pritje {delay:.0f} sekonda ({delay/60:.1f} min)...")
                            time.sleep(delay)
                        else:
                            small_delay = random.uniform(10, 20)
                            self.logger.info(f"➡️ Duke vazhduar te grupi tjetër ({small_delay:.1f}s)")
                            time.sleep(small_delay)
                
                if not self.should_stop:
                    self.logger.info(f"\n🔄 Duke përserëritur qytetet (kërko grupe të REJA)... Totali: {posts_made} postime\n")
            
            self.logger.info(f"\n=== ✅ U NDAL! Totali: {posts_made} postime ===")
            return True
            
        except Exception as e:
            self.logger.error(f"Automation error: {e}")
            return False
        finally:
            self.is_running = False
    
    def comment_on_post(self, group_url):
        """Comment on one post in a Facebook group - COMPLETE with ALL edge cases"""
        try:
            # Check if already commented in this group
            if group_url in self.commented_groups:
                self.logger.warning(f"⚠️ Tashmë kemi komentuar në këtë grup - SKIP: {group_url}")
                return False
            
            self.logger.info(f"💬 Duke komentuar në grupin: {group_url}")
            
            # Navigate to group
            self.driver.get(group_url)
            time.sleep(random.uniform(6, 9))
            
            # CHECK #1: Is this a PRIVATE group we're not member of?
            try:
                page_text = self.driver.find_element(By.TAG_NAME, "body").text.lower()
                
                if "private group" in page_text or "join group" in page_text:
                    self.logger.warning("⚠️ Private group - nuk jemi member! SKIP")
                    self.commented_groups.add(group_url)
                    self._save_commented_groups()
                    return False
                
                if "this content isn't available" in page_text or "content isn't available" in page_text:
                    self.logger.warning("⚠️ Grupi nuk është i aksesueshëm - SKIP")
                    self.commented_groups.add(group_url)
                    self._save_commented_groups()
                    return False
            except:
                pass
            
            # Scroll to find posts - MORE scrolling for better results
            self.logger.info("🔍 Duke kërkuar postime...")
            for scroll_num in range(5):  # 5 scrolls instead of 3
                self.driver.execute_script("window.scrollBy(0, 400);")
                time.sleep(random.uniform(1.5, 2.5))
                self.logger.info(f"  Scroll #{scroll_num + 1}/5")
            
            # CHECK #2: Are there ANY posts visible?
            try:
                page_text = self.driver.find_element(By.TAG_NAME, "body").text.lower()
                
                if "no posts" in page_text or "nothing to show" in page_text:
                    self.logger.warning("⚠️ Grupi nuk ka postime - SKIP")
                    self.commented_groups.add(group_url)
                    self._save_commented_groups()
                    return False
                    
                if "commenting isn't available" in page_text or "can't comment" in page_text:
                    self.logger.warning("⚠️ Komentimi është disabled në këtë grup - SKIP")
                    self.commented_groups.add(group_url)
                    self._save_commented_groups()
                    return False
            except:
                pass
            
            # Find posts with Comment button - ENHANCED with multiple strategies
            self.logger.info("🔍 Duke kërkuar postime me Comment button...")
            
            post_xpaths = [
                "//div[@role='article']",
                "//div[contains(@class, 'x1yztbdb')]",
                "//div[contains(@data-pagelet, 'FeedUnit')]",
            ]
            
            post_element = None
            posts_checked = 0
            
            for xpath in post_xpaths:
                try:
                    posts = self.driver.find_elements(By.XPATH, xpath)
                    self.logger.info(f"  Gjeti {len(posts)} postime me xpath: {xpath}")
                    
                    if posts:
                        # Check up to 10 posts
                        for post in posts[:10]:
                            posts_checked += 1
                            try:
                                # Scroll post into view
                                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", post)
                                time.sleep(0.5)
                                
                                # Get post text to check if valid
                                post_text = post.text.lower()
                                if len(post_text) < 10:
                                    continue
                                
                                # Look for Comment button with MULTIPLE methods
                                comment_button_xpaths = [
                                    ".//div[@aria-label='Comment'][@role='button']",
                                    ".//div[@aria-label='Kommentieren'][@role='button']",
                                    ".//span[text()='Comment']/ancestor::div[@role='button']",
                                    ".//span[text()='Kommentieren']/ancestor::div[@role='button']",
                                    ".//div[@role='button'][contains(., 'Comment')]",
                                    ".//div[@role='button'][contains(., 'Kommentieren')]",
                                ]
                                
                                has_comment_button = False
                                for btn_xpath in comment_button_xpaths:
                                    try:
                                        btns = post.find_elements(By.XPATH, btn_xpath)
                                        if btns:
                                            for btn in btns:
                                                if btn.is_displayed() and btn.is_enabled():
                                                    has_comment_button = True
                                                    self.logger.info(f"  ✅ Gjet Comment button në postim #{posts_checked}")
                                                    break
                                        if has_comment_button:
                                            break
                                    except:
                                        continue
                                
                                if has_comment_button:
                                    post_element = post
                                    self.logger.info(f"✅ U gjet postim i VALID për komentim (#{posts_checked})")
                                    break
                                    
                            except Exception as e:
                                self.logger.debug(f"  Post check error: {e}")
                                continue
                                
                        if post_element:
                            break
                except Exception as e:
                    self.logger.debug(f"XPath error {xpath}: {e}")
                    continue
            
            if not post_element:
                self.logger.warning(f"❌ Nuk u gjet postim me Comment button (kontrolluar {posts_checked} postime)")
                self.commented_groups.add(group_url)
                self._save_commented_groups()
                return False
            
            # Scroll to post
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", post_element)
            time.sleep(random.uniform(1, 2))
            
            # Scroll to post
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", post_element)
            time.sleep(random.uniform(1, 2))
            
            # STEP 1: Find and click "Comment" button FIRST to open comment input
            self.logger.info("👆 Duke klikuar në Comment button...")
            comment_button_xpaths = [
                ".//div[@aria-label='Comment'][@role='button']",
                ".//div[@aria-label='Kommentieren'][@role='button']",
                ".//span[text()='Comment']/ancestor::div[@role='button']",
                ".//span[text()='Kommentieren']/ancestor::div[@role='button']",
                ".//div[@role='button'][contains(., 'Comment')]",
            ]
            
            comment_button = None
            for xpath in comment_button_xpaths:
                try:
                    buttons = post_element.find_elements(By.XPATH, xpath)
                    for btn in buttons:
                        if btn.is_displayed():
                            comment_button = btn
                            break
                    if comment_button:
                        break
                except:
                    continue
            
            if not comment_button:
                self.logger.warning("❌ Comment button nuk u gjet")
                return False
            
            # Click Comment button to open input
            try:
                self.driver.execute_script("arguments[0].click();", comment_button)
            except:
                comment_button.click()
            
            self.logger.info("✅ Comment button u klikua")
            time.sleep(random.uniform(3, 5))  # Wait for comment input to appear
            
            # STEP 2: Find and CLICK on clickable comment text (not input yet!)
            self.logger.info("🔍 Duke kërkuar clickable comment text për të klikuar...")
            
            # ALL POSSIBLE variations of clickable text
            clickable_text_xpaths = [
                # "Comment as Sophie" / "Answer as Sophie"
                "//span[contains(text(), 'Comment as')]",
                "//span[contains(text(), 'Answer as')]",
                "//div[contains(text(), 'Comment as')]",
                "//div[contains(text(), 'Answer as')]",
                
                # German versions
                "//span[contains(text(), 'Kommentieren als')]",
                "//span[contains(text(), 'Antworten als')]",
                "//div[contains(text(), 'Kommentieren als')]",
                "//div[contains(text(), 'Antworten als')]",
                
                # Just "Comment" or "Answer" (without name)
                "//span[text()='Comment']",
                "//span[text()='Answer']",
                "//div[text()='Comment']",
                "//div[text()='Answer']",
                
                # "Write a comment" / "Write an answer"
                "//span[contains(text(), 'Write a comment')]",
                "//span[contains(text(), 'Write an answer')]",
                "//div[contains(text(), 'Write a comment')]",
                "//div[contains(text(), 'Write an answer')]",
                
                # Placeholders that are clickable
                "//div[contains(@aria-placeholder, 'comment')]",
                "//div[contains(@aria-placeholder, 'answer')]",
                "//div[contains(@placeholder, 'comment')]",
                "//div[contains(@placeholder, 'answer')]",
            ]
            
            comment_text_element = None
            for xpath in clickable_text_xpaths:
                try:
                    elements = self.driver.find_elements(By.XPATH, xpath)
                    for elem in elements:
                        try:
                            if elem.is_displayed():
                                comment_text_element = elem
                                self.logger.info(f"✅ U gjet 'Comment as Sophie' TEXT: {xpath}")
                                break
                        except:
                            continue
                    if comment_text_element:
                        break
                except:
                    continue
            
            # If found, CLICK on the text to activate textarea
            if comment_text_element:
                self.logger.info("👆 Duke klikuar në 'Comment as Sophie' TEXT...")
                try:
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", comment_text_element)
                    time.sleep(0.5)
                    comment_text_element.click()
                    self.logger.info("✅ 'Comment as Sophie' TEXT u klikua!")
                    time.sleep(random.uniform(2, 3))  # Wait for textarea to activate
                except Exception as e:
                    self.logger.warning(f"Nuk u klikua text: {e}")
            
            # STEP 3: NOW find the actual textarea input that appeared
            self.logger.info("🔍 Duke kërkuar textarea input...")
            
            comment_input_xpaths = [
                # Contenteditable textarea
                "//div[@contenteditable='true'][@role='textbox']",
                "//div[@contenteditable='true'][contains(@aria-label, 'comment')]",
                "//div[@contenteditable='true'][contains(@aria-label, 'answer')]",
                "//textarea[contains(@placeholder, 'comment')]",
                "//textarea[contains(@placeholder, 'answer')]",
            ]
            
            comment_input = None
            for xpath in comment_input_xpaths:
                try:
                    inputs = self.driver.find_elements(By.XPATH, xpath)
                    for inp in inputs:
                        try:
                            if inp.is_displayed() and inp.is_enabled():
                                comment_input = inp
                                self.logger.info(f"✅ U gjet textarea input: {xpath}")
                                break
                        except:
                            continue
                    if comment_input:
                        break
                except:
                    continue
            
            if not comment_input:
                self.logger.warning("❌ Textarea input nuk u gjet pas klikimit")
                return False
            
            # STEP 4: Click textarea to focus and paste
            self.logger.info("📝 Duke shkruar komentin në textarea...")
            comment_input.click()
            time.sleep(random.uniform(0.8, 1.5))
            
            # Copy to clipboard
            pyperclip.copy(self.comment_template)
            time.sleep(0.3)
            
            # Paste using CTRL+V
            comment_input.send_keys(Keys.CONTROL, 'v')
            time.sleep(random.uniform(1.5, 2.5))
            
            # Send with ENTER
            comment_input.send_keys(Keys.ENTER)
            
            self.logger.info("✅ Komenti u dërgua me sukses!")
            time.sleep(1)
            
            self.logger.info("✅ Komenti u postua me sukses!")
            
            # Add to commented groups and save
            self.commented_groups.add(group_url)
            self._save_commented_groups()
            
            # Update statistics
            self.stats['total_comments'] += 1
            self._save_stats()
            
            self.logger.info(f"💾 Grupi u ruajt në historik: {len(self.commented_groups)} grupe | 📊 Total: {self.stats['total_comments']} komente")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error commenting on post: {e}")
            return False
    
    def run_group_commenting(self, cities_list=None, max_comments=50):
        """Comment on posts in groups automation - Use HARDCODED groups!"""
        try:
            self.is_running = True
            self.should_stop = False
            
            if not self.init_driver():
                return False
            
            if not self.check_login():
                return False
            
            comments_made = 0
            
            self.logger.info(f"\n=== Duke filluar GROUP COMMENTING automation ===")
            self.logger.info(f"Duke përdorur {len(self.german_job_groups)} grupe HARDCODED")
            self.logger.info(f"♾️ INFINITE MODE - Do të vazhdojë deri sa të ndalosh!\n")
            
            # INFINITE LOOP - Use HARDCODED groups (not search!)
            while not self.should_stop:
                # Shuffle groups for variety
                groups = self.german_job_groups.copy()
                random.shuffle(groups)
                
                self.logger.info(f"🔄 Duke kontrolluar {len(groups)} grupe...\n")
                
                for group_url in groups:
                    if self.should_stop:
                        break
                    
                    # Skip if already commented in this group
                    if group_url in self.commented_groups:
                        self.logger.info(f"⏭️ Grup me koment më parë - skip: {group_url}")
                        continue
                    
                    # Comment on one post in group
                    success = self.comment_on_post(group_url)
                    
                    if success:
                        comments_made += 1
                        self.logger.info(f"📊 Totali: {comments_made} komente (INFINITE MODE)")
                        
                        # Delay between comments (30 seconds - 2 minutes)
                        delay = random.uniform(30, 120)
                        self.logger.info(f"⏳ Pritje {delay:.0f} sekonda ({delay/60:.1f} min)...")
                        time.sleep(delay)
                    else:
                        small_delay = random.uniform(10, 20)
                        self.logger.info(f"➡️ Duke vazhduar te grupi tjetër ({small_delay:.1f}s)")
                        time.sleep(small_delay)
                
                if not self.should_stop:
                    self.logger.info(f"\n🔄 Duke përserëritur grupet... Totali: {comments_made} komente\n")
            
            self.logger.info(f"\n=== ✅ U NDAL! Totali: {comments_made} komente ===")
            return True
            
        except Exception as e:
            self.logger.error(f"Automation error: {e}")
            return False
        finally:
            self.is_running = False
    
    def run_auto_mode(self, cities_list, group_url="https://www.facebook.com/groups/werbungprofessional/"):
        """AUTO MODE - Bën të gjitha automatikisht pa ndaluar!"""
        try:
            self.is_running = True
            self.should_stop = False
            
            if not self.init_driver():
                return False
            
            if not self.check_login():
                return False
            
            cycle_count = 0
            
            self.logger.info(f"\n=== 🚀 AUTO MODE AKTIVIZUAR ===")
            self.logger.info(f"Do të bëjë: Posting + Komentim + Shokë + Mesazhe")
            self.logger.info(f"♾️ INFINITE - nuk ndalet kurrë!\n")
            
            while not self.should_stop:
                cycle_count += 1
                self.logger.info(f"\n\n========== 🔄 CIKLI #{cycle_count} ==========\n")
                
                # 1. POST në 1 grup
                if not self.should_stop:
                    self.logger.info("📝 HAPI 1: Duke postuar në grup...")
                    # Search for groups
                    city = random.choice(cities_list)
                    groups = self.search_german_groups(city, max_groups=10)
                    
                    if groups:
                        for group_url_post in groups:
                            if group_url_post not in self.posted_groups:
                                success = self.post_to_group(group_url_post, None)
                                if success:
                                    self.logger.info(f"✅ Postimi u bë! Total: {self.stats['total_posts']}")
                                    time.sleep(random.uniform(30, 60))  # Wait after posting
                                break
                
                # 2. KOMENTIM në 1 grup
                if not self.should_stop:
                    self.logger.info("💬 HAPI 2: Duke komentuar në grup...")
                    city = random.choice(cities_list)
                    groups = self.search_german_groups(city, max_groups=10)
                    
                    if groups:
                        for group_url_comment in groups:
                            if group_url_comment not in self.commented_groups:
                                success = self.comment_on_post(group_url_comment)
                                if success:
                                    self.logger.info(f"✅ Komenti u bë! Total: {self.stats['total_comments']}")
                                    time.sleep(random.uniform(30, 60))
                                break
                
                # 3. SHËNGO 3-5 SHOKË
                if not self.should_stop:
                    self.logger.info("👥 HAPI 3: Duke shëngu shokë...")
                    # Get members from group
                    member_profiles = self.get_group_members(group_url)
                    
                    if member_profiles:
                        friends_added = 0
                        target_friends = random.randint(3, 5)
                        
                        for profile_url in member_profiles[:20]:  # Check first 20
                            if self.should_stop or friends_added >= target_friends:
                                break
                            
                            # Try to send friend request
                            try:
                                self.driver.get(profile_url)
                                time.sleep(random.uniform(2, 4))
                                
                                # Find Add Friend button
                                add_friend_xpaths = [
                                    "//div[@aria-label='Add friend'][@role='button']",
                                    "//div[contains(@aria-label, 'Freund')][@role='button']",
                                ]
                                
                                for xpath in add_friend_xpaths:
                                    try:
                                        btn = self.driver.find_element(By.XPATH, xpath)
                                        if btn.is_displayed():
                                            self.driver.execute_script("arguments[0].click();", btn)
                                            friends_added += 1
                                            self.stats['total_friend_requests'] += 1
                                            self._save_stats()
                                            self.logger.info(f"✅ Shok u shëngu! Total: {self.stats['total_friend_requests']}")
                                            time.sleep(random.uniform(5, 10))
                                            break
                                    except:
                                        continue
                            except:
                                continue
                        
                        self.logger.info(f"✅ U shëngun {friends_added} shokë në këtë cikl")
                
                # 4. DËRGO 2-3 MESAZHE
                if not self.should_stop:
                    self.logger.info("✉️ HAPI 4: Duke dërgu mesazhe...")
                    member_profiles = self.get_group_members(group_url)
                    
                    if member_profiles:
                        messages_sent = 0
                        target_messages = random.randint(2, 3)
                        
                        for profile_url in member_profiles:
                            if self.should_stop or messages_sent >= target_messages:
                                break
                            
                            if profile_url not in self.visited_profiles:
                                success = self.send_message(profile_url)
                                if success:
                                    messages_sent += 1
                                    time.sleep(random.uniform(60, 120))  # 1-2 min between messages
                        
                        self.logger.info(f"✅ U dërgun {messages_sent} mesazhe në këtë cikl")
                
                # Summary
                if not self.should_stop:
                    self.logger.info(f"\n✅ CIKLI #{cycle_count} PERFUNDOI!")
                    self.logger.info(f"📊 Totalet: {self.stats['total_posts']} posts | {self.stats['total_comments']} komente | {self.stats['total_friend_requests']} shokë | {self.stats['total_messages']} mesazhe")
                    self.logger.info(f"\n🔄 Duke filluar cikl të ri pas 2 minutash...\n")
                    time.sleep(120)  # 2 min pause between cycles
            
            self.logger.info(f"\n=== ✅ AUTO MODE U NDAL! ===")
            return True
            
        except Exception as e:
            self.logger.error(f"AUTO MODE error: {e}")
            return False
        finally:
            self.is_running = False
    
    def stop(self):
        """Stop automation"""
        self.should_stop = True
        self.logger.info("🛑 Duke ndalur...")
    
    def cleanup(self):
        """Cleanup"""
        if self.driver:
            try:
                self.driver.quit()
                self.logger.info("Browser closed")
            except:
                pass


class AutoMessengerGUI:
    """GUI"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Facebook Auto Messenger")
        self.root.geometry("900x700")
        self.root.resizable(False, False)
        
        self.automation = FacebookAutoMessenger()
        self.automation_thread = None
        
        self._setup_ui()
        
    def _setup_ui(self):
        """Setup UI"""
        
        # Title
#         title_frame = ttk.Frame(self.root, padding="10")
#         title_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
#         title_label = ttk.Label(
            title_frame,
            text="🚀 Facebook Auto Messenger - FULLY AUTOMATED",
            font=("Arial", 16, "bold")
        )
        title_label.pack()
        
        # Info Frame
#         info_frame = ttk.LabelFrame(self.root, text="ℹ️ Status", padding="10")
#         info_frame.grid(row=1, column=0, padx=10, pady=5, sticky=(tk.W, tk.E))
        
#         ttk.Label(
            info_frame,
            text="✅ Sesioni i ruajtur - LOGIN MOS DUHET!",
            foreground="green",
            font=("Arial", 10, "bold")
        ).pack(pady=2)
        
#         ttk.Label(
            info_frame,
            text="🤖 Programi do të punojë 100% automatikisht - thjesht klik START",
            foreground="blue"
        ).pack(pady=2)
        
        # Settings Frame
#         settings_frame = ttk.LabelFrame(self.root, text="Konfigurimi", padding="10")
#         settings_frame.grid(row=2, column=0, padx=10, pady=5, sticky=(tk.W, tk.E))
        
#         ttk.Label(settings_frame, text="Max Mesazhe:", font=("Arial", 10)).grid(row=0, column=0, sticky=tk.W, pady=5)
#         self.max_messages_var = tk.StringVar(value="20")
#         ttk.Entry(settings_frame, textvariable=self.max_messages_var, width=10, font=("Arial", 10)).grid(row=0, column=1, sticky=tk.W, padx=5)
        
#         ttk.Label(settings_frame, text="Max Friend Requests:", font=("Arial", 10)).grid(row=0, column=2, sticky=tk.W, pady=5, padx=(20,0))
#         self.max_friends_var = tk.StringVar(value="20")
#         ttk.Entry(settings_frame, textvariable=self.max_friends_var, width=10, font=("Arial", 10)).grid(row=0, column=3, sticky=tk.W, padx=5)
        
#         ttk.Label(settings_frame, text="Grupi Facebook:", font=("Arial", 10)).grid(row=1, column=0, sticky=tk.W, pady=5)
#         self.group_entry = ttk.Entry(settings_frame, width=70, font=("Arial", 9))
        self.group_entry.insert(0, "https://www.facebook.com/groups/werbungprofessional/")
#         self.group_entry.grid(row=1, column=1, columnspan=3, padx=5, pady=5, sticky=tk.W)
        
        # Group posting settings
#         ttk.Label(settings_frame, text="Max Postime:", font=("Arial", 10)).grid(row=2, column=0, sticky=tk.W, pady=5)
#         self.max_posts_var = tk.StringVar(value="20")
#         ttk.Entry(settings_frame, textvariable=self.max_posts_var, width=10, font=("Arial", 10)).grid(row=2, column=1, sticky=tk.W, padx=5)
        
#         ttk.Label(settings_frame, text="Qytete (Berlin,München,...):", font=("Arial", 10)).grid(row=2, column=2, sticky=tk.W, pady=5, padx=(20,0))
#         self.cities_var = tk.StringVar(value="Berlin,Stuttgart,München,Hamburg")
#         ttk.Entry(settings_frame, textvariable=self.cities_var, width=30, font=("Arial", 9)).grid(row=2, column=3, sticky=tk.W, padx=5)
        
        # Buttons
#         button_frame = ttk.Frame(self.root, padding="10")
        button_frame.grid(row=3, column=0, pady=10)
        
#         self.add_friends_button = ttk.Button(
            button_frame,
            text="👥  Freunde hinzufügen",
            command=self._start_add_friends,
            width=22
        )
        self.add_friends_button.grid(row=0, column=0, padx=5)
        
#         self.start_button = ttk.Button(
            button_frame,
            text="▶️  START (Mesazhe)",
            command=self._start_automation,
            width=22
        )
        self.start_button.grid(row=0, column=1, padx=5)
        
#         self.post_groups_button = ttk.Button(
            button_frame,
            text="📝  Posto në Grupe",
            command=self._start_group_posting,
            width=22
        )
        self.post_groups_button.grid(row=0, column=2, padx=5)
        
#         self.comment_groups_button = ttk.Button(
            button_frame,
            text="💬  Komento në Grupe",
            command=self._start_group_commenting,
            width=22
        )
        self.comment_groups_button.grid(row=1, column=0, padx=5, pady=5)
        
#         self.stop_button = ttk.Button(
            button_frame,
            text="⬛  STOP",
            command=self._stop_automation,
#             state=tk.DISABLED,
            width=22
        )
        self.stop_button.grid(row=1, column=1, padx=5, pady=5)
        
        # Log
#         log_frame = ttk.LabelFrame(self.root, text="📊 Activity Log", padding="10")
#         log_frame.grid(row=4, column=0, padx=10, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))
        
#         self.log_text = scrolledtext.ScrolledText(log_frame, width=110, height=22, state=tk.DISABLED, font=("Courier", 9))
#         self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Status
#         self.status_var = tk.StringVar(value="Ready - Klik START për të filluar")
#         status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
#         status_bar.grid(row=5, column=0, sticky=(tk.W, tk.E))
        
        self._setup_logging_redirect()
        
    def _setup_logging_redirect(self):
        """Redirect logging to GUI"""
        class TextHandler(logging.Handler):
            def __init__(self, text_widget):
                super().__init__()
                self.text_widget = text_widget
            
            def emit(self, record):
                msg = self.format(record)
                def append():
#                     self.text_widget.configure(state=tk.NORMAL)
#                     self.text_widget.insert(tk.END, msg + '\n')
#                     self.text_widget.configure(state=tk.DISABLED)
#                     self.text_widget.see(tk.END)
                self.text_widget.after(0, append)
        
        text_handler = TextHandler(self.log_text)
        text_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
        logging.getLogger().addHandler(text_handler)
    
    def _start_add_friends(self):
        """Start add friends automation"""
        try:
            max_requests = int(self.max_friends_var.get())
        except:
            max_requests = 20
        
        group_url = self.group_entry.get().strip()
        
        if not group_url:
            messagebox.showerror("Error", "Zgjidh një grup!")
            return
        
#         self.add_friends_button.config(state=tk.DISABLED)
#         self.start_button.config(state=tk.DISABLED)
#         self.post_groups_button.config(state=tk.DISABLED)
#         self.comment_groups_button.config(state=tk.DISABLED)
#         self.stop_button.config(state=tk.NORMAL)
        self.status_var.set("Running - Adding Friends...")
        
        self.automation_thread = threading.Thread(
            target=self._run_add_friends_wrapper,
            args=(max_requests, group_url),
            daemon=True
        )
        self.automation_thread.start()
    
    def _start_automation(self):
        """Start automation"""
        try:
            max_messages = int(self.max_messages_var.get())
        except:
            max_messages = 20
        
        group_url = self.group_entry.get().strip()
        
        if not group_url:
            messagebox.showerror("Error", "Zgjidh një grup!")
            return
        
#         self.add_friends_button.config(state=tk.DISABLED)
#         self.start_button.config(state=tk.DISABLED)
#         self.post_groups_button.config(state=tk.DISABLED)
#         self.comment_groups_button.config(state=tk.DISABLED)
#         self.stop_button.config(state=tk.NORMAL)
        self.status_var.set("Running - Sending Messages...")
        
        self.automation_thread = threading.Thread(
            target=self._run_automation_wrapper,
            args=(max_messages, group_url),
            daemon=True
        )
        self.automation_thread.start()
    
    def _run_add_friends_wrapper(self, max_requests, group_url):
        """Wrapper for add friends"""
        try:
            self.automation.run_add_friends(max_requests, group_url)
        except Exception as e:
            logging.error(f"Failed: {e}")
        finally:
            self.root.after(0, self._automation_finished)
    
    def _run_automation_wrapper(self, max_messages, group_url):
        """Wrapper"""
        try:
            self.automation.run_automation(max_messages, group_url)
        except Exception as e:
            logging.error(f"Failed: {e}")
        finally:
            self.root.after(0, self._automation_finished)
    
    def _start_group_posting(self):
        """Start group posting automation"""
        try:
            max_posts = int(self.max_posts_var.get())
        except:
            max_posts = 20
        
        cities_text = self.cities_var.get().strip()
        if not cities_text:
            messagebox.showerror("Error", "Shto qytete!")
            return
        
        cities_list = [city.strip() for city in cities_text.split(',') if city.strip()]
        
        if not cities_list:
            messagebox.showerror("Error", "Shto qytete të vlefshme!")
            return
        
#         self.add_friends_button.config(state=tk.DISABLED)
#         self.start_button.config(state=tk.DISABLED)
#         self.post_groups_button.config(state=tk.DISABLED)
#         self.comment_groups_button.config(state=tk.DISABLED)
#         self.stop_button.config(state=tk.NORMAL)
        self.status_var.set("Running - Posting to Groups...")
        
        self.automation_thread = threading.Thread(
            target=self._run_group_posting_wrapper,
            args=(cities_list, max_posts),
            daemon=True
        )
        self.automation_thread.start()
    
    def _run_group_posting_wrapper(self, cities_list, max_posts):
        """Wrapper for group posting"""
        try:
            self.automation.run_group_posting(cities_list, max_posts)
        except Exception as e:
            logging.error(f"Failed: {e}")
        finally:
            self.root.after(0, self._automation_finished)
    
    def _start_group_commenting(self):
        """Start group commenting automation"""
        try:
            max_comments = int(self.max_posts_var.get())  # Use same max as posts
        except:
            max_comments = 20
        
        cities_text = self.cities_var.get().strip()
        if not cities_text:
            messagebox.showerror("Error", "Shto qytete!")
            return
        
        cities_list = [city.strip() for city in cities_text.split(',') if city.strip()]
        
        if not cities_list:
            messagebox.showerror("Error", "Shto qytete të vlefshme!")
            return
        
#         self.add_friends_button.config(state=tk.DISABLED)
#         self.start_button.config(state=tk.DISABLED)
#         self.post_groups_button.config(state=tk.DISABLED)
#         self.comment_groups_button.config(state=tk.DISABLED)
#         self.stop_button.config(state=tk.NORMAL)
        self.status_var.set("Running - Commenting on Groups...")
        
        self.automation_thread = threading.Thread(
            target=self._run_group_commenting_wrapper,
            args=(cities_list, max_comments),
            daemon=True
        )
        self.automation_thread.start()
    
    def _run_group_commenting_wrapper(self, cities_list, max_comments):
        """Wrapper for group commenting"""
        try:
            self.automation.run_group_commenting(cities_list, max_comments)
        except Exception as e:
            logging.error(f"Failed: {e}")
        finally:
            self.root.after(0, self._automation_finished)
    
    def _stop_automation(self):
        """Stop"""
        self.automation.stop()
        self.status_var.set("Stopping...")
    
    def _automation_finished(self):
        """Finished"""
#         self.add_friends_button.config(state=tk.NORMAL)
#         self.start_button.config(state=tk.NORMAL)
#         self.post_groups_button.config(state=tk.NORMAL)
#         self.comment_groups_button.config(state=tk.NORMAL)
#         self.stop_button.config(state=tk.DISABLED)
        self.status_var.set("Ready")
        messagebox.showinfo("✅ Perfundoi!", "Automatizimi përfundoi!")
    
    def on_closing(self):
        """Handle closing"""
        if self.automation.is_running:
            if messagebox.askokcancel("Quit", "Programi po punon. Dil?"):
                self.automation.stop()
                self.automation.cleanup()
                self.root.destroy()
        else:
            self.automation.cleanup()
            self.root.destroy()


def main():
    """Main"""
#     root = tk.Tk()
    app = AutoMessengerGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()
