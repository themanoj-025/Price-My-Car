#!/bin/bash
set -e
# =============================================================================
# setup.sh — Streamlit Cloud deployment setup script
# =============================================================================
# This runs automatically BEFORE the app starts on Streamlit Cloud.
# It generates the .npy files from the prepared CSV if they don't exist.
# =============================================================================

echo "🚀 Running setup.sh for AutoIntel Car Price Prediction..."

# Check if ml_ready/ exists
if [ ! -d "ml_ready" ]; then
    echo "📁 Creating ml_ready/ directory..."
    mkdir -p ml_ready/models
fi

# Generate .npy files if missing (they're gitignored due to size)
if [ ! -f "ml_ready/X_train.npy" ] || [ ! -f "ml_ready/preprocessor.pkl" ]; then
    echo "🧠 Generating ML preprocessed data from Cleaned_Car_data.csv..."
    python prepare_ml_data.py
    echo "✅ Preprocessing complete!"
else
    echo "✅ ML artifacts already present — skipping preprocessing."
fi

# Train models if missing
if [ ! -f "ml_ready/models/linear_regression.pkl" ]; then
    echo "🤖 Training ML models..."
    python train_dashboard_models.py
    echo "✅ Model training complete!"
fi

echo "✅ AutoIntel setup complete — starting dashboard..."
