Project Organization
------------

    ├── LICENSE
    ├── Makefile           <- Makefile with dag of train pipeline.
    ├── README.md          <- How to use.
    ├── data
    │   ├── interim        <- Intermediate data that has been transformed.
    │   ├── processed      <- The final, canonical data sets for modeling.
    │   └── raw            <- The original, immutable data dump.
    │
    ├── README.md          <- How to use.
    ├── models             <- Trained and serialized models.
    ├── notebooks         
    │   └──  1.0-EDA.ipynb    <- Exploratory data analisis
    │
    ├── reports            <- Training reports with metrics obtained and corresponding model parameters.
    ├── requirements.txt   <- The requirements file for reproducing the analysis environment.
    ├── setup.py           <- Makes project pip installable (pip install -e .) so src can be imported.
    ├── src                
    │   ├── data           
    │   │   └── make_dataset.py  <- Split data into train-valid-test datasets
    │   │
    │   ├── features       
    │   │   └── build_features.py <- Biuld target encoding for cat features
    │   │
    │   └──  models         <- Scripts to train models and then use trained models to make
    │       │                 predictions
    │       ├── predict_model.py
    │       └── train_model.py
    │
    ├── tests               <- unit tests
    └── tox.ini
--------

<p><small>Project based on the <a target="_blank" href="https://drivendata.github.io/cookiecutter-data-science/">cookiecutter data science project template</a>. #cookiecutterdatascience</small></p>
