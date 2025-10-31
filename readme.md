# 📊 Todoist AI Summary

Automatically generates a smart weekly summary of your completed Todoist tasks and sends it to you via email.

## ✨ Features

- 🤖 **AI Summaries**: Uses GPT-4o-mini to create natural, contextualized summaries
- 📧 **Automatic delivery**: Receive the summary by email every Sunday evening
- 💾 **History**: Local backup in JSON and Markdown
- 🧠 **Historical context**: The model knows the last 4 weeks to ensure continuity
- 📁 **Flexible organization**: Separation of Work / Personal / Tinker Projects
- 💰 **Economical**: ~0.3 cents per summary with GPT-4o-mini
- 🌍 **Multilingual**: Multiples language supported, easy to add more 

## 📋 Prerequisites

- Python 3.8+
- A Todoist account (free or paid)
- An OpenAI API key with credits
- A Gmail account (for sending emails)

## 🚀 Installation

### 1. Clone the project

```bash
cd ~
git clone https://github.com/votre-username/todoist-ai-summary.git
cd todoist-ai-summary
```

### 2. Execute the setupt script

```bash
chmod +x setup_script.sh
./setup_script.sh
```

The script will :
1. Check if Python3 is installed
2. Create a virtual environment and activate
3. Install dependencies
4. Create folder structure and required files
5. Setup environment variables
6. Test the installation
7. Display next steps

### 3. Configuration

#### a) Set language
1. Choose language of your tasks within supported languages.

#### b) Get your Todoist token

1. Go to https://todoist.com/app/settings/integrations/developer
2. Copy your “API token”
3. Paste it into `.env`: `TODOIST_API_TOKEN=your_token`

#### c) Get your OpenAI key

1. Go to https://platform.openai.com/api-keys
2. Create a new API key
3. Paste it into `.env`: `OPENAI_API_KEY=your_key`

#### d) Configure Gmail

**IMPORTANT**: Do NOT use your main Gmail password!

1. Go to https://myaccount.google.com/apppasswords
2. Create an application password named “Todoist Summary”
3. Copy the generated password (16 characters)
4. Configure in `.env`:
```
EMAIL_SEND=True
EMAIL_FROM=votre.email@gmail.com
EMAIL_TO=votre.email@gmail.com  # can be the same
SMTP_PASSWORD=your_app_password
```

#### e) Configure project prefixes

In `.env`, verify that the prefixes match your Todoist projects:
```bash
WORK_PREFIX=Work        # Detects “Work/Project1,” “Work/Project2,” etc.
PERSONAL_PREFIX=Perso   # Detects “Perso,” “Perso/Home,” etc.
TINKER_PREFIX=Tinker    # Detects “Tinker/Project1,” etc.
```

**Important**: Prefixes are case-sensitive and must match the beginning of your Todoist project names **exactly**.

## 🧪 Manual test

Before configuring cron, test the script manually:

```bash
source venv-summary/bin/activate python main.py
```

Check:
- ✅ The logs in `logs/`
- ✅ The files in `data/summaries/`
- ✅ The email received

## ⏰ Configuration of cron (Raspberry Pi)

### 1. Open crontab

```bash 
crontab -e
```

### 2. Add the following line

Execution every Sunday at 9:00 PM:

```bash
0 21 * * 0 /home/pi/todoist-ai-summary/venv-summary/bin/python /home/pi todoist-ai-summary/main.py> > /home/pi/todoist-ai-summary/logs/cron.log 2>&1 
```

**Adaptation**: Replace `/home/pi/` with your actual path.

### 3. Check that cron works

```bash 
# Check that cron is active
sudo systemctl status cron

# Check the executions of cron
grep CRON /var/log/syslog
```

## 📁 Todoist Organization recommended

### Project structure

```
📁 Work                   (Work project)
  └── Sections : Backend, Frontend, Réunions, Admin

📁 Perso                  (Personnal project)
  └── Sections : Home, Groceries, Health

📁 Tinker                 (Side projects)
  └── Sections : Smart Clock, Discord Bot
```

### Format of the generated summary

The script generates a structured summary with **Markdown titles** :

- **Title `##`** for each main category (Work, Perso, Tinker)
- **Title `##`** for each sub-project (Smart clock, Discord Bot, etc.)
- **Factual paragraphs** describing the tasks completed

**Summary example** :

```markdown
## Work

### Machine learning

I worked on improving the machine learning model for the core part. I optimized the settings and performed several validation tests.

### Scripting

I automated the purge of old backups with a Python script.
The script has been deployed in production.

## Personal

I made an appointment with the dentist. I fixed the leak under the sink and did the weekly shopping.

## Tinker

### Smart clock

I wired the LEDs and started integration with the ESP32. The prototype now displays the time via WiFi.

### Discord Bot

I added an automatic moderation command and fixed a bug in the permissions system.
```

## 💰 Cost estimate

With **GPT-4o-mini** (recommended):
- Cost per summary: ~$0.003 (0.3 cents)
- Monthly cost: ~$0.012 (4 runs)
- **Annual cost: ~$0.15** ✅

With GPT-4 (not recommended for this case):
- Annual cost: ~$2-3

## 🔧 Customization

See the **customization** section in the Wiki of this repo

## 📊 Project Structure

```
todoist-ai-summary/
├── .env                    # Configuration (DON'T COMMIT)
├── .env.example            # Configuration template
├── .gitignore
├── README.md
├── requirements.txt
├── main.py                 # Entry point
├── src/
│   ├── __init__.py
│   ├── todoist_client.py   # API Todoist client
│   ├── summarizer.py       # Generate OpenAI summary
│   ├── storage.py          # Local save
│   └── email_sender.py     # Emails send
├── data/
│   └── summaries/          # JSON + Markdown summaries
└── logs/                   # Execution logs
```

## 🔧 Troubleshooting

See Wiki for troubleshooting documentation.

## 🔮 Future improvements

- [ ] Google Docs Integration (API)
- [ ] Apple Notes support via automation
- [ ] More languages supported (PRs are welcome)
- [ ] Telegram/Slack/Teams notifications
- [ ] Web dashboard to consult the history
- [ ] Productivity Charts
- [ ] Comparison week N vs N-1
- [ ] PDF Export

## 📝 Licence

GNU GPLv3

## 🤝 Contribution

Issues and pull requests are welcome!

**Good summary! 🚀**