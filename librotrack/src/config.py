import yaml


def load_config(path: str = "config.yaml") -> dict:
    with open(path, "r", encoding="utf-8") as file:   #encoding utf-8 türkçe karakterler için
        return yaml.safe_load(file)
    
    
    
    