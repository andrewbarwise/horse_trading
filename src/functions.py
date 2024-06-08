from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix
import mlflow

def log_metrics_to_mlflow(accuracy, precision, recall, f1, roc_auc):
    """Logs classification metrics to MLflow."""
    mlflow.log_metric('accuracy', accuracy)
    mlflow.log_metric('precision', precision)
    mlflow.log_metric('recall', recall)
    mlflow.log_metric('f1_score', f1)
    mlflow.log_metric('roc_auc', roc_auc)

def eval_classification_model(test_target, predictions):
    # Evaluate the model
    accuracy = accuracy_score(test_target, predictions)
    precision = precision_score(test_target, predictions)
    recall = recall_score(test_target, predictions)
    f1 = f1_score(test_target, predictions)
    roc_auc = roc_auc_score(test_target, predictions)
    conf_matrix = confusion_matrix(test_target, predictions)
    # [[True Negatives, False Positives], 
    #    [False Negatives, True Positives]]

    return accuracy, precision, recall, f1, roc_auc, conf_matrix

def print_metrics(test_target, predictions):
    accuracy, precision, recall, f1, roc_auc, conf_matrix = eval_classification_model(test_target, predictions)
    
    print(f"\nConfusion Matrix: \n{conf_matrix}")
    print(f"Accuracy: {accuracy}")
    print(f'Precision: {precision}')
    print(f'Recall: {recall}')
    print(f'F1 score: {f1}')
    print(f'ROC AUC score: {roc_auc}')

def eval_print_log(test_target, predictions):
    accuracy, precision, recall, f1, roc_auc, conf_matrix = eval_classification_model(test_target, predictions)

    print_metrics(accuracy, precision, recall, f1, roc_auc, conf_matrix)

    log_metrics_to_mlflow(accuracy, precision, recall, f1, roc_auc)

def get_best_model():
    runs = mlflow.search_runs() # fetch all runs
    best_run = runs.loc[runs['metrics.roc_auc'].idxmax()]

    best_model_uri = f'runs:/{best_run.run_id}/mlruns'
    return best_model_uri


