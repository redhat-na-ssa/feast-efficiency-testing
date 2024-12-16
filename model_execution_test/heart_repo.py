from datetime import timedelta

from numpy import array
import pandas as pd

from feast import (
    Entity,
    FeatureService,
    FeatureView,
    Field,
    Project,
)
from feast.feature_logging import LoggingConfig
from feast.infra.offline_stores.file_source import FileLoggingDestination
from feast.infra.offline_stores.contrib.postgres_offline_store.postgres_source import (
    PostgreSQLSource,
)
from feast.on_demand_feature_view import on_demand_feature_view
from feast.types import Float32, Float64, Int64

# Define a project for the feature repo
project = Project(name="feast_with_model", description="A project for feast statistics")

# Define an entity for the driver. You can think of an entity as a primary key used to
# fetch features.
heart = Entity(name="heart", join_keys=["patient_id"])

heart_values_source = PostgreSQLSource(
    name="heart_values",
    query="SELECT patient_id, age, sex, cp, trtbps, chol, fbs, restecg, thalachh, exng, oldpeak, slp, caa, thall, event_timestamp, created FROM heart_values",
    timestamp_field="event_timestamp",
    created_timestamp_column="created",
)

heart_values_fv = FeatureView(
    # The unique name of this feature view. Two feature views in a single
    # project cannot have the same name
    name="heart_data",
    entities=[heart],
    ttl=timedelta(days=30),
    schema=[
        Field(name="age", dtype=Int64),
        Field(name="sex", dtype=Int64),
        Field(name="cp", dtype=Int64),
        Field(name="trtbps", dtype=Int64),
        Field(name="chol", dtype=Int64),
        Field(name="fbs", dtype=Int64),
        Field(name="restecg", dtype=Int64),
        Field(name="thalachh", dtype=Int64),
        Field(name="exng", dtype=Int64),
        Field(name="oldpeak", dtype=Float64),
        Field(name="slp", dtype=Int64),
        Field(name="caa", dtype=Int64),
        Field(name="thall", dtype=Int64),
    ],
    online=True,
    source=heart_values_source,
    # Tags are user defined key/value pairs that are attached to each
    # feature view
    tags={"body_part": "heart"},
)

@on_demand_feature_view(
    sources=[heart_values_fv],
    schema=[
        Field(name="age", dtype=Float64),
        Field(name="sex", dtype=Float64),
        Field(name="cp", dtype=Float64),
        Field(name="trtbps", dtype=Float64),
        Field(name="chol", dtype=Float64),
        Field(name="fbs", dtype=Float64),
        Field(name="restecg", dtype=Float64),
        Field(name="thalachh", dtype=Float64),
        Field(name="exng", dtype=Float64),
        Field(name="oldpeak", dtype=Float64),
        Field(name="slp", dtype=Float64),
        Field(name="caa", dtype=Float64),
        Field(name="thall", dtype=Float64),
    ],
)
def run_in_memory(this_row: pd.DataFrame) -> pd.DataFrame:
    raw_features = this_row[['age', 'sex', 'cp', 'trtbps', 'chol', 'fbs', 'restecg', 'thalachh',
       'exng', 'oldpeak', 'slp', 'caa', 'thall']]
    features = (raw_features - array([5.46502463e+01, 6.60098522e-01, 1.00985222e+00, 1.30812808e+02,
        2.48448276e+02, 1.28078818e-01, 5.27093596e-01, 1.49655172e+02,
        3.30049261e-01, 1.03300493e+00, 1.40394089e+00, 6.35467980e-01,
        2.33004926e+00])) / array([ 8.99758246,  0.47367548,  1.04098356, 17.02951461, 54.87667351,
         0.33417755,  0.52803654, 22.61651409,  0.47023052,  1.09919108,
         0.61538905,  0.91787029,  0.59920596])
    return features


# This groups features into a model version
heart_v1 = FeatureService(
    name="heart_v1",
    features=[
        run_in_memory,  # Selects all features from the feature view
    ],
    logging_config=LoggingConfig(
        destination=FileLoggingDestination(path="data")
    ),
)
