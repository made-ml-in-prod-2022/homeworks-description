from typing import Optional

from dataclasses import dataclass
from marshmallow_dataclass import class_schema
import yaml

from .split_params import SplittingParams
from .feature_params import FeatureParams
from .train_params import TrainingParams


@dataclass()
class TrainingPipelineParams:
    splitting_params: SplittingParams
    feature_params: FeatureParams
    train_params: TrainingParams
    input_data_path: str
    output_model_path: str = "models/model.pkl"
    report_path: str = "reports/report.json"
    use_mlflow: bool = True
    mlflow_uri: str = "http://18.156.5.226/"
    mlflow_experiment: str = "inference_demo"


TrainingPipelineParamsSchema = class_schema(TrainingPipelineParams)


def read_training_pipeline_params(path: str) -> TrainingPipelineParams:
    with open(path, "r") as input_stream:
        schema = TrainingPipelineParamsSchema()
        config = yaml.safe_load(input_stream)
        return schema.load(config)
