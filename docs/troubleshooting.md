# 🔧 Troubleshooting guide

This guide helps you solve common problems.

## 🔍 General diagnosis

Before looking for the problem, run the script manually with detailed logs:

```bash
cd ~/todoist-ai-summary
source venv-summary/bin/activate
python main.py
```

Look at the logs in:
- Terminal (standard output)
- `logs/execution_YYYYMMDD_HHMMSS.log`

---

## ❌ Common errors

### 1. "TODOIST_API_TOKEN missing in .env"

**Cause** : The `.env` file does not exist or is misconfigured.

**Solution** :
```bash
# Check that the file exists
ls -la .env

# Check content
cat .env | grep TODOIST_API_TOKEN

# If missing, recreate from template
cp .env.example .env
nano .env
```

**Checkpoints** :
- ✅ No spaces around `=`
- ✅ No "quote" around the value
- ✅ No blank line before token

**Correct** :
```bash
TODOIST_API_TOKEN=abc123def456
```

**Incorrect** :
```bash
TODOIST_API_TOKEN = "abc123def456"  # ❌ sapce and quote
TODOIST_API_TOKEN=                  # ❌ empty
```

---

### 2. "No task completed this week"

**Cause**: The script does not find tasks in the period.

**Solutions**:

#### Option A: Check project prefixes

```bash
# In .env, check that the prefixes match your Todoist projects
nano .env

# Prefixes ar case-sensitive and must match the BEGINING of the name !
WORK_PREFIX=Work    # Correct pour "Work/Project1", "Work/Project2"
WORK_PREFIX=work    # ❌ Will not detect "Work/Project1"
WORK_PREFIX=W       # ❌ Too short, will detect others project too
```

**Important** : The script in all projects that **BEGIN WITH** the prefixe.

Detection examples :
- `WORK_PREFIX=Work` detect : `Work`, `Work/Project1`, `Work/Project2`

#### Option B : Test with another period

Modify temporarily `main.py` to test over a month:

```python
# In function get_week_range()
start_date = today - timedelta(days=30)  # Instead of 7
end_date = today
```

#### Option C : Check manually Todoist

1. Go in Todoist
2. Filters → Completed
3. Check that there are somes completed tasks

---

### 3. Email sending errors

**Message** : `SMTPAuthenticationError` or `Authentication failed`

**Cause** : Authentification problem.

**Solutions** :

#### Step 1 : Check that you use an application password

❌ **DON'T use** your normal Gmail password !

✅ **Create an application password** :
1. https://myaccount.google.com/apppasswords
2. Select "Other" → "Todoist Summary"
3. Copy the password (16 characters, format : xxxx xxxx xxxx xxxx)
4. Paste in`.env` **WITHOUT spaces** : `xxxxxxxxxxxxxxxx`

#### Step 2 : Activate 2 factors authentification

If you don't have access to applications password :
1. https://myaccount.google.com/security
2. Activate 2FA
3. Wait few minutes
4. Create the application password

#### Étape 3 : Check configuration

```bash
cat .env | grep EMAIL
```

Should show :
```bash
EMAIL_SEND=True
EMAIL_FROM=your.email@gmail.com
EMAIL_TO=your.email@gmail.com
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_PASSWORD=xxxxxxxxxxxxxxxx
```

#### Step 4 : Try manually SMTP

```python
import smtplib
server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()
server.login('your.email@gmail.com', 'your_app_password')
server.quit()
print("✅ Connection OK")
```

---

### 4. OpenAI error "Invalid API Key"

**Solutions** :

#### Check the key
```bash
cat .env | grep OPENAI_API_KEY
```

#### Try the key manually
```python
from openai import OpenAI
client = OpenAI(api_key='your_key')
response = client.models.list()
print("✅ Valid key")
```

#### Check credits
1. https://platform.openai.com/account/billing
2. Check that you have credits
3. If you don't have credits, add some

---

### 5. Cron don't execute

**Diagnosis** :

```bash
# Check that cron is active
sudo systemctl status cron

# Check cron logs
grep CRON /var/log/syslog | tail -20

# Check scripts logs
tail -f ~/todoist-ai-summary/logs/cron.log
```

**Solutions** :

#### Problem 1 : wrong paths

In `crontab -e`, use **absolute paths** :

❌ **Incorrect** :
```bash
0 21 * * 0 python main.py
```

✅ **Correct** :
```bash
0 21 * * 0 /home/pi/todoist-ai-summary/venv-summmary/bin/python /home/pi/todoist-ai-summary/main.py >> /home/pi/todoist-ai-summary/logs/cron.log 2>&1
```

#### Problem 2 : environment variables

Cron doesn't have access to same variables than your terminal.

**Solution** : Aadd at the top of the crontab :

```bash
SHELL=/bin/bash
PATH=/usr/local/bin:/usr/bin:/bin
```

#### Problem 3 : Permissions

```bash
# Check permissions
ls -la ~/todoist-ai-summary/main.py
ls -la ~/todoist-ai-summary/venv-summary/bin/python

# If necessary, correct
chmod +x ~/todoist-ai-summary/main.py
```

#### Manually try cron command

Copy the cron line and execute :

```bash
/home/pi/todoist-ai-summary/venv-summary/bin/python /home/pi/todoist-ai-summary/main.py
```

If it works manually but not with cron → problem with PATH or environment variables.

---

### 6. "Module not found" or ImportError

**Cause** : Dependencies not installed or bad virtual environment.

**Solutions** :

```bash
# Reinstall dependencies
cd ~/todoist-ai-summary
source venv-summary/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Check installation
pip list | grep -E "requests|openai|python-dotenv"
```

**Should show** :
```
openai         1.12.0
python-dotenv  1.0.0
requests       2.31.0
```

---

### 7. "Rate limit exceeded" (OpenAI)

**Cause** : Too many requests in a short time.

**Solutions** :

1. **Wait few minutes** and retry
2. **Chekc your tier** : https://platform.openai.com/account/limits
3. **Reduce WEEKS_OF_CONTEXT** in `.env` (from 4 to 2)

---

### 8. Bad quality summary

**Possible causes** :
- Badly named tasks in Todoist
- Not enough context
- Model extrapole emotions

**Solutions** :

#### Enhanced tasks names

❌ **Bad** :
- "Do that"
- "Things"
- "TODO"

✅ **Good** :
- "Optimize neural network parameters"
- "Repair leak in the kitchen sink "
- "Wire LEDs to the smart clock ESP32"

The more descriptive the tasks, the more factual and accurate the summary will be.

#### Adjust the model

In `.env`, try `gpt-4o>(more expensive but better):
```bash
OPENAI_MODEL=gpt-4o
```

#### Modify the prompt for more factuality

Edit `src/summarizer.py`   method >_build_prompt()>.

Currently, the prompt already insists on:
- "Remain strictly factual"
- "Do NOT extrapolate emotions or feelings"
- "Describe what was done, not how I felt"

If the model still extrapolates too much, you can reinforce these instructions.

---

## 🧪 Debug mode

For more detailed logs, modify in `.env` :

```bash
LOG_LEVEL=DEBUG
```

Then restart :
```bash
python main.py
```

---

## 📞 Need help ?

If no solutions works :

1. **Copy logs** :
```bash
cat logs/execution_*.log | tail -100
```

2. **Check your configuration** :
```bash
cat .env | grep -v PASSWORD  # Show config without password
```

3. **Open an issue** on GitHub with :
   - Complete error messages
   - The relevant logs (WITHOUT the API keys!)
   - Your configuration (WITHOUT the secrets!)

---

## ✅ Diagnostic checklist

Before asking for help, check :

- [ ] The `.env` file exists and is filled in
- [ ] API tokens are valid (Todoist + OpenAI)
- [ ] The Gmail password is an app password
- [ ] Project names match exactly
- [ ] The virtual environment is activated
- [ ] Dependencies are installed
- [ ] There are tasks completed in Todoist
- [ ] You have OpenAI credits
- [ ] The script works manually (before testing with cron)

---

**Good debugging! 🔍**