import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from templates.main_page import MAIN_PAGE_HTML

app = FastAPI()


@app.get("/")
async def root():
    return HTMLResponse(MAIN_PAGE_HTML)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
