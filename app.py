
import os
import re
import html
from urllib.parse import urljoin

import pandas as pd
import streamlit as st

# ============================================================
# PAGE CONFIGURATION
# ============================================================
st.set_page_config(
    page_title="Livat Hammersmith Search",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

SITE_URL = "https://preprod.livli.com/hammersmith/en"
LIVAT_LOGO_URL = (
    "https://images.ctfassets.net/vy8x7x5kxmef/"
    "27fmsyCnbniUE3l4KAgNIG/"
    "bf2879e358e7757d7f50fd8eef8f0705/livat.svg"
)
DATA_FILE = "livli_search_data_clean.csv"

# ============================================================
# IMAGE URLS
# These are illustrative stock images, not verified official
# photographs of the individual businesses.
# ============================================================
MAIN_IMAGES = {
    "Shops": "https://images.unsplash.com/photo-1441986300917-64674bd600d8?auto=format&fit=crop&w=900&q=85",
    "Food & Drink": "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?auto=format&fit=crop&w=900&q=85",
    "Services": "https://images.unsplash.com/photo-1497366754035-f200968a6e72?auto=format&fit=crop&w=900&q=85",
    "Offers & Events": "https://images.unsplash.com/photo-1492684223066-81342ee5ff30?auto=format&fit=crop&w=900&q=85",
}

SHOP_CATEGORY_IMAGES = {
    "Fashion": "https://images.unsplash.com/photo-1483985988355-763728e1935b?auto=format&fit=crop&w=700&q=85",
    "Womenswear": "https://images.unsplash.com/photo-1485230895905-ec40ba36b9bc?auto=format&fit=crop&w=700&q=85",
    "Menswear": "https://images.unsplash.com/photo-1516257984-b1b4d707412e?auto=format&fit=crop&w=700&q=85",
    "Childrenswear": "https://images.unsplash.com/photo-1519238263530-99bdd11df2ea?auto=format&fit=crop&w=700&q=85",
    "Footwear": "https://images.unsplash.com/photo-1543163521-1bf539c55dd2?auto=format&fit=crop&w=700&q=85",
    "Accessories & Watches": "https://images.unsplash.com/photo-1523170335258-f5ed11844a49?auto=format&fit=crop&w=700&q=85",
    "Electronic & Media": "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?auto=format&fit=crop&w=700&q=85",
    "Grocery": "https://images.unsplash.com/photo-1542838132-92c53300491e?auto=format&fit=crop&w=700&q=85",
    "Bank": "https://images.unsplash.com/photo-1444653614773-995cb1ef9efa?auto=format&fit=crop&w=700&q=85",
    "Home & Decor": "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?auto=format&fit=crop&w=700&q=85",
    "Health & Wellness": "https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?auto=format&fit=crop&w=700&q=85",
    "Pharmacy & Optometry": "https://images.unsplash.com/photo-1511499767150-a48a237f0083?auto=format&fit=crop&w=700&q=85",
    "Perfumery": "https://images.unsplash.com/photo-1541643600914-78b084683601?auto=format&fit=crop&w=700&q=85",
    "Sport": "https://images.unsplash.com/photo-1461896836934-ffe607ba8211?auto=format&fit=crop&w=700&q=85",
    "Other": "https://images.unsplash.com/photo-1497366811353-6870744d04b2?auto=format&fit=crop&w=700&q=85",
}

FOOD_IMAGES = {
    "Coffee": "https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?auto=format&fit=crop&w=700&q=85",
    "Tea": "https://images.unsplash.com/photo-1544787219-7f47ccb76574?auto=format&fit=crop&w=700&q=85",
    "Juice": "https://images.unsplash.com/photo-1600271886742-f049cd451bba?auto=format&fit=crop&w=700&q=85",
    "Food": "https://images.unsplash.com/photo-1504674900247-0877df9cc836?auto=format&fit=crop&w=700&q=85",
}

SERVICE_IMAGES = {
    "Banking": "https://images.unsplash.com/photo-1444653614773-995cb1ef9efa?auto=format&fit=crop&w=700&q=85",
    "Mobile & Technology": "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?auto=format&fit=crop&w=700&q=85",
    "Health & Optical": "https://images.unsplash.com/photo-1511499767150-a48a237f0083?auto=format&fit=crop&w=700&q=85",
    "Community & Other Services": "https://images.unsplash.com/photo-1521737711867-e3b97375f902?auto=format&fit=crop&w=700&q=85",
}

EVENT_IMAGES = {
    "Offers": "https://images.unsplash.com/photo-1607083206968-13611e3d76db?auto=format&fit=crop&w=700&q=85",
    "Events": "https://images.unsplash.com/photo-1506157786151-b8491531f063?auto=format&fit=crop&w=700&q=85",
    "What's On": "https://images.unsplash.com/photo-1514525253161-7a46d19cd819?auto=format&fit=crop&w=700&q=85",
}

SHOP_IMAGES = {
    "Atelier100": "https://images.unsplash.com/photo-1490481651871-ab68de25d43d?auto=format&fit=crop&w=700&q=85",
    "Bluebird - 1": "https://images.unsplash.com/photo-1445205170230-053b83016050?auto=format&fit=crop&w=700&q=85",
    "Clarks": "https://images.unsplash.com/photo-1543163521-1bf539c55dd2?auto=format&fit=crop&w=700&q=85",
    "EE": "https://images.unsplash.com/photo-1556656793-08538906a9f8?auto=format&fit=crop&w=700&q=85",
    "Foot Locker": "https://images.unsplash.com/photo-1552346154-21d32810aba3?auto=format&fit=crop&w=700&q=85",
    "Frame": "https://images.unsplash.com/photo-1576091160550-2173dba999ef?auto=format&fit=crop&w=700&q=85",
    "H&M": "https://images.unsplash.com/photo-1485230895905-ec40ba36b9bc?auto=format&fit=crop&w=700&q=85",
    "IKEA": "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?auto=format&fit=crop&w=700&q=85",
    "JD Sports": "https://images.unsplash.com/photo-1461896836934-ffe607ba8211?auto=format&fit=crop&w=700&q=85",
    "Library of Things": "https://images.unsplash.com/photo-1494438639946-1ebd1d20bf85?auto=format&fit=crop&w=700&q=85",
    "Lidl": "https://images.unsplash.com/photo-1542838132-92c53300491e?auto=format&fit=crop&w=700&q=85",
    "Lidl-1": "https://images.unsplash.com/photo-1604719312566-8912e9c8a213?auto=format&fit=crop&w=700&q=85",
    "Metro Bank": "https://images.unsplash.com/photo-1444653614773-995cb1ef9efa?auto=format&fit=crop&w=700&q=85",
    "NatWest Bank": "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?auto=format&fit=crop&w=700&q=85",
    "O2": "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?auto=format&fit=crop&w=700&q=85",
    "Primark": "https://images.unsplash.com/photo-1483985988355-763728e1935b?auto=format&fit=crop&w=700&q=85",
    "Sainsbury’s": "https://images.unsplash.com/photo-1604719312566-8912e9c8a213?auto=format&fit=crop&w=700&q=85",
    "Santander": "https://images.unsplash.com/photo-1460925895917-afdab827c52f?auto=format&fit=crop&w=700&q=85",
    "Sook": "https://images.unsplash.com/photo-1473186505569-9c61870c11f9?auto=format&fit=crop&w=700&q=85",
    "Specsavers": "https://images.unsplash.com/photo-1511499767150-a48a237f0083?auto=format&fit=crop&w=700&q=85",
    "The Fragrance Shop": "https://images.unsplash.com/photo-1541643600914-78b084683601?auto=format&fit=crop&w=700&q=85",
    "Three": "https://images.unsplash.com/photo-1598327105666-5b89351aff97?auto=format&fit=crop&w=700&q=85",
    "Chamber 9": "https://images.unsplash.com/photo-1414235077428-338989a2e8c0?auto=format&fit=crop&w=700&q=85",
    "Costa Coffee": "https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?auto=format&fit=crop&w=700&q=85",
    "IKEA Restaurant": "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?auto=format&fit=crop&w=700&q=85",
    "Wasabi": "https://images.unsplash.com/photo-1579871494447-9811cf80d66c?auto=format&fit=crop&w=700&q=85",
}

# ============================================================
# CATEGORY DEFINITIONS
# ============================================================
CATEGORIES = {
    "Shops": [
        "Fashion", "Womenswear", "Menswear", "Childrenswear",
        "Footwear", "Accessories & Watches", "Electronic & Media",
        "Grocery", "Bank", "Home & Decor", "Health & Wellness",
        "Pharmacy & Optometry", "Perfumery", "Sport", "Other",
    ],
    "Food & Drink": ["Coffee", "Tea", "Juice", "Food"],
    "Services": [
        "Banking", "Mobile & Technology", "Health & Optical",
        "Community & Other Services",
    ],
    "Offers & Events": ["Offers", "Events", "What's On"],
}

KNOWN_SHOP_CATEGORIES = {
    "Atelier100": ["Accessories & Watches", "Womenswear", "Menswear", "Home & Decor", "Other"],
    "Bluebird - 1": ["Fashion", "Accessories & Watches"],
    "Clarks": ["Footwear"],
    "EE": ["Electronic & Media"],
    "Foot Locker": ["Footwear", "Menswear"],
    "Frame": ["Health & Wellness"],
    "H&M": ["Fashion", "Womenswear", "Menswear", "Childrenswear"],
    "IKEA": ["Home & Decor"],
    "JD Sports": ["Sport"],
    "Library of Things": ["Other"],
    "Lidl": ["Grocery"],
    "Lidl-1": ["Fashion", "Menswear", "Womenswear", "Grocery"],
    "Metro Bank": ["Bank"],
    "NatWest Bank": ["Bank"],
    "O2": ["Electronic & Media"],
    "Primark": ["Womenswear", "Menswear", "Childrenswear", "Home & Decor"],
    "Sainsbury’s": ["Grocery"],
    "Santander": ["Bank"],
    "Sook": ["Other"],
    "Specsavers": ["Pharmacy & Optometry", "Accessories & Watches"],
    "The Fragrance Shop": ["Perfumery"],
    "Three": ["Electronic & Media"],
}

# Explicit service mappings. The Shops directory can contain these
# same businesses, so service results are selected from all directory
# records rather than only pages categorized as Services.
SERVICE_SHOP_NAMES = {
    "Banking": [
        "Metro Bank",
        "NatWest Bank",
        "Santander",
    ],
    "Mobile & Technology": [
        "EE",
        "O2",
        "Three",
    ],
    "Health & Optical": [
        "Frame",
        "Specsavers",
    ],
    "Community & Other Services": [
        "Library of Things",
        "Sook",
    ],
}

NON_DIRECTORY_TERMS = [
    "cookie notice",
    "privacy policy",
    "terms and conditions",
    "contact us",
    "accessibility",
    "christmas at livat",
    "site map",
    "sitemap",
    "legal notice",
]


# ============================================================
# CSS
# ============================================================
st.markdown(
    """
    <style>
    html, body, .stApp,
    [data-testid="stAppViewContainer"],
    [data-testid="stMain"] {
        background: #ffffff !important;
    }

    [data-testid="stHeader"] {
        background: rgba(255, 255, 255, 0.98) !important;
    }

    [data-testid="stAppViewContainer"] > .main,
    [data-testid="stMainBlockContainer"],
    .block-container {
        position: relative;
        z-index: 1;
    }

    .block-container {
        width: 100% !important;
        max-width: 1600px !important;
        padding: 1.2rem clamp(1rem, 3vw, 3rem) 2rem !important;
    }

    .livat-header {
        display: flex;
        align-items: center;
        justify-content: flex-start;
        width: 100%;
        min-height: 76px;
        margin: 0 0 16px;
        padding: 8px 0;
        overflow: visible;
    }

    .livat-header a {
        display: inline-flex;
        align-items: center;
        max-width: 100%;
        overflow: visible;
    }

    .livat-logo-img {
        display: block;
        width: 180px;
        max-width: min(48vw, 220px);
        height: auto;
        max-height: 64px;
        object-fit: contain;
        object-position: left center;
    }

    /* Decorative yellow curves remain outside the content area. */
    .stApp::before,
    .stApp::after {
        content: "";
        position: fixed;
        z-index: 0;
        pointer-events: none;
        border: 34px solid #ffdf00;
        border-radius: 50%;
    }

    .stApp::before {
        width: 360px;
        height: 440px;
        left: -330px;
        bottom: -370px;
        transform: rotate(-20deg);
    }

    .stApp::after {
        width: 430px;
        height: 170px;
        right: -390px;
        bottom: -125px;
        transform: rotate(-29deg);
    }

    .section-title {
        font-size: clamp(20px, 2vw, 25px);
        font-weight: 750;
        margin: 22px 0 15px;
        color: #202020;
        letter-spacing: -0.25px;
    }

    .category-card {
        border: 1px solid #eaded2;
        border-radius: 18px;
        overflow: hidden;
        background: #f7f3ef;
        margin-bottom: 8px;
        box-shadow: 0 4px 14px rgba(55, 40, 25, 0.06);
        transition: transform 0.18s ease, box-shadow 0.18s ease;
    }

    .category-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 7px 18px rgba(55, 40, 25, 0.10);
    }

    .category-card img {
        width: 100%;
        height: clamp(120px, 13vw, 175px);
        object-fit: cover;
        display: block;
    }

    .category-card-title {
        padding: 12px 13px;
        font-weight: 750;
        font-size: 14px;
        min-height: 46px;
        color: #202020;
        background: #f7f3ef;
    }

    .result-card {
        border: 1px solid #eaded2;
        border-radius: 18px;
        overflow: hidden;
        background: #ffffff;
        margin-bottom: 8px;
        box-shadow: 0 4px 14px rgba(55, 40, 25, 0.06);
        height: 100%;
    }

    .result-card img {
        width: 100%;
        height: clamp(140px, 13vw, 180px);
        object-fit: cover;
        display: block;
    }

    .result-body {
        padding: 14px;
        background: #ffffff;
    }

    .result-name {
        font-size: 16px;
        font-weight: 750;
        margin-bottom: 6px;
        color: #202020;
        overflow-wrap: anywhere;
    }

    .result-category {
        font-size: 12px;
        color: #006b78;
        margin-bottom: 8px;
        font-weight: 650;
    }

    .result-description {
        font-size: 13px;
        color: #555555;
        line-height: 1.5;
        min-height: 38px;
    }

    [data-testid="stTextInput"] input {
        border-radius: 28px !important;
        min-height: 48px;
        background: #f7f3ef !important;
        border: 1px solid #e8d8c9 !important;
        padding-left: 18px;
        color: #202020 !important;
        box-shadow: none !important;
    }

    [data-testid="stTextInput"] input:focus {
        border-color: #d7b900 !important;
        box-shadow: 0 0 0 2px rgba(255, 223, 0, 0.22) !important;
    }

    .stButton > button,
    .stLinkButton > a {
        border-radius: 24px !important;
        border: 1px solid #e2d1c2 !important;
        min-height: 42px;
        background: #ffffff !important;
        color: #202020 !important;
        font-weight: 600 !important;
        transition: background 0.15s ease, border-color 0.15s ease;
    }

    .stButton > button:hover,
    .stLinkButton > a:hover {
        border-color: #ffdf00 !important;
        background: #ffdf00 !important;
        color: #202020 !important;
    }

    .feedback-bubble {
        position: fixed;
        right: clamp(18px, 4vw, 70px);
        bottom: 24px;
        z-index: 2;
        background: #bfdbc9;
        color: #006b78;
        border-radius: 48% 52% 48% 45%;
        padding: 19px 20px;
        text-align: center;
        width: 170px;
        font-weight: 750;
        font-size: 14px;
        line-height: 1.4;
        box-shadow: 0 4px 14px rgba(0, 80, 80, 0.08);
    }

    .feedback-bubble a {
        font-weight: 500;
        color: #006b78;
        font-size: 12px;
        text-decoration: underline;
    }

    .footer-note {
        font-size: 12px;
        color: #777777;
        margin-top: 28px;
        padding: 12px 0 8px;
    }

    @media (max-width: 700px) {
        .block-container {
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }

        .livat-header {
            min-height: 64px;
        }

        .livat-logo-img {
            width: 155px;
            max-height: 56px;
        }

        .category-card img {
            height: 105px;
        }

        .category-card-title {
            padding: 9px;
            font-size: 12px;
        }

        .feedback-bubble {
            position: relative;
            right: auto;
            bottom: auto;
            margin: 24px 0 0 auto;
            width: 150px;
            padding: 14px;
        }

        .stApp::before {
            left: -345px;
            bottom: -400px;
        }

        .stApp::after {
            right: -405px;
            bottom: -145px;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# LOAD CSV
# ============================================================
@st.cache_data
def load_data():
    if not os.path.exists(DATA_FILE):
        return pd.DataFrame(
            columns=["title", "url", "content", "content_status"]
        )

    data = pd.read_csv(DATA_FILE).fillna("")

    for column in ["title", "url", "content", "content_status"]:
        if column not in data.columns:
            data[column] = ""

        data[column] = data[column].astype(str)

    data = data[data["title"].str.strip().ne("")]
    data = data.drop_duplicates(subset=["url"], keep="first")

    return data.reset_index(drop=True)


def norm(value):
    return re.sub(
        r"[^a-z0-9]+",
        " ",
        str(value).lower(),
    ).strip()


def title_of(row):
    title = str(row.get("title", "")).strip()

    if title:
        return title

    return (
        str(row.get("url", ""))
        .rstrip("/")
        .split("/")[-1]
        .replace("-", " ")
        .title()
    )


def is_directory_page(row):
    title = norm(title_of(row))
    url = str(row.get("url", "")).lower()

    valid_path = any(
        path in url
        for path in [
            "/shops/",
            "/eat-and-drink/",
            "/restaurants/",
            "/food-and-drink/",
            "/services/",
            "/offers",
            "/events",
            "/whats-on",
            "/what-s-on",
        ]
    )

    if any(norm(term) in title for term in NON_DIRECTORY_TERMS):
        return False

    if any(
        term in url
        for term in [
            "cookie",
            "privacy",
            "contact",
            "terms",
            "accessibility",
            "sitemap",
        ]
    ):
        return False

    return valid_path


def main_category(row):
    url = str(row.get("url", "")).lower()
    title = norm(title_of(row))

    if any(
        path in url
        for path in [
            "/eat-and-drink/",
            "/restaurants/",
            "/food-and-drink/",
        ]
    ):
        return "Food & Drink"

    if any(
        path in url
        for path in [
            "/offers",
            "/events",
            "/whats-on",
            "/what-s-on",
        ]
    ):
        return "Offers & Events"

    if "/services/" in url or "/service/" in url:
        return "Services"

    if "/shops/" in url:
        return "Shops"

    if any(
        name in title
        for name in [
            "costa coffee",
            "wasabi",
            "chamber 9",
            "ikea restaurant",
        ]
    ):
        return "Food & Drink"

    return "Shops"


def shop_categories(title):
    normalized_title = norm(title)

    for known_name, categories in KNOWN_SHOP_CATEGORIES.items():
        if norm(known_name) == normalized_title:
            return categories

    return ["Other"]


def food_subcategory(title, content=""):
    text = norm(str(title) + " " + str(content))

    if any(word in text for word in ["costa", "coffee", "cafe"]):
        return "Coffee"

    if "tea" in text:
        return "Tea"

    if any(word in text for word in ["juice", "smoothie"]):
        return "Juice"

    return "Food"


def service_subcategory(title, content=""):
    text = norm(str(title) + " " + str(content))

    if any(word in text for word in ["bank", "financial", "atm"]):
        return "Banking"

    if any(
        word in text
        for word in ["mobile", "phone", "technology", "telecom"]
    ):
        return "Mobile & Technology"

    if any(
        word in text
        for word in [
            "health",
            "optical",
            "optician",
            "pharmacy",
            "wellness",
        ]
    ):
        return "Health & Optical"

    return "Community & Other Services"


def event_subcategory(title, content=""):
    text = norm(str(title) + " " + str(content))

    if any(
        word in text
        for word in ["offer", "discount", "sale", "promotion", "deal"]
    ):
        return "Offers"

    if any(
        word in text
        for word in ["event", "festival", "workshop", "celebration"]
    ):
        return "Events"

    return "What's On"


def image_for(title, category):
    normalized_title = norm(title)

    for shop_name, image_url in SHOP_IMAGES.items():
        if norm(shop_name) == normalized_title:
            return image_url

    if category == "Food & Drink":
        return FOOD_IMAGES[food_subcategory(title)]

    if category == "Services":
        return SERVICE_IMAGES[service_subcategory(title)]

    if category == "Offers & Events":
        return EVENT_IMAGES[event_subcategory(title)]

    categories = shop_categories(title)

    return SHOP_CATEGORY_IMAGES.get(
        categories[0],
        SHOP_CATEGORY_IMAGES["Other"],
    )


def description_of(row):
    content = re.sub(
        r"\s+",
        " ",
        str(row.get("content", "")).strip(),
    )

    if not content:
        return "Explore this destination at Livat Hammersmith."

    content = re.sub(r"https?://\S+", "", content).strip()

    if len(content) > 135:
        content = content[:132].rsplit(" ", 1)[0] + "..."

    return content or "Explore this destination at Livat Hammersmith."


# ============================================================
# SEARCH
# ============================================================
def search_data(data, query):
    if not query:
        return data.copy()

    terms = [
        term for term in norm(query).split()
        if len(term) > 1
    ]

    scored = data.copy()
    scored["_score"] = 0

    normalized_titles = scored["title"].map(norm)
    normalized_urls = scored["url"].map(norm)
    normalized_content = scored["content"].map(norm)

    for term in terms:
        title_matches = normalized_titles.str.contains(
            re.escape(term), na=False
        ).astype(int)

        url_matches = normalized_urls.str.contains(
            re.escape(term), na=False
        ).astype(int)

        content_matches = normalized_content.str.contains(
            re.escape(term), na=False
        ).astype(int)

        scored["_score"] += title_matches * 5
        scored["_score"] += url_matches * 3
        scored["_score"] += content_matches

    return (
        scored[scored["_score"] > 0]
        .sort_values("_score", ascending=False)
        .drop(columns="_score")
    )


# ============================================================
# FILTER SERVICE RESULTS FROM THE COMPLETE DIRECTORY
# This is the important fix for the Services section.
# ============================================================
def filter_service_results(all_directory, subcategory):
    allowed_names = {
        norm(name)
        for name in SERVICE_SHOP_NAMES.get(subcategory, [])
    }

    if not allowed_names:
        return all_directory.iloc[0:0].copy()

    normalized_titles = all_directory["title"].map(norm)

    results = all_directory[
        normalized_titles.isin(allowed_names)
    ].copy()

    # Include any actual service pages whose titles match the selected
    # service type, without restricting results to /services/ URLs.
    if subcategory == "Banking":
        extra_terms = ["bank", "banking"]
    elif subcategory == "Mobile & Technology":
        extra_terms = ["mobile", "telecom", "technology"]
    elif subcategory == "Health & Optical":
        extra_terms = ["optical", "optician", "health", "pharmacy"]
    else:
        extra_terms = ["community", "library of things", "sook"]

    extra_mask = all_directory.apply(
        lambda row: (
            "/services/" in str(row.get("url", "")).lower()
            and any(
                term in norm(
                    title_of(row) + " " + str(row.get("content", ""))
                )
                for term in extra_terms
            )
        ),
        axis=1,
    )

    extra_results = all_directory[extra_mask].copy()

    results = pd.concat(
        [results, extra_results],
        ignore_index=True,
    )

    return results.drop_duplicates(subset=["url"], keep="first")


# ============================================================
# SESSION STATE
# ============================================================
data = load_data()

if "selected_category" not in st.session_state:
    st.session_state.selected_category = ""

if "selected_subcategory" not in st.session_state:
    st.session_state.selected_subcategory = ""


def select_category(category):
    st.session_state.selected_category = category
    st.session_state.selected_subcategory = ""


def select_subcategory(category, subcategory):
    st.session_state.selected_category = category
    st.session_state.selected_subcategory = subcategory


# ============================================================
# HEADER
# ============================================================
st.markdown(
    f"""
    <div class="livat-header">
        <a href="{SITE_URL}"
           target="_blank"
           rel="noopener noreferrer">
            <img
                class="livat-logo-img"
                src="{LIVAT_LOGO_URL}"
                alt="Livat"
            >
        </a>
    </div>
    """,
    unsafe_allow_html=True,
)

query = st.text_input(
    "Search",
    placeholder="Search shops, food, services and offers...",
    label_visibility="collapsed",
    key="livat_query",
).strip()

# ============================================================
# FOUR MAIN HOMEPAGE OPTIONS
# ============================================================
st.markdown(
    '<div class="section-title">Browse categories</div>',
    unsafe_allow_html=True,
)

main_columns = st.columns(4, gap="medium")

for index, category in enumerate(CATEGORIES):
    with main_columns[index]:
        st.markdown(
            f"""
            <div class="category-card">
                <img
                    src="{MAIN_IMAGES[category]}"
                    alt="{html.escape(category, quote=True)}"
                >
                <div class="category-card-title">
                    {html.escape(category)}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.button(
            f"Explore {category}",
            key=f"main_{category}",
            width="stretch",
            on_click=select_category,
            args=(category,),
        )

# ============================================================
# SUBCATEGORY CARDS
# ============================================================
selected = st.session_state.selected_category

if selected in CATEGORIES:
    st.markdown(
        f'<div class="section-title">{html.escape(selected)}</div>',
        unsafe_allow_html=True,
    )

    subcategories = CATEGORIES[selected]
    subcategory_columns = st.columns(4, gap="medium")

    for index, subcategory in enumerate(subcategories):
        if selected == "Shops":
            image_url = SHOP_CATEGORY_IMAGES[subcategory]
        elif selected == "Food & Drink":
            image_url = FOOD_IMAGES[subcategory]
        elif selected == "Services":
            image_url = SERVICE_IMAGES[subcategory]
        else:
            image_url = EVENT_IMAGES[subcategory]

        with subcategory_columns[index % 4]:
            st.markdown(
                f"""
                <div class="category-card">
                    <img
                        src="{image_url}"
                        alt="{html.escape(subcategory, quote=True)}"
                    >
                    <div class="category-card-title">
                        {html.escape(subcategory)}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.button(
                f"Select {subcategory}",
                key=f"sub_{selected}_{subcategory}",
                width="stretch",
                on_click=select_subcategory,
                args=(selected, subcategory),
            )

# ============================================================
# DIRECTORY DATA
# ============================================================
if data.empty:
    directory = data.copy()
else:
    directory = data[
        data.apply(is_directory_page, axis=1)
    ].copy()

subcategory = st.session_state.selected_subcategory

# ============================================================
# CHOOSE RESULTS
# ============================================================
if query:
    results = search_data(directory, query)
    heading = f'Search results for "{html.escape(query)}"'

elif selected == "Services" and subcategory:
    # FIX: search the complete directory, not just pages classified
    # as Services. Many banks/mobile/optical businesses are in Shops.
    results = filter_service_results(directory, subcategory)
    heading = f"{html.escape(subcategory)} results"

elif selected:
    results = directory[
        directory.apply(main_category, axis=1) == selected
    ].copy()

    heading = f"Explore {html.escape(selected)}"

else:
    results = directory.iloc[0:0].copy()
    heading = ""

# ============================================================
# FILTER NON-SERVICE SUBCATEGORIES
# ============================================================
if (
    subcategory
    and selected != "Services"
    and not query
    and not results.empty
):
    if selected == "Shops":
        results = results[
            results["title"].apply(
                lambda title: subcategory in shop_categories(title)
            )
        ].copy()

    elif selected == "Food & Drink":
        results = results[
            results.apply(
                lambda row: food_subcategory(
                    row["title"], row["content"]
                ) == subcategory,
                axis=1,
            )
        ].copy()

    elif selected == "Offers & Events":
        results = results[
            results.apply(
                lambda row: event_subcategory(
                    row["title"], row["content"]
                ) == subcategory,
                axis=1,
            )
        ].copy()

    heading = f"{html.escape(subcategory)} results"

# ============================================================
# DISPLAY RESULTS
# ============================================================
if heading:
    st.markdown(
        f'<div class="section-title">{heading}</div>',
        unsafe_allow_html=True,
    )

    if results.empty:
        st.info(
            "No matching pages were found in the scraped data. "
            "Check that the relevant pages exist in your CSV."
        )

    else:
        result_columns = st.columns(4, gap="medium")

        for index, (_, row) in enumerate(
            results.head(32).iterrows()
        ):
            title = title_of(row)
            category = main_category(row)
            image_url = image_for(title, category)
            description = description_of(row)
            url = str(row.get("url", "")).strip()

            if url.startswith("http"):
                target_url = url
            elif url:
                target_url = urljoin(
                    SITE_URL.rstrip("/") + "/",
                    url.lstrip("/"),
                )
            else:
                target_url = SITE_URL

            with result_columns[index % 4]:
                st.markdown(
                    f"""
                    <div class="result-card">
                        <img
                            src="{image_url}"
                            alt="{html.escape(title, quote=True)}"
                        >
                        <div class="result-body">
                            <div class="result-name">
                                {html.escape(title)}
                            </div>
                            <div class="result-category">
                                {html.escape(category)}
                            </div>
                            <div class="result-description">
                                {html.escape(description)}
                            </div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                st.link_button(
                    "View details",
                    target_url,
                    width="stretch",
                )

else:
    st.caption(
        "Choose a category above or enter a search term "
        "to see relevant shops and pages."
    )

# ============================================================
# FEEDBACK BUBBLE AND FOOTER
# ============================================================
st.markdown(
    f"""
    <div class="feedback-bubble">
        We'd love to hear<br>
        your feedback<br>
        <a href="{SITE_URL}" target="_blank" rel="noopener noreferrer">
            Let's go
        </a>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="footer-note">
        Category and shop images are illustrative stock photos,
        not verified official business photographs. Search results
        are based on locally scraped website data.
    </div>
    """,
    unsafe_allow_html=True,
)
