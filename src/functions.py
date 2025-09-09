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

def profit_calculation(df, stake = 1):
    """
    Calculate ROI, total returns from the model predictions.

    Args:
        df (pd.Dataframe): A dataframe that has a column holding the model predictions
        stake (int): The amount staked for each bet

    Returns:
        print() 
    """
    # Filter rows where model_preds == 1
    bets = df[df['model_preds'] == 1].copy()

    # Calculate returns
    bets['Return'] = bets.apply(
        lambda row: (row['BF Decimal SP1'] - 1) * stake if row['Won (1=Won, 0=Lost)'] == 1 else -1,
        axis=1
    )

    # Total return
    total_return = bets['Return'].sum()

    # total number of bets
    total_bets = len(bets)

    # Calculate accuracy: Percentage of correct predictions where the model predicted 1 and won
    correct_predictions = bets[bets['Won (1=Won, 0=Lost)'] == 1].shape[0]

    if total_bets > 0:
        accuracy = (correct_predictions / total_bets) * 100  # Accuracy in percentage
        return_per_pound = total_return / (total_bets * stake)
    else:
        accuracy = 0
        return_per_pound = 0

    print(f"Total number of bets: {total_bets}")
    print(f"Total return from betting £{stake:.2f} on each prediction where model_preds == 1: £{total_return:.2f}")
    print(f"Return per pound invested: £{return_per_pound:.2f}")
    print(f"Model accuracy: {accuracy:.2f}%")

def calculate_lay_stakes_multiple_runners(accepted_bets, other_horse_odds, profit_margin=0.05):
    """
    Calculate lay stakes for remaining horses to balance the book
    when accepting multiple bets.

    Args:
        accepted_bets (list of tuples): a list of tuples where each tuple contains (stake, odds)
            for accepted bets.
        other_horse_odds (list): list of decimal odds for the remaining horses
        profit_margin(float): desired profit margin ( default equals 5%)

    Returns:
        dict: a dictionary of lay stakes for each remaining horse

    Example usage:
        accepted_bets = [(100, 3.0), (150, 4.0)]  # (stake, odds) for Horse 1 and Horse 2
        other_horses_odds = [7.0, 9.0]  # Odds for Horse 3 and Horse 4

        lay_stakes = calculate_lay_stakes_multiple_accepted(accepted_bets, other_horses_odds)
        print(lay_stakes)
    """
    # calculate total liability from the accepted bets
    total_liability = sum(stake * (odds - 1) for stake, odds in accepted_bets)

    # calculate lay stakes for remaining horses
    lay_stakes = {}
    for i, odds in enumerate(other_horse_odds, start = len(accepted_bets) + 1):
        lay_stake = (total_liability * (1 + profit_margin)) / (odds - 1)
        lay_stakes[f'Horse {i}'] = round(lay_stake, 2)

    return lay_stakes

def fetch_race_results(market_ids, trading):
    try:
        data = trading.race_card.get_race_result(market_ids=market_ids)
    except Exception as e:
        print(f"An error occurred: {e}")
        data = []

    # Process and display the data
    flat_data = []

    for race in data:
        for runner in race.get('runners', []):
            for selection in runner.get('selections', []):
                if selection['marketType'] == 'WIN' and 'bsp' in selection:
                    flat_data.append({
                        'race_id': race.get('raceId'),
                        'country_code': race.get('course', {}).get('countryCode'),
                        'race_title': race.get('raceTitle'),
                        'race_class': race.get('raceClassification', {}).get('classification'),
                        'distance': race.get('distance'),
                        'course_type': race.get('course', {}).get('courseType'),
                        'surface_type': race.get('course', {}).get('surfaceType'),
                        'market_id': selection.get('marketId'),
                        'horse_id': runner.get('horseId'),
                        'saddle_cloth': runner.get('saddleCloth'),
                        'isNonRunner': runner.get('isNonRunner'),
                        'position': runner.get('position'),
                        'selection_id': selection.get('selectionId'),
                        'bsp': selection.get('bsp')
                    })

    return pd.DataFrame(flat_data)

def monte_carlo_sim(df_race, n_sims = 10000, seed = 42):
    """
    df_race: df one race, each row represents a horse
    Returns: df with simulated win prob's and expected value of SP bets
    
    """
    rng = np.random.default_rng(seed)
    n_horses = len(df_race)
    win_counts = np.zeros(n_horses)

    for _ in range(n_sims):
        winner = rng.choice(
            df_race.index,
            p=df_race['pred_prob']/df_race['pred_prob'].sum()
        )
        win_counts[winner] += 1

    df_out = df_race.copy()
    df_out['mc_win_prob'] = win_counts / n_sims
    df_out['ev'] = df_out['BF Decimal SP1'] * df_out['mc_win_prob'] - 1
    return df_out
