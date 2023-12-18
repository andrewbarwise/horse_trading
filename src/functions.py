from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, roc_curve
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

    return accuracy, precision, recall, f1, roc_auc

def print_metrics(accuracy, precision, recall, f1, roc_auc):
    print(f"Accuracy: {accuracy}")
    print(f'Precision: {precision}')
    print(f'Recall: {recall}')
    print(f'F1 score: {f1}')
    print(f'ROC AUC score: {roc_auc}')

def eval_print_log(test_target, predictions):
    accuracy, precision, recall, f1, roc_auc = eval_classification_model(test_target, predictions)

    print_metrics(accuracy, precision, recall, f1, roc_auc)

    log_metrics_to_mlflow(accuracy, precision, recall, f1, roc_auc)

def get_best_model():
    runs = mlflow.search_runs() # fetch all runs
    best_run = runs.loc[runs['metrics.roc_auc'].idxmax()]

    best_model_uri = f'runs:/{best_run.run_id}/mlruns'
    return best_model_uri

def split_data(data, column_name, test_size = 0.2):

    unique_ids = data[column_name]

    # determine the number of samples for the test set based on test size
    test_samples = int(len(unique_ids.unique()) * test_size)

    # split the unique identifiers into training and test sets
    test_unique_ids = unique_ids.unique()[:test_samples]
    train_unique_ids = unique_ids.unique()[test_samples:]

    train_data = data[data[column_name].isin(train_unique_ids)]
    test_data = data[data[column_name].isin(test_unique_ids)]

    return train_data, test_data
