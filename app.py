"""
app3.py
=======
Pure viewer — zero processing in Streamlit.

Before running this app, run the pre-processing script ONCE:
  ./stonex-venv/bin/python stone_clustering_app/preprocess_results.py

Then launch this app:
  ./stonex-venv/bin/streamlit run stone_clustering_app/app3.py
"""

import streamlit as st
import json
from pathlib import Path

# -----------------------------------------------------------------------
# Page config
# -----------------------------------------------------------------------
st.set_page_config(
    page_title="Stone Tile Cluster Viewer",
    page_icon="🪨",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# -----------------------------------------------------------------------
# Styling
# -----------------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');

html, body, [class*="css"] { font-family: 'Outfit', sans-serif; }

.hero-title {
    font-size: 2.6rem;
    font-weight: 800;
    background: linear-gradient(135deg, #c0a96e 0%, #e8d5a3 50%, #c0a96e 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.2rem;
}
.hero-sub {
    font-size: 1.05rem;
    font-weight: 300;
    color: #888;
    margin-bottom: 2rem;
}

/* Selector container */
.selector-wrap {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.09);
    border-radius: 16px;
    padding: 2rem 2.5rem;
    margin-bottom: 2rem;
}
.selector-label {
    font-size: 0.85rem;
    font-weight: 600;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: #c0a96e;
    margin-bottom: 0.6rem;
}

/* Stats bar */
.stats-bar {
    display: flex;
    gap: 2.5rem;
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 14px;
    padding: 1.2rem 2rem;
    margin-bottom: 2rem;
}
.stat { text-align: center; }
.stat-val { font-size: 2rem; font-weight: 800; color: #c0a96e; }
.stat-lbl { font-size: 0.78rem; color: #777; text-transform: uppercase; letter-spacing: 1px; }

/* Group card */
.group-card {
    background: rgba(255,255,255,0.025);
    border: 1px solid rgba(192,169,110,0.18);
    border-radius: 14px;
    padding: 1.2rem 1.5rem 0.5rem 1.5rem;
    margin-bottom: 2rem;
}
.group-title {
    font-size: 1.1rem;
    font-weight: 600;
    color: #c0a96e;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

/* Not ready banner */
.not-ready {
    background: rgba(255,180,0,0.06);
    border: 1px solid rgba(255,180,0,0.25);
    border-radius: 12px;
    padding: 1.5rem 2rem;
    color: #f0c060;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------
# Paths
# -----------------------------------------------------------------------
app_dir      = Path(__file__).parent.resolve()
manifest_dir = app_dir / "precomputed"

# -----------------------------------------------------------------------
# Hero header
# -----------------------------------------------------------------------
st.markdown('<div class="hero-title">🪨 Stone Tile Cluster Viewer</div>', unsafe_allow_html=True)
# st.markdown('<div class="hero-sub">Browse pre-computed visual similarity groups — no processing required.</div>', unsafe_allow_html=True)

# -----------------------------------------------------------------------
# Check if manifests exist
# -----------------------------------------------------------------------
if not manifest_dir.exists() or not any(manifest_dir.iterdir()):
    st.markdown("""
    <div class="not-ready">
        <b>⚠️ Pre-computed results not found.</b><br><br>
        Run the pre-processing script once to generate the results:<br><br>
        <code>./stonex-venv/bin/python stone_clustering_app/preprocess_results.py</code>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# -----------------------------------------------------------------------
# Discover available stone categories (subfolders that have results.json)
# -----------------------------------------------------------------------
available = sorted([
    d.name for d in manifest_dir.iterdir()
    if d.is_dir() and (d / "results.json").exists()
])

if not available:
    st.warning("No processed categories found. Run `preprocess_results.py` first.")
    st.stop()

# -----------------------------------------------------------------------
# Category selector
# -----------------------------------------------------------------------
# st.markdown('<div class="selector-wrap">', unsafe_allow_html=True)
st.markdown('<div class="selector-label">Select Stone Category</div>', unsafe_allow_html=True)

selected_category = st.selectbox(
    label="stone_category",
    options=available,
    label_visibility="collapsed",
    index=0,
)
st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------------------------------------------------
# Load manifest for selected category
# -----------------------------------------------------------------------
manifest_path = manifest_dir / selected_category / "results.json"

with open(manifest_path, "r") as f:
    manifest = json.load(f)

groups        = manifest.get("groups", {})
total_images  = manifest.get("total_images", 0)
num_groups    = manifest.get("num_groups", 0)
threshold     = manifest.get("threshold", "—")
processed_at  = manifest.get("processed_at", "—")

# -----------------------------------------------------------------------
# Stats bar
# -----------------------------------------------------------------------
st.markdown(f"""
<div class="stats-bar">
    <div class="stat">
        <div class="stat-val">{num_groups}</div>
        <div class="stat-lbl">Groups Found</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.divider()

# -----------------------------------------------------------------------
# Display groups
# -----------------------------------------------------------------------
if not groups:
    st.info("No cluster groups found in the manifest for this category.")
    st.stop()

for group_key in sorted(groups.keys(), key=lambda x: int(x) if str(x).isdigit() else x):
    image_paths = groups[group_key]
    valid_paths = []
    for p in image_paths:
        if 'precomputed_output' in p:
            rel_part = p[p.index('precomputed_output'):]
            local_path = app_dir / rel_part
            if local_path.exists():
                valid_paths.append(str(local_path))
        elif Path(p).exists():
            valid_paths.append(p)
    
    missing = len(image_paths) - len(valid_paths)

    st.markdown(f"""
    <div class="group-card">
        📦 Group {group_key}
    </div>
    """, unsafe_allow_html=True)

    if not valid_paths:
        st.warning(f"All images for Group {group_key} are missing from disk.")
        continue

    cols = st.columns(4)
    for idx, img_path in enumerate(valid_paths):
        with cols[idx % 4]:
            st.image(
                img_path,
                caption=Path(img_path).name,
                use_container_width=True,
            )

    st.markdown("")  # breathing room between groups
