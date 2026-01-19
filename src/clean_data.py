import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data", "raw")

# ENROLMENT DATA
enrolment_path = os.path.join(DATA_DIR, "enrolment")

enrolment_files = [
    os.path.join(enrolment_path, f)
    for f in os.listdir(enrolment_path)
    if f.endswith(".csv")
]

enrolment_dfs = []

for file in enrolment_files:
    df = pd.read_csv(file)
    enrolment_dfs.append(df)

enrolment = pd.concat(enrolment_dfs, ignore_index=True)
print("Enrolment data shape:", enrolment.shape)

enrolment.columns = enrolment.columns.str.lower().str.strip()
enrolment = enrolment.drop_duplicates()

cleaned_dir = os.path.join(BASE_DIR, "data", "cleaned")
os.makedirs(cleaned_dir, exist_ok=True)

enrolment.to_csv(
    os.path.join(cleaned_dir, "enrolment_cleaned.csv"),
    index=False
)

print(" Enrolment data cleaned and saved successfully")

# DEMOGRAPHIC DATA

demographic_path = os.path.join(DATA_DIR, "demographic")

demographic_files = [
    os.path.join(demographic_path, f)
    for f in os.listdir(demographic_path)
    if f.endswith(".csv")
]

demographic_dfs = []

for file in demographic_files:
    df = pd.read_csv(file)
    demographic_dfs.append(df)

demographic = pd.concat(demographic_dfs, ignore_index=True)
print("Demographic data shape:", demographic.shape)

demographic.columns = demographic.columns.str.lower().str.strip()
demographic = demographic.drop_duplicates()

demographic.to_csv(
    os.path.join(cleaned_dir, "demographic_cleaned.csv"),
    index=False
)

print(" Demographic data cleaned and saved successfully")

# BIOMETRIC DATA

biometric_path = os.path.join(DATA_DIR, "biometric")

biometric_files = [
    os.path.join(biometric_path, f)
    for f in os.listdir(biometric_path)
    if f.endswith(".csv")
]

biometric_dfs = []

for file in biometric_files:
    df = pd.read_csv(file)
    biometric_dfs.append(df)

biometric = pd.concat(biometric_dfs, ignore_index=True)
print("Biometric data shape:", biometric.shape)

biometric.columns = biometric.columns.str.lower().str.strip()
biometric = biometric.drop_duplicates()

biometric.to_csv(
    os.path.join(cleaned_dir, "biometric_cleaned.csv"),
    index=False
)

print(" Biometric data cleaned and saved successfully")
