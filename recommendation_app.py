# 🛒 Product Recommendation System
import streamlit as st
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import random

# -------------------------
# 1. Sample Product Dataset (20+ Products)
# -------------------------
products = pd.DataFrame({
    "product_id": list(range(1, 21)),
    "product_name": [
        "Laptop", "Phone", "Headphones", "Camera", "Smartwatch",
        "Tablet", "Bluetooth Speaker", "Gaming Console", "TV", "Microwave",
        "Refrigerator", "Washing Machine", "Air Conditioner", "Oven", "Mixer Grinder",
        "Shoes", "Backpack", "Sunglasses", "Wrist Watch", "Jacket"
    ],
    "category": [
        "Electronics", "Electronics", "Electronics", "Electronics", "Wearable",
        "Electronics", "Electronics", "Gaming", "Electronics", "Appliance",
        "Appliance", "Appliance", "Appliance", "Appliance", "Appliance",
        "Fashion", "Fashion", "Fashion", "Fashion", "Fashion"
    ],
    "thumbnail": [
        "https://via.placeholder.com/100?text=Laptop",
        "https://via.placeholder.com/100?text=Phone",
        "https://via.placeholder.com/100?text=Headphones",
        "https://via.placeholder.com/100?text=Camera",
        "https://via.placeholder.com/100?text=Smartwatch",
        "https://via.placeholder.com/100?text=Tablet",
        "https://via.placeholder.com/100?text=Speaker",
        "https://via.placeholder.com/100?text=Console",
        "https://via.placeholder.com/100?text=TV",
        "https://via.placeholder.com/100?text=Microwave",
        "https://via.placeholder.com/100?text=Fridge",
        "https://via.placeholder.com/100?text=Washer",
        "https://via.placeholder.com/100?text=AC",
        "https://via.placeholder.com/100?text=Oven",
        "https://via.placeholder.com/100?text=Mixer",
        "https://via.placeholder.com/100?text=Shoes",
        "https://via.placeholder.com/100?text=Backpack",
        "https://via.placeholder.com/100?text=Glasses",
        "https://via.placeholder.com/100?text=Watch",
        "https://via.placeholder.com/100?text=Jacket"
    ]
})

# -------------------------
# 2. Dummy Ratings Dataset (user_id, product_id, rating)
# -------------------------
ratings = []
for user in range(1, 11):  # 10 users
    for prod in random.sample(range(1, 21), 8):  # each user rates 8 products
        ratings.append([user, prod, random.randint(2, 5)])

ratings = pd.DataFrame(ratings, columns=["user_id", "product_id", "rating"])

# -------------------------
# 3. Content-Based Filtering (TF-IDF)
# -------------------------
products["text"] = products["product_name"] + " " + products["category"]

vectorizer = TfidfVectorizer(stop_words="english")
tfidf_matrix = vectorizer.fit_transform(products["text"])
cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

def recommend_content(product_name, top_n=5):
    idx = products[products["product_name"].str.lower() == product_name.lower()].index[0]
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)[1:top_n+1]
    rec_idx = [i[0] for i in sim_scores]
    return products.iloc[rec_idx]

# -------------------------
# 4. Collaborative Filtering (User-Item Matrix)
# -------------------------
user_item_matrix = ratings.pivot_table(
    index="user_id", columns="product_id", values="rating"
).fillna(0)

user_sim = cosine_similarity(user_item_matrix)

def recommend_collaborative(user_id, top_n=5):
    if user_id not in user_item_matrix.index:
        return pd.DataFrame()
    user_idx = user_item_matrix.index.get_loc(user_id)
    sim_scores = list(enumerate(user_sim[user_idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)[1:]
    similar_users = [i[0] for i in sim_scores[:3]]  # top-3 similar users

    recs = []
    for u in similar_users:
        top_products = user_item_matrix.iloc[u].sort_values(ascending=False).head(top_n).index
        recs.extend(top_products)

    recs = list(set(recs))  # unique products
    return products[products["product_id"].isin(recs)].head(top_n)

# -------------------------
# 5. Streamlit UI
# -------------------------
st.set_page_config(page_title="🛒 Product Recommendation System", layout="wide")
st.title("🛒 Product Recommendation System")

st.sidebar.header("Options")
mode = st.sidebar.radio("Choose Recommendation Type:", ["Content-Based", "Collaborative"])

if mode == "Content-Based":
    product_choice = st.selectbox("Select a product:", products["product_name"])
    if st.button("Recommend"):
        recs = recommend_content(product_choice)
        st.subheader(f"Products similar to {product_choice}:")
        for _, row in recs.iterrows():
            st.image(row["thumbnail"], width=100)
            st.write(f"**{row['product_name']}** ({row['category']})")
        # Export to CSV
        recs.to_csv("recommendations.csv", index=False)
        st.download_button(
            label="💾 Download Recommendations CSV",
            data=recs.to_csv(index=False).encode("utf-8"),
            file_name="recommendations.csv",
            mime="text/csv"
        )

elif mode == "Collaborative":
    user_choice = st.selectbox("Select a User ID:", ratings["user_id"].unique())
    if st.button("Recommend"):
        recs = recommend_collaborative(user_choice)
        if recs.empty:
            st.warning("No collaborative recommendations found for this user.")
        else:
            st.subheader(f"Recommended products for User {user_choice}:")
            for _, row in recs.iterrows():
                st.image(row["thumbnail"], width=100)
                st.write(f"**{row['product_name']}** ({row['category']})")
            # Export to CSV
            recs.to_csv("recommendations.csv", index=False)
            st.download_button(
                label="💾 Download Recommendations CSV",
                data=recs.to_csv(index=False).encode("utf-8"),
                file_name="recommendations.csv",
                mime="text/csv"
            )
