from dataclasses import dataclass, field
from marshmallow.exceptions import ValidationError


@dataclass()
class TrainingParams:
    model: str
    random_state: int = field(default=255)
    param_dict: dict = field(default_factory=dict)

    def __post_init__(self):
        if self.model not in ['lightgbm', 'catboost']:
            raise ValidationError(
                f'{self.model} is not supported'
            )
