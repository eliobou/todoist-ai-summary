# 🎨 Guide de personnalisation

Ce guide explique comment personnaliser le comportement du script selon vos besoins.

---

## 📝 Personnaliser le ton du résumé

### Ton actuel : Factuel et professionnel

Le prompt actuel génère des résumés factuels sans extrapolation émotionnelle.

**Exemple** : 
> "J'ai optimisé les paramètres du réseau de neurones et effectué plusieurs tests de validation."

### Modifier le ton

Éditez `src/summarizer.py`, méthode `_build_prompt()`, section `STYLE :`.

#### Option 1 : Ton plus technique

```python
STYLE :
- Ton technique et précis
- Vocabulaire spécialisé du domaine
- Détails d'implémentation
- Métriques et résultats quantifiables
- À la 1ère personne
```

**Résultat** :
> "J'ai optimisé les hyperparamètres du CNN (learning rate: 0.001, batch size: 32), obtenant une accuracy de 94.2% sur le validation set."

#### Option 2 : Ton plus décontracté

```python
STYLE :
- Ton décontracté mais professionnel
- Langage naturel et fluide
- Peut inclure des observations personnelles factuelles
- À la 1ère personne
```

**Résultat** :
> "J'ai passé du temps à peaufiner le modèle de ML. Les résultats sont prometteurs après ajustement des paramètres."

#### Option 3 : Ton corporate/formel

```python
STYLE :
- Ton formel et professionnel
- Terminologie corporate
- Focus sur les objectifs et livrables
- À la 1ère personne
```

**Résultat** :
> "J'ai contribué à l'optimisation du modèle de machine learning, aligné avec les objectifs du sprint. Les livrables ont été validés par l'équipe."

---

## 🔧 Ajuster les préfixes de projets

### Configuration actuelle

Dans `.env` :
```bash
WORK_PREFIX=ECL
PERSONAL_PREFIX=Perso
TINKER_PREFIX=Tinker
```

### Exemples d'autres configurations

#### Entreprise différente
```bash
WORK_PREFIX=ACME
PERSONAL_PREFIX=Perso
TINKER_PREFIX=Side
```

#### Multi-entreprises (freelance)
```bash
WORK_PREFIX=Client
PERSONAL_PREFIX=Perso
TINKER_PREFIX=Pro
```

Vos projets Todoist : `Client/Apple`, `Client/Google`, `Perso`, `Pro/Formation`

#### Plusieurs catégories de projets perso

Si vous avez beaucoup de catégories, vous pouvez :

**Option A** : Utiliser un seul préfixe avec sous-projets
```
Perso/Maison
Perso/Sport
Perso/Finance
```

**Option B** : Modifier le code pour supporter plus de préfixes

Dans `src/todoist_client.py`, ajoutez :
```python
self.hobby_prefix = os.getenv('HOBBY_PREFIX', 'Hobby')
```

Et dans la méthode `organize_tasks_by_category()` :
```python
if prefix not in [self.work_prefix, self.personal_prefix, 
                  self.tinker_prefix, self.hobby_prefix]:
    continue
```

Puis dans `.env` :
```bash
HOBBY_PREFIX=Hobby
```

---

## 📅 Changer la période d'analyse

### Actuellement : Semaine écoulée (lundi-dimanche)

Le script analyse du lundi au dimanche de la semaine précédente.

### Modifier la période

Éditez `main.py`, fonction `get_week_range()` :

#### Option 1 : Derniers 30 jours
```python
def get_week_range():
    today = datetime.now().date()
    start_date = today - timedelta(days=30)
    end_date = today
    return start_date, end_date
```

#### Option 2 : Mois précédent complet
```python
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta  # pip install python-dateutil

def get_week_range():
    today = datetime.now().date()
    # Premier jour du mois précédent
    start_date = (today.replace(day=1) - timedelta(days=1)).replace(day=1)
    # Dernier jour du mois précédent
    end_date = today.replace(day=1) - timedelta(days=1)
    return start_date, end_date
```

#### Option 3 : Semaine glissante (7 derniers jours)
```python
def get_week_range():
    today = datetime.now().date()
    start_date = today - timedelta(days=7)
    end_date = today
    return start_date, end_date
```

---

## 🎯 Personnaliser la structure du résumé

### Structure actuelle

```markdown
## ECL

### Vision
[paragraphe]

### Infrastructure
[paragraphe]

## Perso

[paragraphe]

## Tinker

### Bot Discord
[paragraphe]
```

### Ajouter une introduction générale

Éditez `src/summarizer.py`, méthode `_build_prompt()`, section `FORMAT REQUIS` :

```python
prompt += """
FORMAT REQUIS (STRUCTURE MARKDOWN) :

**Introduction**
[Un paragraphe d'introduction résumant la semaine globalement]
"""

# Puis ajouter la structure existante...
for category in organized_tasks.keys():
    prompt += f"\n## {category}\n"
    # ...
```

### Ajouter des métriques

```python
prompt += """
**Métriques**
- Total de tâches complétées
- Répartition par catégorie
- Temps estimé (si disponible)
"""
```

### Changer les titres des catégories

Si vous voulez que "ECL" s'affiche comme "Travail" dans le résumé :

Éditez `src/summarizer.py`, méthode `_build_prompt()` :

```python
# Mapping des préfixes vers les titres
title_mapping = {
    'ECL': 'Travail',
    'Perso': 'Personnel',
    'Tinker': 'Projets personnels'
}

for category in organized_tasks.keys():
    display_title = title_mapping.get(category, category)
    prompt += f"\n## {display_title}\n"
```

---

## 📊 Ajouter des statistiques dans le résumé

### Statistiques de temps

Si vous utilisez le time tracking dans Todoist, vous pouvez demander au modèle d'inclure :

Dans `_build_prompt()`, ajoutez :

```python
prompt += """
STYLE :
[...]
- Si des durées sont indiquées, les mentionner (ex: "3h", "30min")
"""
```

### Comparaison avec les semaines précédentes

```python
prompt += """
STYLE :
[...]
- Comparer avec les semaines précédentes si pertinent (augmentation/diminution d'activité)
- Identifier les tendances (projets en accélération, projets ralentis)
```

---

## 🧠 Ajuster le contexte historique

### Actuellement : 4 semaines

Dans `.env` :
```bash
WEEKS_OF_CONTEXT=4
```

### Recommandations

- **1-2 semaines** : Contexte minimal, coût minimum, résumés indépendants
- **4 semaines** : Bon équilibre (recommandé)
- **6-8 semaines** : Contexte riche, continuité narrative forte, coût légèrement plus élevé

**Impact sur le coût** :
- 1 semaine : ~2500 tokens input
- 4 semaines : ~3500 tokens input (+40%)
- 8 semaines : ~5000 tokens input (+100%)

Avec GPT-4o-mini, même 8 semaines reste très économique (~$0.005 par résumé).

---

## 🎨 Personnaliser l'email

### Style actuel : HTML moderne avec dégradé violet

Éditez `src/email_sender.py`, méthode `_format_html_body()`.

#### Changer les couleurs

```css
.header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    /* Changer pour vos couleurs */
}
```

**Exemples** :
- Bleu professionnel : `linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%)`
- Vert nature : `linear-gradient(135deg, #065f46 0%, #10b981 100%)`
- Orange énergique : `linear-gradient(135deg, #ea580c 0%, #fb923c 100%)`

#### Changer le style

```css
body {
    font-family: 'Georgia', serif;  /* Plus classique */
    /* ou */
    font-family: 'Courier New', monospace;  /* Style code */
}
```

#### Ajouter un logo

```html
<div class="header">
    <img src="https://votre-url.com/logo.png" alt="Logo" style="height: 40px; margin-bottom: 10px;">
    <h1>📊 Résumé hebdomadaire</h1>
    <!-- ... -->
</div>
```

---

## 🔔 Ajouter des notifications

### En cas d'erreur

Ajoutez dans `main.py`, section `except Exception` :

```python
except Exception as e:
    logger.error(f"❌ Erreur : {str(e)}", exc_info=True)
    
    # Envoi d'un email d'alerte
    try:
        alert_sender = EmailSender()
        alert_sender.send_alert(error=str(e))
    except:
        pass
    
    sys.exit(1)
```

Puis créez la méthode dans `src/email_sender.py` :

```python
def send_alert(self, error: str):
    """Envoie un email d'alerte en cas d'erreur"""
    msg = MIMEText(f"Le script Todoist AI Summary a échoué:\n\n{error}")
    msg['Subject'] = "🚨 Erreur Todoist AI Summary"
    msg['From'] = self.email_from
    msg['To'] = self.email_to
    
    with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
        server.starttls()
        server.login(self.email_from, self.smtp_password)
        server.send_message(msg)
```

---

## 📈 Tracking des coûts

### Ajouter un suivi des coûts

Créez un fichier `data/costs.json` pour tracker :

```python
# Dans src/storage.py
def save_cost(self, cost: float, tokens: int):
    """Sauvegarde le coût de génération"""
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

Puis appelez-la dans `src/summarizer.py` après génération.

---

## 🚀 Idées d'améliorations avancées

### 1. Dashboard web pour consulter l'historique

Créez un `dashboard.py` avec Flask ou Streamlit pour visualiser les résumés passés.

### 2. Graphiques de productivité

Utilisez matplotlib pour générer des graphiques :
- Tâches par semaine
- Répartition par projet
- Tendances

### 3. Export PDF

Utilisez `reportlab` ou `weasyprint` pour générer des PDFs des résumés.

### 4. Intégration Notion

Envoyez automatiquement les résumés dans une page Notion.

### 5. Notifications Telegram/Slack

Ajoutez un envoi vers Telegram ou Slack en plus de l'email.

---

**Besoin d'aide pour une personnalisation spécifique ?** Ouvrez une issue sur GitHub !
