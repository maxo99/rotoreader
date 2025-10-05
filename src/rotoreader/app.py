from dotenv import load_dotenv
from fastapi import FastAPI

from rotoreader.config import APP_PORT, ROOT_DIR
from rotoreader.service.feedsreader import collect_feeddata

app = FastAPI()

load_dotenv(ROOT_DIR)


@app.get("/")
def health():
    return {"status": "running"}


@app.post("/collect")
def collect():
    return collect_feeddata()


# @app.get("/feed", response_model_exclude_none=True)
# def feeds():
#     return get_feeddata()


# @app.get("/feed/{team_id}", response_model_exclude_none=True)
# def team_feeds(team_id: int):
#     return get_teamfeeds(team_id)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=APP_PORT)
