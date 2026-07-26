批次 2：后端 Schema、Router、Service 拆分

把本目录中的文件复制到 backend/ 下：
- main.py（覆盖）
- schemas.py（覆盖）
- dependencies.py（新增）
- routers/（新增）
- services/（新增）

保留原有：
- agent_service.py
- database.py
- models.py
- tests/
- pyproject.toml

验证命令：
python -m ruff format .
python -m ruff check .
python -m pytest
