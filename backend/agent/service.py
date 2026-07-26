from agents import Agent

from agent.client import create_deepseek_model
from agent.context import CustomerServiceContext
from agent.prompts import CUSTOMER_SERVICE_INSTRUCTIONS
from agent.tools import (
    create_return_request,
    get_logistics,
    get_order,
    request_refund,
    search_faq,
)

customer_service_agent = Agent[CustomerServiceContext](
    name="电商售后客服",
    instructions=CUSTOMER_SERVICE_INSTRUCTIONS,
    model=create_deepseek_model(),
    tools=[
        get_order,
        get_logistics,
        search_faq,
        create_return_request,
        request_refund,
    ],
)
