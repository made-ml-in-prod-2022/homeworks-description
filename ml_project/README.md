# ML production ready project example
## How to use
#### Dag of train pipeline is implemented with *Makefile*.
To run whole train pipeline including requirements installation and raw data download use:
```commandline
make all
```
Train config fpath by default is *configs/train_config.yaml*. To provide another config fpath set also config variable:
```commandline
make all CONFIG=config/catboost_config.yaml
```
To run only train pipeline use:
```commandline
make train_model
```
## Project about
- **Project organization**:\
The schema of project organization is represented in *docs/README_project_organization.md*
- **Makefile commands**:\
Every train pipeline part could be run separately with ```make```. See more details in the *Makefile*.
- **Data source**:\
  Kaggle dataset [Heart Disease Cleveland UCI](https://www.kaggle.com/datasets/cherngs/heart-disease-cleveland-uci) is used in the project
