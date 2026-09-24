# Edit finetuning_base_config.py according to preferences and pointing to own file paths

**data_root**\
NOTE: data_root is defined more than once in the config, change all paths\
Change to data path. In the base config, the testing data_root is different. This path is only used when running test.py\
Folder structure should be as follows;
- data_root (testing)
    - images
    - masks
- data_root (validation and training)
    - training
        - images
        - masks
    - validation
        - images
        - masks

**default_hooks**
- checkpoint -> interval: the number of iterations after which the model creates a checkpoint, i.e. a saved model
    - Advised to set this to (a multiple of) the validation interval, so that you can identify which muscle IoU corresponded to that checkpoint
    - Previously one tenth of the total
- logger -> interval: determines how often details are logged (training rate etc., as well as the ETA)
    - Recommended to leave this set to 50, like in the original configuration

**load_from**\
Important: defines which checkpoint is loaded as base model\
- .pth file

**train_cfg**
- max_iters -> number of iterations the model runs
- batch_size -> number of training data examples the model processes before it updates its internal parameters or weights
- val_interval -> refers to how often the model checks your validation set to see how well it is performing. Should align with the checkpoint interval

**val_dataloader**
- batch_size -> change according to needs

**save_dir**\
Directory to save visualisation results

**work_dir**\
Directory to save results, logs, new checkpoints
- Can also be specified when running train.py, but advised to update in the config  
