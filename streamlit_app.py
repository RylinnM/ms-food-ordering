import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
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
      .dish-photo{width:100%;height:auto;border-radius:6px;margin-bottom:8px}
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
    st.session_state.orders = pd.DataFrame(
        columns=["date", "amount", "items", "cat", "rating", "dish"]
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
        "肉沫焖豆角": (13.14, "🫛", "肉沫 & 豆角"),
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
    "Main dish / 主食": {
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
    },
}

# ---------------------------------------
# ------------  SIDEBAR CART ------------
# ---------------------------------------
with st.sidebar:
    st.header("🛒  Cart")
    if st.session_state.cart:
        for dish, (qty, price) in st.session_state.cart.items():
            st.write(f"**{dish}** × {qty} = ${qty*price:.2f}")
            if st.button(f"✖ Remove {dish}", key=f"rm_{dish}"):
                del st.session_state.cart[dish]
                st.rerun()
        st.markdown("---")
        if st.button("🚀 Place Order", type="primary"):
            new_rows = []
            for dish, (qty, price) in st.session_state.cart.items():
                new_rows.extend([{
                    "date": datetime.now(),
                    "amount": price,
                    "items": 1,
                    "cat": "Mixed",
                    "rating": 5,
                    "dish": dish
                }] * qty)
            st.session_state.orders = pd.concat(
                [st.session_state.orders, pd.DataFrame(new_rows)],
                ignore_index=True
            )
            st.session_state.cart.clear()
            st.success("Order placed! 🎉")
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
            file_name = dish.lower().replace(" ", "_") + ".jpeg"
            img_path = f"dish_photos/{file_name}"
            with cols[i % 3]:
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.markdown(
                    f'<img src="{img_path}" class="dish-photo" alt="{dish}" />',
                    unsafe_allow_html=True
                )
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
    now = datetime.now()
    df_3 = st.session_state.orders[
        st.session_state.orders["date"] >= now - timedelta(days=3)
    ]
    df_14 = st.session_state.orders[
        st.session_state.orders["date"] >= now - timedelta(days=14)
    ]

    def most_liked(df):
        return df.groupby("dish")["rating"].mean().idxmax() if not df.empty else "N/A"

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Past 3 Days")
        st.metric("Total Orders", f"{len(df_3):,}")
        st.metric("Most-Liked Dish", most_liked(df_3))
        avg3 = df_3["rating"].mean() if not df_3.empty else 0
        st.metric("Average Rating", f"{avg3:.1f} / 5")
    with col2:
        st.subheader("Past 14 Days")
        st.metric("Total Orders", f"{len(df_14):,}")
        st.metric("Most-Liked Dish", most_liked(df_14))
        avg14 = df_14["rating"].mean() if not df_14.empty else 0
        st.metric("Average Rating", f"{avg14:.1f} / 5")

    st.markdown("----")
    if not df_14.empty:
        daily = df_14.groupby(df_14["date"].dt.date).size().reset_index(name="orders")
        st.plotly_chart(
            px.bar(daily, x="date", y="orders", title="Daily Order Count (14d)"),
            use_container_width=True,
        )

st.markdown("---")
st.write("© 2025 Copyright Mr. Ma  |  With Little Song")
