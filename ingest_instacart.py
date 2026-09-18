import os
import zipfile
import snowflake.connector
from kaggle.api.kaggle_api_extended import KaggleApi

# 1. Authentification Kaggle et téléchargement du dataset public
print("⬇️ Connexion à Kaggle et téléchargement...")
api = KaggleApi()
api.authenticate()

data_dir = "./instacart_data"
os.makedirs(data_dir, exist_ok=True)

# Téléchargement depuis le miroir public officiel du dataset
dataset_slug = "psparks/instacart-market-basket-analysis"
api.dataset_download_files(dataset_slug, path=data_dir, unzip=True)

print("📦 Décompression des fichiers CSV compressés...")
for item in os.listdir(data_dir):
    if item.endswith(".zip"):
        with zipfile.ZipFile(os.path.join(data_dir, item), 'r') as zip_ref:
            zip_ref.extractall(data_dir)

print("✅ Fichiers CSV prêts en local.")

# 2. Connexion à Snowflake
print("❄️ Connexion à Snowflake...")
conn = snowflake.connector.connect(
    user='',
    password='',
    account='',
    warehouse='DBT_WH',
    database='INSTACART_DB',
    schema='RAW',
    role='DBT_ROLE'
)
cur = conn.cursor()

# 3. Préparation du Stage interne
print("⚙️ Configuration du stage de chargement...")
cur.execute("CREATE OR REPLACE FILE FORMAT CSV_FORMAT TYPE = CSV FIELD_DELIMITER = ',' SKIP_HEADER = 1 FIELD_OPTIONALLY_ENCLOSED_BY = '\"';")
cur.execute("CREATE OR REPLACE STAGE INSTACART_STAGE FILE_FORMAT = CSV_FORMAT;")

# Mapping tables cibles / fichiers sources
files_to_load = {
    "RAW_AISLES": "aisles.csv",
    "RAW_DEPARTMENTS": "departments.csv",
    "RAW_PRODUCTS": "products.csv",
    "RAW_ORDERS": "orders.csv",
    "RAW_ORDER_PRODUCTS": "order_products__prior.csv"
}

# 4. Ingestion via Stage et COPY INTO
for table, filename in files_to_load.items():
    local_path = os.path.join(data_dir, filename)
    if os.path.exists(local_path):
        print(f"🚀 Téléversement de {filename} vers Snowflake Stage...")
        cur.execute(f"PUT file://{os.path.abspath(local_path)} @INSTACART_STAGE AUTO_COMPRESS=TRUE OVERWRITE=TRUE;")
        
        print(f"⚡ Ingestion dans {table} via COPY INTO...")
        cur.execute(f"COPY INTO {table} FROM @INSTACART_STAGE/{filename} FILE_FORMAT = CSV_FORMAT ON_ERROR = 'CONTINUE';")
        print(f"   -> Table {table} chargée avec succès.")
    else:
        print(f"⚠️ Fichier introuvable : {filename}")

cur.close()
conn.close()
print("🎉 Ingestion complète terminée !")
