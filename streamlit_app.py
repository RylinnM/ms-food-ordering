import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import plotly.express as px
import time

# ---------------------------------------
# --------  PAGE CONFIG & STYLE  --------
# ---------------------------------------
st.set_page_config(
    page_title="Little rabbit's kitchen 🐰",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.markdown(
    """
    <style>
      .main-header{font-size:3rem;font-weight:700;color:#FF6B35;text-align:center}
      .category{background:linear-gradient(90deg,#FF6B35,#F7931E);
                padding:8px;border-radius:8px;color:#fff;font-weight:600;margin:4px 0}
      .card{background:#fafafa;border:1px solid #eee;
            border-radius:8px;padding:14px;box-shadow:0 1px 3px rgba(0,0,0,0.06)}
      .metric-card{background:#fff;border:1px solid #eee;border-radius:8px;
                   text-align:center;padding:16px;box-shadow:0 1px 3px rgba(0,0,0,0.06)}
      .order-box{background:#e8f5e8;border-left:4px solid #28a745;
                 border-radius:6px;padding:10px}
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------
# ------------  APP STATE  --------------
# ---------------------------------------
if "cart" not in st.session_state:
    st.session_state.cart = {}
if "orders" not in st.session_state:
    # create dummy historical orders for analytics
    rng = pd.date_range("2024-01-01", "2024-12-31", freq="D")
    st.session_state.orders = pd.DataFrame(
        {
            "date": np.random.choice(rng, 800),
            "amount": np.random.normal(25, 9, 800).clip(5, 100),
            "items": np.random.poisson(3, 800),
            "cat": np.random.choice(
                ["Pizza", "Burgers", "Pasta", "Salads", "Desserts"], 800
            ),
            "rating": np.random.choice([3, 4, 5], 800, p=[0.1, 0.3, 0.6]),
        }
    )

# ---------------------------------------
# -------------  MENU DATA  -------------
# ---------------------------------------
menu = {
        "Chef's Favorites / 主厨推荐": {

        "咖喱土豆鸡": (20.20, "🍛", "鸡肉 & 土豆"),
        "土豆炒肉沫": (13.14, "🥔", "土豆 & 肉沫"),
        "糖醋虾仁": (20.20, "🦐", "虾仁 & 鸡蛋"),
        "可乐鸡翅": (19.85, "🍗", "鸡翅 & 可乐"),
        "香辣大虾": (20.20, "🦐", "大虾 & 辣椒"),
        "椒盐蟹柳": (20.20, "🦀", "蟹柳 & 椒盐"),
    },

    "Meats / 肉食": {
        "水煮肉片": (28.95, "🥩", "猪肉片 & 辣椒"),
        "肉沫闷豆角": (13.14, "🫛", "肉沫 & 豆角"),
        "青椒炒鸡腿肉": (8.5, "🍗", "青椒 & 鸡肉"),
        "土豆丝炒肉": (13.14, "🥔", "土豆 & 肉沫"),
        "辣炒花甲": (28.95, "🦪", "花甲"),
        "孜然鸡腿": (19.85, "🍖", "鸡腿肉 & 孜然"),
        "手撕鸡腿肉": (10.19, "🍗", "鸡腿肉"),
        "油焖大虾": (25.89, "🦐", "大虾"),

    },
    "Vegetables / 蔬菜": {
        "蒜香蚝油生菜": (5.20, "🥬", "生菜"),
        "辣拌白菜": (5.21, "🥬", "白菜"),
        "香辣茄子": (10.19, "🍆", "茄子"),
        "番茄鸡蛋火腿": (10.19, "🍅", "番茄 & 鸡蛋 & 火腿"),
        "酸辣土豆丝": (10.19, "🥔", "土豆"),
        "干煸豆角": (10.19, "🫛", "豆角"),
        "火腿炒鸡蛋": (5.21, "🥚", "火腿 & 鸡蛋"),


    },
    "Main dish / 主食":{
        "黑胡椒虾仁炒面": (10.19, "🦐", "虾仁 & 黑胡椒 & 面条"),
        "拉条子": (18.99, "🍝", "面条"),
        "米饭": (0.85, "🍚", "白米饭"),
        "生菜三明治": (10.85, "🥪", "生菜 & 鸡蛋 & 面包 & 午餐肉"),
        "彩椒碗": (8.5, "🌶️", "辣椒 & 肉松 & 鸡胸肉"),
        "洋葱肥牛饭": (20.20, "🧅", "肥牛 & 洋葱"),

    },
    "Instant Food / 速食": {
        "螺蛳粉": (8.5, "🍜", "螺蛳粉 & 豆腐泡 & 木耳"),
        "肥汁米线": (8.5, "🍲", "米线 & 肉酱"),
        "新疆炒米粉": (10.19, "🍝", "米粉 & 牛肉 & 辣椒"),
        "鸡汤面": (8.5, "🍜", "鸡汤 & 面条 & 鸡肉"),
        "火鸡面": (5.21, "🌶️", "辣酱 & 面条"),
        
    },
     "Beverages / 饮品": {
        "杨枝甘露": (10.99, "🥭", "芒果 & 西米露"),
        "可乐们": (0.99, "🥤", "可乐 / 雪碧 / 芬达"),
        "酸奶们": (0.99, "🍶", "草莓 / 黄桃 / 原味酸奶"),
        "椰子水": (0.99, "🥥", "纯椰子水"),
        "果汁们": (0.99, "🧃", "橙汁 / 苹果汁 / 胡萝卜汁"),
    }
}

# ---------------------------------------
# ------------  SIDEBAR CART ------------
# ---------------------------------------
with st.sidebar:
    st.header("🛒  Cart")
    if st.session_state.cart:
        total = 0.0
        for item, data in list(st.session_state.cart.items()):
            qty, price = data
            st.write(f"**{item}**  × {qty}  =  ${qty*price:.2f}")
            total += qty * price
            if st.button(f"✖ Remove {item}", key=f"rm_{item}"):
                del st.session_state.cart[item]
                st.rerun()
        st.markdown("---")
        st.subheader(f"Total  **${total:.2f}**")
        if st.button("🚀  Place Order", type="primary"):
            if total:
                st.success("Order placed! 🎉")
                # append to analytics
                new = pd.DataFrame(
                    {
                        "date": [datetime.now()],
                        "amount": [total],
                        "items": [sum(q for q, _ in st.session_state.cart.values())],
                        "cat": ["Mixed"],
                        "rating": [5],
                    }
                )
                st.session_state.orders = pd.concat(
                    [st.session_state.orders, new], ignore_index=True
                )
                st.session_state.cart.clear()
                time.sleep(1)
                st.rerun()
    else:
        st.info("Cart is empty")

    st.markdown("---")
    st.header("🔍  Filters")
    pr = st.slider("Price range", 0, 50, (0, 50), step=5)
    cats = st.multiselect("Categories", list(menu.keys()), default=list(menu.keys()))

# ---------------------------------------
# -------------  MAIN TABS  -------------
# ---------------------------------------
st.markdown('<div class="main-header">🍽️ Little Rabbit Kitchen 🐰</div>', unsafe_allow_html=True)
tab_menu, tab_dash = st.tabs(["🍴 Menu", "📊 Analytics"])

# ----- MENU TAB -----
with tab_menu:
    for cat, items in menu.items():
        if cat not in cats:
            continue
        st.markdown(f'<div class="category">{cat}</div>', unsafe_allow_html=True)
        cols = st.columns(3)
        for i, (dish, (price, emoji, desc)) in enumerate(items.items()):
            if not pr[0] <= price <= pr[1]:
                continue
            with cols[i % 3]:
                with st.container():
                    st.markdown('<div class="card">', unsafe_allow_html=True)
                    st.subheader(f"{emoji} {dish}")
                    st.caption(desc)
                    st.write(f"**${price:.2f}**")
                    qty = st.number_input(
                        "Qty", 0, 10, 0, key=f"q_{cat}_{dish}", label_visibility="collapsed"
                    )
                    if st.button("Add to cart", key=f"add_{cat}_{dish}"):
                        if qty:
                            st.session_state.cart[dish] = (
                                st.session_state.cart.get(dish, (0, price))[0] + qty,
                                price,
                            )
                            st.success(f"Added {qty} × {dish}")
                            st.rerun()
                        else:
                            st.warning("Select quantity > 0")
                    st.markdown("</div>", unsafe_allow_html=True)

# ----- DASHBOARD TAB -----
with tab_dash:
    st.header("📊 Restaurant Dashboard")
    orders = st.session_state.orders
    today = orders[orders["date"].dt.date == datetime.now().date()]
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(
            "Total Revenue",
            f"${orders['amount'].sum():,.2f}",
            f"${today['amount'].sum():.2f} today",
        )
    with col2:
        st.metric("Total Orders", f"{len(orders):,}", f"{len(today)} today")
    with col3:
        st.metric("Avg Order", f"${orders['amount'].mean():.2f}")
    with col4:
        st.metric("Avg Rating", f"{orders['rating'].mean():.1f} / 5")

    # charts
    c1, c2 = st.columns(2)
    with c1:
        daily = (
            orders.groupby(orders["date"].dt.date)["amount"]
            .sum()
            .reset_index(name="revenue")
        )
        st.plotly_chart(
            px.line(daily.tail(30), x="date", y="revenue", title="Daily Revenue (30 d)")
        )
    with c2:
        pop = orders["cat"].value_counts()
        st.plotly_chart(
            px.pie(values=pop.values, names=pop.index, title="Popular Categories")
        )

    c3, c4 = st.columns(2)
    with c3:
        orders["hour"] = orders["date"].dt.hour
        hr = orders.groupby("hour").size().reset_index(name="orders")
        st.plotly_chart(
            px.bar(hr, x="hour", y="orders", title="Orders by Hour").update_traces(marker_color="#F7931E")
        )
    with c4:
        rate = orders["rating"].value_counts().sort_index()
        st.plotly_chart(
            px.bar(
                x=[f"{r}★" for r in rate.index],
                y=rate.values,
                title="Rating Distribution",
            ).update_traces(marker_color="#28a745")
        )

    st.subheader("🔔 Insights")
    st.info(
        f"""Today: **{len(today)} orders** • Revenue **${today['amount'].sum():.2f}**
        \nPeak hour: **{orders['hour'].mode()[0]}:00**  
        Top category: **{pop.idxmax()}**"""
    )

st.markdown("---")
st.write("© 2025 Copyright Mr. Ma  |  With Little Song")
