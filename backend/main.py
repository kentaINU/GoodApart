# main.py
from api.routers import properties
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Chorei Monthly API")

# フロントエンドからアクセスを許可するための設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 開発時はすべて許可
    allow_methods=["*"],
    allow_headers=["*"],
)

# 各ルーターの登録（将来的に他のAPIが増えたらここに include_router を追加していく）
app.include_router(properties.router)

# 起動コマンド memo
# python -m uvicorn main:app --host 0.0.0.0 --reload
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
