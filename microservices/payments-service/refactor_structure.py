import os
import shutil

# ---------------------------------------------
# CONFIGURATION
# ---------------------------------------------
DRY_RUN = False # ⚠️ Mettre False après confirmation
BASE_DIR = os.getcwd()  # détecte automatiquement le dossier courant

print(f"Working directory: {BASE_DIR}")

# ❌ Ancienne structure à supprimer
OLD_PATHS = [
    "prisma",
    "config",
    "shared",
    "apps",
    "manage.py",
    "requirements.txt",
    ".env",
    ".env.example",
    "docker-entrypoint.sh"
]

# ✅ Nouvelle structure Java à créer
NEW_STRUCTURE = [
    "src/main/java/com/lms/payment/model/entity",
    "src/main/java/com/lms/payment/model/enums",
    "src/main/java/com/lms/payment/repository",
    "src/main/java/com/lms/payment/service",
    "src/main/java/com/lms/payment/gateway",
    "src/main/java/com/lms/payment/controller",
    "src/main/java/com/lms/payment/dto",
    "src/main/java/com/lms/payment/exception",
    "src/main/java/com/lms/payment/config",
    "src/main/resources",
]

FILES_TO_CREATE = [
    "Dockerfile",
    "docker-compose.yml",
    "pom.xml",
    "src/main/resources/application.yml",
]

# ---------------------------------------------
# SUPPRESSION DE L’ANCIENNE STRUCTURE
# ---------------------------------------------
print("\n--- Removing old files & folders ---")

for item in OLD_PATHS:
    path = os.path.join(BASE_DIR, item)
    if os.path.exists(path):
        if DRY_RUN:
            print(f"[DRY-RUN] Would remove: {path}")
        else:
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)
            print(f"Removed: {path}")
    else:
        print(f"Not found (skip): {path}")

# ---------------------------------------------
# CRÉATION DE LA NOUVELLE STRUCTURE
# ---------------------------------------------
print("\n--- Creating new structure ---")

for folder in NEW_STRUCTURE:
    path = os.path.join(BASE_DIR, folder)
    if DRY_RUN:
        print(f"[DRY-RUN] Would create folder: {path}")
    else:
        os.makedirs(path, exist_ok=True)
        print(f"Created: {path}")

# ---------------------------------------------
# CRÉATION DES FICHIERS VIDES
# ---------------------------------------------
print("\n--- Creating required files ---")

for file in FILES_TO_CREATE:
    path = os.path.join(BASE_DIR, file)
    if DRY_RUN:
        print(f"[DRY-RUN] Would create file: {path}")
    else:
        # créer dossier parent si nécessaire
        os.makedirs(os.path.dirname(path), exist_ok=True)
        open(path, 'a').close()
        print(f"Created: {path}")

print("\n--- DONE ---")
print("⚠️ DRY_RUN is ON — no changes were actually made.")
print("Set DRY_RUN = False when you're ready to apply changes.")
