# Price-My-Car — Architecture

```mermaid
graph TB
    subgraph UI ["Streamlit Dashboard"]
        A[streamlit_app.py] --> B[Prediction Form]
        A --> C[Model Dashboard]
        A --> D[Data Explorer]
    end

    subgraph ML ["ML Pipeline"]
        E[helpers.py]
        F[train_dashboard_models.py]
        G[tune_hyperparameters.py]
        H[prepare_ml_data.py]
    end

    subgraph Models ["Trained Models"]
        I[ml_ready/preprocessor.pkl]
        J[ml_ready/feature_names.pkl]
        K[ml_ready/models/*.pkl]
    end

    subgraph Data ["Dataset"]
        L[Cleaned_Car_data.csv]
    end

    UI --> E
    UI --> I
    UI --> J
    UI --> K
    ML --> L
    ML --> I
    ML --> K
```

## Key Patterns

- **Multiple models compared**: Linear, Ridge, Lasso, KNN, SVR, Random Forest, Gradient Boosting, XGBoost
- **Feature engineering**: Preprocessor pipeline in `ml_ready/preprocessor.pkl`
- **No external API**: Fully local inference — no data sent to external services
- **Notebook generation**: `create_notebook.py` auto-generates Jupyter notebooks from markdown
