# feast-efficiency-testing

This repository exists to demonstrate Feast's speed capabilities in comparison to running directly in memory. If you intend to make any changes to run (e.g. running tests across a variety of inputs), you must tear down all of the manifests before starting again. This prevents leakage between runs. feature_pull_test and model_execution_test may be run sequentially without resetting the infrastructure.

This project requires the Crunchy Postgres Operator installed. It is used as the offline feature store and has no impact on the speed testing, but is required as a starting point for Feast to materialize into Redis.

## Running fewer features

If you want to run fewer features for the model execution test, you have to make changes in numerous places.

* crunch.yaml: Remove features from the table definition (starting on line 12)
* model_execution_test.ipynb: Follow the TODO instructions.
* heart_repo.py:
* * Remove columns from the query on line 30. Columns must match what you put in crunch.yaml
* * Remove columns from the FeatureView: lines 42-54.
* * Remove columns from the @on_demand_feature_view: lines 66-78
* * Remove columns from run_in_memory. Drop feature columns here, and remove the corresponding records from the 2 arrays in the `features` definition. Note that this matches a function in model_execution_test.ipynb.

## Results

### Feature Pull Test

#### Raw Data

| # Iterations | Feast - All Features | Feast - Single Feature | Memory - All Features | Memory - Single Feature |
| ------------ | -------------------- | ---------------------- | --------------------- | ----------------------- |
| 100 | 0.804300746 | 0.25184985 | 0.125650087 | 0.080412246 |
| 1000 | 8.128420083 | 2.490629541 | 1.168418238 | 0.708987286 |
| 10000 | 76.77849899 | 24.44982316 | 11.77525323 | 6.956995329 |

#### Plots

![](/images/Mulitple_Feature_Transactions_Per_Second.png)
![](/images/Single_Feature_Transactions_Per_Second.png) <br />

### Model Execution Test

#### Raw Data

Test was taken over a 1 hour period

Number of calls:

| # Records | Feast - 13 features | In-memory - 13 features | Feast - 6 features | In-memory - 6 features | Feast - 3 features | In-memory - 3 features |
| --------- | ------------------- | ----------------------- | ------------------ | ---------------------- | ------------------ | ----------------------- |
| 100000 | 350664 | 5780773 | 524290 | 6271129 | 669143 | 6264126 |
| 1000 | 346676 | 5956829 | 530417 | 6477448 | 662946 | 6343208 |

This math follows the exact definition for a Poisson Process, therefore variance = mean.

Uncertainty in number of calls:

| # Records | Feast - 13 features | In-memory - 13 features | Feast - 6 features | In-memory - 6 features | Feast - 3 features | In-memory - 3 features |
| --------- | ------------------- | ----------------------- | ------------------ | ---------------------- | ------------------ | ----------------------- |
| 100000 | 592.17 | 2404.32 | 724.08 | 2504.22 | 818.01 | 2502.82 |
| 1000 | 588.79 | 2440.66 | 728.30 | 2545.08 | 814.21 | 2518.57 |

#### Plots

![](/images/Transactions_Per_Second.png) <br />
