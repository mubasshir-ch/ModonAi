import os
import json
from dotenv import load_dotenv

class Config:
    def __init__(self):
        load_dotenv()
        
        # Secrets from .env
        self.TOKEN = os.getenv('BOT_TOKEN')
        self.MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
        
        # Load config.json
        config_path = "config.json"
        self.ENVIRONMENT = "production"
        if os.path.exists('debug_config.json'):
            config_path = 'debug_config.json'
            self.ENVIRONMENT = "development"
            
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Configuration file {config_path} not found.")
            
        with open(config_path, "r") as f:
            data = json.load(f)
            
        self.PREFIX = os.getenv("BOT_PREFIX", data.get("BOT_PREFIX", "!"))
        self.DEVS = data.get("DEVS", [])
        self.TEST_GUILDS = data.get("TEST_GUILDS", [])

# Singleton instance
config = Config()
