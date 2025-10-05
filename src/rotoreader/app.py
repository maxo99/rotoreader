from dotenv import load_dotenv
from fastapi import FastAPI

from rotoreader.config import APP_PORT, ROOT_DIR
from rotoreader.service.feedsreader import (
    collect_and_process_feeddata,
    get_feeddatas,
)

app = FastAPI()

load_dotenv(ROOT_DIR)


@app.get("/")
def health():
    return {"status": "running"}


@app.post("/collect")
def collect():
    return collect_and_process_feeddata()


@app.get("/feed", response_model_exclude_none=True)
def feeds():
    return get_feeddatas()


@app.get("/feed/{team_abbr}", response_model_exclude_none=True)
def team_feeds(team_abbr: str):
    return get_feeddatas(team_abbr)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=APP_PORT)
