ORDERS = {
    "ORD001": {
        "order_id": "ORD001",
        "user_id": "USER001",
        "product_name": "无线机械键盘",
        "quantity": 1,
        "amount": 399.00,
        "status": "shipped",
        "created_at": "2026-07-20",
    },
    "ORD002": {
        "order_id": "ORD002",
        "user_id": "USER002",
        "product_name": "27 英寸显示器",
        "quantity": 1,
        "amount": 1599.00,
        "status": "delivered",
        "created_at": "2026-07-15",
    },
    "ORD003": {
        "order_id": "ORD003",
        "user_id": "USER001",
        "product_name": "人体工学鼠标",
        "quantity": 2,
        "amount": 458.00,
        "status": "pending",
        "created_at": "2026-07-24",
    },
}


LOGISTICS = {
    "ORD001": {
        "order_id": "ORD001",
        "company": "顺丰速运",
        "tracking_number": "SF1234567890",
        "status": "运输中",
        "latest_event": "快件已到达上海转运中心",
        "estimated_delivery": "2026-07-27",
    },
    "ORD002": {
        "order_id": "ORD002",
        "company": "京东物流",
        "tracking_number": "JD9876543210",
        "status": "已签收",
        "latest_event": "本人签收",
        "estimated_delivery": "2026-07-18",
    },
}
