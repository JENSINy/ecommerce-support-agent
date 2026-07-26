import json
import time

from agents import RunContextWrapper, function_tool
from sqlalchemy import select

from agent.context import CustomerServiceContext
from agent.logging import save_tool_log
from database import SessionLocal
from models import Faq


@function_tool
def search_faq(
    context: RunContextWrapper[CustomerServiceContext],
    question: str,
    reason: str,
) -> str:
    started_at = time.perf_counter()

    normalized_question = question.strip()

    status = "success"
    error_message = None
    result = ""

    db = SessionLocal()

    try:
        faqs = db.scalars(select(Faq)).all()

        question_lower = normalized_question.lower()
        matched_faqs = []

        for faq in faqs:
            keywords = [
                keyword.strip().lower()
                for keyword in faq.keywords.split(",")
                if keyword.strip()
            ]

            score = sum(1 for keyword in keywords if keyword in question_lower)

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
            result = json.dumps(
                {
                    "success": True,
                    "question": normalized_question,
                    "matches": matched_faqs[:3],
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

        save_tool_log(
            session_id=context.context.session_id,
            tool_name="search_faq",
            reason=reason,
            input_params={
                "question": normalized_question,
            },
            output_result=result,
            status=status,
            duration_ms=round(
                (time.perf_counter() - started_at) * 1000,
                2,
            ),
            error_message=error_message,
        )

    return result
