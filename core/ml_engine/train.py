import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import xgboost as xgb
import joblib

# Import your functioning Phase 1 extractor class directly
from extractor import URLExtractor

def generate_balanced_dataset():
    """
    Simulates and assembles an engineered training dataset consisting of 
    verified safe domains and advanced multi-tier phishing links.
    """
    print("[*] Initializing raw source URL records mapping...")
    
    # 1. Clean / Legitimate Domain Targets
    legitimate_urls = [
        "https://google.com", "https://github.com", "https://amazon.in",
        "https://microsoft.com", "https://stackoverflow.com", "https://linkedin.com",
        "https://netflix.com", "https://wikipedia.org", "https://apple.com",
        "https://medium.com", "https://twitter.com", "https://chatgpt.com"
    ]
    
    # 2. Synthetic & High-Risk Phishing/Malicious Patterns
    phishing_urls = [
        "http://signin.paypal.com.verify-security-update.x92nslw.net/login.php",
        "https://secure-login-chasebank-update.com/auth",
        "http://verify-your-holding-account-now.top/login",
        "http://netflix-billing-issue-resolve.xyz/signin",
        "https://amazon-security-check-verification.info/index.html",
        "http://office365-password-reset-portal.cn/login",
        "http://xn--appl-ep0a.com-security-setting.org/login",
        "http://secure-update-identity-routing.biz/verify",
        "https://facebook-login-identity-checkpoint.net/secure",
        "http://immediate-action-required-suspension-notice.cc/auth"
    ]
    
    extractor = URLExtractor()
    dataset_records = []
    
    # Process legitimate urls (Label = 0)
    for url in legitimate_urls:
        features = extractor.extract_features(url)
        metrics = features["metrics"]
        metrics["label"] = 0  # 0 indicates Safe/Legitimate
        dataset_records.append(metrics)
        
    # Process phishing urls (Label = 1)
    for url in phishing_urls:
        features = extractor.extract_features(url)
        metrics = features["metrics"]
        metrics["label"] = 1  # 1 indicates Phishing/Malicious
        dataset_records.append(metrics)
        
    # Transform raw array dicts into a structured mathematical matrix DataFrame
    df = pd.DataFrame(dataset_records)
    print(f"[+] Matrix compilation complete. Total Samples processed: {len(df)}")
    return df

def run_ml_pipeline():
    print("\n==================================================")
    print("      TRUSTLENS AI CYBER-MODEL TRAINING SYSTEM      ")
    print("==================================================\n")
    
    # 1. Generate clean structural data table
    df = generate_balanced_dataset()
    
    # Isolate our target input features (X) and label weights (y)
    feature_columns = [
        "url_length", "dot_count", "hyphen_count", 
        "digit_density", "subdomain_count", "keyword_match_count", "domain_entropy"
    ]
    
    X = df[feature_columns]
    y = df["label"]
    
    # 2. Partition data into Train/Test subsets (80% training logic, 20% validation logic)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=42)
    
    print(f"[*] Training Subset Size: {len(X_train)} samples")
    print(f"[*] Evaluation Subset Size: {len(X_test)} samples")
    
    # 3. Instantiate and train our optimized XGBoost Classifier engine
    print("[*] Launching Extreme Gradient Boosting Tree Classifier...")
    model = xgb.XGBClassifier(
        n_estimators=50,
        max_depth=3,
        learning_rate=0.1,
        random_state=42,
        eval_metric="logloss"
    )
    
    # Train the model mapping logic
    model.fit(X_train, y_train)
    print("[+] Model optimization training complete.")
    
    # 4. Run active prediction validation testing
    y_pred = model.predict(X_test)
    
    # Compute accuracy evaluation scores
    accuracy = accuracy_score(y_test, y_pred)
    print(f"\n[+] Validation Phase Matrix Accuracy: {accuracy * 100:.2f}%")
    print("\n--- DETAILED CLASSIFICATION ANALYSIS REPORT ---")
    print(classification_report(y_test, y_pred, target_names=["Legitimate (0)", "Phishing (1)"]))
    
    # 5. Export our binary weights matrix model artifact to disk using joblib
    model_output_path = "phishing_model.joblib"
    joblib.dump(model, model_output_path)
    print(f"[+] Success! Compiled production model saved to: {os.path.abspath(model_output_path)}")

if __name__ == "__main__":
    run_ml_pipeline()