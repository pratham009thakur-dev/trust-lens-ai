import xgboost as xgb
import pandas as pd
import numpy as np

print("Initializing TrustLens AI Model Training (Advanced Dataset)...")

# Set a random seed so the results are reproducible
np.random.seed(42)

# 1. GENERATE LEGITIMATE SITES (Class 0)
# Clean, short URLs with low entropy and normal structures
n_safe = 100
safe_data = pd.DataFrame({
    "url_length": np.random.randint(15, 45, n_safe),
    "domain_entropy": np.random.uniform(1.5, 3.5, n_safe),
    "qty_hyphens": np.random.randint(0, 2, n_safe),
    "qty_dots": np.random.randint(1, 3, n_safe),
    "qty_questionmarks": np.random.randint(0, 2, n_safe),
    "qty_slash": np.random.randint(1, 4, n_safe),
    "contains_scam_keywords": np.random.choice([0, 1], p=[0.95, 0.05], size=n_safe)
})
safe_data['label'] = 0

# 2. GENERATE PHISHING SITES (Class 1)
# Chaotic, long URLs designed to trick users and bypass filters
n_malicious = 100
malicious_data = pd.DataFrame({
    "url_length": np.random.randint(50, 150, n_malicious),
    "domain_entropy": np.random.uniform(4.0, 5.5, n_malicious),
    "qty_hyphens": np.random.randint(2, 7, n_malicious),
    "qty_dots": np.random.randint(3, 8, n_malicious),
    "qty_questionmarks": np.random.randint(0, 4, n_malicious),
    "qty_slash": np.random.randint(3, 8, n_malicious),
    "contains_scam_keywords": np.random.choice([0, 1], p=[0.1, 0.9], size=n_malicious)
})
malicious_data['label'] = 1

# 3. COMBINE AND SHUFFLE
df = pd.concat([safe_data, malicious_data]).sample(frac=1).reset_index(drop=True)

# Separate features (X) from the target label (y)
X = df.drop('label', axis=1)
y = df['label']

print(f"Training on {len(df)} URLs...")

# 4. TRAIN THE XGBOOST MODEL
model = xgb.XGBClassifier(eval_metric='logloss', max_depth=4, learning_rate=0.1)
model.fit(X, y)

# 5. SAVE THE SMARTER MODEL
model.save_model("trustlens_xgb_model.json")
print("SUCCESS: Advanced 'trustlens_xgb_model.json' has been generated and saved!")