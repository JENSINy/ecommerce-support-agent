from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from dependencies import get_db
from routers.chat import router as chat_router
from routers.conversations import router as conversations_router
from routers.orders import router as orders_router
from routers.refunds import router as refunds_router
from routers.returns import router as returns_router
from routers.tool_logs import router as tool_logs_router

app = FastAPI(
    title="电商售后 Agent API",
    description="支持订单查询和多轮对话的电商售后接口",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(orders_router)
app.include_router(chat_router)
app.include_router(tool_logs_router)
app.include_router(conversations_router)
app.include_router(refunds_router)
app.include_router(returns_router)


@app.get("/")
def read_root():
    return {
        "message": "电商售后 Agent API 已启动",
    }


__all__ = ["app", "get_db"]
