# Equipment Maintenance Decision System — Web App (Omar)

A live, interactive website version of the project. **Runs 100% offline** — no API
key, no internet calls — so it works on PythonAnywhere's **free** tier and anywhere
in the world, including mainland China.

- `flask_app.py` — the whole app (logic + web pages + charts), one file.
- `requirements.txt` — Python packages.

---

## A) Run it locally first (to preview)

```bash
cd Omar_webapp
pip3 install -r requirements.txt
python3 flask_app.py
```
Then open **http://localhost:5000** in your browser.

---

## B) Put it online — PythonAnywhere (free), like fayazpainda.pythonanywhere.com

> ⚠️ A **free** PythonAnywhere account gives **one** web app at
> `https://<your-username>.pythonanywhere.com`. If your own account already hosts
> another project, **Omar should make his own free account** so the URL is his
> (e.g. `https://omar.pythonanywhere.com`).

### 1. Create a free account
Go to https://www.pythonanywhere.com → **Pricing & signup → Create a Beginner account (free)**.
The username you pick becomes the web address.

### 2. Get the code onto PythonAnywhere
On the **Consoles** tab → start a **Bash** console, then run:
```bash
git clone https://github.com/fayazpainda/equipment-maintenance
```
(The web-app files are in the `webapp/` folder of that repo.)

Install the packages for the Python version you'll use (3.10 shown):
```bash
pip3.10 install --user flask pandas numpy matplotlib scikit-learn
```

### 3. Create the web app
**Web** tab → **Add a new web app** → **Manual configuration** → **Python 3.10**.

### 4. Point it at the code
On the **Web** tab, click the **WSGI configuration file** link and replace its
entire contents with (change `omar` to your username):
```python
import sys
path = '/home/omar/equipment-maintenance/webapp'
if path not in sys.path:
    sys.path.append(path)

from flask_app import app as application
```
Save it.

### 5. Reload
Back on the **Web** tab, click the big green **Reload** button, then open
`https://<your-username>.pythonanywhere.com`.

That's the link to send the teacher. 🎉

---

## Why this works on the free tier
The free plan blocks outbound internet to non-whitelisted sites, but this app makes
**no external calls at all** — all the data, scoring, anomaly detection and
recommendations are computed locally. So nothing is blocked.

## Updating later
After editing the code on GitHub, in the PythonAnywhere Bash console:
```bash
cd ~/equipment-maintenance && git pull
```
then **Reload** the web app.
