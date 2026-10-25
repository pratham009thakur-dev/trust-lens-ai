import math
import tldextract

class URLExtractor:
    def __init__(self):
        # High-risk target keywords frequently used in phishing schemes
        self.suspicious_keywords = [
            "login", "verify", "secure", "update", "banking", 
            "account", "paypal", "signin", "auth", "support"
        ]

    def calculate_shannon_entropy(self, text: str) -> float:
        """
        Calculates the mathematical randomness (entropy) of a string.
        High entropy indicates randomly generated domain names (DGA).
        """
        if not text:
            return 0.0
        
        # Calculate the frequency of each unique character in the string
        frequencies = {char: text.count(char) / len(text) for char in set(text)}
        
        # Apply the Shannon Entropy Formula: H(X) = -sum(P(x) * log2(P(x)))
        entropy = -sum(p * math.log2(p) for p in frequencies.values())
        return round(entropy, 4)

    def extract_features(self, url: str) -> dict:
        """
        Parses a raw URL string and converts its attributes into a 
        structured dictionary of numerical mathematical vectors.
        """
        # Lowercase the target string to prevent casing evasion bypasses
        url = url.lower().strip()
        
        # Clean out basic protocol prefixes for isolated string structural metrics
        clean_url = url.replace("http://", "").replace("https://", "").replace("www.", "")
        
        # Parse the domain architecture using tldextract (separates subdomain, domain, and TLD)
        extracted = tldextract.extract(url)
        domain_parts = extracted.domain
        subdomain_parts = extracted.subdomain
        fqdn = f"{subdomain_parts}.{domain_parts}" if subdomain_parts else domain_parts

        # 1. Structural Lexical Geometry Metrics
        url_length = len(url)
        dot_count = url.count('.')
        hyphen_count = url.count('-')
        digit_count = sum(char.isdigit() for char in url)
        digit_density = round(digit_count / url_length, 4) if url_length > 0 else 0.0

        # 2. Subdomain Nesting Depth Tracker
        # Splitting subdomains by '.' gives us how deep the attacker nested their links
        subdomain_count = len(subdomain_parts.split('.')) if subdomain_parts else 0

        # 3. Text Context Risk Assessment
        # Count how many scam-related keywords exist inside the path string
        keyword_match_count = sum(1 for keyword in self.suspicious_keywords if keyword in url)

        # 4. Computational Randomness Evaluation
        domain_entropy = self.calculate_shannon_entropy(fqdn)

        # Consolidate all data into a clean, uniform pipeline payload schema
        return {
            "url": url,
            "metrics": {
                "url_length": url_length,
                "dot_count": dot_count,
                "hyphen_count": hyphen_count,
                "digit_density": digit_density,
                "subdomain_count": subdomain_count,
                "keyword_match_count": keyword_match_count,
                "domain_entropy": domain_entropy
            }
        }

# =====================================================================
# LOCAL TESTING SUITE
# =====================================================================
if __name__ == "__main__":
    extractor = URLExtractor()
    
    # Let's test a known safe domain vs an obvious multi-tiered phishing setup
    safe_url = "https://google.com"
    phish_url = "http://signin.paypal.com.verify-security-update.x92nslw.net/login.php"
    
    print("\n--- STANDALONE FEATURE EXTRACTION TEST RUN ---")
    print("\n[TESTING SAFE LINK]:", safe_url)
    print(extractor.extract_features(safe_url))
    
    print("\n[TESTING PHISHING LINK]:", phish_url)
    print(extractor.extract_features(phish_url))