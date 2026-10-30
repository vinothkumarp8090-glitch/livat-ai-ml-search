import os
import re
import html
import json
from difflib import SequenceMatcher
from urllib.parse import urljoin

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components


# ------------------------------------------------------------
# PAGE CONFIGURATION
# ------------------------------------------------------------
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


def _img(photo_id, width=700):
    return (
        f"https://images.unsplash.com/{photo_id}"
        f"?auto=format&fit=crop&w={width}&q=85"
    )


# ------------------------------------------------------------
# HOMEPAGE IMAGES
# ------------------------------------------------------------
MAIN_IMAGES = {
    "Shops": _img("photo-1441986300917-64674bd600d8", 900),
    "Food & Drink": _img("photo-1517248135467-4c7edcad34c4", 900),
    "Services": _img("photo-1497366754035-f200968a6e72", 900),
    "Offers & Events": _img("photo-1492684223066-81342ee5ff30", 900),
}

SHOP_CATEGORY_IMAGES = {
    "Fashion": _img("photo-1483985988355-763728e1935b"),
    "Womenswear": _img("photo-1485230895905-ec40ba36b9bc"),
    "Menswear": _img("photo-1516257984-b1b4d707412e"),
    "Childrenswear": _img("photo-1519238263530-99bdd11df2ea"),
    "Footwear": _img("photo-1543163521-1bf539c55dd2"),
    "Accessories & Watches": _img("photo-1523170335258-f5ed11844a49"),
    "Electronic & Media": _img("photo-1511707171634-5f897ff02aa9"),
    "Grocery": _img("photo-1542838132-92c53300491e"),
    "Bank": _img("photo-1444653614773-995cb1ef9efa"),
    "Home & Decor": _img("photo-1555041469-a586c61ea9bc"),
    "Health & Wellness": _img("photo-1544367567-0f2fcb009e0b"),
    "Pharmacy & Optometry": _img("photo-1511499767150-a48a237f0083"),
    "Perfumery": _img("photo-1541643600914-78b084683601"),
    "Sport": _img("photo-1461896836934-ffe607ba8211"),
    "Other": _img("photo-1497366811353-6870744d04b2"),
}

FOOD_IMAGES = {
    "Coffee": _img("photo-1495474472287-4d71bcdd2085"),
    "Tea": _img("photo-1544787219-7f47ccb76574"),
    "Juice": _img("photo-1600271886742-f049cd451bba"),
    "Food": _img("photo-1504674900247-0877df9cc836"),
}

SERVICE_IMAGES = {
    "Banking": _img("photo-1450101499163-c8848c66ca85"),
    "Mobile & Technology": _img("photo-1519389950473-47ba0277781c"),
    "Health & Optical": _img("photo-1576091160399-112ba8d25d1d"),
    "Community & Other Services": _img("photo-1521737711867-e3b97375f902"),
}

EVENT_IMAGES = {
    "Offers": _img("photo-1607083206968-13611e3d76db"),
    "Events": _img("photo-1506157786151-b8491531f063"),
    "What's On": _img("photo-1514525253161-7a46d19cd819"),
}

SHOP_IMAGES = {
    "Atelier100": _img("photo-1490481651871-ab68de25d43d"),
    "Bluebird - 1": _img("photo-1445205170230-053b83016050"),
    "Clarks": _img("photo-1543163521-1bf539c55dd2"),
    "EE": _img("photo-1556656793-08538906a9f8"),
    "Foot Locker": _img("photo-1552346154-21d32810aba3"),
    "Frame": _img("photo-1576091160550-2173dba999ef"),
    "H&M": _img("photo-1485230895905-ec40ba36b9bc"),
    "IKEA": _img("photo-1555041469-a586c61ea9bc"),
    "JD Sports": _img("photo-1461896836934-ffe607ba8211"),
    "Library of Things": _img("photo-1494438639946-1ebd1d20bf85"),
    "Lidl": _img("photo-1542838132-92c53300491e"),
    "Lidl-1": _img("photo-1604719312566-8912e9c8a213"),
    "Metro Bank": _img("photo-1444653614773-995cb1ef9efa"),
    "NatWest Bank": _img("photo-1486406146926-c627a92ad1ab"),
    "O2": _img("photo-1511707171634-5f897ff02aa9"),
    "Primark": _img("photo-1483985988355-763728e1935b"),
    "Sainsbury’s": _img("photo-1604719312566-8912e9c8a213"),
    "Santander": _img("photo-1460925895917-afdab827c52f"),
    "Sook": _img("photo-1473186505569-9c61870c11f9"),
    "Specsavers": _img("photo-1511499767150-a48a237f0083"),
    "The Fragrance Shop": _img("photo-1541643600914-78b084683601"),
    "Three": _img("photo-1598327105666-5b89351aff97"),
    "Chamber 9": _img("photo-1414235077428-338989a2e8c0"),
    "Costa Coffee": FOOD_IMAGES["Coffee"],
    "IKEA Restaurant": _img("photo-1555396273-367ea4eb4db5"),
    "Wasabi": _img("photo-1579871494447-9811cf80d66c"),
}


# ------------------------------------------------------------
# CATEGORIES
# ------------------------------------------------------------
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
    "Atelier100": [
        "Accessories & Watches", "Womenswear", "Menswear",
        "Home & Decor", "Other",
    ],
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

NON_DIRECTORY_TERMS = [
    "cookie notice", "privacy policy", "terms and conditions",
    "contact us", "accessibility", "christmas at livat",
    "site map", "sitemap", "legal notice",
]


# ------------------------------------------------------------
# CSS / DESIGN
# ------------------------------------------------------------
# Geometry shared by the header band, search bar and dropdown.
# Change these in one place to move the whole search area.
st.markdown(
    """
<style>
:root {
    color-scheme: light;
    --band-bg: #f7f3ef;
    --band-line: #e3d8cf;
    --search-left: clamp(170px, 20vw, 300px);
    --search-right: clamp(1rem, 10vw, 180px);
    --search-top: 28px;
    --search-h: 48px;
    --band-h: 76px;
}

html, body, .stApp,
[data-testid="stAppViewContainer"],
[data-testid="stMain"] {
    background: #ffffff !important;
}

/* Hide Streamlit's own header so our beige band is the header */
[data-testid="stHeader"] {
    background: transparent !important;
    z-index: 1 !important;
}

.stApp::before,
.stApp::after {
    content: "";
    position: fixed;
    z-index: 0;
    pointer-events: none;
    border: clamp(22px,3.2vw,54px) solid #ffdf00;
    border-radius: 50%;
}
.stApp::before {
    width: clamp(330px,36vw,650px);
    height: clamp(520px,58vw,850px);
    left: clamp(-520px,-25vw,-280px);
    bottom: clamp(-560px,-30vw,-300px);
    transform: rotate(-22deg);
}
.stApp::after {
    width: clamp(360px,39vw,700px);
    height: clamp(170px,20vw,360px);
    right: clamp(-520px,-27vw,-260px);
    bottom: clamp(-290px,-17vw,-150px);
    transform: rotate(-30deg);
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
    min-height: calc(100vh - 1rem);
    padding: calc(var(--band-h) + 1rem) clamp(1.25rem,3.5vw,3.5rem) 2.5rem !important;
}

.section-title {
    font-size: 23px;
    font-weight: 750;
    margin: 28px 0 16px;
    color: #171717;
    letter-spacing: -.25px;
}

.category-card, .result-card {
    border: 1px solid #eee1d8;
    border-radius: 17px;
    overflow: hidden;
    background: #f7f3ef;
    margin-bottom: 8px;
    box-shadow: 0 1px 1px rgba(30,20,10,.02);
}
.category-card img {
    width: 100%;
    height: clamp(130px,13vw,190px);
    object-fit: cover;
    display: block;
}
.category-card-title {
    padding: 12px 13px;
    font-weight: 750;
    font-size: 14px;
    min-height: 45px;
    color: #171717;
}
.result-card { background: #ffffff; height: 100%; }
.result-card img {
    width: 100%;
    height: clamp(145px,13vw,180px);
    object-fit: cover;
    display: block;
}
.result-body { padding: 13px; }
.result-name {
    font-size: 16px; font-weight: 750; margin-bottom: 5px; color: #171717;
}
.result-category { font-size: 12px; color: #8a634a; margin-bottom: 8px; }
.result-description {
    font-size: 13px; color: #555; line-height: 1.5; min-height: 38px;
}

.stButton > button, .stLinkButton > a {
    border-radius: 24px !important;
    border: 1px solid #e3d2c5 !important;
    min-height: 42px;
    background: #ffffff !important;
    color: #171717 !important;
}
.stButton > button:hover, .stLinkButton > a:hover {
    border-color: #b79a84 !important;
    background: #faf7f4 !important;
}

/* ---------- Misc ---------- */

@media (max-width: 700px) {
    :root { --band-h: 126px; }
    .block-container { padding-left: 1rem !important; padding-right: 1rem !important; }
    .category-card img { height: 110px; }
    .stApp::before, .stApp::after { opacity: .75; }
}
</style>
""",
    unsafe_allow_html=True,
)


# ------------------------------------------------------------
# LOAD SCRAPED CSV DATA
# ------------------------------------------------------------
@st.cache_data
def load_data():
    cols = ["title", "url", "content", "content_status"]

    if not os.path.exists(DATA_FILE):
        return pd.DataFrame(columns=cols)

    data = pd.read_csv(DATA_FILE).fillna("")

    for col in cols:
        if col not in data.columns:
            data[col] = ""
        data[col] = data[col].astype(str)

    data = data[data["title"].str.strip().ne("")]
    data = data.drop_duplicates(subset=["url"], keep="first")

    return data.reset_index(drop=True)


# ------------------------------------------------------------
# HELPER FUNCTIONS
# ------------------------------------------------------------
def norm(value):
    """Convert text into lowercase searchable words."""
    return re.sub(r"[^a-z0-9]+", " ", str(value).lower()).strip()


def title_of(row):
    title = str(row.get("title", "")).strip()
    if title:
        return title
    return (
        str(row.get("url", "")).rstrip("/").split("/")[-1]
        .replace("-", " ").title()
    )


VALID_PATHS = [
    "/shops/", "/eat-and-drink/", "/restaurants/", "/food-and-drink/",
    "/services/", "/offers", "/events", "/whats-on", "/what-s-on",
    "/news",
]


def is_directory_page(row):
    title = norm(title_of(row))
    url = str(row.get("url", "")).lower()

    if any(norm(term) in title for term in NON_DIRECTORY_TERMS):
        return False

    if any(
        term in url
        for term in ["cookie", "privacy", "contact", "terms",
                     "accessibility", "sitemap"]
    ):
        return False

    return any(path in url for path in VALID_PATHS)


def main_category(row):
    url = str(row.get("url", "")).lower()
    title = norm(title_of(row))

    if any(p in url for p in ["/eat-and-drink/", "/restaurants/", "/food-and-drink/"]):
        return "Food & Drink"

    if any(p in url for p in ["/offers", "/events", "/whats-on", "/what-s-on"]):
        return "Offers & Events"

    if "/news" in url:
        return "News"

    if "/services/" in url or "/service/" in url:
        return "Services"

    if "/shops/" in url:
        return "Shops"

    if any(
        name in title
        for name in ["costa coffee", "wasabi", "chamber 9", "ikea restaurant"]
    ):
        return "Food & Drink"

    return "Shops"


def shop_categories(title):
    title_normalized = norm(title)
    for known_name, categories in KNOWN_SHOP_CATEGORIES.items():
        if norm(known_name) == title_normalized:
            return categories
    return ["Other"]


def food_subcategory(title, content=""):
    text = norm(title + " " + content)
    if any(w in text for w in ["costa", "coffee", "cafe", "café"]):
        return "Coffee"
    if "tea" in text:
        return "Tea"
    if any(w in text for w in ["juice", "smoothie"]):
        return "Juice"
    return "Food"


def service_subcategory(title, content=""):
    text = norm(title + " " + content)
    if any(w in text for w in ["bank", "financial", "atm"]):
        return "Banking"
    if any(w in text for w in ["mobile", "phone", "technology", "telecom"]):
        return "Mobile & Technology"
    if any(w in text for w in ["health", "optical", "optician", "pharmacy", "wellness"]):
        return "Health & Optical"
    return "Community & Other Services"


def event_subcategory(title, content=""):
    text = norm(title + " " + content)
    if any(w in text for w in ["offer", "discount", "sale", "promotion", "deal"]):
        return "Offers"
    if any(w in text for w in ["event", "festival", "workshop", "celebration"]):
        return "Events"
    return "What's On"


def image_for(title, category):
    title_normalized = norm(title)

    for name, image_url in SHOP_IMAGES.items():
        if norm(name) == title_normalized:
            return image_url

    if category == "Food & Drink":
        return FOOD_IMAGES[food_subcategory(title)]
    if category == "Services":
        return SERVICE_IMAGES[service_subcategory(title)]
    if category in ("Offers & Events", "News"):
        return EVENT_IMAGES[event_subcategory(title)]

    return SHOP_CATEGORY_IMAGES.get(
        shop_categories(title)[0], SHOP_CATEGORY_IMAGES["Other"]
    )


def description_of(row):
    content = re.sub(r"\s+", " ", str(row.get("content", "")).strip())

    if not content:
        return "Explore this destination at Livat Hammersmith."

    content = re.sub(r"https?://\S+", "", content).strip()

    if len(content) > 135:
        content = content[:132].rsplit(" ", 1)[0] + "..."

    return content or "Explore this destination at Livat Hammersmith."


def get_page_url(row):
    url = str(row.get("url", "")).strip()
    if not url:
        return SITE_URL
    if url.startswith("http://") or url.startswith("https://"):
        return url
    return urljoin(SITE_URL + "/", url.lstrip("/"))


# ------------------------------------------------------------
# SEARCH
# ------------------------------------------------------------
def search_data(data, query):
    """Rank pages by title first, then URL, then (longer queries) content."""
    if data.empty or not query.strip():
        return data.iloc[0:0].copy()

    q = norm(query)
    if not q:
        return data.iloc[0:0].copy()

    scored = data.copy()
    scored["_title"] = scored["title"].map(norm)
    scored["_url"] = scored["url"].map(norm)
    scored["_content"] = scored["content"].map(norm)
    scored["_score"] = 0

    pattern = re.escape(q)

    in_title = scored["_title"].str.contains(pattern, na=False)
    scored.loc[in_title, "_score"] += 100

    # Titles that START with the query rank above mid-title matches.
    scored.loc[scored["_title"].str.startswith(q, na=False), "_score"] += 40

    scored.loc[scored["_url"].str.contains(pattern, na=False), "_score"] += 15

    if len(q.replace(" ", "")) >= 3:
        scored.loc[scored["_content"].str.contains(pattern, na=False), "_score"] += 2

    for term in q.split():
        if len(term) < 2:
            continue
        t = re.escape(term)
        scored.loc[scored["_title"].str.contains(t, na=False), "_score"] += 8
        scored.loc[scored["_url"].str.contains(t, na=False), "_score"] += 4

    results = scored[scored["_score"] > 0].copy()
    if results.empty:
        return data.iloc[0:0].copy()

    results = results.sort_values(by=["_score", "title"], ascending=[False, True])
    return results.drop(columns=["_title", "_url", "_content", "_score"], errors="ignore")


# ------------------------------------------------------------
# AI SEARCH  (hybrid: semantic embeddings + TF-IDF + fuzzy)
# ------------------------------------------------------------
# 1. Semantic  - sentence embeddings (meaning): "buy trainers" -> JD Sports
# 2. TF-IDF    - word + character n-grams (importance + typo tolerance)
# 3. Fuzzy     - edit-distance similarity on the title
# Each part is optional: whatever is installed is used, the rest is skipped.
#   pip install scikit-learn rapidfuzz sentence-transformers
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False

try:
    from rapidfuzz import fuzz as _rf_fuzz
except ImportError:
    _rf_fuzz = None


@st.cache_resource(show_spinner="Loading AI model...")
def load_embedder():
    try:
        from sentence_transformers import SentenceTransformer
        return SentenceTransformer("all-MiniLM-L6-v2")
    except Exception:
        return None


def page_text(row):
    content = re.sub(r"\s+", " ", str(row.get("content", ""))).strip()[:500]
    return f"{title_of(row)}. {main_category(row)}. {content}"


@st.cache_resource(show_spinner="Building AI search index...")
def build_ai_index(texts):
    index = {"emb": None, "word": None, "char": None, "wm": None, "cm": None}

    embedder = load_embedder()
    if embedder is not None:
        index["emb"] = embedder.encode(
            list(texts), normalize_embeddings=True, show_progress_bar=False
        )

    if HAS_SKLEARN:
        index["word"] = TfidfVectorizer(
            stop_words="english", ngram_range=(1, 2), sublinear_tf=True
        )
        index["wm"] = index["word"].fit_transform(texts)
        index["char"] = TfidfVectorizer(
            analyzer="char_wb", ngram_range=(2, 4), sublinear_tf=True
        )
        index["cm"] = index["char"].fit_transform(texts)

    return index


def _fuzzy_score(query, title):
    q, t = norm(query), norm(title)
    if _rf_fuzz is not None:
        return _rf_fuzz.WRatio(q, t) / 100.0
    return SequenceMatcher(None, q, t).ratio()


def _unit(values):
    top = max(values) if len(values) else 0
    return [v / top if top > 0 else 0.0 for v in values]


def ai_search(frame, query, limit=24):
    """Return (results_dataframe, description_of_methods_used)."""
    if frame.empty or not query.strip():
        return frame.iloc[0:0].copy(), ""

    frame = frame.reset_index(drop=True)
    texts = tuple(page_text(row) for _, row in frame.iterrows())
    index = build_ai_index(texts)

    parts, weights, used = [], [], []

    if index["emb"] is not None:
        qv = load_embedder().encode([query], normalize_embeddings=True)[0]
        sims = (index["emb"] @ qv).clip(min=0)
        parts.append(_unit(list(sims)))
        weights.append(0.5)
        used.append("semantic embeddings")

    if index["wm"] is not None:
        word_sim = cosine_similarity(index["word"].transform([query]), index["wm"])[0]
        char_sim = cosine_similarity(index["char"].transform([query]), index["cm"])[0]
        parts.append(_unit(list(0.6 * word_sim + 0.4 * char_sim)))
        weights.append(0.3)
        used.append("TF-IDF")

    parts.append(_unit([_fuzzy_score(query, title_of(r)) for _, r in frame.iterrows()]))
    weights.append(0.2)
    used.append("fuzzy matching")

    total = sum(weights)
    final = [
        sum(w * part[i] for w, part in zip(weights, parts)) / total
        for i in range(len(frame))
    ]

    ranked = frame.assign(_ai=final).sort_values("_ai", ascending=False)
    ranked = ranked[ranked["_ai"] > 0.15].head(limit)
    return ranked.drop(columns=["_ai"]), "Ranked using " + " + ".join(used) + "."


# ------------------------------------------------------------
# SESSION STATE
# ------------------------------------------------------------
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


# ------------------------------------------------------------
# DIRECTORY PAGES
# ------------------------------------------------------------
directory = (
    data[data.apply(is_directory_page, axis=1)].copy()
    if not data.empty
    else data.copy()
)


# ------------------------------------------------------------
# LIVE SEARCH (header band + search bar + suggestions)
# ------------------------------------------------------------
# Everything is drawn inside one small embedded widget so that
# suggestions can update on every keystroke (st.text_input only
# updates on Enter). The widget filters the scraped data in the
# browser, expands over the page while open, and dims the page.
SEARCH_WIDGET = """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="color-scheme" content="light">
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap');
:root { color-scheme: light; }
* { box-sizing: border-box; }
html, body {
    margin: 0; padding: 0; background: transparent;
    font-family: 'Poppins', 'Segoe UI', Arial, sans-serif;
    color: #171717; overflow: hidden;
}
#dim {
    position: fixed; inset: 0; background: rgba(0,0,0,.38);
    display: none;
}
body.open #dim { display: block; }

#band { position: relative; background: transparent; min-height: 76px; }
body.open #band {
    background: #f7f3ef; min-height: 104px;
    border-radius: 0 0 22px 22px;
    box-shadow: 0 10px 30px rgba(0,0,0,.14);
}

/* Closed: small yellow pill in the top-right corner */
#box {
    margin: 15px auto; width: min(420px, calc(100% - 48px));
    background: #ffdf00; border: 1px solid #ffdf00; border-radius: 28px;
    overflow: hidden;
}
body:not(.open) #box { height: 46px; }
#q::placeholder { color: #5c5200; }
/* Open: wide white search with dropdown */
body.open #box {
    margin: 28px auto; width: min(1000px, calc(100% - 180px));
    background: #fff; border-color: #e3d8cf;
}
body.open #q::placeholder { color: #8d8d8d; }
#row { position: relative; height: 46px; display: flex; align-items: center; }
#q {
    flex: 1; height: 46px; border: 0; outline: 0; background: transparent;
    padding: 0 130px 0 26px; font: inherit; font-size: 15px; color: #171717;
}
#q::placeholder { color: #8d8d8d; }
#clear {
    position: absolute; right: 62px; top: 11px; width: 24px; height: 24px;
    border: 0; background: transparent; cursor: pointer; padding: 0; display: none;
}
body.open.has-q #clear { display: block; }
#sep { position: absolute; right: 52px; top: 13px; height: 20px; border-left: 1px solid #cfc6bd; }
#go {
    position: absolute; right: 18px; top: 13px; width: 20px; height: 20px;
    border: 0; background: transparent; padding: 0; cursor: pointer;
}
#list { display: none; margin: 0 27px; border-top: 1px solid #d9cfc6; padding: 8px 0 14px; }
body.open.has-q #list { display: block; }
.item {
    display: block; padding: 10px 6px; text-decoration: none; color: #171717;
    font-size: 17px; line-height: 1.35; border-radius: 10px; cursor: pointer;
}
.item:hover, .item.active { background: #f6f2ee; }
.item.smart { border-top: 1px solid #e8dfd6; border-radius: 0 0 10px 10px; margin-top: 6px; }
.item b { font-weight: 600; letter-spacing: -.1px; color: #3a3a3a; }
.item span { font-size: 12px; color: #444; margin-left: 5px; font-weight: 400; }
.empty { padding: 14px 6px; font-size: 14px; color: #777; }

#close {
    position: absolute; right: 3%; top: 36px; width: 64px; height: 64px;
    border-radius: 50%; border: 0; background: #fff; cursor: pointer;
    box-shadow: 0 2px 8px rgba(0,0,0,.12); display: none;
}
body.open #close { display: block; }

@media (max-width: 700px) {
    #box { margin: 15px 12px; width: auto; }
    body.open #box { margin: 58px 16px 16px 16px; width: auto; }
    body.open #band { min-height: 126px; }
    #close { right: 12px; top: 8px; width: 42px; height: 42px; }
    .item { font-size: 15px; }
}
</style>
</head>
<body>
<div id="dim"></div>
<div id="band">
    <div id="box">
        <div id="row">
            <input id="q" type="text" autocomplete="off" spellcheck="false"
                   placeholder="What are you looking for?" aria-label="Search">
            <button id="clear" aria-label="Clear" title="Clear">
                <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="#444" stroke-width="2.6" stroke-linecap="round"><line x1="5" y1="5" x2="19" y2="19"/><line x1="19" y1="5" x2="5" y2="19"/></svg>
            </button>
            <span id="sep"></span>
            <button id="go" aria-label="Search">
                <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="#333" stroke-width="2.8" stroke-linecap="round"><circle cx="10.5" cy="10.5" r="6.5"/><line x1="15.5" y1="15.5" x2="21" y2="21"/></svg>
            </button>
        </div>
        <div id="list"></div>
    </div>
    <button id="close" aria-label="Close search">
        <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="#333" stroke-width="3.2" stroke-linecap="round"><line x1="5" y1="5" x2="19" y2="19"/><line x1="19" y1="5" x2="5" y2="19"/></svg>
    </button>
</div>

<script>
const DATA = __DATA__;
const frame = window.frameElement;
const q = document.getElementById('q');
const list = document.getElementById('list');
let shown = [];
let active = -1;

const norm = s => String(s).toLowerCase().replace(/[^a-z0-9]+/g, ' ').trim();
const esc = s => String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));

DATA.forEach(r => { r._t = norm(r.t); r._u = norm(r.u); r._x = norm(r.x); });

function closedH() { return 76; }

function setFrame(open) {
    if (!frame) return;
    let pw = window.innerWidth;
    try { pw = window.parent.innerWidth; } catch (e) {}
    const mobile = pw < 700;
    let left = 0, width = pw;
    if (!open) {
        if (mobile) { left = 130; width = Math.max(pw - 130, 200); }
        else { width = Math.min(480, pw); left = Math.round((pw - width) / 2); }
    }
    Object.assign(frame.style, {
        position: 'fixed', top: '0', left: left + 'px', width: width + 'px',
        transform: 'none', border: '0', zIndex: '1000000',
        background: 'transparent',
        height: open ? '100vh' : closedH() + 'px'
    });
}

function setOpen(open) {
    document.body.classList.toggle('open', open);
    setFrame(open);
}

function lev(a, b) {
    const m = a.length, n = b.length;
    let prev = Array.from({length: n + 1}, (_, j) => j);
    for (let i = 1; i <= m; i++) {
        const cur = [i];
        for (let j = 1; j <= n; j++) {
            cur[j] = Math.min(prev[j] + 1, cur[j - 1] + 1,
                              prev[j - 1] + (a[i - 1] === b[j - 1] ? 0 : 1));
        }
        prev = cur;
    }
    return prev[n];
}

// Typo tolerance: "specsaver", "foot lokcer", "ikia" still match
function fuzzy(r, terms) {
    let n = 0;
    const words = r._t.split(' ');
    for (const t of terms) {
        if (t.length < 3) continue;
        let best = 0;
        for (const w of words) {
            if (Math.abs(w.length - t.length) > 2) continue;
            const sim = 1 - lev(t, w) / Math.max(t.length, w.length);
            if (sim > best) best = sim;
        }
        if (best >= 0.7) n += Math.round(25 * best);
    }
    return n;
}

function smartUrl() {
    let base = location.href;
    try { base = window.parent.location.href; } catch (e) {}
    return base.split('?')[0] + '?ai=' + encodeURIComponent(q.value.trim());
}

function score(r, s, terms) {
    let n = 0;
    if (r._t.includes(s)) n += 100;
    if (r._t.startsWith(s)) n += 40;
    if (r._t.split(' ').some(w => w.startsWith(s))) n += 30;
    if (r._u.includes(s)) n += 15;
    if (s.replace(/ /g, '').length >= 3 && r._x.includes(s)) n += 2;
    for (const t of terms) {
        if (t.length < 2) continue;
        if (r._t.includes(t)) n += 8;
        if (r._u.includes(t)) n += 4;
    }
    if (n === 0) n += fuzzy(r, terms);
    return n;
}

function render() {
    const s = norm(q.value);
    document.body.classList.toggle('has-q', q.value.trim().length > 0);
    active = -1;
    if (!s) { shown = []; list.innerHTML = ''; return; }

    const terms = s.split(' ');
    shown = DATA
        .map(r => ({ r, n: score(r, s, terms) }))
        .filter(o => o.n > 0)
        .sort((a, b) => b.n - a.n || a.r.t.localeCompare(b.r.t))
        .slice(0, 8)
        .map(o => o.r);

    list.innerHTML = shown.length
        ? shown.map((r, i) =>
            '<a class="item" data-i="' + i + '" href="' + esc(r.u) +
            '" target="_blank" rel="noopener noreferrer"><b>' + esc(r.t) +
            '</b><span>' + esc(r.k) + '</span></a>').join('')
        : '<div class="empty">No exact matches. Try Smart search below.</div>';

    list.innerHTML += '<a class="item smart" href="' + esc(smartUrl()) +
        '" target="_blank" rel="noopener noreferrer"><b>\u2728 Smart search</b>' +
        '<span>meaning-based results for \u201c' + esc(q.value.trim()) + '\u201d</span></a>';
}

function highlight() {
    list.querySelectorAll('.item').forEach((el, i) => el.classList.toggle('active', i === active));
}

q.addEventListener('focus', () => { setOpen(true); render(); });
q.addEventListener('input', () => { setOpen(true); render(); });
q.addEventListener('keydown', e => {
    if (e.key === 'ArrowDown' && shown.length) { e.preventDefault(); active = (active + 1) % shown.length; highlight(); }
    else if (e.key === 'ArrowUp' && shown.length) { e.preventDefault(); active = (active <= 0 ? shown.length : active) - 1; highlight(); }
    else if (e.key === 'Enter' && shown.length) { window.open(shown[Math.max(active, 0)].u, '_blank', 'noopener'); }
    else if (e.key === 'Enter' && q.value.trim()) { window.open(smartUrl(), '_blank', 'noopener'); }
    else if (e.key === 'Escape') { q.blur(); setOpen(false); }
});

document.getElementById('clear').addEventListener('click', () => { q.value = ''; render(); q.focus(); });
document.getElementById('go').addEventListener('click', () => {
    if (shown.length) window.open(shown[0].u, '_blank', 'noopener');
    else if (q.value.trim()) window.open(smartUrl(), '_blank', 'noopener');
    else q.focus();
});
document.getElementById('close').addEventListener('click', () => { q.blur(); setOpen(false); });
document.getElementById('dim').addEventListener('click', () => { q.blur(); setOpen(false); });
const onResize = () => setFrame(document.body.classList.contains('open'));
window.addEventListener('resize', onResize);
try { window.parent.addEventListener('resize', onResize); } catch (e) {}

setFrame(false);
</script>
</body>
</html>
"""


@st.cache_data
def build_search_records(frame):
    records = []
    for _, row in frame.iterrows():
        records.append(
            {
                "t": title_of(row),
                "k": main_category(row),
                "u": get_page_url(row),
                "x": re.sub(r"\s+", " ", str(row.get("content", "")))[:300],
            }
        )
    return records


payload = json.dumps(build_search_records(directory), ensure_ascii=False)
payload = payload.replace("</", "<\\/")

components.html(
    SEARCH_WIDGET
    .replace("__DATA__", payload)
    .replace("__SITE_URL__", SITE_URL)
    .replace("__LOGO__", LIVAT_LOGO_URL),
    height=1,
)


# ------------------------------------------------------------
# CATEGORIES BAR (one button in the corner; everything inside it)
# ------------------------------------------------------------
CATEGORY_COLOURS = {
    "CATEGORYS":"#ff000d",
    "Shops": "#bf249b",
    "Food & Drink": "#17efeb",
    "Services": "#1a45d3",
    "Offers & Events": "#EFEA5A",
}


def slug(text):
    return text.replace(" ", "_").replace("&", "and").replace("'", "")


side_css = "".join(
    f".st-key-cat_{slug(name)} details{{border:2px solid {colour} !important;"
    f"border-radius:14px !important;background:{colour}33 !important;}}"
    f".st-key-cat_{slug(name)} summary{{background:{colour} !important;"
    f"font-weight:700;border-radius:12px;}}"
    for name, colour in CATEGORY_COLOURS.items()
)
st.markdown(
    f"""
<style>
{side_css}
/* The corner "Categories" button */
.st-key-catpop {{
    position: fixed !important;
    top: 15px; left: 24px;
    width: auto !important;
    z-index: 1000002;
}}
.st-key-catpop > div > button,
.st-key-catpop [data-testid="stPopover"] > button {{
    background: #171717 !important; color: #ffffff !important;
    border: none !important; border-radius: 26px !important;
    min-height: 46px; padding: 0 22px; font-weight: 700;
}}
[data-testid="stPopoverBody"] {{ min-width: min(340px, 90vw); }}
[data-testid="stPopoverBody"] .stButton > button {{
    min-height: 36px; font-size: 13px; justify-content: flex-start;
    background: #ffffff !important; border: 1px solid #e3d8cf !important;
}}
[data-testid="stPopoverBody"] .stButton > button[kind="primary"] {{
    background: #171717 !important; color: #fff !important;
    border-color: #171717 !important;
}}
@media (max-width: 700px) {{
    .st-key-catpop {{ left: 12px; top: 15px; }}
}}
</style>
""",
    unsafe_allow_html=True,
)

selected = st.session_state.selected_category
selected_sub = st.session_state.selected_subcategory

with st.container(key="catpop"):
    with st.popover("☰ Categories"):
        for category, subs in CATEGORIES.items():
            with st.container(key=f"cat_{slug(category)}"):
                with st.expander(category, expanded=(category == selected)):
                    st.button(
                        f"All {category}",
                        key=f"all_{slug(category)}",
                        width="stretch",
                        type=(
                            "primary"
                            if category == selected and not selected_sub
                            else "secondary"
                        ),
                        on_click=select_category,
                        args=(category,),
                    )
                    for subcategory in subs:
                        st.button(
                            subcategory,
                            key=f"sub_{slug(category)}_{slug(subcategory)}",
                            width="stretch",
                            type=(
                                "primary"
                                if category == selected and subcategory == selected_sub
                                else "secondary"
                            ),
                            on_click=select_subcategory,
                            args=(category, subcategory),
                        )


# ------------------------------------------------------------
# RESULTS
# ------------------------------------------------------------
ai_query = str(st.query_params.get("ai", "")).strip()
ai_note = ""

if ai_query:
    results, ai_note = ai_search(directory, ai_query)
    heading = f'Smart results for "{html.escape(ai_query)}"'
    selected_sub = ""
elif selected:
    results = directory[directory.apply(main_category, axis=1) == selected].copy()
    heading = f"Explore {html.escape(selected)}"
else:
    results = directory.iloc[0:0].copy()
    heading = ""

if selected_sub and not results.empty and not ai_query:
    if selected == "Shops":
        results = results[results["title"].apply(lambda t: selected_sub in shop_categories(t))]
    elif selected == "Food & Drink":
        results = results[results.apply(lambda r: food_subcategory(r["title"], r["content"]) == selected_sub, axis=1)]
    elif selected == "Services":
        results = results[results.apply(lambda r: service_subcategory(r["title"], r["content"]) == selected_sub, axis=1)]
    elif selected == "Offers & Events":
        results = results[results.apply(lambda r: event_subcategory(r["title"], r["content"]) == selected_sub, axis=1)]

    heading = f"{html.escape(selected_sub)} results"

if heading:
    st.markdown(f'<div class="section-title">{heading}</div>', unsafe_allow_html=True)

    if ai_query:
        if ai_note:
            st.caption(ai_note)
        if st.button("Clear smart search"):
            st.query_params.clear()
            st.rerun()

    if results.empty:
        st.info(
            "No matching pages were found in the scraped data. "
            "Try another category or search term."
        )
    else:
        cols = st.columns(4, gap="medium")

        for i, (_, row) in enumerate(results.head(32).iterrows()):
            title = title_of(row)
            category = main_category(row)
            image_url = image_for(title, category)
            description = description_of(row)
            target = get_page_url(row)

            with cols[i % 4]:
                st.markdown(
                    f"""
                    <div class="result-card">
                        <img src="{image_url}" alt="{html.escape(title, quote=True)}">
                        <div class="result-body">
                            <div class="result-name">{html.escape(title)}</div>
                            <div class="result-category">{html.escape(category)}</div>
                            <div class="result-description">{html.escape(description)}</div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                st.link_button("View details", target, width="stretch")
