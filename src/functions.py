from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, roc_curve

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