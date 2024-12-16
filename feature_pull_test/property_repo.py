# This is an example feature definition file

from datetime import timedelta

import pandas as pd

from feast import (
    Entity,
    FeatureService,
    FeatureView,
    Field,
    Project,
    RequestSource,
)
from feast.feature_logging import LoggingConfig
from feast.infra.offline_stores.file_source import FileLoggingDestination
from feast.infra.offline_stores.contrib.postgres_offline_store.postgres_source import (
    PostgreSQLSource,
)
from feast.on_demand_feature_view import on_demand_feature_view
from feast.types import Float32, Float64, Int64

# Define a project for the feature repo
project = Project(name="feast_speed_testing", description="A project for feast statistics")

# Define an entity for the driver. You can think of an entity as a primary key used to
# fetch features.
address = Entity(name="address", join_keys=["address_id"])

address_values_source = PostgreSQLSource(
    name="address_values",
    query="SELECT address_id, num_beds, norm_basement_sq_ft, event_timestamp, created FROM address_values",
    timestamp_field="event_timestamp",
    created_timestamp_column="created",
)

address_values_fv = FeatureView(
    # The unique name of this feature view. Two feature views in a single
    # project cannot have the same name
    name="address_data",
    entities=[address],
    ttl=timedelta(days=30),
    # home_sq_ft will only ever be passed and then transformed.
    # num_bedrooms is stored and will be transformed.
    # normalized_basement_sq_ft will be pulled as is.
    schema=[
        Field(name="num_beds", dtype=Float64),
        Field(name="norm_basement_sq_ft", dtype=Float64, description="Prepared feature value"),
    ],
    online=True,
    source=address_values_source,
    # Tags are user defined key/value pairs that are attached to each
    # feature view
    tags={"team": "address"},
)

# Define a request data source which encodes features / information only
# available at request time (e.g. part of the user initiated HTTP request)
input_request = RequestSource(
    name="vals_to_add",
    schema=[
        Field(name="home_sq_ft", dtype=Float64),
    ],
)


# Define an on demand feature view which can generate new features based on
# existing feature views and RequestSource features
@on_demand_feature_view(
    sources=[address_values_fv, input_request],
    schema=[
        Field(name="norm_home_sq_ft", dtype=Float64),
        Field(name="norm_num_beds", dtype=Float64),
    ],
)
def transformed_conv_rate(inputs: pd.DataFrame) -> pd.DataFrame:
    df = pd.DataFrame()
    df["norm_home_sq_ft"] = inputs["home_sq_ft"] / 3500
    df["norm_num_beds"] = inputs["num_beds"] / 10
    return df


# This groups features into a model version
address_v1 = FeatureService(
    name="address_v1",
    features=[
        address_values_fv[["norm_basement_sq_ft"]],  # Sub-selects a feature from a feature view
        transformed_conv_rate,  # Selects all features from the feature view
    ],
    logging_config=LoggingConfig(
        destination=FileLoggingDestination(path="data")
    ),
)
