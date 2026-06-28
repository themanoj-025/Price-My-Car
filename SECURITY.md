# Security Policy for Price-My-Car

## Reporting a Vulnerability

If you discover a security vulnerability in Price-My-Car, please report it privately.

**How to report:**
- Open a private security advisory on GitHub (if this repository is public).
- Email **manojjana.0025@gmail.com** directly. This contact is also listed in our [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).
- If neither channel works, open a standard issue with the label `security` without including exploit details.

**Expectations:**
- We will acknowledge receipt within 5 business days.
- We will respond with an assessment within 10 business days.

## Security Posture

**⚠️ Important:** Price-My-Car is an educational/data-science application. It is **not designed for production deployment** without security hardening.

## Security Measures

### Implemented
- **None.** This project has no authentication, no input sanitization, and no HTTPS enforcement.

### Not Implemented (Critical Gaps)
- **No authentication:** The Streamlit app is open to all visitors.
- **No input sanitization:** User-provided car parameters are used directly for predictions.
- **No rate limiting:** The app can be called unlimited times.
- **No HTTPS:** All communication is plain HTTP.
- **No API:** The application has no REST API — it is a single-user Streamlit interface only.

## Data Privacy

- The dataset (`Cleaned_Car_data.csv`) contains used car listing data — it does **not** contain personal user information.
- Trained models (`.pkl` files) are serialized scikit-learn pipelines and models. Treat them as potentially untrusted if sourced externally.
- No user data is collected, stored, or transmitted to external services.

## Model Security

- Serialized scikit-learn models (`.pkl` files) can potentially execute arbitrary code when deserialized. **Only load models from trusted sources.**
- Models are stored in `ml_ready/` and `models/` directories. Ensure these directories have appropriate filesystem permissions.

## Recommended Hardening

If deploying this application publicly:

1. Add basic authentication (Streamlit supports secrets-based auth).
2. Add input validation to sanitize user-provided car parameters.
3. Implement rate limiting at the reverse proxy level.
4. Deploy behind a TLS-terminating reverse proxy.
5. Use trusted model files only — do not load `.pkl` files from untrusted sources.

## Dependency Security

```bash
pip-audit -r requirements.txt
```

Key dependencies: scikit-learn, XGBoost, pandas, numpy — keep these updated for security patches.
