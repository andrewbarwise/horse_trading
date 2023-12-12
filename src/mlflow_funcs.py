import mlflow

def log_metrics_to_mlflow(accuracy, precision, recall, f1, roc_auc):
    """Logs classification metrics to MLflow."""
    mlflow.log_metric('accuracy', accuracy)
    mlflow.log_metric('precision', precision)
    mlflow.log_metric('recall', recall)
    mlflow.log_metric('f1_score', f1)
    mlflow.log_metric('roc_auc', roc_auc)