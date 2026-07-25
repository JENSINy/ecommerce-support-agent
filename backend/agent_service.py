import json
import os
import time
import uuid
from dataclasses import dataclass

from agents import (
    Agent,
    OpenAIChatCompletionsModel,
    RunContextWrapper,
    Runner,
    function_tool,
    set_tracing_disabled,
)
from dotenv import load_dotenv
from openai import AsyncOpenAI
from sqlalchemy import select
from datetime import datetime

from database import SessionLocal
from models import Faq, Logistics, Order, ToolLog, ReturnRequest, RefundRequest



load_dotenv()

api_key = os.getenv("DEEPSEEK_API_KEY")

if not api_key:
    raise ValueError("没有找到 DEEPSEEK_API_KEY，请检查 .env 文件")


deepseek_client = AsyncOpenAI(
    api_key=api_key,
    base_url="https://api.deepseek.com",
)

deepseek_model = OpenAIChatCompletionsModel(
    model="deepseek-v4-flash",
    openai_client=deepseek_client,
)

# 不上传 OpenAI tracing 数据，当前只使用本地 SQLite 工具日志。
set_tracing_disabled(True)


@dataclass
class CustomerServiceContext:
    session_id: str


def save_tool_log(
    session_id: str,
    tool_name: str,
    reason: str,
    input_params: dict,
    output_result: str,
    status: str,
    duration_ms: float,
    error_message: str | None = None,
) -> None:
    db = SessionLocal()

    try:
        tool_log = ToolLog(
            session_id=session_id,
            tool_name=tool_name,
            reason=reason,
            input_params=json.dumps(
                input_params,
                ensure_ascii=False,
            ),
            output_result=output_result,
            status=status,
            duration_ms=duration_ms,
            error_message=error_message,
        )

        db.add(tool_log)
        db.commit()
    except Exception as error:
        db.rollback()
        print(f"保存工具日志失败：{error}")
    finally:
        db.close()


@function_tool
def get_order(
    context: RunContextWrapper[CustomerServiceContext],
    order_id: str,
    reason: str,
) -> str:
    """
    根据订单号查询订单基础信息，例如商品、金额和订单状态。

    Args:
        order_id: 用户提供的订单号。
        reason: 调用这个工具的简短原因。
    """
    started_at = time.perf_counter()
    normalized_order_id = order_id.strip().upper()

    status = "success"
    error_message = None
    result = ""

    db = SessionLocal()

    try:
        statement = select(Order).where(
            Order.order_id == normalized_order_id
        )
        order = db.scalars(statement).first()

        if order is None:
            status = "not_found"
            result = json.dumps(
                {
                    "success": False,
                    "message": "没有找到该订单",
                    "order_id": normalized_order_id,
                },
                ensure_ascii=False,
            )
        else:
            order_data = {
                column.name: getattr(order, column.name)
                for column in Order.__table__.columns
            }

            result = json.dumps(
                {
                    "success": True,
                    "order": order_data,
                },
                ensure_ascii=False,
                default=str,
            )
    except Exception as error:
        status = "failed"
        error_message = str(error)

        result = json.dumps(
            {
                "success": False,
                "message": "查询订单时发生错误",
                "error": error_message,
            },
            ensure_ascii=False,
        )
    finally:
        db.close()

        duration_ms = round(
            (time.perf_counter() - started_at) * 1000,
            2,
        )

        save_tool_log(
            session_id=context.context.session_id,
            tool_name="get_order",
            reason=reason,
            input_params={
                "order_id": normalized_order_id,
            },
            output_result=result,
            status=status,
            duration_ms=duration_ms,
            error_message=error_message,
        )

    return result


@function_tool
def get_logistics(
    context: RunContextWrapper[CustomerServiceContext],
    order_id: str,
    reason: str,
) -> str:
    """
    根据订单号查询物流信息，例如快递公司、运单号、物流状态和最新位置。

    Args:
        order_id: 用户提供的订单号。
        reason: 调用这个工具的简短原因。
    """
    started_at = time.perf_counter()
    normalized_order_id = order_id.strip().upper()

    status = "success"
    error_message = None
    result = ""

    db = SessionLocal()

    try:
        statement = select(Logistics).where(
            Logistics.order_id == normalized_order_id
        )
        logistics = db.scalars(statement).first()

        if logistics is None:
            status = "not_found"
            result = json.dumps(
                {
                    "success": False,
                    "message": "没有找到该订单的物流信息",
                    "order_id": normalized_order_id,
                },
                ensure_ascii=False,
            )
        else:
            logistics_data = {
                column.name: getattr(logistics, column.name)
                for column in Logistics.__table__.columns
            }

            result = json.dumps(
                {
                    "success": True,
                    "logistics": logistics_data,
                },
                ensure_ascii=False,
                default=str,
            )
    except Exception as error:
        status = "failed"
        error_message = str(error)

        result = json.dumps(
            {
                "success": False,
                "message": "查询物流时发生错误",
                "error": error_message,
            },
            ensure_ascii=False,
        )
    finally:
        db.close()

        duration_ms = round(
            (time.perf_counter() - started_at) * 1000,
            2,
        )

        save_tool_log(
            session_id=context.context.session_id,
            tool_name="get_logistics",
            reason=reason,
            input_params={
                "order_id": normalized_order_id,
            },
            output_result=result,
            status=status,
            duration_ms=duration_ms,
            error_message=error_message,
        )

    return result


@function_tool
def search_faq(
    context: RunContextWrapper[CustomerServiceContext],
    question: str,
    reason: str,
) -> str:
    """
    查询商品常见问题知识库。

    用于回答商品功能、商品参数、兼容性、保修、
    退换货规则等不需要订单号的问题。

    Args:
        question: 用户的商品或售后常见问题。
        reason: 调用这个工具的简短原因。
    """
    started_at = time.perf_counter()
    normalized_question = question.strip()

    status = "success"
    error_message = None
    result = ""

    db = SessionLocal()

    try:
        faqs = db.scalars(select(Faq)).all()

        matched_faqs = []

        for faq in faqs:
            keywords = [
                keyword.strip().lower()
                for keyword in faq.keywords.split(",")
                if keyword.strip()
            ]

            question_lower = normalized_question.lower()

            score = sum(
                1
                for keyword in keywords
                if keyword in question_lower
            )

            if score > 0:
                matched_faqs.append(
                    {
                        "score": score,
                        "id": faq.id,
                        "question": faq.question,
                        "answer": faq.answer,
                        "category": faq.category,
                    }
                )

        matched_faqs.sort(
            key=lambda item: item["score"],
            reverse=True,
        )

        if not matched_faqs:
            status = "not_found"

            result = json.dumps(
                {
                    "success": False,
                    "message": "知识库中没有找到匹配的常见问题",
                    "question": normalized_question,
                },
                ensure_ascii=False,
            )
        else:
            top_faqs = matched_faqs[:3]

            result = json.dumps(
                {
                    "success": True,
                    "question": normalized_question,
                    "matches": top_faqs,
                },
                ensure_ascii=False,
            )
    except Exception as error:
        status = "failed"
        error_message = str(error)

        result = json.dumps(
            {
                "success": False,
                "message": "查询常见问题时发生错误",
                "error": error_message,
            },
            ensure_ascii=False,
        )
    finally:
        db.close()

        duration_ms = round(
            (time.perf_counter() - started_at) * 1000,
            2,
        )

        save_tool_log(
            session_id=context.context.session_id,
            tool_name="search_faq",
            reason=reason,
            input_params={
                "question": normalized_question,
            },
            output_result=result,
            status=status,
            duration_ms=duration_ms,
            error_message=error_message,
        )

    return result


@function_tool
def create_return_request(
    context: RunContextWrapper[CustomerServiceContext],
    order_id: str,
    reason: str,
    tool_reason: str,
) -> str:
    """
    为指定订单创建退货申请。

    只有在用户明确表示要申请退货，并且已提供订单号和退货原因时使用。
    创建后状态为 pending_review，表示等待人工审核。

    Args:
        order_id: 用户需要退货的订单号。
        reason: 用户说明的退货原因。
        tool_reason: 调用该工具的简短原因。
    """
    started_at = time.perf_counter()
    normalized_order_id = order_id.strip().upper()
    normalized_reason = reason.strip()

    status = "success"
    error_message = None
    result = ""

    db = SessionLocal()

    try:
        order_statement = select(Order).where(
            Order.order_id == normalized_order_id
        )
        order = db.scalars(order_statement).first()

        if order is None:
            status = "not_found"

            result = json.dumps(
                {
                    "success": False,
                    "message": "没有找到该订单，无法创建退货申请",
                    "order_id": normalized_order_id,
                },
                ensure_ascii=False,
            )
        elif not normalized_reason:
            status = "failed"

            result = json.dumps(
                {
                    "success": False,
                    "message": "缺少退货原因，无法创建退货申请",
                },
                ensure_ascii=False,
            )
        else:
            return_no = (
                f"RET{datetime.now().strftime('%Y%m%d%H%M%S')}"
                f"{uuid.uuid4().hex[:4].upper()}"
            )

            return_request = ReturnRequest(
                return_no=return_no,
                order_id=normalized_order_id,
                reason=normalized_reason,
                status="pending_review",
            )

            db.add(return_request)
            db.commit()
            db.refresh(return_request)

            result = json.dumps(
                {
                    "success": True,
                    "message": "退货申请已提交，等待人工审核",
                    "return_request": {
                        "return_no": return_request.return_no,
                        "order_id": return_request.order_id,
                        "reason": return_request.reason,
                        "status": return_request.status,
                    },
                },
                ensure_ascii=False,
            )
    except Exception as error:
        db.rollback()

        status = "failed"
        error_message = str(error)

        result = json.dumps(
            {
                "success": False,
                "message": "创建退货申请时发生错误",
                "error": error_message,
            },
            ensure_ascii=False,
        )
    finally:
        db.close()

        duration_ms = round(
            (time.perf_counter() - started_at) * 1000,
            2,
        )

        save_tool_log(
            session_id=context.context.session_id,
            tool_name="create_return_request",
            reason=tool_reason,
            input_params={
                "order_id": normalized_order_id,
                "reason": normalized_reason,
            },
            output_result=result,
            status=status,
            duration_ms=duration_ms,
            error_message=error_message,
        )

    return result


@function_tool
def request_refund(
    context: RunContextWrapper[CustomerServiceContext],
    order_id: str,
    amount: float,
    reason: str,
    tool_reason: str,
) -> str:
    """
    为订单创建待人工审批的退款申请。

    这个工具不会直接退款，只会创建 pending_approval 状态的申请。
    只有人工在审批中心批准后，后端才会执行实际退款。

    Args:
        order_id: 用户申请退款的订单号。
        amount: 用户申请退款的金额。
        reason: 用户说明的退款原因。
        tool_reason: 调用该工具的简短原因。
    """
    started_at = time.perf_counter()
    normalized_order_id = order_id.strip().upper()
    normalized_reason = reason.strip()

    status = "success"
    error_message = None
    result = ""

    db = SessionLocal()

    try:
        order_statement = select(Order).where(
            Order.order_id == normalized_order_id
        )
        order = db.scalars(order_statement).first()

        if order is None:
            status = "not_found"

            result = json.dumps(
                {
                    "success": False,
                    "message": "没有找到该订单，无法创建退款申请",
                    "order_id": normalized_order_id,
                },
                ensure_ascii=False,
            )
        elif amount <= 0:
            status = "failed"

            result = json.dumps(
                {
                    "success": False,
                    "message": "退款金额必须大于 0",
                },
                ensure_ascii=False,
            )
        elif amount > order.amount:
            status = "failed"

            result = json.dumps(
                {
                    "success": False,
                    "message": "退款金额不能超过订单实付金额",
                    "order_amount": order.amount,
                    "requested_amount": amount,
                },
                ensure_ascii=False,
            )
        elif not normalized_reason:
            status = "failed"

            result = json.dumps(
                {
                    "success": False,
                    "message": "缺少退款原因，无法创建退款申请",
                },
                ensure_ascii=False,
            )
        else:
            refund_no = (
                f"REF{datetime.now().strftime('%Y%m%d%H%M%S')}"
                f"{uuid.uuid4().hex[:4].upper()}"
            )

            refund_request = RefundRequest(
                refund_no=refund_no,
                order_id=normalized_order_id,
                amount=amount,
                reason=normalized_reason,
                status="pending_approval",
            )

            db.add(refund_request)
            db.commit()
            db.refresh(refund_request)

            result = json.dumps(
                {
                    "success": True,
                    "message": (
                        "退款申请已创建，正在等待人工审批。"
                        "在人工批准前不会执行退款。"
                    ),
                    "refund_request": {
                        "id": refund_request.id,
                        "refund_no": refund_request.refund_no,
                        "order_id": refund_request.order_id,
                        "amount": refund_request.amount,
                        "reason": refund_request.reason,
                        "status": refund_request.status,
                    },
                },
                ensure_ascii=False,
            )
    except Exception as error:
        db.rollback()

        status = "failed"
        error_message = str(error)

        result = json.dumps(
            {
                "success": False,
                "message": "创建退款申请时发生错误",
                "error": error_message,
            },
            ensure_ascii=False,
        )
    finally:
        db.close()

        duration_ms = round(
            (time.perf_counter() - started_at) * 1000,
            2,
        )

        save_tool_log(
            session_id=context.context.session_id,
            tool_name="request_refund",
            reason=tool_reason,
            input_params={
                "order_id": normalized_order_id,
                "amount": amount,
                "reason": normalized_reason,
            },
            output_result=result,
            status=status,
            duration_ms=duration_ms,
            error_message=error_message,
        )

    return result


customer_service_agent = Agent[CustomerServiceContext](
    name="电商售后客服",
    instructions="""
你是一名电商售后客服，使用简洁、友好的中文回答。

你可以处理三类业务：

1. 订单查询
- 用户询问订单状态、商品、金额、下单信息时，调用 get_order。
- 用户提供订单号后，必须调用 get_order 查询，不能编造数据。

2. 物流查询
- 用户询问物流、快递、配送进度、运单号、包裹位置时，调用 get_logistics。
- 用户提供订单号后，必须调用 get_logistics 查询，不能编造物流数据。

3. 商品常见问题
- 用户询问商品功能、参数、是否支持某种连接、系统兼容性、
  保修、退货规则等问题时，调用 search_faq。
- FAQ 查询通常不需要订单号。
- 不要假装知道商品参数，必须先调用 search_faq。

通用规则：
1. 调用任意工具时，reason 参数必须简短说明调用原因。
2. 订单或物流查询缺少订单号时，先礼貌地要求用户提供订单号。
3. 工具返回 success 为 false 时，如实告诉用户没有找到对应信息。
4. 不要把工具返回的 JSON 原样输出，应整理为自然语言。
5. 不要承诺无法确认的配送时间。
6. 不要执行退款、取消订单等敏感操作。

4. 退货申请
- 用户明确表示要退货、申请退货或商品不想要了时，处理退货申请。
- 创建退货申请前，必须收集订单号和具体退货原因。
- 如果缺少订单号，询问订单号。
- 如果缺少退货原因，询问退货原因。
- 同时具备订单号和退货原因后，调用 create_return_request。
- create_return_request 创建的是待人工审核申请，不代表退款成功。
- 不要自行承诺退货一定通过，也不要调用任何退款操作。

5. 退款申请
- 用户明确提出退款、申请退款、退款到账等诉求时，处理退款申请。
- 退款是敏感操作，绝对不能直接退款。
- 只能调用 request_refund 创建待人工审批的退款申请。
- 创建退款申请前，必须收集订单号、退款金额和退款原因。
- 用户要求全额退款时，先调用 get_order 查询订单金额，再以订单实付金额创建退款申请。
- 如果退款金额超过订单金额，如实说明不能创建。
- 创建成功后，明确告知用户：退款申请已提交，正在等待人工审批。
- 不要承诺一定会通过审批，也不要说退款已经到账。

reason 示例：
- 用户希望查询 ORD001 的订单状态
- 用户希望查询 ORD001 的物流进度
- 用户询问无线机械键盘是否支持蓝牙连接
- 用户询问商品的退货规则
""",
    model=deepseek_model,
    tools=[
        get_order,
        get_logistics,
        search_faq,
        create_return_request,
        request_refund,
    ],
)



def run_chat() -> None:
    conversation = []
    session_id = str(uuid.uuid4())

    print("电商售后 Agent 已启动（模型：DeepSeek）")
    print(f"当前会话编号：{session_id}")
    print("输入 exit 可以结束对话")

    while True:
        user_input = input("\n用户：").strip()

        if user_input.lower() in {"exit", "quit"}:
            print("Agent：再见！")
            break

        if not user_input:
            continue

        conversation.append(
            {
                "role": "user",
                "content": user_input,
            }
        )

        try:
            result = Runner.run_sync(
                customer_service_agent,
                conversation,
                context=CustomerServiceContext(
                    session_id=session_id,
                ),
            )

            print(f"Agent：{result.final_output}")
            conversation = result.to_input_list()
        except Exception as error:
            print(f"Agent 运行失败：{error}")


if __name__ == "__main__":
    run_chat()
