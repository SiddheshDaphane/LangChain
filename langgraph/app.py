"""
Utility Bill Verification - Agentic AI Demo
============================================
A simplified demo of the agentic extraction → verification → anomaly → scoring → routing pipeline.
Run: streamlit run app.py
"""

import streamlit as st
import json
import time
import random
# import google.generativeai as genai  # Uncomment when using Gemini
# import PIL.Image  # Uncomment when using Gemini

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="Utility Bill Verification Agent",
    page_icon="⚡",
    layout="wide",
)

# ============================================================
# CUSTOM CSS
# ============================================================
st.markdown("""
<style>
    .main-header { font-size: 28px; font-weight: 700; color: #FF9900; margin-bottom: 0; }
    .sub-header { font-size: 14px; color: #AAAAAA; margin-top: 0; }
    .phase-header { font-size: 18px; font-weight: 600; color: #FF9900; border-left: 4px solid #FF9900; padding-left: 10px; margin: 20px 0 10px 0; }
    .metric-card { background: rgba(255,255,255,0.05); border-radius: 8px; padding: 12px 16px; border-left: 4px solid; margin: 4px 0; }
    .confidence-high { color: #4ADE80; font-weight: 700; }
    .confidence-mid { color: #FBBF24; font-weight: 700; }
    .confidence-low { color: #F87171; font-weight: 700; }
    .tier-badge { display: inline-block; padding: 6px 16px; border-radius: 20px; font-weight: 700; font-size: 14px; }
    .tier1 { background: rgba(74,222,128,0.15); color: #4ADE80; }
    .tier2 { background: rgba(251,191,36,0.15); color: #FBBF24; }
    .tier3 { background: rgba(248,113,113,0.15); color: #F87171; }
    .agent-thought { background: rgba(139,92,246,0.12); border-radius: 8px; padding: 10px 14px; margin: 6px 0; font-size: 13px; border-left: 3px solid #8B5CF6; color: #D4BFFF; }
    .tool-call { background: rgba(45,212,191,0.12); border-radius: 8px; padding: 10px 14px; margin: 6px 0; font-size: 13px; border-left: 3px solid #2DD4BF; color: #99F6E4; }
    .self-heal { background: rgba(251,146,60,0.12); border-radius: 8px; padding: 10px 14px; margin: 6px 0; font-size: 13px; border-left: 3px solid #FB923C; color: #FED7AA; }
    .stProgress > div > div > div > div { background-color: #FF9900; }
</style>
""", unsafe_allow_html=True)


# ============================================================
# DUMMY DATA - SIMULATING BDA EXTRACTION
# ============================================================
SAMPLE_BILLS = {
    "Clean Digital PDF (High Confidence)": {
        "file_type": "Digital PDF",
        "extraction": {
            "provider": {"value": "Duke Energy", "confidence": 0.97},
            "amount": {"value": "$142.50", "confidence": 0.95},
            "due_date": {"value": "2025-04-15", "confidence": 0.99},
            "account_number": {"value": "ACC-78234", "confidence": 0.96},
            "consumption": {"value": "1,200 kWh", "confidence": 0.93},
        },
        "customer_match": "full",  # full, partial, not_found
        "historical_avg": 135.00,
        "bill_amount_numeric": 142.50,
    },
    "Scanned Bill (Medium Confidence)": {
        "file_type": "Scanned PDF",
        "extraction": {
            "provider": {"value": "Con Edison", "confidence": 0.88},
            "amount": {"value": "$287.30", "confidence": 0.72},
            "due_date": {"value": "2025-05-01", "confidence": 0.91},
            "account_number": {"value": "CE-991204", "confidence": 0.85},
            "consumption": {"value": "2,450 kWh", "confidence": 0.78},
        },
        "customer_match": "partial",
        "historical_avg": 120.00,
        "bill_amount_numeric": 287.30,
    },
    "Blurry Phone Photo (Low Confidence)": {
        "file_type": "JPEG Image",
        "extraction": {
            "provider": {"value": "Pacific Gas", "confidence": 0.65},
            "amount": {"value": "$89.??", "confidence": 0.38},
            "due_date": {"value": "2025-??-20", "confidence": 0.42},
            "account_number": {"value": "PG-?????", "confidence": 0.30},
            "consumption": {"value": "??? kWh", "confidence": 0.25},
        },
        "customer_match": "not_found",
        "historical_avg": 95.00,
        "bill_amount_numeric": 89.00,
    },
    "Anomalous Bill (3x Higher)": {
        "file_type": "Digital PDF",
        "extraction": {
            "provider": {"value": "Florida Power", "confidence": 0.98},
            "amount": {"value": "$487.60", "confidence": 0.97},
            "due_date": {"value": "2025-06-01", "confidence": 0.99},
            "account_number": {"value": "FPL-55678", "confidence": 0.96},
            "consumption": {"value": "4,100 kWh", "confidence": 0.94},
        },
        "customer_match": "full",
        "historical_avg": 155.00,
        "bill_amount_numeric": 487.60,
    },
}

# ============================================================
# GEMINI EXTRACTION (COMMENTED OUT - UNCOMMENT TO USE)
# ============================================================
# def extract_with_gemini(uploaded_file):
#     """
#     Call Gemini API to extract fields from an uploaded bill.
#     Set your API key: export GOOGLE_API_KEY=your_key
#     """
#     genai.configure(api_key="YOUR_API_KEY_HERE")
#     model = genai.GenerativeModel("gemini-1.5-flash")
#
#     image = PIL.Image.open(uploaded_file)
#
#     prompt = """
#     You are a utility bill extraction agent. Extract the following fields from this bill image.
#     Return ONLY valid JSON, no markdown, no explanation.
#
#     {
#       "provider": {"value": "string", "confidence": 0.0-1.0},
#       "amount": {"value": "string with $", "confidence": 0.0-1.0},
#       "due_date": {"value": "YYYY-MM-DD", "confidence": 0.0-1.0},
#       "account_number": {"value": "string", "confidence": 0.0-1.0},
#       "consumption": {"value": "string with unit", "confidence": 0.0-1.0}
#     }
#
#     If a field is unclear or unreadable, set confidence below 0.5.
#     Be honest about confidence - blurry or partially visible fields should have low confidence.
#     """
#
#     response = model.generate_content([prompt, image])
#     text = response.text.strip()
#     # Clean potential markdown wrapping
#     if text.startswith("```"):
#         text = text.split("\n", 1)[1].rsplit("```", 1)[0]
#     return json.loads(text)


# ============================================================
# CORE LOGIC FUNCTIONS
# ============================================================

FIELD_WEIGHTS = {
    "amount": 0.35,
    "due_date": 0.25,
    "account_number": 0.20,
    "provider": 0.10,
    "consumption": 0.10,
}

def compute_extraction_score(extraction):
    """Weighted extraction confidence score."""
    score = 0
    for field, weight in FIELD_WEIGHTS.items():
        score += extraction[field]["confidence"] * weight
    return score

def get_verification_multiplier(match_type):
    """Verification multiplier based on customer match."""
    return {"full": 1.0, "partial": 0.7, "not_found": 0.3}[match_type]

def get_anomaly_multiplier(bill_amount, historical_avg):
    """Anomaly multiplier based on Z-score approximation."""
    if historical_avg == 0:
        return 1.0
    ratio = bill_amount / historical_avg
    if ratio <= 1.5:
        return 1.0  # normal
    elif ratio <= 3.0:
        return 0.8  # mild anomaly
    else:
        return 0.5  # severe anomaly

def get_anomaly_label(multiplier):
    if multiplier == 1.0:
        return "Normal", "🟢"
    elif multiplier == 0.8:
        return "Mild anomaly", "🟡"
    else:
        return "Severe anomaly", "🔴"

def compute_composite_score(extraction_score, verification_mult, anomaly_mult):
    return extraction_score * verification_mult * anomaly_mult

def get_tier(composite_score):
    if composite_score >= 0.95:
        return 1, "Auto-Approve", "tier1"
    elif composite_score >= 0.75:
        return 2, "Light HITL Review", "tier2"
    else:
        return 3, "Full HITL Review", "tier3"

def confidence_class(conf):
    if conf >= 0.85:
        return "confidence-high"
    elif conf >= 0.60:
        return "confidence-mid"
    else:
        return "confidence-low"

def simulate_self_heal(extraction):
    """Simulate self-healing cascade for low-confidence fields."""
    healed = {}
    attempts = []
    for field, data in extraction.items():
        if data["confidence"] < 0.85:
            # Step 1: Re-prompt
            new_conf = min(data["confidence"] + random.uniform(0.08, 0.15), 0.99)
            attempts.append(f"🔄 **Re-prompt** for `{field}`: {data['confidence']:.0%} → {new_conf:.0%}")
            if new_conf >= 0.85:
                healed[field] = {"value": data["value"], "confidence": round(new_conf, 2)}
                continue

            # Step 2: Switch model
            new_conf2 = min(new_conf + random.uniform(0.05, 0.12), 0.99)
            attempts.append(f"🔀 **Switch model** for `{field}`: {new_conf:.0%} → {new_conf2:.0%}")
            if new_conf2 >= 0.85:
                healed[field] = {"value": data["value"], "confidence": round(new_conf2, 2)}
                continue

            # Step 3: Enhance image
            new_conf3 = min(new_conf2 + random.uniform(0.03, 0.10), 0.99)
            attempts.append(f"🖼️ **Enhance image** for `{field}`: {new_conf2:.0%} → {new_conf3:.0%}")
            healed[field] = {"value": data["value"], "confidence": round(new_conf3, 2)}
        else:
            healed[field] = data
    return healed, attempts


# ============================================================
# UI
# ============================================================

st.markdown('<p class="main-header">⚡ Utility Bill Verification Agent</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Agentic AI Demo — Single Agent, Multiple Tool Groups — ReAct Pattern</p>', unsafe_allow_html=True)
st.markdown("---")

# Sidebar
with st.sidebar:
    st.markdown("### 📋 Select a Test Scenario")
    scenario = st.selectbox(
        "Choose a bill type:",
        list(SAMPLE_BILLS.keys()),
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.markdown("### ⚙️ Configuration")
    extraction_threshold = st.slider("Extraction confidence threshold", 0.5, 1.0, 0.85, 0.05)
    auto_approve_threshold = st.slider("Auto-approve composite threshold", 0.7, 1.0, 0.95, 0.05)
    enable_self_heal = st.checkbox("Enable self-healing cascade", value=True)

    st.markdown("---")
    st.markdown("### 📂 Or Upload a Bill")
    uploaded_file = st.file_uploader("Upload PDF/Image", type=["pdf", "jpg", "jpeg", "png"])
    if uploaded_file:
        st.info("To process uploads, uncomment the Gemini section in the code and add your API key.")

    st.markdown("---")
    st.markdown("### 🏗️ Architecture")
    st.markdown("""
    **Single Bedrock Agent** with:
    - 🔍 Extraction tools (BDA)
    - ✅ Verification tools (DynamoDB)
    - 📊 Anomaly tools (Z-score)
    - 📚 Knowledge Base (RAG)

    **Control flow** by Step Functions
    (deterministic, not LLM-decided)
    """)

run = st.button("🚀 Run Agent Pipeline", type="primary", use_container_width=True)

if run:
    bill = SAMPLE_BILLS[scenario]

    # ============================================================
    # PHASE 1: RECEIVE & CLASSIFY
    # ============================================================
    st.markdown('<p class="phase-header">Phase 1 — Receive & Classify</p>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    col1.metric("File Type", bill["file_type"])
    col2.metric("Scenario", scenario.split("(")[0].strip())
    col3.metric("Dedup Check", "✅ New bill")

    st.markdown(f'<div class="agent-thought">🧠 <b>Agent thinks:</b> This is a <b>{bill["file_type"]}</b>. I\'ll pass the S3 key to BDA with utility bill blueprint.</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="tool-call">🔧 <b>Tool call:</b> BDA.extract(s3_key="bills/sample_{scenario.lower().replace(" ", "_")}", blueprint="utility_bill_v1")</div>', unsafe_allow_html=True)

    progress = st.progress(0)
    for i in range(25):
        time.sleep(0.02)
        progress.progress(i + 1)

    # ============================================================
    # PHASE 2: EXTRACTION RESULTS
    # ============================================================
    st.markdown('<p class="phase-header">Phase 2 — Extraction Results (BDA)</p>', unsafe_allow_html=True)

    extraction = bill["extraction"]

    # Show extraction table
    cols = st.columns(5)
    for i, (field, data) in enumerate(extraction.items()):
        with cols[i]:
            conf = data["confidence"]
            css_class = confidence_class(conf)
            icon = "🟢" if conf >= 0.85 else ("🟡" if conf >= 0.60 else "🔴")
            st.markdown(f"""
            <div class="metric-card" style="border-color: {'#1A9C3E' if conf >= 0.85 else ('#ED8B00' if conf >= 0.60 else '#D13212')}">
                <div style="font-size: 11px; color: #94A3B8; text-transform: uppercase;">{field.replace('_', ' ')}</div>
                <div style="font-size: 16px; font-weight: 600; color: #E2E8F0; margin: 4px 0;">{data['value']}</div>
                <div class="{css_class}">{icon} {conf:.0%}</div>
            </div>
            """, unsafe_allow_html=True)

    extraction_score = compute_extraction_score(extraction)
    st.markdown(f'<div class="agent-thought">🧠 <b>Agent observes:</b> Weighted extraction score = <b>{extraction_score:.1%}</b></div>', unsafe_allow_html=True)

    for i in range(25, 40):
        time.sleep(0.02)
        progress.progress(i + 1)

    # ============================================================
    # PHASE 2.5: SELF-HEALING (if needed)
    # ============================================================
    low_conf_fields = [f for f, d in extraction.items() if d["confidence"] < extraction_threshold]

    if low_conf_fields and enable_self_heal:
        st.markdown('<p class="phase-header">Phase 2.5 — Self-Healing Cascade</p>', unsafe_allow_html=True)
        st.markdown(f'<div class="agent-thought">🧠 <b>Agent thinks:</b> Fields below {extraction_threshold:.0%} threshold: <b>{", ".join(low_conf_fields)}</b>. Entering self-heal cascade.</div>', unsafe_allow_html=True)

        healed_extraction, heal_attempts = simulate_self_heal(extraction)

        for attempt in heal_attempts:
            st.markdown(f'<div class="self-heal">{attempt}</div>', unsafe_allow_html=True)
            time.sleep(0.3)

        # Check if healing was enough
        still_low = [f for f, d in healed_extraction.items() if d["confidence"] < extraction_threshold]
        if still_low:
            st.warning(f"⚠️ Fields still below threshold after 3 retries: {', '.join(still_low)}")
        else:
            st.success("✅ Self-healing successful! All fields now above threshold.")

        extraction = healed_extraction
        extraction_score = compute_extraction_score(extraction)
        st.markdown(f'<div class="agent-thought">🧠 <b>Agent observes:</b> Updated extraction score = <b>{extraction_score:.1%}</b></div>', unsafe_allow_html=True)

    elif low_conf_fields and not enable_self_heal:
        st.markdown('<p class="phase-header">Phase 2.5 — Self-Healing (Disabled)</p>', unsafe_allow_html=True)
        st.info(f"Self-healing disabled. Fields below threshold: {', '.join(low_conf_fields)}")

    for i in range(40, 55):
        time.sleep(0.02)
        progress.progress(i + 1)

    # ============================================================
    # PHASE 3: VERIFICATION
    # ============================================================
    st.markdown('<p class="phase-header">Phase 3 — Verification (DynamoDB)</p>', unsafe_allow_html=True)

    st.markdown(f'<div class="tool-call">🔧 <b>Tool call:</b> DynamoDB.query(account="{extraction["account_number"]["value"]}")</div>', unsafe_allow_html=True)

    match_type = bill["customer_match"]
    ver_mult = get_verification_multiplier(match_type)

    match_display = {
        "full": ("✅ Full match", "Customer found. Provider, address, account all match.", "#4ADE80"),
        "partial": ("🟡 Partial match", "Customer found but address differs. Provider matches.", "#FBBF24"),
        "not_found": ("🔴 Not found", "No customer record for this account. Fuzzy search returned 0 close matches.", "#F87171"),
    }

    icon, desc, color = match_display[match_type]
    st.markdown(f"""
    <div class="metric-card" style="border-color: {color}">
        <div style="font-size: 16px; font-weight: 600; color: {color};">{icon}</div>
        <div style="font-size: 13px; color: #CBD5E1; margin-top: 4px;">{desc}</div>
        <div style="font-size: 13px; color: {color}; margin-top: 4px;">Verification multiplier: <b>{ver_mult}</b></div>
    </div>
    """, unsafe_allow_html=True)

    for i in range(55, 70):
        time.sleep(0.02)
        progress.progress(i + 1)

    # ============================================================
    # PHASE 4: ANOMALY DETECTION
    # ============================================================
    st.markdown('<p class="phase-header">Phase 4 — Anomaly Detection</p>', unsafe_allow_html=True)

    st.markdown(f'<div class="tool-call">🔧 <b>Tool call:</b> Lambda.fetch_history(account="{extraction["account_number"]["value"]}", months=6)</div>', unsafe_allow_html=True)

    anomaly_mult = get_anomaly_multiplier(bill["bill_amount_numeric"], bill["historical_avg"])
    anomaly_label, anomaly_icon = get_anomaly_label(anomaly_mult)
    ratio = bill["bill_amount_numeric"] / bill["historical_avg"] if bill["historical_avg"] > 0 else 0

    col1, col2, col3 = st.columns(3)
    col1.metric("Current Bill", f"${bill['bill_amount_numeric']:.2f}")
    col2.metric("6-Month Average", f"${bill['historical_avg']:.2f}")
    col3.metric("Ratio", f"{ratio:.1f}x", delta=f"{anomaly_icon} {anomaly_label}")

    st.markdown(f'<div class="agent-thought">🧠 <b>Agent observes:</b> Bill is <b>{ratio:.1f}x</b> the historical average. Classification: <b>{anomaly_label}</b>. Anomaly multiplier: <b>{anomaly_mult}</b></div>', unsafe_allow_html=True)

    for i in range(70, 85):
        time.sleep(0.02)
        progress.progress(i + 1)

    # ============================================================
    # PHASE 5: COMPOSITE SCORING & ROUTING
    # ============================================================
    st.markdown('<p class="phase-header">Phase 5 — Composite Scoring & Tier Routing</p>', unsafe_allow_html=True)

    composite = compute_composite_score(extraction_score, ver_mult, anomaly_mult)

    # Show formula
    st.markdown(f"""
    <div class="agent-thought">
        🧠 <b>Computing composite score:</b><br>
        &nbsp;&nbsp;&nbsp; Extraction: <b>{extraction_score:.1%}</b> × Verification: <b>{ver_mult}</b> × Anomaly: <b>{anomaly_mult}</b> = <b>{composite:.1%}</b>
    </div>
    """, unsafe_allow_html=True)

    tier_num, tier_label, tier_class = get_tier(composite)

    # Big result display
    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown(f"""
        <div style="background: rgba(255,255,255,0.06); border-radius: 12px; padding: 20px; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.08);">
            <div style="font-size: 13px; color: #94A3B8; text-transform: uppercase;">Composite Score</div>
            <div style="font-size: 48px; font-weight: 700; color: {'#1A9C3E' if composite >= 0.95 else ('#ED8B00' if composite >= 0.75 else '#D13212')};">{composite:.1%}</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        tier_colors = {"tier1": ("rgba(74,222,128,0.12)", "#4ADE80"), "tier2": ("rgba(251,191,36,0.12)", "#FBBF24"), "tier3": ("rgba(248,113,113,0.12)", "#F87171")}
        bg, fg = tier_colors[tier_class]
        st.markdown(f"""
        <div style="background: {bg}; border-radius: 12px; padding: 20px; text-align: center; border: 2px solid {fg};">
            <div style="font-size: 13px; color: #94A3B8; text-transform: uppercase;">Routing Decision</div>
            <div style="font-size: 28px; font-weight: 700; color: {fg};">Tier {tier_num}</div>
            <div style="font-size: 14px; color: {fg}; margin-top: 4px;">{tier_label}</div>
        </div>
        """, unsafe_allow_html=True)

    progress.progress(100)

    # ============================================================
    # PHASE 6: NEXT STEPS
    # ============================================================
    st.markdown('<p class="phase-header">Phase 6 — Output</p>', unsafe_allow_html=True)

    if tier_num == 1:
        st.success("✅ Bill auto-approved → Written to DynamoDB → EventBridge `bill.verified` event emitted → Downstream triggered")
    elif tier_num == 2:
        st.warning("🟡 Bill sent to Amazon A2I light review queue. Reviewer will see extracted data with low-confidence fields highlighted.")
        if st.button("👤 Simulate HITL Review (Approve)", key="hitl_approve"):
            st.success("✅ Human approved → Bill verified → Written to DynamoDB → Downstream triggered")
            st.info("📝 Human correction stored in S3 for BDA blueprint refinement")
    else:
        st.error("🔴 Bill sent to full manual review. Senior reviewer will see agent reasoning trace + fuzzy customer matches.")
        if st.button("👤 Simulate HITL Review (Correct & Approve)", key="hitl_correct"):
            st.success("✅ Human corrected and approved → Bill verified → Written to DynamoDB → Downstream triggered")
            st.info("📝 Human correction stored in S3 for BDA blueprint refinement + Knowledge Base update")

    # ============================================================
    # AGENT TRACE LOG (collapsible)
    # ============================================================
    with st.expander("📋 Full Agent Reasoning Trace (for debugging)"):
        trace = {
            "bill_id": f"BILL-{random.randint(10000, 99999)}",
            "scenario": scenario,
            "file_type": bill["file_type"],
            "extraction_score": round(extraction_score, 4),
            "verification": {"match_type": match_type, "multiplier": ver_mult},
            "anomaly": {"ratio": round(ratio, 2), "label": anomaly_label, "multiplier": anomaly_mult},
            "composite_score": round(composite, 4),
            "tier": tier_num,
            "tier_label": tier_label,
            "self_heal_triggered": bool(low_conf_fields),
            "fields": {k: {"value": v["value"], "confidence": v["confidence"]} for k, v in extraction.items()},
        }
        st.json(trace)