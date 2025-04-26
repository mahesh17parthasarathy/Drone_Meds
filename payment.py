import streamlit as st
import pandas as pd
import random
from datetime import datetime
import geocoder
import qrcode
from io import BytesIO

# Load product data
products = pd.read_csv("medicine_database.csv")

st.set_page_config(page_title="DroneMeds - Pharmacy E-commerce", layout="wide")

# --- Header ---
st.markdown("""
    <style>
        .title {
            font-size: 48px;
            font-weight: bold;
            color: #2c3e50;
            text-align: center;
            margin-bottom: 20px;
        }
        .subtitle {
            font-size: 20px;
            color: #7f8c8d;
            text-align: center;
            margin-bottom: 40px;
        }
        .footer {
            text-align: center;
            color: gray;
            font-size: 14px;
            margin-top: 50px;
        }
    </style>
    <div class="title">💊 DroneMeds</div>
    <div class="subtitle">
        Swift. Safe. Seamless. <br> India's Trusted Drone-Powered Pharmacy Delivery Platform.
    </div>
""", unsafe_allow_html=True)

# --- Sidebar ---
st.sidebar.title("🛒 Place Your Order")
st.sidebar.header("🏥 Select Medicines")
selected = st.sidebar.multiselect("Choose your required products:", options=products["Name"].tolist())

st.sidebar.markdown("---")
st.sidebar.header("📞 Customer Support")
st.sidebar.markdown("""
**Email:** support@dronemeds.in  
**Phone:** +91 98765 43210  
**Service Hours:** 9:00 AM - 6:00 PM (Mon–Sat)
""")

st.sidebar.header("🏢 Company Address")
st.sidebar.markdown("""
DroneMeds Pvt Ltd  
5th Floor, MedTech Tower  
Chennai, Tamil Nadu - 600 001  
India
""")

# --- Product Selection Section ---
selected_products = products[products["Name"].isin(selected)]

if not selected_products.empty:
    st.subheader("📦 Selected Medicines")
    st.table(selected_products.style.format({"Price (INR)": "₹{:.2f}"}))

    total = selected_products["Price (INR)"].sum()
    st.markdown(f"<h4 style='color:#2c3e50;'>Total Payable Amount: ₹{total:.2f}</h4>", unsafe_allow_html=True)

    with st.form("delivery_form"):
        st.subheader("🚚 Delivery & Customer Details")
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Full Name")
            address = st.text_area("Delivery Address")
        with col2:
            g = geocoder.ip('me')
            default_location = f"{g.latlng[0]},{g.latlng[1]}" if g.latlng else ""
            location = st.text_input("GPS Coordinates (Lat, Long)", value=default_location)
            delivery_time = st.selectbox("Preferred Delivery Slot", ["Morning", "Afternoon", "Evening"])

        submitted = st.form_submit_button("✅ Confirm Order")

        if submitted:
            if location.strip() and "," in location:
                try:
                    lat, lon = map(float, location.split(","))
                    order_id = f"MD-{random.randint(1000,9999)}"
                    now = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

                    order_data = {
                        "Order ID": order_id,
                        "Name": name,
                        "Address": address,
                        "Location": location,
                        "Delivery Time": delivery_time,
                        "Products": ", ".join(selected_products["Name"].tolist()),
                        "Total Amount": total,
                        "Timestamp": now
                    }

                    order_df = pd.DataFrame([order_data])
                    csv_file = "orders.csv"
                    try:
                        existing_orders = pd.read_csv(csv_file)
                        updated_orders = pd.concat([existing_orders, order_df], ignore_index=True)
                    except FileNotFoundError:
                        updated_orders = order_df
                    updated_orders.to_csv(csv_file, index=False)

                    st.success(f"🎉 Order **{order_id}** has been successfully placed!")
                    st.info(f"Drone will be dispatched for **{delivery_time.lower()}** delivery.")
                    st.map(pd.DataFrame([{"lat": lat, "lon": lon}]))
                    st.balloons()

                    with st.expander("🧾 View Detailed Order Summary"):
                        st.json(order_data)

                    # --- Payment Section ---
                    st.markdown("## 💳 Complete Your Payment")
                    st.markdown("""
                    To ensure fast and verified delivery, please scan the UPI QR code below to make your payment.
                    """)

                    upi_id = "mastermahesh17@okhdfcbank"  # Update with your real UPI ID
                    upi_url = f"upi://pay?pa={upi_id}&pn=DroneMeds&am={total}&cu=INR"

                    qr = qrcode.make(upi_url)
                    buffer = BytesIO()
                    qr.save(buffer)
                    st.image(buffer, caption="📱 Scan this QR Code to Pay via any UPI App", use_column_width=False)

                    st.markdown(f"**Total Amount:** ₹{total:.2f}<br>**UPI ID:** `{upi_id}`", unsafe_allow_html=True)
                    st.warning("Please ensure the payment is made within 30 minutes to avoid auto-cancellation.")

                except ValueError:
                    st.error("Invalid GPS format. Please enter coordinates like: `12.9716, 77.5946`")
            else:
                st.warning("Please enter valid GPS coordinates.")
else:
    st.info("🔎 Select at least one product from the sidebar to proceed with your order.")

# --- Footer ---
st.markdown("""
    <div class="footer">
        &copy; 2025 <strong>DroneMeds</strong>. All rights reserved. | Powered by <a href="https://streamlit.io" target="_blank">Streamlit</a>
    </div>
""", unsafe_allow_html=True)
