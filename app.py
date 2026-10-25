import streamlit as st
import json
import os
import io
import pandas as pd
import plotly.express as px
from google import genai
from google.genai import types
from fpdf import FPDF

# Page setup
st.set_page_config(
    page_title="PlanCraft AI - Celebration & Event Planner",
    page_icon="🎉",
    layout="wide"
)

# PDF Generation Class
class EventPlanPDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 15)
        self.cell(0, 10, "PlanCraft AI - Official Event Blueprint", border=False, align="C")
        self.ln(7)
        self.set_font("Helvetica", "I", 9)
        self.cell(0, 6, "AI-Generated Strategic Execution Plan", border=False, align="C")
        self.ln(8)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}", border=False, align="C")

def build_pdf_document(plan_data, category, budget, guests, days, theme):
    pdf = EventPlanPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    def clean_text(text):
        return str(text).encode('latin-1', 'replace').decode('latin-1')

    # 1. Executive Summary
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "1. Executive Summary & Parameters", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(95, 6, f"Event Category: {clean_text(category)}", border=0)
    pdf.cell(95, 6, f"Total Budget: INR {budget:,}", border=0, new_x="LMARGIN", new_y="NEXT")
    pdf.cell(95, 6, f"Expected Guests: {guests}", border=0)
    pdf.cell(95, 6, f"Countdown: {days} Days Left", border=0, new_x="LMARGIN", new_y="NEXT")
    pdf.multi_cell(0, 6, f"Theme & Vibe: {clean_text(theme)}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)

    pdf.set_font("Helvetica", "I", 10)
    pdf.multi_cell(0, 5, f"Overview: {clean_text(plan_data.get('event_overview', ''))}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)

    # 2. Budget Allocation
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "2. Budget Allocation", new_x="LMARGIN", new_y="NEXT")
    
    # Table Header
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_fill_color(235, 235, 235)
    pdf.cell(45, 7, "Category", border=1, fill=True)
    pdf.cell(28, 7, "Amount (INR)", border=1, fill=True)
    pdf.cell(22, 7, "Share (%)", border=1, fill=True)
    pdf.cell(95, 7, "Practical Tip", border=1, fill=True, new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("Helvetica", "", 8)
    for b in plan_data.get("budget_breakdown", []):
        cat = clean_text(b.get("category", ""))
        amt = f"{b.get('amount', 0):,}"
        pct = f"{b.get('percentage', 0)}%"
        tip = clean_text(b.get("practical_tip", ""))

        pdf.cell(45, 6, cat[:24], border=1)
        pdf.cell(28, 6, amt, border=1)
        pdf.cell(22, 6, pct, border=1)
        pdf.cell(95, 6, tip[:65], border=1, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)

    # 3. Milestone Timeline & Schedule
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "3. Milestone Timeline & Schedule", new_x="LMARGIN", new_y="NEXT")
    for phase in plan_data.get("milestone_timeline", []):
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(0, 6, f"[{clean_text(phase.get('phase', ''))}]", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 9)
        for task in phase.get("tasks", []):
            pdf.multi_cell(0, 5, f"  * [ ] {clean_text(task)}", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(2)
    pdf.ln(3)

    # 4. Vendor Checklists
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "4. Vendor Due Diligence Checklists", new_x="LMARGIN", new_y="NEXT")
    for vendor in plan_data.get("vendor_checklists", []):
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(0, 6, f"Vendor Type: {clean_text(vendor.get('vendor_type', ''))}", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 9)
        deliv = clean_text(vendor.get('deliverables', ''))
        pdf.multi_cell(0, 5, f"Deliverables: {deliv}", new_x="LMARGIN", new_y="NEXT")
        
        questions = vendor.get("key_questions_to_ask", [])
        if isinstance(questions, list):
            for q in questions:
                pdf.multi_cell(0, 5, f"  - {clean_text(q)}", new_x="LMARGIN", new_y="NEXT")
        elif isinstance(questions, str):
            pdf.multi_cell(0, 5, f"  - {clean_text(questions)}", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(2)
    pdf.ln(3)

    # 5. Personalized Ideas
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "5. Personalized Creative Concepts", new_x="LMARGIN", new_y="NEXT")
    for idea in plan_data.get("personalized_ideas", []):
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(0, 6, f"{clean_text(idea.get('title', ''))} ({clean_text(idea.get('category', ''))})", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 9)
        pdf.multi_cell(0, 5, clean_text(idea.get('details', '')), new_x="LMARGIN", new_y="NEXT")
        pdf.ln(2)

    return bytes(pdf.output())

# Initialize Gemini Client
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    st.sidebar.warning("GEMINI_API_KEY environment variable not found. Enter your key below.")
    api_key = st.sidebar.text_input("Enter Gemini API Key:", type="password")

client = genai.Client(api_key=api_key) if api_key else None

st.title("PlanCraft AI - Smart Celebration & Event Planner")
st.markdown("Gemini-powered end-to-end planning assistant for Weddings, Birthdays, and Community Events.")

# --- SIDEBAR INPUTS ---
st.sidebar.header("Event Parameters")

event_type = st.sidebar.selectbox(
    "Event Category",
    ["Wedding", "Birthday Party", "Community Meetup / Fest", "Anniversary Celebration", "Corporate Gala"]
)

total_budget = st.sidebar.number_input(
    "Total Budget (INR)",
    min_value=5000,
    max_value=10000000,
    value=50000,
    step=5000
)

guest_count = st.sidebar.number_input(
    "Expected Guests",
    min_value=5,
    max_value=2000,
    value=100,
    step=10
)

timeline_days = st.sidebar.slider(
    "Days Left Until Event",
    min_value=1,
    max_value=180,
    value=30
)

theme_vibe = st.sidebar.text_input(
    "Theme / Vibe / Style",
    value="Minimalist, Eco-friendly with live acoustic music"
)

special_notes = st.sidebar.text_area(
    "Specific Constraints / Requirements",
    value="Vegetarian food preferred, indoor hall setup, need return gift ideas"
)

generate_btn = st.sidebar.button("Generate Event Plan", type="primary")

# --- PROMPT FUNCTION ---
def generate_event_plan(category, budget, guests, days, theme, notes):
    system_instruction = (
        "You are an expert event planner specializing in weddings, birthdays, and community gatherings. "
        "Create an actionable, highly structured, realistic event plan based on user budget and constraints. "
        "Strictly calculate the budget breakdown so that allocated amounts sum up to the total budget. "
        "Return the result ONLY as a valid JSON object matching the requested schema."
    )

    user_prompt = f"""
    Event Category: {category}
    Total Budget: {budget} INR
    Expected Guests: {guests}
    Timeline Available: {days} days
    Theme/Vibe: {theme}
    Additional Notes: {notes}

    Generate a complete celebration blueprint in JSON with the following structure:
    {{
      "event_overview": "Brief summary of the concept and experience",
      "budget_breakdown": [
        {{"category": "Venue & Logistics", "amount": 0, "percentage": 0, "practical_tip": "Cost saving tip"}},
        {{"category": "Food & Catering", "amount": 0, "percentage": 0, "practical_tip": "Cost saving tip"}},
        {{"category": "Decor & Ambiance", "amount": 0, "percentage": 0, "practical_tip": "Cost saving tip"}},
        {{"category": "Entertainment & Photography", "amount": 0, "percentage": 0, "practical_tip": "Cost saving tip"}},
        {{"category": "Contingency & Miscellaneous", "amount": 0, "percentage": 0, "practical_tip": "Cost saving tip"}}
      ],
      "milestone_timeline": [
        {{"phase": "Early Planning Phase", "tasks": ["task 1", "task 2"]}},
        {{"phase": "Mid Execution Phase", "tasks": ["task 3", "task 4"]}},
        {{"phase": "Final 48 Hours", "tasks": ["task 5", "task 6"]}},
        {{"phase": "Event Day Run-Down", "tasks": ["task 7", "task 8"]}}
      ],
      "vendor_checklists": [
        {{"vendor_type": "Catering", "key_questions_to_ask": ["question 1", "question 2"], "deliverables": "Deliverable description"}},
        {{"vendor_type": "Venue Manager", "key_questions_to_ask": ["question 1", "question 2"], "deliverables": "Deliverable description"}},
        {{"vendor_type": "Photographer", "key_questions_to_ask": ["question 1", "question 2"], "deliverables": "Deliverable description"}}
      ],
      "personalized_ideas": [
        {{"title": "Idea Name", "category": "Decor / Activity / Souvenir", "details": "Practical step to implement"}}
      ]
    }}
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=user_prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            response_mime_type="application/json",
            temperature=0.3
        )
    )
    return json.loads(response.text)

# --- APP WORKFLOW ---
if generate_btn:
    if not client:
        st.error("Please enter a valid Gemini API Key to proceed.")
    else:
        with st.spinner("Analyzing parameters and synthesizing event blueprint with Gemini..."):
            try:
                plan = generate_event_plan(event_type, total_budget, guest_count, timeline_days, theme_vibe, special_notes)
                st.session_state["event_plan"] = plan
                st.success("Event plan generated successfully!")
            except Exception as e:
                st.error(f"Error generating plan: {str(e)}")

# --- DISPLAY PLAN OUTPUT ---
if "event_plan" in st.session_state:
    data = st.session_state["event_plan"]

    st.info(f"**Event Concept:** {data.get('event_overview', '')}")

    tab1, tab2, tab3, tab4 = st.tabs([
        "Budget Planner",
        "Timelines & Schedule",
        "Vendor Checklist",
        "Personalized Ideas"
    ])

    # Tab 1: Budget
    with tab1:
        st.subheader("Budget Allocation & Cost Optimization")
        budget_list = data.get("budget_breakdown", [])
        if budget_list:
            df_budget = pd.DataFrame(budget_list)
            col1, col2 = st.columns([1.2, 1])

            with col1:
                st.dataframe(
                    df_budget[["category", "amount", "percentage", "practical_tip"]],
                    column_config={
                        "category": "Category",
                        "amount": st.column_config.NumberColumn("Allocated (INR)", format="%d"),
                        "percentage": st.column_config.NumberColumn("Share (%)", format="%d%%"),
                        "practical_tip": "Cost Saving Tip"
                    },
                    use_container_width=True,
                    hide_index=True
                )

            with col2:
                fig = px.pie(
                    df_budget,
                    values="amount",
                    names="category",
                    hole=0.4,
                    title="Budget Distribution"
                )
                fig.update_layout(margin=dict(l=20, r=20, t=40, b=20))
                st.plotly_chart(fig, use_container_width=True)

    # Tab 2: Timelines
    with tab2:
        st.subheader("Event Countdown & Phase Roadmap")
        timeline_list = data.get("milestone_timeline", [])
        for item in timeline_list:
            with st.expander(f"📍 {item.get('phase', 'Phase')}", expanded=True):
                for task in item.get("tasks", []):
                    st.checkbox(task, key=f"task_{task[:15]}_{item.get('phase', '')}")

    # Tab 3: Vendor Checklist
    with tab3:
        st.subheader("Vendor Due Diligence & Requirements")
        vendor_list = data.get("vendor_checklists", [])
        for v in vendor_list:
            st.markdown(f"### 📦 {v.get('vendor_type')}")
            st.write(f"**Expected Deliverables:** {v.get('deliverables')}")
            st.write("**Key Questions to Ask Before Booking:**")
            for q in v.get("key_questions_to_ask", []):
                st.markdown(f"- [ ] {q}")
            st.divider()

    # Tab 4: Ideas
    with tab4:
        st.subheader("Curated Creative Touchpoints")
        ideas_list = data.get("personalized_ideas", [])
        cols = st.columns(len(ideas_list) if 0 < len(ideas_list) <= 3 else 3)
        for idx, idea in enumerate(ideas_list):
            with cols[idx % 3]:
                st.markdown(f"#### 🌟 {idea.get('title')}")
                st.caption(f"Category: {idea.get('category')}")
                st.write(idea.get("details"))

    # Direct PDF Download Button
    st.divider()
    try:
        pdf_bytes = build_pdf_document(
            plan_data=data,
            category=event_type,
            budget=total_budget,
            guests=guest_count,
            days=timeline_days,
            theme=theme_vibe
        )

        st.download_button(
            label="📄 Download Event Blueprint (PDF)",
            data=pdf_bytes,
            file_name="PlanCraft_Event_Blueprint.pdf",
            mime="application/pdf"
        )
    except Exception as pdf_err:
        st.error(f"Error compiling PDF: {str(pdf_err)}")

