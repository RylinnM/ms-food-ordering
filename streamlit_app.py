import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import time, os, json, requests
from PIL import Image

# ---------- PAGE CONFIG & STYLE ----------
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
      /* cards all same height */
      [data-testid="stVerticalBlock"] > div {height:100%}
      .card{background:#fafafa;border:1px solid #eee;border-radius:8px;
            padding:14px;box-shadow:0 1px 3px rgba(0,0,0,0.06);height:100%;
            display:flex;flex-direction:column}
      .dish-photo{width:100%;height:180px;object-fit:cover;border-radius:6px;margin-bottom:8px}
    </style>""",
    unsafe_allow_html=True,
)

# ---------- APP STATE ----------
if "cart" not in st.session_state:
    st.session_state.cart = {}
if "orders" not in st.session_state:
    st.session_state.orders = pd.DataFrame(
        columns=["date", "amount", "items", "cat", "rating", "dish"]
    )
if "pending_ratings" not in st.session_state:
    st.session_state.pending = []

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

# ---------- HELPERS ----------
def send_slack_msg(text: str):
    url = st.secrets.get("slack_webhook")
    if not url:
        return
    try:
        requests.post(url, json={"text": text}, timeout=5)
    except Exception as e:
        st.warning(f"Slack notification failed: {e}")

def add_ratings_UI():
    if not st.session_state.pending:
        return
    with st.sidebar.expander("⭐ Rate your dishes!", expanded=True):
        for dish in st.session_state.pending.copy():
            stars = st.feedback("stars", key=f"rate_{dish}")
            if stars is not None:
                # stars is 0-based → +1 for human rating
                rows = st.session_state.orders[
                    (st.session_state.orders["dish"] == dish) &
                    (st.session_state.orders["rating"].isna())
                ].index
                st.session_state.orders.loc[rows, "rating"] = stars + 1
                st.session_state.pending.remove(dish)
                st.toast(f"Thanks for rating {dish}!")

# ---------- SIDEBAR CART ----------
with st.sidebar:
    st.header("🛒  Cart")
    if st.session_state.cart:
        for dish, (qty, price) in st.session_state.cart.items():
            st.write(f"**{dish}** × {qty} = ${qty*price:.2f}")
            if st.button(f"✖ Remove {dish}", key=f"rm_{dish}"):
                del st.session_state.cart[dish]; st.rerun()

        st.markdown("---")
        if st.button("🚀 Place Order", type="primary"):
            new_rows = []
            for dish, (qty, price) in st.session_state.cart.items():
                new_rows.extend([{
                    "date": datetime.now(),
                    "amount": price,
                    "items": 1,
                    "cat": "Mixed",
                    "rating": None,         # will be filled later
                    "dish": dish
                }] * qty)
            st.session_state.orders = pd.concat(
                [st.session_state.orders, pd.DataFrame(new_rows)],
                ignore_index=True
            )
            # remember dishes needing ratings
            st.session_state.pending.extend({r["dish"] for r in new_rows})
            # build Slack message
            total = sum(qty*price for qty, price in st.session_state.cart.values())
            lines = [f"*New order* – {datetime.now():%Y-%m-%d %H:%M}"]
            for dish,(qty,price) in st.session_state.cart.items():
                lines.append(f"• {qty} × {dish} – ${qty*price:.2f}")
            lines.append(f"*Total:* ${total:.2f}")
            send_slack_msg("\n".join(lines))
            st.session_state.cart.clear()
            st.success("Order placed! 🎉  Please rate your dishes ➡")
            time.sleep(1); st.rerun()
    else:
        st.info("Cart is empty")

    st.markdown("---")
    with st.expander("🔍 Browse", expanded=False):   # ← collapsible filters
        pr = st.slider("Price range", 0, 50, (0, 50), step=5)
        cats = st.multiselect("Categories", list(menu.keys()), default=list(menu.keys()))

# ---------- MAIN TABS ----------
st.markdown('<div class="main-header">🍽️ Little Rabbit Kitchen 🐰</div>', unsafe_allow_html=True)
tab_menu, tab_dash = st.tabs(["🍴 Menu", "📊 Analytics"])

# ----- MENU TAB -----
with tab_menu:
    add_ratings_UI()  # show rating prompt if needed

    for cat, items in menu.items():
        if cat not in cats:
            continue
        st.markdown(f'<div class="category">{cat}</div>', unsafe_allow_html=True)
        cols = st.columns(3)
        for i, (dish, (price, emoji, desc)) in enumerate(items.items()):
            if not pr[0] <= price <= pr[1]:
                continue
            with cols[i % 3]:
                tile = st.container(height=430, border=False, key=f"tile_{cat}_{dish}")  # fixed height[4]
                with tile:
                    img_path = f"dish_photos/{dish.lower().replace(' ','_')}.jpeg"
                    try:
                        st.image(img_path, use_container_width=True, caption=None, output_format="JPEG")
                    except:
                        st.info("📸 Image coming soon!")
                    st.subheader(f"{emoji} {dish}")
                    st.caption(desc)
                    st.write(f"**${price:.2f}**")
                    qty = st.number_input("Qty", 0, 10, 0,
                        key=f"q_{cat}_{dish}", label_visibility="collapsed")
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

# ----- DASHBOARD TAB -----
with tab_dash:
    st.header("📊 Restaurant Dashboard")
    now = datetime.now()
    df_3  = st.session_state.orders[st.session_state.orders["date"] >= now - timedelta(days=3)]
    df_14 = st.session_state.orders[st.session_state.orders["date"] >= now - timedelta(days=14)]

    def most_liked(df):
        return df.groupby("dish")["rating"].mean().idxmax() if not df.empty else "N/A"

    col1, col2 = st.columns(2)
    for df, title, col in [(df_3,"Past 3 Days",col1),(df_14,"Past 14 Days",col2)]:
        with col:
            st.subheader(title)
            st.metric("Total Orders", f"{len(df):,}")
            st.metric("Most-Liked Dish", most_liked(df))
            avg = df["rating"].mean() if not df.empty else 0
            st.metric("Average Rating", f"{avg:.1f} / 5")

    st.markdown("----")
    if not df_14.empty:
        daily = df_14.groupby(df_14["date"].dt.date).size().reset_index(name="orders")
        st.plotly_chart(
            px.bar(daily, x="date", y="orders", title="Daily Order Count (14 days)"),
            use_container_width=True,
        )

st.markdown("---")
st.write("© 2025 Mr. Ma  |  With Little Song")
