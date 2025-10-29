# 🔧 Guide de dépannage

Ce guide vous aide à résoudre les problèmes courants.

## 🔍 Diagnostic général

Avant de chercher le problème, lancez le script manuellement avec logs détaillés :

```bash
cd ~/todoist-ai-summary
source venv/bin/activate
python main.py
```

Regardez les logs dans :
- Console (sortie standard)
- `logs/execution_YYYYMMDD_HHMMSS.log`

---

## ❌ Erreurs courantes

### 1. "TODOIST_API_TOKEN manquant dans .env"

**Cause** : Le fichier `.env` n'existe pas ou est mal configuré.

**Solution** :
```bash
# Vérifier que le fichier existe
ls -la .env

# Vérifier son contenu
cat .env | grep TODOIST_API_TOKEN

# Si absent, recréer depuis le template
cp .env.example .env
nano .env
```

**Points à vérifier** :
- ✅ Pas d'espaces autour du `=`
- ✅ Pas de guillemets autour de la valeur
- ✅ Pas de ligne vide avant le token

**Correct** :
```bash
TODOIST_API_TOKEN=abc123def456
```

**Incorrect** :
```bash
TODOIST_API_TOKEN = "abc123def456"  # ❌ espaces et guillemets
TODOIST_API_TOKEN=                  # ❌ vide
```

---

### 2. "Aucune tâche complétée cette semaine"

**Cause** : Le script ne trouve pas de tâches dans la période.

**Solutions** :

#### Option A : Vérifier les préfixes de projets

```bash
# Dans .env, vérifiez que les préfixes correspondent à vos projets Todoist
nano .env

# Les préfixes sont case-sensitive et doivent correspondre au DÉBUT du nom !
WORK_PREFIX=ECL        # Correct pour "ECL/Vision", "ECL/Infrastructure"
WORK_PREFIX=ecl        # ❌ Ne détectera pas "ECL/Vision"
WORK_PREFIX=E          # ❌ Trop court, détectera aussi d'autres projets
```

**Important** : Le script cherche tous les projets qui **COMMENCENT PAR** le préfixe.

Exemples de détection :
- `WORK_PREFIX=ECL` détecte : `ECL/Vision`, `ECL/Infrastructure`, `ECL`
- `PERSONAL_PREFIX=Perso` détecte : `Perso`, `Perso/Maison`
- `TINKER_PREFIX=Tinker` détecte : `Tinker/Bot`, `Tinker/Horloge`

#### Option B : Tester avec une autre période

Modifiez temporairement `main.py` pour tester sur un mois :

```python
# Dans la fonction get_week_range()
start_date = today - timedelta(days=30)  # Au lieu de 7
end_date = today
```

#### Option C : Vérifier manuellement dans Todoist

1. Allez dans Todoist
2. Filtres → Complété
3. Vérifiez qu'il y a bien des tâches complétées

---

### 3. Erreur d'envoi d'email

**Message** : `SMTPAuthenticationError` ou `Authentication failed`

**Cause** : Problème d'authentification Gmail.

**Solutions** :

#### Étape 1 : Vérifier que vous utilisez un mot de passe d'application

❌ **N'utilisez PAS** votre mot de passe Gmail normal !

✅ **Créez un mot de passe d'application** :
1. https://myaccount.google.com/apppasswords
2. Sélectionnez "Autre" → "Todoist Summary"
3. Copiez le mot de passe (16 caractères, format : xxxx xxxx xxxx xxxx)
4. Collez dans `.env` **SANS les espaces** : `xxxxxxxxxxxxxxxx`

#### Étape 2 : Activer l'authentification à 2 facteurs

Si vous n'avez pas accès aux mots de passe d'application :
1. https://myaccount.google.com/security
2. Activez l'authentification à 2 facteurs
3. Attendez quelques minutes
4. Créez ensuite le mot de passe d'application

#### Étape 3 : Vérifier la configuration

```bash
cat .env | grep EMAIL
```

Doit afficher :
```bash
EMAIL_FROM=votre.email@gmail.com
EMAIL_TO=votre.email@gmail.com
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_PASSWORD=xxxxxxxxxxxxxxxx
```

#### Étape 4 : Tester manuellement SMTP

```python
import smtplib
server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()
server.login('votre.email@gmail.com', 'votre_mot_de_passe_app')
server.quit()
print("✅ Connexion OK")
```

---

### 4. Erreur OpenAI "Invalid API Key"

**Solutions** :

#### Vérifier la clé
```bash
cat .env | grep OPENAI_API_KEY
```

#### Tester la clé manuellement
```python
from openai import OpenAI
client = OpenAI(api_key='votre_clé')
response = client.models.list()
print("✅ Clé valide")
```

#### Vérifier les crédits
1. https://platform.openai.com/account/billing
2. Vérifiez que vous avez des crédits
3. Si pas de crédits, ajoutez un moyen de paiement

---

### 5. Cron ne s'exécute pas

**Diagnostic** :

```bash
# Vérifier que cron est actif
sudo systemctl status cron

# Voir les logs cron
grep CRON /var/log/syslog | tail -20

# Voir les logs du script
tail -f ~/todoist-ai-summary/logs/cron.log
```

**Solutions** :

#### Problème 1 : Chemins incorrects

Dans `crontab -e`, utilisez des **chemins absolus** :

❌ **Incorrect** :
```bash
0 21 * * 0 python main.py
```

✅ **Correct** :
```bash
0 21 * * 0 /home/pi/todoist-ai-summary/venv/bin/python /home/pi/todoist-ai-summary/main.py >> /home/pi/todoist-ai-summary/logs/cron.log 2>&1
```

#### Problème 2 : Variables d'environnement

Cron n'a pas accès aux mêmes variables que votre shell.

**Solution** : Ajouter en haut du crontab :

```bash
SHELL=/bin/bash
PATH=/usr/local/bin:/usr/bin:/bin
```

#### Problème 3 : Permissions

```bash
# Vérifier les permissions
ls -la ~/todoist-ai-summary/main.py
ls -la ~/todoist-ai-summary/venv/bin/python

# Si nécessaire, corriger
chmod +x ~/todoist-ai-summary/main.py
```

#### Test manuel de la commande cron

Copiez la ligne de cron et exécutez-la :

```bash
/home/pi/todoist-ai-summary/venv/bin/python /home/pi/todoist-ai-summary/main.py
```

Si ça fonctionne manuellement mais pas avec cron → problème de PATH ou variables d'environnement.

---

### 6. "Module not found" ou ImportError

**Cause** : Dépendances non installées ou mauvais environnement virtuel.

**Solutions** :

```bash
# Réinstaller les dépendances
cd ~/todoist-ai-summary
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Vérifier l'installation
pip list | grep -E "requests|openai|python-dotenv"
```

**Doit afficher** :
```
openai         1.12.0
python-dotenv  1.0.0
requests       2.31.0
```

---

### 7. "Rate limit exceeded" (OpenAI)

**Cause** : Trop de requêtes en peu de temps.

**Solutions** :

1. **Attendez quelques minutes** et relancez
2. **Vérifiez votre tier** : https://platform.openai.com/account/limits
3. **Réduisez WEEKS_OF_CONTEXT** dans `.env` (de 4 à 2)

---

### 8. Résumé de mauvaise qualité ou trop émotionnel

**Causes possibles** :
- Tâches mal nommées dans Todoist
- Pas assez de contexte
- Le modèle extrapole des émotions

**Solutions** :

#### Améliorer les noms de tâches

❌ **Mauvais** :
- "Faire ça"
- "Trucs"
- "TODO"

✅ **Bon** :
- "Optimiser paramètres réseau neurones"
- "Réparer fuite évier cuisine"
- "Câbler LEDs horloge ESP32"

Plus les tâches sont descriptives, plus le résumé sera factuel et précis.

#### Ajuster le modèle

Dans `.env`, essayez `gpt-4o` (plus cher mais meilleur) :
```bash
OPENAI_MODEL=gpt-4o
```

#### Modifier le prompt pour plus de factualité

Éditez `src/summarizer.py` → méthode `_build_prompt()`.

Actuellement, le prompt insiste déjà sur :
- "Rester strictement factuel"
- "Ne PAS extrapoler d'émotions ou de ressentis"
- "Décrire ce qui a été fait, pas comment je me suis senti"

Si le modèle extrapole encore trop, vous pouvez renforcer ces instructions.

---

## 🧪 Mode debug

Pour des logs plus détaillés, modifiez dans `.env` :

```bash
LOG_LEVEL=DEBUG
```

Puis relancez :
```bash
python main.py
```

---

## 📞 Besoin d'aide ?

Si aucune solution ne fonctionne :

1. **Copiez les logs** :
```bash
cat logs/execution_*.log | tail -100
```

2. **Vérifiez votre configuration** :
```bash
cat .env | grep -v PASSWORD  # Affiche la config sans le mot de passe
```

3. **Ouvrez une issue** sur GitHub avec :
   - Le message d'erreur complet
   - Les logs pertinents (SANS les clés API !)
   - Votre configuration (SANS les secrets !)

---

## ✅ Checklist de diagnostic

Avant de demander de l'aide, vérifiez :

- [ ] Le fichier `.env` existe et est rempli
- [ ] Les tokens API sont valides (Todoist + OpenAI)
- [ ] Le mot de passe Gmail est un mot de passe d'application
- [ ] Les noms de projets correspondent exactement
- [ ] L'environnement virtuel est activé
- [ ] Les dépendances sont installées
- [ ] Il y a des tâches complétées dans Todoist
- [ ] Vous avez des crédits OpenAI
- [ ] Le script fonctionne manuellement (avant de tester avec cron)

---

**Bon debugging ! 🔍**
