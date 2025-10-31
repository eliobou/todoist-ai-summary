# 🎨 Customization guide

This guide explains how to customize the behavior of the script according to your needs.

---

## 📝 Customize the tone of the summary

### Current tone: Factual and professional

The current prompt generates factual summaries without emotional extrapolation.

**Example**:
> "I have optimized the neural network parameters and performed several validation tests."

### Change the tone

Edit `src/summarizer.py`, method `_build_prompt()>, section `STYLE:`.

#### Option 1: More technical tone

```python
STYLE:
- Technical and precise tone
- Specialized vocabulary of the field
- Implementation details
- Metrics and quantifiable results
- Speak in the first person
```

**Results** :
> "I optimized the hyperparameters of the CNN (taux d’apprentissage : 0,001, batch size : 32), obtaining an accuracy of 94,2% on the validation set."

#### Option 2 : More relaxed tone

```python
STYLE:
- casual but professional tone
- Natural and fluid language
- May include factual personal observations
- Speak in the first person
```

**Results** :
> "I spent time fine-tuning the ML model. The results are promising after adjusting the parameters."

#### Option 3 : Corporate/formal tone

```python
STYLE :
- formal and professional tone
- Corporate terminology
- Focus on objectives and deliverables
- Speak in the first person
```

**Résultat** :
> "I contributed to the optimization of the machine learning model, aligned with the objectives of the sprint. The deliverables have been validated by the team."

---

## 🔧 Adjust project prefixes

### Current configuration

In `.env` :
```bash
WORK_PREFIX=Work
PERSONAL_PREFIX=Perso
TINKER_PREFIX=Tinker
```

### Examples with other configurations

#### Different names
```bash
WORK_PREFIX=ACME
PERSONAL_PREFIX=Perso
TINKER_PREFIX=Side
```

#### Multi-companies (freelance)
```bash
WORK_PREFIX=Client
PERSONAL_PREFIX=Perso
TINKER_PREFIX=Pro
```

Your Todoist projects : `Client/Apple`, `Client/Google`, `Perso`, `Pro/Formation`

#### Several categories of personal projects

If you have many categories, you can:

**Option A**: Use only one prefix with subprojects
```
Perso/Home
Perso/Sport
Perso/Finance
```

**Option B**: Edit the code to support more prefixes

In `src/todoist_client.py`, add :
```python
self.hobby_prefix = os.getenv('HOBBY_PREFIX', 'Hobby')
```

And in method `organize_tasks_by_category()` :
```python
if prefix not in [self.work_prefix, self.personal_prefix, 
                  self.tinker_prefix, self.hobby_prefix]:
    continue
```

Then in `.env` :
```bash
HOBBY_PREFIX=Hobby
```

---

## 📅 Change the analysis period

### Currently: Past week (Monday-Sunday)

The script analyzes from Monday to Sunday of the previous week.

### Modify the period

Edit `main.py`, function `get_week_range()` :

#### Option 1: Last 30 days
```python
def get_week_range():
    today = datetime.now().date()
    start_date = today - timedelta(days=30)
    end_date = today
    return start_date, end_date
```

#### Option 2 : Complete previous month
```python
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta  # pip install python-dateutil

def get_week_range():
    today = datetime.now().date()
    # First day of previous month
    start_date = (today.replace(day=1) - timedelta(days=1)).replace(day=1)
    # Last day of previous month
    end_date = today.replace(day=1) - timedelta(days=1)
    return start_date, end_date
```

#### Option 3 : Rolling week (last 7 days)
```python
def get_week_range():
    today = datetime.now().date()
    start_date = today - timedelta(days=7)
    end_date = today
    return start_date, end_date
```

---

## 🎯 Customize the summary structure

### Current structure

```markdown
## Work

### Project1
[paragraph]

### Project2
[paragraph]

## Personal

[paragraph]

## Tinker

### Discord Bot
[paragraph]
```

### Add a general introduction

Edit `src/summarizer.py`, method `_build_prompt()`, section `REQUIRED FORMAT`:

```python
prompt += """
REQUIRED FORMAT (MARKDOWN STRUCTURE):

**Introduction**
[An introductory paragraph summarizing the week as a whole]
"""

# Then add the existing structure...
for category in organized_tasks.keys():
    prompt += f"\n## {category}\n"
    # ...
```

### Add metrics

```python
prompt += """
**Métriques**
- Total de tâches complétées
- Répartition par catégorie
- Temps estimé (si disponible)
"""
```

### Change category titles

If you want "Work" to appear as "Company" in the summary:

Edit `src/summarizer.py`, method `_build_prompt()`:

```python
# Map prefixes to titles
title_mapping = {
    'Work': 'Company',
    'Perso': 'Personnel',
    'Tinker': 'Side projects'
}

for category in organized_tasks.keys():
    display_title = title_mapping.get(category, category)
    prompt += f"\n## {display_title}\n"
```

---

## 📊 Add statistics to the summary

### Time statistics

If you use time tracking in Todoist, you can ask the template to include:

In `_build_prompt()`, add:

```python
prompt += """
STYLE :
[...]
- If durations are specified, mention them (e.g., “3 hours,” “30 minutes”).
"""
```

### Compare with previous weeks

```python
prompt += """
STYLE :
[...]
- Compare with previous weeks if relevant (increase/decrease in activity)
- Identify trends (projects accelerating, projects slowing down)
```

---

## 🧠 Adjust the historical context

### Currently: 4 weeks

In `.env` :
```bash
WEEKS_OF_CONTEXT=4
```

### Recommandations

- **1-2 weeks**: Minimal context, minimal cost, independent summaries
- **4 weeks**: Good balance (recommended)
- **6-8 weeks**: Rich context, strong narrative continuity, slightly higher cost

**Impact on cost**:
- 1 week: ~2500 input tokens
- 4 weeks: ~3500 input tokens (+40%)
- 8 weeks: ~5000 input tokens (+100%)

With GPT-4o-mini, even 8 weeks remains very economical (~$0.005 per summary).

---

## 🎨 Customize the email

### Current style: Modern HTML with purple gradient

Edit `src/email_sender.py`, method `_format_html_body()`.

#### Change colors

```css
.header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    /* Change for your colors */
}
```

**Examples**:
- Professional blue: `linear-gradient(135deg, #e3a8a 0%, #3b82f6 100%)`
- Natural green: `linear-gradient(135deg, #065f46 0%, #10b981 100%)`
- Energetic orange: `linear-gradient(135deg, #ea580c 0%, #fb923c 100%)`

#### Change the style

```css
body {
    font-family: 'Georgia', serif;  /* More classic */
    /* or */
    font-family: 'Courier New', monospace;  /* Code style */
}
```

#### Add a logo

```html
<div class="header">
    <img src="https://your-url.com/logo.png" alt="Logo" style="height: 40px; margin-bottom: 10px;">
    <h1>📊 Weekly summary</h1>
    <!-- ... -->
</div>
```

---

## 🔔 Add notifications

### In case of error

Add in `main.py`, in `except Exception` :

```python
except Exception as e:
    logger.error(f"❌ Error : {str(e)}", exc_info=True)
    
    # Send alert email
    try:
        alert_sender = EmailSender()
        alert_sender.send_alert(error=str(e))
    except:
        pass
    
    sys.exit(1)
```

Then create method in `src/email_sender.py` :

```python
def send_alert(self, error: str):
    """Send an alert email in case of errors"""
    msg = MIMEText(f"Todoist AI Summary script failed:\n\n{error}")
    msg['Subject'] = "🚨 Todoist AI Summary error"
    msg['From'] = self.email_from
    msg['To'] = self.email_to
    
    with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
        server.starttls()
        server.login(self.email_from, self.smtp_password)
        server.send_message(msg)
```

---

## 📈 Cost tracking

### Add cost tracking

Create a `data/costs.json` file to track:

```python
# In src/storage.py
def save_cost(self, cost: float, tokens: int):
    """Save cost of generation"""
    cost_file = Path("data/costs.json")
    
    if cost_file.exists():
        with open(cost_file, 'r') as f:
            costs = json.load(f)
    else:
        costs = []
    
    costs.append({
        'date': datetime.now().isoformat(),
        'cost': cost,
        'tokens': tokens
    })
    
    with open(cost_file, 'w') as f:
        json.dump(costs, f, indent=2)
```

Then call it in `src/summarizer.py` after generation.

---

## 🚀 Advanced improvement ideas

### 1. Web dashboard to view history

Create a `dashboard.py` with Flask or Streamlit to view past summaries.

### 2. Productivity charts

Use matplotlib to generate charts:
- Tasks per week
- Distribution by project
- Trends

### 3. PDF export

Use `reportlab` or `weasyprint` to generate PDFs of the summaries.

### 4. Notion integration

Automatically send summaries to a Notion page.

### 5. Telegram/Slack notifications

Add sending to Telegram or Slack in addition to email.