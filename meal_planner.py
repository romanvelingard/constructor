import streamlit as st
import pandas as pd
import random
import os
import json

# Page configuration
st.set_page_config(
    page_title="Premium Food Planner & Shopping List",
    page_icon="📅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling for Premium Aesthetics
st.markdown("""
<style>
    /* Styling variables and layout details */
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    /* Header Container styling */
    .title-container {
        background: rgba(255, 255, 255, 0.85);
        backdrop-filter: blur(10px);
        padding: 2rem;
        border-radius: 16px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.5);
        margin-bottom: 2rem;
    }
    
    /* Custom Card Design */
    .card {
        background: rgba(255, 255, 255, 0.9);
        border-radius: 12px;
        padding: 1.2rem;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.7);
        margin-bottom: 1rem;
    }
    
    /* Metrics display */
    .metric-value {
        font-size: 2.2rem;
        font-weight: 800;
        color: #2E5BFF;
        margin: 0;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin: 0;
    }
    
    .badge {
        display: inline-block;
        padding: 0.35em 0.65em;
        font-size: 85%;
        font-weight: 700;
        line-height: 1;
        text-align: center;
        white-space: nowrap;
        vertical-align: baseline;
        border-radius: 9999px;
        color: #fff;
        margin-top: 10px;
    }
    .badge-protein {
        background-color: #3B82F6;
    }
</style>
""", unsafe_allow_html=True)

# Cache translation loading to optimize performance
@st.cache_data
def load_translations(lang_code):
    path = os.path.join("locales", f"{lang_code}.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        # Fallback to prevent app crashes if file is missing/corrupted
        return {
            "ui": {}, "foods": {}, "days": {}, "category_display": {}
        }

# Initialize Session State Language
if 'lang' not in st.session_state:
    st.session_state.lang = 'ru'

lang = st.session_state.lang
translations = load_translations(lang)

# Localization Helpers
def _t(key):
    return translations.get("ui", {}).get(key, key)

def translate_food(key):
    return translations.get("foods", {}).get(key, key)

# 2. State Management & Initial Database
# We define keys in English internally to remain language-independent
if 'proteins_db' not in st.session_state or 'Turkey' not in st.session_state.proteins_db:
    st.session_state.proteins_db = {
        'Turkey': 25.0, 'Chicken': 24.0, 'Fish': 21.0, 'Beef': 26.0, 
        'Liver': 20.0, 'Tuna': 22.0, 'Sardines': 23.0, 'Beans': 8.0, 'Cottage Cheese': 15.0,
        'Tofu': 15.0
    }

if 'garnishes_db' not in st.session_state or 'Buckwheat' not in st.session_state.garnishes_db:
    st.session_state.garnishes_db = ['Buckwheat', 'Quinoa', 'Rice', 'Potato', 'Pasta']

if 'snacks_db' not in st.session_state or 'Almonds' not in st.session_state.snacks_db:
    st.session_state.snacks_db = {
        'Almonds': 21.0,
        'Cashews': 18.0,
        'Walnuts': 15.0
    }

# Active week pool state bindings (references English keys)
if 'active_proteins' not in st.session_state or not all(k in st.session_state.proteins_db for k in st.session_state.active_proteins):
    st.session_state.active_proteins = list(st.session_state.proteins_db.keys())[:7]

if 'active_garnishes' not in st.session_state or not all(k in st.session_state.garnishes_db for k in st.session_state.active_garnishes):
    st.session_state.active_garnishes = st.session_state.garnishes_db[:4]

if 'active_snacks' not in st.session_state or not all(k in st.session_state.snacks_db for k in st.session_state.active_snacks):
    st.session_state.active_snacks = list(st.session_state.snacks_db.keys())

if 'checked_groceries' not in st.session_state:
    st.session_state.checked_groceries = set()

days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

# Preload/upgrade initial plan using English keys
if 'meal_plan' not in st.session_state or 'Monday' not in st.session_state.meal_plan or 'Завтрак' not in st.session_state.meal_plan['Monday']:
    st.session_state.meal_plan = {
        day: {
            "Завтрак": {"protein": "Cottage Cheese", "garnish": "None"},
            "Обед": {"protein": "Chicken", "garnish": "Buckwheat"},
            "Ужин": {"protein": "Turkey", "garnish": "Rice"},
            "Снэк": {"snack": "Almonds"}
        } for day in days_of_week
    }

# Modal Dialog Function
@st.dialog(_t('dialog_title'))
def add_product_dialog():
    category_options = ["Proteins", "Garnish", "Snack"]
    
    category = st.selectbox(
        _t('type_label'), 
        category_options, 
        format_func=lambda x: translations.get("category_display", {}).get(x, x)
    )
    name = st.text_input(_t('name_label'), placeholder=_t('name_placeholder'))
    
    # Enable double/float input for protein density
    protein_density = st.number_input(
        _t('protein_density_label'), 
        min_value=0.0, 
        max_value=100.0, 
        value=15.0, 
        step=0.5, 
        format="%.1f",
        disabled=(category == "Garnish")
    )
    
    if st.button(_t('save_btn'), use_container_width=True):
        clean_name = name.strip()
        if clean_name:
            if category == "Proteins":
                st.session_state.proteins_db[clean_name] = protein_density
                if clean_name not in st.session_state.active_proteins:
                    st.session_state.active_proteins.append(clean_name)
            elif category == "Snack":
                st.session_state.snacks_db[clean_name] = protein_density
                if clean_name not in st.session_state.active_snacks:
                    st.session_state.active_snacks.append(clean_name)
            else:
                if clean_name not in st.session_state.garnishes_db:
                    st.session_state.garnishes_db.append(clean_name)
                if clean_name not in st.session_state.active_garnishes:
                    st.session_state.active_garnishes.append(clean_name)
            st.success(_t('success_added_msg').format(name=clean_name))
            st.rerun()
        else:
            st.error(_t('error_empty_name'))

# 3. Sidebar Controls
with st.sidebar:
    st.header(_t('actions_header'))
    
    # Language Selector Toggle
    lang_choices = {"ru": "🇷🇺 Русский", "en": "🇬🇧 English"}
    lang_val = st.selectbox(
        _t('lang_label'), 
        options=list(lang_choices.keys()), 
        format_func=lambda x: lang_choices[x],
        index=0 if lang == 'ru' else 1
    )
    if lang_val != st.session_state.lang:
        st.session_state.lang = lang_val
        st.rerun()
        
    st.divider()
    
    # Dialog Trigger Button
    if st.button(_t('add_product_btn'), use_container_width=True, type="primary"):
        add_product_dialog()
        
    st.divider()
    
    # Portions
    st.subheader(_t('portion_header'))
    protein_portion = st.slider(_t('protein_portion_label'), min_value=50, max_value=400, value=150, step=10)
    garnish_portion = st.slider(_t('garnish_portion_label'), min_value=30, max_value=300, value=80, step=5)
    snack_portion = st.slider(_t('snack_portion_label'), min_value=10, max_value=150, value=30, step=5)
    
    st.divider()
    
    st.subheader(_t('goals_header'))
    target_protein = st.slider(_t('target_protein_label'), min_value=50, max_value=250, value=130, step=5)
    
    # Extra shopping list notes
    st.subheader(_t('additional_list_header'))
    extra_items_input = st.text_area(_t('additional_list_header'), 
                                    placeholder=_t('additional_placeholder'),
                                    label_visibility="collapsed")

# 4. Header Title
st.markdown(f"""
<div class="title-container">
    <h1 style="margin:0; font-size:2.5rem; color:#1e293b; font-weight:800;">{_t('title')}</h1>
    <p style="margin:0.5rem 0 0 0; color:#64748b; font-size:1.1rem;">{_t('subtitle')}</p>
</div>
""", unsafe_allow_html=True)

# 5. Multiselect for active week pool (from the database)
col_sel1, col_sel2, col_sel3 = st.columns(3)
with col_sel1:
    selected_proteins = st.multiselect(
        _t('select_proteins_label'), 
        options=list(st.session_state.proteins_db.keys()),
        key="active_proteins",
        format_func=translate_food
    )
with col_sel2:
    selected_garnishes = st.multiselect(
        _t('select_garnishes_label'), 
        options=st.session_state.garnishes_db,
        key="active_garnishes",
        format_func=translate_food
    )
with col_sel3:
    selected_snacks = st.multiselect(
        _t('select_snacks_label'),
        options=list(st.session_state.snacks_db.keys()),
        key="active_snacks",
        format_func=translate_food
    )

# Prepare lists for selection
active_proteins_options = ["None"] + st.session_state.active_proteins
active_garnishes_options = ["None"] + st.session_state.active_garnishes
active_snacks_options = ["None"] + st.session_state.active_snacks

# Main Workspace Tabs
tab_menu, tab_list, tab_stats = st.tabs([
    _t('tab_menu'), 
    _t('tab_list'), 
    _t('tab_stats')
])

# ---- TAB 1: WEEKLY PLANNER ----
with tab_menu:
    col_mon, col_tue, col_wed, col_thu = st.columns(4)
    col_fri, col_sat, col_sun, col_act = st.columns(4)
    
    days_cols = {
        "Monday": col_mon,
        "Tuesday": col_tue,
        "Wednesday": col_wed,
        "Thursday": col_thu,
        "Friday": col_fri,
        "Saturday": col_sat,
        "Sunday": col_sun
    }
    
    for day, col in days_cols.items():
        with col:
            with st.container(border=True):
                # Localized day name
                st.markdown(f"### 📅 {translations.get('days', {}).get(day, day)}")
                
                # Check for breakfast selections
                stored_break_p = st.session_state.meal_plan[day]["Завтрак"]["protein"]
                stored_break_g = st.session_state.meal_plan[day]["Завтрак"]["garnish"]
                
                break_p_idx = active_proteins_options.index(stored_break_p) if stored_break_p in active_proteins_options else 0
                break_g_idx = active_garnishes_options.index(stored_break_g) if stored_break_g in active_garnishes_options else 0
                
                st.markdown(f"**{_t('breakfast')}**")
                break_p = st.selectbox(f"Протеин (Завтрак)##{day}", active_proteins_options, index=break_p_idx, format_func=translate_food, label_visibility="collapsed")
                break_g = st.selectbox(f"Гарнир (Завтрак)##{day}", active_garnishes_options, index=break_g_idx, format_func=translate_food, label_visibility="collapsed")
                
                # Check for lunch selections
                stored_lunch_p = st.session_state.meal_plan[day]["Обед"]["protein"]
                stored_lunch_g = st.session_state.meal_plan[day]["Обед"]["garnish"]
                
                lunch_p_idx = active_proteins_options.index(stored_lunch_p) if stored_lunch_p in active_proteins_options else 0
                lunch_g_idx = active_garnishes_options.index(stored_lunch_g) if stored_lunch_g in active_garnishes_options else 0
                
                st.markdown(f"**{_t('lunch')}**")
                lunch_p = st.selectbox(f"Протеин (Обед)##{day}", active_proteins_options, index=lunch_p_idx, format_func=translate_food, label_visibility="collapsed")
                lunch_g = st.selectbox(f"Гарнир (Обед)##{day}", active_garnishes_options, index=lunch_g_idx, format_func=translate_food, label_visibility="collapsed")
                
                # Check for dinner selections
                stored_dinner_p = st.session_state.meal_plan[day]["Ужин"]["protein"]
                stored_dinner_g = st.session_state.meal_plan[day]["Ужин"]["garnish"]
                
                dinner_p_idx = active_proteins_options.index(stored_dinner_p) if stored_dinner_p in active_proteins_options else 0
                dinner_g_idx = active_garnishes_options.index(stored_dinner_g) if stored_dinner_g in active_garnishes_options else 0
                
                st.markdown(f"**{_t('dinner')}**")
                dinner_p = st.selectbox(f"Протеин (Ужин)##{day}", active_proteins_options, index=dinner_p_idx, format_func=translate_food, label_visibility="collapsed")
                dinner_g = st.selectbox(f"Гарнир (Ужин)##{day}", active_garnishes_options, index=dinner_g_idx, format_func=translate_food, label_visibility="collapsed")
                
                # Check for snack selections
                stored_snack_s = st.session_state.meal_plan[day]["Снэк"]["snack"]
                snack_s_idx = active_snacks_options.index(stored_snack_s) if stored_snack_s in active_snacks_options else 0
                
                st.markdown(f"**{_t('snack')}**")
                snack_s = st.selectbox(f"Снэк (Перекус)##{day}", active_snacks_options, index=snack_s_idx, format_func=translate_food, label_visibility="collapsed")
                
                # Save choice to session state
                st.session_state.meal_plan[day]["Завтрак"]["protein"] = break_p
                st.session_state.meal_plan[day]["Завтрак"]["garnish"] = break_g
                st.session_state.meal_plan[day]["Обед"]["protein"] = lunch_p
                st.session_state.meal_plan[day]["Обед"]["garnish"] = lunch_g
                st.session_state.meal_plan[day]["Ужин"]["protein"] = dinner_p
                st.session_state.meal_plan[day]["Ужин"]["garnish"] = dinner_g
                st.session_state.meal_plan[day]["Снэк"]["snack"] = snack_s
                
                # Calculate daily protein content
                day_protein = 0
                for meal_type in ["Завтрак", "Обед", "Ужин"]:
                    p = st.session_state.meal_plan[day][meal_type]["protein"]
                    if p != "None" and p in st.session_state.proteins_db:
                        day_protein += (protein_portion / 100) * st.session_state.proteins_db[p]
                
                s = st.session_state.meal_plan[day]["Снэк"]["snack"]
                if s != "None" and s in st.session_state.snacks_db:
                    day_protein += (snack_portion / 100) * st.session_state.snacks_db[s]
                
                st.markdown(f"<span class='badge badge-protein'>{_t('chart_y_label')}: {day_protein:.1f} g</span>" if lang == 'en' else f"<span class='badge badge-protein'>Белок: {day_protein:.1f} г</span>", unsafe_allow_html=True)
                
    # Quick Actions inside col_act
    with col_act:
        with st.container(border=True):
            st.markdown(_t('quick_actions_header'))
            
            if st.button(_t('autofill_btn'), use_container_width=True):
                for day in days_of_week:
                    st.session_state.meal_plan[day]["Завтрак"]["protein"] = random.choice(st.session_state.active_proteins) if st.session_state.active_proteins else "None"
                    st.session_state.meal_plan[day]["Завтрак"]["garnish"] = random.choice(st.session_state.active_garnishes) if st.session_state.active_garnishes else "None"
                    st.session_state.meal_plan[day]["Обед"]["protein"] = random.choice(st.session_state.active_proteins) if st.session_state.active_proteins else "None"
                    st.session_state.meal_plan[day]["Обед"]["garnish"] = random.choice(st.session_state.active_garnishes) if st.session_state.active_garnishes else "None"
                    st.session_state.meal_plan[day]["Ужин"]["protein"] = random.choice(st.session_state.active_proteins) if st.session_state.active_proteins else "None"
                    st.session_state.meal_plan[day]["Ужин"]["garnish"] = random.choice(st.session_state.active_garnishes) if st.session_state.active_garnishes else "None"
                    st.session_state.meal_plan[day]["Снэк"]["snack"] = random.choice(st.session_state.active_snacks) if st.session_state.active_snacks else "None"
                st.rerun()
                
            if st.button(_t('copy_mon_btn'), use_container_width=True):
                mon_plan = st.session_state.meal_plan["Monday"]
                for day in days_of_week[1:]:
                    st.session_state.meal_plan[day] = {
                        "Завтрак": mon_plan["Завтрак"].copy(),
                        "Обед": mon_plan["Обед"].copy(),
                        "Ужин": mon_plan["Ужин"].copy(),
                        "Снэк": mon_plan["Снэк"].copy()
                    }
                st.rerun()
                
            if st.button(_t('clear_menu_btn'), use_container_width=True):
                for day in days_of_week:
                    st.session_state.meal_plan[day]["Завтрак"]["protein"] = "None"
                    st.session_state.meal_plan[day]["Завтрак"]["garnish"] = "None"
                    st.session_state.meal_plan[day]["Обед"]["protein"] = "None"
                    st.session_state.meal_plan[day]["Обед"]["garnish"] = "None"
                    st.session_state.meal_plan[day]["Ужин"]["protein"] = "None"
                    st.session_state.meal_plan[day]["Ужин"]["garnish"] = "None"
                    st.session_state.meal_plan[day]["Снэк"]["snack"] = "None"
                st.rerun()

# ---- TAB 2: SHOPPING LIST ----
with tab_list:
    st.markdown(_t('shopping_list_title'))
    st.write(_t('shopping_list_desc'))
    
    # Aggregate quantities
    shopping_proteins = {}
    shopping_garnishes = {}
    shopping_snacks = {}
    
    for day in days_of_week:
        for meal in ["Завтрак", "Обед", "Ужин"]:
            p = st.session_state.meal_plan[day][meal]["protein"]
            g = st.session_state.meal_plan[day][meal]["garnish"]
            
            if p != "None" and p in st.session_state.proteins_db:
                shopping_proteins[p] = shopping_proteins.get(p, 0) + protein_portion
            if g != "None" and g in st.session_state.garnishes_db:
                shopping_garnishes[g] = shopping_garnishes.get(g, 0) + garnish_portion
                
        s = st.session_state.meal_plan[day]["Снэк"]["snack"]
        if s != "None" and s in st.session_state.snacks_db:
            shopping_snacks[s] = shopping_snacks.get(s, 0) + snack_portion

    # Parse extra items
    extra_items_list = []
    if extra_items_input:
        extra_items_list = [item.strip() for item in extra_items_input.split(",") if item.strip()]

    # Layout: two columns for display and text copy
    col_check, col_raw = st.columns([2, 1])
    
    unit_g = 'г' if lang == 'ru' else 'g'
    
    with col_check:
        st.markdown(_t('checklist_header'))
        
        has_items = False
        
        # Display Proteins
        if shopping_proteins:
            has_items = True
            st.markdown(_t('shopping_proteins_section'))
            for item, weight in shopping_proteins.items():
                item_label = f"{translate_food(item)} — {weight} {unit_g}"
                item_key = f"chk_protein_{item}_{weight}"
                is_checked = item_key in st.session_state.checked_groceries
                
                if st.checkbox(item_label, value=is_checked, key=item_key):
                    st.session_state.checked_groceries.add(item_key)
                else:
                    st.session_state.checked_groceries.discard(item_key)
        
        # Display Garnishes
        if shopping_garnishes:
            has_items = True
            st.markdown(_t('shopping_garnishes_section'))
            for item, weight in shopping_garnishes.items():
                item_label = f"{translate_food(item)} — {weight} {unit_g}"
                item_key = f"chk_garnish_{item}_{weight}"
                is_checked = item_key in st.session_state.checked_groceries
                
                if st.checkbox(item_label, value=is_checked, key=item_key):
                    st.session_state.checked_groceries.add(item_key)
                else:
                    st.session_state.checked_groceries.discard(item_key)
                    
        # Display Snacks
        if shopping_snacks:
            has_items = True
            st.markdown(_t('shopping_snacks_section'))
            for item, weight in shopping_snacks.items():
                item_label = f"{translate_food(item)} — {weight} {unit_g}"
                item_key = f"chk_snack_{item}_{weight}"
                is_checked = item_key in st.session_state.checked_groceries
                
                if st.checkbox(item_label, value=is_checked, key=item_key):
                    st.session_state.checked_groceries.add(item_key)
                else:
                    st.session_state.checked_groceries.discard(item_key)
                    
        # Display Extras
        if extra_items_list:
            has_items = True
            st.markdown(_t('shopping_extras_section'))
            for i, item in enumerate(extra_items_list):
                item_key = f"chk_extra_{item}_{i}"
                is_checked = item_key in st.session_state.checked_groceries
                
                if st.checkbox(item, value=is_checked, key=item_key):
                    st.session_state.checked_groceries.add(item_key)
                else:
                    st.session_state.checked_groceries.discard(item_key)
                    
        if not has_items:
            st.info(_t('empty_shopping_list_info'))
            
    with col_raw:
        st.markdown(_t('raw_text_header'))
        # Build text string
        raw_text = f"🛒 {_t('shopping_list_title').replace('### ', '').strip().upper()}\n"
        raw_text += "===========================\n\n"
        if shopping_proteins:
            raw_text += f"🥩 {_t('shopping_proteins_section').replace('##### ', '').strip().upper()}:\n"
            for item, weight in shopping_proteins.items():
                raw_text += f"- {translate_food(item)}: {weight} {unit_g}\n"
            raw_text += "\n"
        if shopping_garnishes:
            raw_text += f"🌾 GАРНИРЫ:\n" if lang == 'ru' else f"🌾 GARNISHES:\n"
            for item, weight in shopping_garnishes.items():
                raw_text += f"- {translate_food(item)}: {weight} {unit_g}\n"
            raw_text += "\n"
        if shopping_snacks:
            raw_text += f"🥨 {_t('shopping_snacks_section').replace('##### ', '').strip().upper()}:\n"
            for item, weight in shopping_snacks.items():
                raw_text += f"- {translate_food(item)}: {weight} {unit_g}\n"
            raw_text += "\n"
        if extra_items_list:
            raw_text += f"🥗 {_t('shopping_extras_section').replace('##### ', '').strip().upper()}:\n"
            for item in extra_items_list:
                raw_text += f"- {item}\n"
            raw_text += "\n"
        
        st.text_area(_t('copy_text_area_label'), value=raw_text, height=280)
        st.caption(_t('copy_instructions'))

# ---- TAB 3: STATISTICS & ANALYTICS ----
with tab_stats:
    st.markdown(_t('stats_title'))
    
    # Calculations
    total_weekly_p = 0
    daily_protein_data = []
    
    for day in days_of_week:
        day_p = 0
        for meal in ["Завтрак", "Обед", "Ужин"]:
            p = st.session_state.meal_plan[day][meal]["protein"]
            if p != "None" and p in st.session_state.proteins_db:
                day_p += (protein_portion / 100) * st.session_state.proteins_db[p]
        
        s = st.session_state.meal_plan[day]["Снэк"]["snack"]
        if s != "None" and s in st.session_state.snacks_db:
            day_p += (snack_portion / 100) * st.session_state.snacks_db[s]
            
        total_weekly_p += day_p
        
        # Localize day name for index display
        localized_day = translations.get("days", {}).get(day, day)
        daily_protein_data.append({_t('day_label_column'): localized_day, _t('chart_y_label'): round(day_p, 1)})
        
    avg_daily_p = total_weekly_p / 7
    progress = min(1.0, avg_daily_p / target_protein) if target_protein > 0 else 0.0
    
    # Metric cards display
    col_stat1, col_stat2, col_stat3 = st.columns(3)
    
    with col_stat1:
        st.markdown(f"""
        <div class="card">
            <p class="metric-value">{avg_daily_p:.1f} {unit_g}</p>
            <p class="metric-label">{_t('stat_card_avg')}</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col_stat2:
        st.markdown(f"""
        <div class="card">
            <p class="metric-value">{progress*100:.0f}%</p>
            <p class="metric-label">{_t('stat_card_goal')} ({target_protein}{unit_g})</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col_stat3:
        st.markdown(f"""
        <div class="card">
            <p class="metric-value">{total_weekly_p:.1f} {unit_g}</p>
            <p class="metric-label">{_t('stat_card_total')}</p>
        </div>
        """, unsafe_allow_html=True)
        
    # Progress bar and status feedback
    st.markdown(_t('progress_bar_header'))
    st.progress(progress)
    
    if avg_daily_p >= target_protein:
        st.success(_t('success_goal_msg').format(avg=avg_daily_p, target=target_protein))
    elif avg_daily_p >= target_protein * 0.8:
        st.warning(_t('warning_goal_msg').format(avg=avg_daily_p, percent=progress*100, target=target_protein))
    else:
        st.error(_t('error_goal_msg').format(avg=avg_daily_p, target=target_protein))
        
    # Chart
    st.markdown(_t('chart_header'))
    df_daily = pd.DataFrame(daily_protein_data)
    st.bar_chart(df_daily.set_index(_t('day_label_column')))

st.divider()
st.caption(_t('footer_caption'))