# 📊 Todoist AI Summary

Génère automatiquement un résumé hebdomadaire intelligent de vos tâches Todoist complétées, avec envoi par email.

## ✨ Fonctionnalités

- 🤖 **Résumés IA** : Utilise GPT-4o-mini pour créer des résumés naturels et contextualisés
- 📧 **Envoi automatique** : Reçoit le résumé par email chaque dimanche soir
- 💾 **Historique** : Sauvegarde locale en JSON et Markdown
- 🧠 **Contexte historique** : Le modèle connaît les 4 dernières semaines pour assurer une continuité
- 📁 **Organisation flexible** : Séparation Travail / Personnel / Projets Tinker
- 💰 **Économique** : ~0.3 centimes par résumé avec GPT-4o-mini

## 📋 Prérequis

- Python 3.8+
- Un compte Todoist (gratuit ou payant)
- Une clé API OpenAI avec des crédits
- Un compte Gmail (pour l'envoi d'emails)
- Un Raspberry Pi ou serveur Linux avec cron

## 🚀 Installation

### 1. Cloner le projet

```bash
cd ~
git clone https://github.com/votre-username/todoist-ai-summary.git
cd todoist-ai-summary
```

### 2. Créer l'environnement virtuel

```bash
python3 -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4. Configuration

#### a) Créer le fichier .env

```bash
cp .env.example .env
nano .env  # ou votre éditeur préféré
```

#### b) Obtenir votre token Todoist

1. Allez sur https://todoist.com/app/settings/integrations/developer
2. Copiez votre "API token"
3. Collez-le dans `.env` : `TODOIST_API_TOKEN=votre_token`

#### c) Obtenir votre clé OpenAI

1. Allez sur https://platform.openai.com/api-keys
2. Créez une nouvelle clé API
3. Collez-la dans `.env` : `OPENAI_API_KEY=votre_clé`

#### d) Configurer Gmail

**IMPORTANT** : N'utilisez PAS votre mot de passe Gmail principal !

1. Allez sur https://myaccount.google.com/apppasswords
2. Créez un mot de passe d'application nommé "Todoist Summary"
3. Copiez le mot de passe généré (16 caractères)
4. Configurez dans `.env` :
   ```
   EMAIL_SEND=True
   EMAIL_FROM=votre.email@gmail.com
   EMAIL_TO=votre.email@gmail.com  # peut être le même
   SMTP_PASSWORD=votre_mot_de_passe_app
   ```

#### e) Configurer les préfixes de projets

Dans `.env`, vérifiez que les préfixes correspondent à vos projets Todoist :
```bash
WORK_PREFIX=ECL           # Détecte "ECL/Vision", "ECL/Infrastructure", etc.
PERSONAL_PREFIX=Perso     # Détecte "Perso", "Perso/Maison", etc.
TINKER_PREFIX=Tinker      # Détecte "Tinker/Bot Discord", etc.
```

**Important** : Les préfixes sont sensibles à la casse et doivent correspondre **exactement** au début de vos noms de projets Todoist.

### 5. Créer la structure des dossiers

```bash
mkdir -p data/summaries logs src
```

### 6. Créer les fichiers Python

Créez les fichiers suivants dans le dossier `src/` :
- `__init__.py` (fichier vide)
- `todoist_client.py`
- `summarizer.py`
- `storage.py`
- `email_sender.py`

Copiez le code des artifacts correspondants.

## 🧪 Test manuel

Avant de configurer cron, testez le script manuellement :

```bash
source venv/bin/activate
python main.py
```

Vérifiez :
- ✅ Les logs dans `logs/`
- ✅ Les fichiers dans `data/summaries/`
- ✅ L'email reçu

## ⏰ Configuration de cron (Raspberry Pi)

### 1. Ouvrir crontab

```bash
crontab -e
```

### 2. Ajouter la ligne suivante

Exécution tous les dimanches à 21h00 :

```bash
0 21 * * 0 /home/pi/todoist-ai-summary/venv/bin/python /home/pi/todoist-ai-summary/main.py >> /home/pi/todoist-ai-summary/logs/cron.log 2>&1
```

**Adaptation** : Remplacez `/home/pi/` par votre chemin réel.

### 3. Vérifier que cron fonctionne

```bash
# Vérifier que cron est actif
sudo systemctl status cron

# Voir les exécutions de cron
grep CRON /var/log/syslog
```

## 📁 Organisation Todoist recommandée

### Structure des projets

```
📁 ECL                    (Projet travail)
  └── Sections : Backend, Frontend, Réunions, Admin

📁 Perso                  (Projet personnel)
  └── Sections : Maison, Courses, Santé

📁 Tinker                 (Projets techniques)
  └── Sections : Horloge connectée, Bot Discord, Scraper web
```

### Format du résumé généré

Le script génère un résumé structuré avec des **titres Markdown** :

- **Titre `##`** pour chaque catégorie principale (ECL, Perso, Tinker)
- **Titre `###`** pour chaque sous-projet (Vision, Bot Discord, etc.)
- **Paragraphes factuels** décrivant les tâches complétées

**Exemple de résumé** :

```markdown
## ECL

### Vision

J'ai travaillé sur l'amélioration du modèle de machine learning pour 
la partie localisation. J'ai optimisé les paramètres et effectué 
plusieurs tests de validation.

### Scripting backup purge

J'ai automatisé la purge des anciens backups avec un script Python. 
Le script a été déployé en production.

## Perso

J'ai pris rendez-vous chez le dentiste. J'ai réparé la fuite sous 
l'évier et fait les courses hebdomadaires.

## Tinker

### Horloge connectée

J'ai câblé les LEDs et commencé l'intégration avec l'ESP32. Le 
prototype affiche maintenant l'heure via WiFi.

### Bot Discord

J'ai ajouté une commande de modération automatique et corrigé un bug 
dans le système de permissions.
```

## 💰 Estimation des coûts

Avec **GPT-4o-mini** (recommandé) :
- Coût par résumé : ~$0.003 (0.3 centimes)
- Coût mensuel : ~$0.012 (4 exécutions)
- **Coût annuel : ~$0.15** ✅

Avec GPT-4 (non recommandé pour ce cas) :
- Coût annuel : ~$2-3

## 🔧 Personnalisation

### Changer le jour d'exécution

Dans cron, le format est : `minute heure jour mois jour_semaine`
- Dimanche = 0
- Lundi = 1
- etc.

Exemples :
```bash
# Tous les vendredis à 18h00
0 18 * * 5 /chemin/vers/script

# Tous les 1er du mois à 9h00
0 9 1 * * /chemin/vers/script
```

### Changer le ton du résumé

Le ton par défaut est **factuel et professionnel**. Si vous voulez le modifier, éditez `src/summarizer.py` dans la méthode `_build_prompt()`.

Exemples de modifications possibles :
- Plus technique avec jargon métier
- Plus décontracté avec humour
- Plus formel et corporate

### Changer le nombre de semaines de contexte

Dans `.env` : `WEEKS_OF_CONTEXT=4` (1-8 recommandé)

### Désactiver l'envoi d'email temporairement

Commentez l'étape 5 dans `main.py` :

```python
# email_sender.send_summary(...)
```

## 📊 Structure du projet

```
todoist-ai-summary/
├── .env                    # Configuration (NE PAS COMMIT)
├── .env.example            # Template de configuration
├── .gitignore
├── README.md
├── requirements.txt
├── main.py                 # Point d'entrée
├── src/
│   ├── __init__.py
│   ├── todoist_client.py   # Client API Todoist
│   ├── summarizer.py       # Génération résumés OpenAI
│   ├── storage.py          # Sauvegarde locale
│   └── email_sender.py     # Envoi emails
├── data/
│   └── summaries/          # Résumés JSON + Markdown
└── logs/                   # Logs d'exécution
```

## 🐛 Dépannage

### Erreur "TODOIST_API_TOKEN manquant"
- Vérifiez que le fichier `.env` existe
- Vérifiez que le token est bien copié sans espaces

### Erreur d'envoi d'email
- Vérifiez que vous utilisez un **mot de passe d'application** Gmail
- Vérifiez que l'authentification à 2 facteurs est activée sur Gmail
- Testez la connexion SMTP manuellement

### Aucune tâche récupérée
- Vérifiez que vos projets ont les bons noms (ECL, Perso, Tinker)
- Vérifiez que vous avez complété des tâches cette semaine
- Testez avec `python main.py` en mode debug

### Cron ne s'exécute pas
```bash
# Vérifier les logs
tail -f /home/pi/todoist-ai-summary/logs/cron.log

# Vérifier cron
sudo systemctl status cron

# Tester manuellement la commande cron
/home/pi/todoist-ai-summary/venv/bin/python /home/pi/todoist-ai-summary/main.py
```

## 🔮 Futures améliorations

- [ ] Intégration Google Docs (API)
- [ ] Support Apple Notes via automation
- [ ] Dashboard web pour consulter l'historique
- [ ] Graphiques de productivité
- [ ] Comparaison semaine N vs N-1
- [ ] Export PDF
- [ ] Notifications Telegram/Slack

## 📝 Licence

MIT

## 🤝 Contribution

Les issues et pull requests sont les bienvenues !

## 👤 Auteur

Créé pour gérer efficacement vos tâches Todoist avec l'aide de l'IA.

---

**Bon résumé ! 🚀**
