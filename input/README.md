Edit finetuning_base_config.py according to preferences and pointing to own file paths

**data_root**\
NOTE: data_root is defined more than once in the config\
Change to data path\
Folder structure should be as follows;
- data_root
    - training
        - images
        - masks
    - validation
        - images
        - masks

**default_hooks**\
- checkpoint -> interval: the number of iterations after which the model creates a checkpoint, i.e. a saved model
    - Advised to set this to (a multiple of) the validation set, so that you can identify which muscle IoU corresponded to that checkpoint
    - Previously one tenth of the total
- logger -> interval: determines how often details are logged (training rate etc., as well as the ETA)
    - Recommended to leave this set to 50, like in the original configuration

**load_from**\
Important: defines which checkpoint is loaded as base model\
- .pth file
