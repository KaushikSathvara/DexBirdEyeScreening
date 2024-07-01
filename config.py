import os

import dotenv

dotenv.load_dotenv()


class Config:
    BIRD_EYE_TOKEN = os.environ.get("BIRD_EYE_TOKEN")
    BIRD_EYE_URL = "https://public-api.birdeye.so/defi"
