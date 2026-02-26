import streamlit as st
import os
from pathlib import Path

# Fix pythonpath so we can import from src
import sys
sys.path.append(str(Path(__file__).resolve().parent))

from src.config import load_config
from src.data.loader import load_restaurants
from src.data.indexes import RestaurantIndex
from src.services.restaurant_query_service import UserPreferences, query_restaurants
from src.llm.client import call_gemini_for_recommendations
from src.utils.logger import configure_logging

# Page configuration
st.set_page_config(
    page_title="AI Restaurant Recommender",
    page_icon="🍴",
    layout="wide",
)

# Custom CSS for a premium look
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #ff4b4b;
        color: white;
    }
    .restaurant-card {
        padding: 1.5rem;
        border-radius: 10px;
        background-color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)

@st.cache_resource
def get_index():
    """Build the restaurant index and cache it."""
    restaurants = load_restaurants()
    return RestaurantIndex(restaurants)

def main():
    st.title("🍴 AI Restaurant Recommender")
    st.markdown("Discover the best places to eat in Bangalore, powered by AI.")

    # Load configuration
    cfg = load_config()
    configure_logging(cfg.log_level)

    # Initialize data
    with st.spinner("Loading restaurant database..."):
        index = get_index()

    # Sidebar: Search Filters
    st.sidebar.header("Search Preferences")
    
    city = st.sidebar.selectbox(
        "Area (Bangalore)",
        options=["", "Banashankari", "Basavanagudi", "Koramangala", "Indiranagar", "Jayanagar", "HSR", "Whitefield", "MG Road", "Brigade Road", "Marathahalli", "Electronic City", "JP Nagar", "BTM Layout", "Malleshwaram"],
        format_func=lambda x: "Any area" if x == "" else x
    )

    cuisines_list = sorted(list(index.by_cuisine.keys()))
    cuisine = st.sidebar.selectbox(
        "Cuisine",
        options=[""] + cuisines_list,
        format_func=lambda x: "Any cuisine" if x == "" else x
    )

    min_rating = st.sidebar.slider("Minimum Rating", 0.0, 5.0, 4.0, 0.1)

    price_options = {
        "": "Any price",
        "1": "Up to 400",
        "2": "400 – 800",
        "3": "800 – 1500",
        "4": "1500+"
    }
    max_price = st.sidebar.selectbox(
        "Max Price (for two)",
        options=list(price_options.keys()),
        format_func=lambda x: price_options[x]
    )

    max_results = st.sidebar.number_input("Max Results", 1, 10, 5)

    if st.sidebar.button("Find Restaurants"):
        prefs = UserPreferences(
            city=city if city else None,
            cuisines=[cuisine] if cuisine else None,
            min_rating=min_rating,
            max_price_range=int(max_price) if max_price else None,
            max_results=max_results
        )

        with st.spinner("Searching and generating AI summaries..."):
            # 1. Query candidates
            results = query_restaurants(index, prefs)

            if not results:
                st.warning("No restaurants matched your filters. Try broadening your search!")
                return

            # 2. Call Gemini
            explanation = "Showing best matches based on your filters."
            summaries = {}
            
            if cfg.gemini_api_key and cfg.enable_gemini:
                try:
                    explanation, summaries = call_gemini_for_recommendations(prefs, results)
                except Exception as e:
                    st.error(f"AI generation failed: {e}")

            # 3. Display results
            st.subheader("Results")
            st.info(explanation)

            for res in results:
                with st.container():
                    st.markdown(f"""
                        <div class="restaurant-card">
                            <h3>{res.name}</h3>
                            <p><b>📍 {res.locality if res.locality else res.city}</b> • {', '.join(res.cuisines)}</p>
                            <p>⭐ {res.aggregate_rating} ({res.votes} votes) • 💰 Cost for two: {res.average_cost_for_two}</p>
                            <p><i>{summaries.get(res.id, "No AI summary available.")}</i></p>
                        </div>
                    """, unsafe_allow_html=True)

    else:
        # Initial landing view
        st.info("Adjust the filters in the sidebar and click 'Find Restaurants' to get started.")
        
        # Show some top-rated restaurants by default
        st.subheader("Top Rated Today")
        top_recos = index.all[:3]
        cols = st.columns(3)
        for i, res in enumerate(top_recos):
            with cols[i]:
                st.markdown(f"**{res.name}**")
                st.write(f"⭐ {res.aggregate_rating}")
                st.write(f"{', '.join(res.cuisines[:2])}")

if __name__ == "__main__":
    main()
