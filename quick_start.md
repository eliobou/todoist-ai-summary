# 🚀 Guide de démarrage rapide

Ce guide vous permet de lancer Todoist AI Summary en 10 minutes.

## Étape 1 : Cloner et installer (2 min)

```bash
cd ~
git clone https://github.com/votre-username/todoist-ai-summary.git
cd todoist-ai-summary
chmod +x setup.sh
./setup.sh
```

## Étape 2 : Obtenir les tokens API (5 min)

### Token Todoist

1. Allez sur https://todoist.com/app/settings/integrations/developer
2. Copiez votre "API token"

### Clé OpenAI

1. Allez sur https://platform.openai.com/api-keys
2. Cliquez "Create new secret key"
3. Nommez-la "Todoist Summary"
4. Copiez la clé (vous ne pourrez plus la voir après)

### Mot de passe Gmail

1. Activez l'authentification à 2 facteurs sur votre compte Google (si ce n'est pas déjà fait)
2. Allez sur https://myaccount.google.com/apppasswords
3. Créez un mot de passe pour "Todoist Summary"
4. Copiez le mot de passe (16 caractères sans espaces)

## Étape 3 : Configuration (2 min)

```bash
nano .env
```

Remplissez les valeurs suivantes :

```bash
# Todoist
TODOIST_API_TOKEN=votre_token_todoist

# Préfixes des projets (détection automatique)
WORK_PREFIX=ECL
PERSONAL_PREFIX=Perso
TINKER_PREFIX=Tinker

# OpenAI
OPENAI_API_KEY=votre_clé_openai

# Email
EMAIL_SEND=True
EMAIL_FROM=votre.email@gmail.com
EMAIL_TO=votre.email@gmail.com
SMTP_PASSWORD=votre_mot_de_passe_app_gmail
```

Sauvegardez avec `Ctrl+O`, puis `Ctrl+X`.

## Étape 4 : Premier test (1 min)

```bash
source venv/bin/activate
python main.py
```

Vous devriez voir :
- ✅ Logs de connexion à Todoist
- ✅ Récupération des tâches
- ✅ Génération du résumé
- ✅ Sauvegarde locale
- ✅ Envoi de l'email

Vérifiez votre boîte mail ! 📧

## Étape 5 : Automatisation avec cron (1 min)

Pour que le script s'exécute automatiquement tous les dimanches à 21h :

```bash
crontab -e
```

Ajoutez cette ligne (adaptez le chemin si nécessaire) :

```bash
0 21 * * 0 /home/pi/todoist-ai-summary/venv/bin/python /home/pi/todoist-ai-summary/main.py >> /home/pi/todoist-ai-summary/logs/cron.log 2>&1
```

Sauvegardez et quittez.

## ✅ C'est tout !

Chaque dimanche à 21h, vous recevrez automatiquement votre résumé hebdomadaire ! 🎉

---

## 📱 Organisation Todoist

Pour profiter au maximum du script, organisez vos projets avec des **préfixes** :

```
📁 ECL/Vision              → Catégorie: ECL, Sous-projet: Vision
📁 ECL/Infrastructure      → Catégorie: ECL, Sous-projet: Infrastructure
📁 Perso                   → Catégorie: Perso (sans sous-projet)
📁 Tinker/Horloge          → Catégorie: Tinker, Sous-projet: Horloge
📁 Tinker/Bot Discord      → Catégorie: Tinker, Sous-projet: Bot Discord
```

Le résumé générera automatiquement :
- Un titre `##` par catégorie (ECL, Perso, Tinker)
- Un titre `###` par sous-projet avec son paragraphe distinct

---

## 🆘 Problème ?

### Le script ne trouve aucune tâche
- Vérifiez que vos projets commencent bien par "ECL/", "Perso" ou "Tinker/"
- Ou modifiez les préfixes dans `.env` pour correspondre à vos noms de projets

### L'email n'arrive pas
- Vérifiez que vous utilisez un **mot de passe d'application** (pas votre mot de passe Gmail normal)
- Vérifiez que l'authentification 2FA est activée sur Gmail

### Erreur de token
- Vérifiez qu'il n'y a pas d'espaces avant/après les tokens dans `.env`

---

**Besoin d'aide ?** Consultez le [README.md](README.md) complet.
