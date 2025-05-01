import os,yaml


# Only for internal use
_config = None

# It will give dir as path/to/core directly 
# dir_path = os.path.dirname(os.path.realpath(__file__))
# print(dir_path)

def load_config():
    global _config

    # Parse YAML only once
    if _config is None:  
        print("Configuration file parsing...")

        # for this we need to be present in right dir
        project_path = os.getcwd()
        # print(project_path)
        
        with open(f"{project_path}/config.yaml") as f:
            _config = yaml.safe_load(f) or {}

        print("Configuration file parsed...")
    return _config
