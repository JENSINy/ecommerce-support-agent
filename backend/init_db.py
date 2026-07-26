from sqlalchemy import select

from database import SessionLocal, engine
from models import Base, Faq, Logistics, Order


def add_order_if_not_exists(db, order_data: dict) -> None:
    statement = select(Order).where(Order.order_id == order_data["order_id"])
    existing_order = db.scalars(statement).first()

    if existing_order is None:
        db.add(Order(**order_data))
        print(f"订单已插入：{order_data['order_id']}")
    else:
        print(f"订单已存在：{order_data['order_id']}")


def add_logistics_if_not_exists(db, logistics_data: dict) -> None:
    statement = select(Logistics).where(
        Logistics.order_id == logistics_data["order_id"]
    )
    existing_logistics = db.scalars(statement).first()

    if existing_logistics is None:
        db.add(Logistics(**logistics_data))
        print(f"物流已插入：{logistics_data['order_id']}")
    else:
        print(f"物流已存在：{logistics_data['order_id']}")


def add_faq_if_not_exists(db, faq_data: dict) -> None:
    statement = select(Faq).where(Faq.question == faq_data["question"])
    existing_faq = db.scalars(statement).first()

    if existing_faq is None:
        db.add(Faq(**faq_data))
        print(f"FAQ 已插入：{faq_data['question']}")
    else:
        print(f"FAQ 已存在：{faq_data['question']}")


def init_database() -> None:
    # 创建所有尚不存在的表，不删除当前已有数据。
    Base.metadata.create_all(bind=engine)

    orders = [
        {
            "order_id": "ORD001",
            "user_id": "USER001",
            "product_name": "无线机械键盘",
            "quantity": 1,
            "amount": 399,
            "status": "shipped",
            "created_at": "2026-07-20",
        },
        {
            "order_id": "ORD002",
            "user_id": "USER001",
            "product_name": "蓝牙静音鼠标",
            "quantity": 1,
            "amount": 129,
            "status": "shipped",
            "created_at": "2026-07-21",
        },
        {
            "order_id": "ORD003",
            "user_id": "USER002",
            "product_name": "Type-C 扩展坞",
            "quantity": 1,
            "amount": 259,
            "status": "delivered",
            "created_at": "2026-07-18",
        },
        {
            "order_id": "ORD004",
            "user_id": "USER003",
            "product_name": "机械键盘键帽套装",
            "quantity": 2,
            "amount": 158,
            "status": "paid",
            "created_at": "2026-07-22",
        },
        {
            "order_id": "ORD005",
            "user_id": "USER004",
            "product_name": "无线机械键盘",
            "quantity": 1,
            "amount": 399,
            "status": "refunded",
            "created_at": "2026-07-15",
        },
        {
            "order_id": "ORD006",
            "user_id": "USER005",
            "product_name": "显示器支架",
            "quantity": 1,
            "amount": 219,
            "status": "shipped",
            "created_at": "2026-07-22",
        },
    ]

    logistics_records = [
        {
            "order_id": "ORD001",
            "company": "顺丰速运",
            "tracking_number": "SF1234567890",
            "status": "运输中",
            "latest_location": ("包裹已到达上海市浦东新区配送中心，预计今天送达。"),
            "updated_at": "2026-07-21 10:30:00",
        },
        {
            "order_id": "ORD002",
            "company": "中通快递",
            "tracking_number": "ZT20260721001",
            "status": "已揽收",
            "latest_location": ("商家已将包裹交给中通快递，正在等待转运。"),
            "updated_at": "2026-07-21 16:20:00",
        },
        {
            "order_id": "ORD003",
            "company": "京东物流",
            "tracking_number": "JD20260718008",
            "status": "已签收",
            "latest_location": (
                "包裹已由用户本人签收，如有问题请在签收后及时申请售后。"
            ),
            "updated_at": "2026-07-19 14:05:00",
        },
        {
            "order_id": "ORD006",
            "company": "圆通速递",
            "tracking_number": "YT20260722003",
            "status": "运输中",
            "latest_location": ("包裹已从杭州市转运中心发出，正在发往目的地。"),
            "updated_at": "2026-07-22 18:40:00",
        },
    ]

    faqs = [
        {
            "question": "无线机械键盘支持蓝牙连接吗？",
            "answer": (
                "支持。这款无线机械键盘支持蓝牙 5.0、"
                "2.4G 无线连接和 USB 有线连接，"
                "最多可连接 3 台蓝牙设备。"
            ),
            "keywords": "蓝牙,无线,连接,键盘,蓝牙连接",
            "category": "商品参数",
        },
        {
            "question": "无线机械键盘的保修期是多久？",
            "answer": (
                "该无线机械键盘提供 1 年保修服务。"
                "如商品存在非人为损坏的质量问题，"
                "请提供订单号后申请售后。"
            ),
            "keywords": "保修,质保,保修期,售后,质量问题,键盘",
            "category": "售后政策",
        },
        {
            "question": "商品收到后可以退货吗？",
            "answer": (
                "支持 7 天无理由退货。商品需保持完好，"
                "配件、包装和赠品齐全，不影响二次销售。"
            ),
            "keywords": "退货,退款,七天,7天,无理由,退换货",
            "category": "退换货政策",
        },
        {
            "question": "键盘支持 Windows 和 Mac 吗？",
            "answer": (
                "支持 Windows 和 macOS 系统。"
                "键盘提供 Windows/Mac 双系统按键布局，"
                "可通过组合键切换系统模式。"
            ),
            "keywords": "Windows,Mac,macOS,苹果,系统,兼容,键盘",
            "category": "商品参数",
        },
        {
            "question": "蓝牙静音鼠标支持充电吗？",
            "answer": (
                "支持。蓝牙静音鼠标使用 Type-C 接口充电，充满电后正常使用约 30 天。"
            ),
            "keywords": "鼠标,充电,Type-C,续航,蓝牙,静音",
            "category": "商品参数",
        },
    ]

    db = SessionLocal()

    try:
        for order_data in orders:
            add_order_if_not_exists(db, order_data)

        for logistics_data in logistics_records:
            add_logistics_if_not_exists(db, logistics_data)

        for faq_data in faqs:
            add_faq_if_not_exists(db, faq_data)

        db.commit()
        print("数据库初始化完成")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    init_database()
