import streamlit as st
import pandas as pd
import random
import os
import json
import db

class DBWrapper:
    @property
    def uid(self):
        return st.session_state.user_id

    def _get_cache(self):
        if 'db_cache' not in st.session_state:
            st.session_state.db_cache = {}
        return st.session_state.db_cache

    def _clear_cache(self, prefix=None):
        cache = self._get_cache()
        cache.clear()

    def get_foods_by_category(self, cat):
        return db_original.get_foods_by_category(cat)

    def get_all_food_macros(self):
        return db_original.get_all_food_macros()

    def add_food_to_db(self, *args, **kwargs):
        return db_original.add_food_to_db(*args, **kwargs)

    def get_meal_plan_from_db(self):
        return db_original.get_meal_plan_from_db(self.uid)

    def update_meal_plan_in_db(self, day, meal_type, food_name, garnish_name=None):
        return db_original.update_meal_plan_in_db(self.uid, day, meal_type, food_name, garnish_name)

    def get_checked_groceries_from_db(self):
        return db_original.get_checked_groceries_from_db(self.uid)

    def set_grocery_checked_state(self, item_key, is_checked):
        return db_original.set_grocery_checked_state(self.uid, item_key, is_checked)

    def get_setting_value(self, key, default):
        return db_original.get_setting_value(self.uid, key, default)

    def update_setting_value(self, key, value):
        return db_original.update_setting_value(self.uid, key, value)

    def get_weight_history(self):
        cache = self._get_cache()
        key = ("get_weight_history",)
        if key not in cache:
            cache[key] = db_original.get_weight_history(self.uid)
        return cache[key]

    def add_weight_entry(self, date_str, weight):
        self._clear_cache("get_weight_history")
        return db_original.add_weight_entry(self.uid, date_str, weight)

    def delete_weight_entry(self, date_str):
        self._clear_cache("get_weight_history")
        return db_original.delete_weight_entry(self.uid, date_str)

    def get_injection_history(self):
        cache = self._get_cache()
        key = ("get_injection_history",)
        if key not in cache:
            cache[key] = db_original.get_injection_history(self.uid)
        return cache[key]

    def add_injection_entry(self, date_str, medication, dose):
        self._clear_cache("get_injection_history")
        return db_original.add_injection_entry(self.uid, date_str, medication, dose)

    def delete_injection_entry(self, entry_id):
        self._clear_cache("get_injection_history")
        return db_original.delete_injection_entry(self.uid, entry_id)

    def get_food_log(self, date_str):
        cache = self._get_cache()
        key = ("get_food_log", date_str)
        if key not in cache:
            cache[key] = db_original.get_food_log(self.uid, date_str)
        return cache[key]

    def add_food_log_entry(self, date_str, meal_type, food_name, garnish_name, food_portion, garnish_portion, protein_density=0.0, carbs_density=0.0, fat_density=0.0):
        self._clear_cache("get_food_log")
        self._clear_cache("get_actual_intake_in_range")
        return db_original.add_food_log_entry(self.uid, date_str, meal_type, food_name, garnish_name, food_portion, garnish_portion, protein_density, carbs_density, fat_density)

    def delete_food_log_entry(self, entry_id):
        self._clear_cache("get_food_log")
        self._clear_cache("get_actual_intake_in_range")
        return db_original.delete_food_log_entry(self.uid, entry_id)

    def get_actual_intake_in_range(self, start_date_str, end_date_str):
        cache = self._get_cache()
        key = ("get_actual_intake_in_range", start_date_str, end_date_str)
        if key not in cache:
            cache[key] = db_original.get_actual_intake_in_range(self.uid, start_date_str, end_date_str)
        return cache[key]

    def get_profile_value(self, key, default=""):
        return db_original.get_profile_value(self.uid, key, default)

    def update_profile_value(self, key, value):
        return db_original.update_profile_value(self.uid, key, value)

    def verify_user(self, email, password):
        return db_original.verify_user(email, password)

    def change_user_password(self, new_password):
        return db_original.change_user_password(self.uid, new_password)

    def init_db(self):
        return db_original.init_db()

db_original = db
db = DBWrapper()

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
    st.session_state.lang = 'en'

lang = st.session_state.lang
translations = load_translations(lang)

# Localization Helpers
def _t(key):
    return translations.get("ui", {}).get(key, key)

def translate_food(key):
    return translations.get("foods", {}).get(key, key)

# 2. State Management & Initial Database
# We define keys in English internally to remain language-independent
if 'db_initialized' not in st.session_state:
    db.init_db()
    st.session_state.db_initialized = True

# Login Screen logic
if 'authenticated' not in st.session_state or not st.session_state.authenticated:
    col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
    with col_l2:
        with st.container(border=True):
            st.markdown(f"<h2 style='text-align: center;'>{_t('login_title')}</h2>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align: center; color: #64748b;'>{_t('login_subtitle')}</p>", unsafe_allow_html=True)
            
            email_input = st.text_input(_t('email_label'), key="login_email_input")
            password_input = st.text_input(_t('password_label'), type="password", key="login_password_input")
            
            if st.button(_t('login_button'), use_container_width=True, type="primary"):
                user_info = db.verify_user(email_input, password_input)
                if user_info:
                    st.session_state.user_id = user_info[0]
                    st.session_state.user_email = user_info[1]
                    st.session_state.authenticated = True
                    # Load saved language from DB if available
                    st.session_state.lang = db.get_setting_value('lang', 'en')
                    # Reset db_loaded to force reloading user specific values
                    if 'db_loaded' in st.session_state:
                        del st.session_state.db_loaded
                    st.rerun()
                else:
                    st.error(_t('login_error'))
    st.stop()

if 'db_loaded' not in st.session_state:
    st.session_state.proteins_db = db.get_foods_by_category("Proteins")
    st.session_state.garnishes_db = db.get_foods_by_category("Garnish")
    st.session_state.snacks_db = db.get_foods_by_category("Snack")
    st.session_state.salads_db = db.get_foods_by_category("Salad")
    st.session_state.dressings_db = db.get_foods_by_category("Dressing")
    st.session_state.others_db = db.get_foods_by_category("Other")
    st.session_state.food_macros = db.get_all_food_macros()
    st.session_state.meal_plan = db.get_meal_plan_from_db()
    st.session_state.checked_groceries = db.get_checked_groceries_from_db()
    st.session_state.db_loaded = True

# Load settings from db to session_state
if 'protein_portion' not in st.session_state:
    st.session_state.protein_portion = int(db.get_setting_value('protein_portion', 150.0))
if 'garnish_portion' not in st.session_state:
    st.session_state.garnish_portion = int(db.get_setting_value('garnish_portion', 80.0))
if 'snack_portion' not in st.session_state:
    st.session_state.snack_portion = int(db.get_setting_value('snack_portion', 30.0))
if 'target_protein' not in st.session_state:
    st.session_state.target_protein = int(db.get_setting_value('target_protein', 130.0))
if 'target_carbs' not in st.session_state:
    st.session_state.target_carbs = int(db.get_setting_value('target_carbs', 150.0))
if 'target_fat' not in st.session_state:
    st.session_state.target_fat = int(db.get_setting_value('target_fat', 60.0))

protein_portion = st.session_state.protein_portion
garnish_portion = st.session_state.garnish_portion
snack_portion = st.session_state.snack_portion



if 'profile_username' not in st.session_state:
    st.session_state.profile_username = db.get_profile_value('username', '')
if 'profile_password' not in st.session_state:
    st.session_state.profile_password = db.get_profile_value('password', '')
if 'profile_email' not in st.session_state:
    st.session_state.profile_email = db.get_profile_value('email', '')
if 'profile_gender' not in st.session_state:
    st.session_state.profile_gender = db.get_profile_value('gender', 'Male')

# Active week pool state bindings (references English keys)
if 'active_proteins' not in st.session_state or not all(k in st.session_state.proteins_db for k in st.session_state.active_proteins):
    st.session_state.active_proteins = list(st.session_state.proteins_db)[:7]

if 'active_garnishes' not in st.session_state or not all(k in st.session_state.garnishes_db for k in st.session_state.active_garnishes):
    st.session_state.active_garnishes = st.session_state.garnishes_db[:4]

if 'active_snacks' not in st.session_state or not all(k in st.session_state.snacks_db for k in st.session_state.active_snacks):
    st.session_state.active_snacks = list(st.session_state.snacks_db)


days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

# Modal Dialog Function
@st.dialog(_t('dialog_title'))
def add_product_dialog():
    category_options = ["Proteins", "Garnish", "Snack", "Salad", "Dressing", "Other"]
    
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
    
    # New Carbs and Fat inputs
    carbs_density = st.number_input(
        _t('carbs_density_label'), 
        min_value=0.0, 
        max_value=100.0, 
        value=15.0 if category == "Garnish" else 0.0, 
        step=0.5, 
        format="%.1f"
    )
    
    fat_density = st.number_input(
        _t('fat_density_label'), 
        min_value=0.0, 
        max_value=100.0, 
        value=0.0, 
        step=0.5, 
        format="%.1f"
    )
    
    if st.button(_t('save_btn'), use_container_width=True):
        clean_name = name.strip()
        if clean_name:
            actual_density = 0.0 if category == "Garnish" else protein_density
            success = db.add_food_to_db(clean_name, category, actual_density, carbs_density, fat_density)
            if success:
                if category == "Proteins":
                    if clean_name not in st.session_state.proteins_db:
                        st.session_state.proteins_db.append(clean_name)
                    if clean_name not in st.session_state.active_proteins:
                        st.session_state.active_proteins.append(clean_name)
                elif category == "Snack":
                    if clean_name not in st.session_state.snacks_db:
                        st.session_state.snacks_db.append(clean_name)
                    if clean_name not in st.session_state.active_snacks:
                        st.session_state.active_snacks.append(clean_name)
                elif category == "Garnish":
                    if clean_name not in st.session_state.garnishes_db:
                        st.session_state.garnishes_db.append(clean_name)
                    if clean_name not in st.session_state.active_garnishes:
                        st.session_state.active_garnishes.append(clean_name)
                elif category == "Salad":
                    if clean_name not in st.session_state.salads_db:
                        st.session_state.salads_db.append(clean_name)
                elif category == "Dressing":
                    if clean_name not in st.session_state.dressings_db:
                        st.session_state.dressings_db.append(clean_name)
                elif category == "Other":
                    if clean_name not in st.session_state.others_db:
                        st.session_state.others_db.append(clean_name)
                
                # Update cache
                st.session_state.food_macros[clean_name] = {
                    'protein': actual_density,
                    'carbs': carbs_density,
                    'fat': fat_density
                }
                
                st.success(_t('success_added_msg').format(name=clean_name))
                st.rerun()
            else:
                st.error("This product already exists in the database!")
        else:
            st.error(_t('error_empty_name'))

# 3. Settings Helpers
def update_portion_setting(key):
    db.update_setting_value(key, float(st.session_state[key]))

extra_items_input = st.session_state.get("extra_items_input", "")

# 4. Header Title
st.markdown(f"""
<div class="title-container">
    <h1 style="margin:0; font-size:2.5rem; color:#1e293b; font-weight:800;">{_t('title')}</h1>
    <p style="margin:0.5rem 0 0 0; color:#64748b; font-size:1.1rem;">{_t('subtitle')}</p>
</div>
""", unsafe_allow_html=True)


# Prepare lists for selection
active_proteins_options = ["None"] + st.session_state.active_proteins
active_garnishes_options = ["None"] + st.session_state.active_garnishes
active_snacks_options = ["None"] + st.session_state.active_snacks

# Main Workspace Tabs
tab_log, tab_menu, tab_list, tab_stats, tab_weight, tab_glp1, tab_settings = st.tabs([
    _t('tab_log'), 
    _t('tab_menu'), 
    _t('tab_list'), 
    _t('tab_stats'),
    _t('tab_weight'),
    _t('tab_glp1'),
    _t('tab_settings')
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
                
                # Check for Snack 1 selections
                stored_snack_1 = st.session_state.meal_plan[day]["Снэк 1"]["snack"]
                snack_1_idx = active_snacks_options.index(stored_snack_1) if stored_snack_1 in active_snacks_options else 0
                
                st.markdown(f"**{_t('snack_1')}**")
                snack_1 = st.selectbox(f"Снэк 1##{day}", active_snacks_options, index=snack_1_idx, format_func=translate_food, label_visibility="collapsed")

                # Check for lunch selections
                stored_lunch_p = st.session_state.meal_plan[day]["Обед"]["protein"]
                stored_lunch_g = st.session_state.meal_plan[day]["Обед"]["garnish"]
                
                lunch_p_idx = active_proteins_options.index(stored_lunch_p) if stored_lunch_p in active_proteins_options else 0
                lunch_g_idx = active_garnishes_options.index(stored_lunch_g) if stored_lunch_g in active_garnishes_options else 0
                
                st.markdown(f"**{_t('lunch')}**")
                lunch_p = st.selectbox(f"Протеин (Обед)##{day}", active_proteins_options, index=lunch_p_idx, format_func=translate_food, label_visibility="collapsed")
                lunch_g = st.selectbox(f"Гарнир (Обед)##{day}", active_garnishes_options, index=lunch_g_idx, format_func=translate_food, label_visibility="collapsed")
                
                # Check for Snack 2 selections
                stored_snack_2 = st.session_state.meal_plan[day]["Снэк 2"]["snack"]
                snack_2_idx = active_snacks_options.index(stored_snack_2) if stored_snack_2 in active_snacks_options else 0
                
                st.markdown(f"**{_t('snack_2')}**")
                snack_2 = st.selectbox(f"Снэк 2##{day}", active_snacks_options, index=snack_2_idx, format_func=translate_food, label_visibility="collapsed")

                # Check for dinner selections
                stored_dinner_p = st.session_state.meal_plan[day]["Ужин"]["protein"]
                stored_dinner_g = st.session_state.meal_plan[day]["Ужин"]["garnish"]
                
                dinner_p_idx = active_proteins_options.index(stored_dinner_p) if stored_dinner_p in active_proteins_options else 0
                dinner_g_idx = active_garnishes_options.index(stored_dinner_g) if stored_dinner_g in active_garnishes_options else 0
                
                st.markdown(f"**{_t('dinner')}**")
                dinner_p = st.selectbox(f"Протеин (Ужин)##{day}", active_proteins_options, index=dinner_p_idx, format_func=translate_food, label_visibility="collapsed")
                dinner_g = st.selectbox(f"Гарнир (Ужин)##{day}", active_garnishes_options, index=dinner_g_idx, format_func=translate_food, label_visibility="collapsed")
                
                # Save choice to session state & DB if changed
                if break_p != stored_break_p or break_g != stored_break_g:
                    st.session_state.meal_plan[day]["Завтрак"]["protein"] = break_p
                    st.session_state.meal_plan[day]["Завтрак"]["garnish"] = break_g
                    db.update_meal_plan_in_db(day, "Завтрак", break_p, break_g)
                
                if snack_1 != stored_snack_1:
                    st.session_state.meal_plan[day]["Снэк 1"]["snack"] = snack_1
                    db.update_meal_plan_in_db(day, "Снэк 1", snack_1)

                if lunch_p != stored_lunch_p or lunch_g != stored_lunch_g:
                    st.session_state.meal_plan[day]["Обед"]["protein"] = lunch_p
                    st.session_state.meal_plan[day]["Обед"]["garnish"] = lunch_g
                    db.update_meal_plan_in_db(day, "Обед", lunch_p, lunch_g)
                
                if snack_2 != stored_snack_2:
                    st.session_state.meal_plan[day]["Снэк 2"]["snack"] = snack_2
                    db.update_meal_plan_in_db(day, "Снэк 2", snack_2)

                if dinner_p != stored_dinner_p or dinner_g != stored_dinner_g:
                    st.session_state.meal_plan[day]["Ужин"]["protein"] = dinner_p
                    st.session_state.meal_plan[day]["Ужин"]["garnish"] = dinner_g
                    db.update_meal_plan_in_db(day, "Ужин", dinner_p, dinner_g)
                
                # Calculate daily macronutrient values
                day_protein = 0.0
                day_carbs = 0.0
                day_fat = 0.0

                for meal_type in ["Завтрак", "Обед", "Ужин"]:
                    p = st.session_state.meal_plan[day][meal_type]["protein"]
                    g = st.session_state.meal_plan[day][meal_type]["garnish"]
                    
                    if p != "None" and p in st.session_state.food_macros:
                        day_protein += (protein_portion / 100.0) * st.session_state.food_macros[p]['protein']
                        day_carbs += (protein_portion / 100.0) * st.session_state.food_macros[p]['carbs']
                        day_fat += (protein_portion / 100.0) * st.session_state.food_macros[p]['fat']
                    
                    if g != "None" and g in st.session_state.food_macros:
                        day_protein += (garnish_portion / 100.0) * st.session_state.food_macros[g]['protein']
                        day_carbs += (garnish_portion / 100.0) * st.session_state.food_macros[g]['carbs']
                        day_fat += (garnish_portion / 100.0) * st.session_state.food_macros[g]['fat']

                for snack_type in ["Снэк 1", "Снэк 2"]:
                    s = st.session_state.meal_plan[day][snack_type]["snack"]
                    if s != "None" and s in st.session_state.food_macros:
                        day_protein += (snack_portion / 100.0) * st.session_state.food_macros[s]['protein']
                        day_carbs += (snack_portion / 100.0) * st.session_state.food_macros[s]['carbs']
                        day_fat += (snack_portion / 100.0) * st.session_state.food_macros[s]['fat']

                label_p = 'Protein' if lang == 'en' else 'Белки'
                label_c = 'Carbs' if lang == 'en' else 'Угл'
                label_f = 'Fats' if lang == 'en' else 'Жиры'
                st.markdown(
                    f"<span class='badge badge-protein'>{label_p}: {day_protein:.1f}g | {label_c}: {day_carbs:.1f}g | {label_f}: {day_fat:.1f}g</span>"
                    if lang == 'en' else
                    f"<span class='badge badge-protein'>Б: {day_protein:.1f}г | У: {day_carbs:.1f}г | Ж: {day_fat:.1f}г</span>",
                    unsafe_allow_html=True
                )

                
    # Quick Actions inside col_act
    with col_act:
        with st.container(border=True):
            st.markdown(_t('quick_actions_header'))
            
            if st.button(_t('autofill_btn'), use_container_width=True):
                for day in days_of_week:
                    break_p = random.choice(st.session_state.active_proteins) if st.session_state.active_proteins else "None"
                    break_g = random.choice(st.session_state.active_garnishes) if st.session_state.active_garnishes else "None"
                    snack_1 = random.choice(st.session_state.active_snacks) if st.session_state.active_snacks else "None"
                    lunch_p = random.choice(st.session_state.active_proteins) if st.session_state.active_proteins else "None"
                    lunch_g = random.choice(st.session_state.active_garnishes) if st.session_state.active_garnishes else "None"
                    snack_2 = random.choice(st.session_state.active_snacks) if st.session_state.active_snacks else "None"
                    dinner_p = random.choice(st.session_state.active_proteins) if st.session_state.active_proteins else "None"
                    dinner_g = random.choice(st.session_state.active_garnishes) if st.session_state.active_garnishes else "None"
                    
                    st.session_state.meal_plan[day] = {
                        "Завтрак": {"protein": break_p, "garnish": break_g},
                        "Снэк 1": {"snack": snack_1},
                        "Обед": {"protein": lunch_p, "garnish": lunch_g},
                        "Снэк 2": {"snack": snack_2},
                        "Ужин": {"protein": dinner_p, "garnish": dinner_g}
                    }
                    
                    db.update_meal_plan_in_db(day, "Завтрак", break_p, break_g)
                    db.update_meal_plan_in_db(day, "Снэк 1", snack_1)
                    db.update_meal_plan_in_db(day, "Обед", lunch_p, lunch_g)
                    db.update_meal_plan_in_db(day, "Снэк 2", snack_2)
                    db.update_meal_plan_in_db(day, "Ужин", dinner_p, dinner_g)
                st.rerun()
                
            if st.button(_t('copy_mon_btn'), use_container_width=True):
                mon_plan = st.session_state.meal_plan["Monday"]
                for day in days_of_week[1:]:
                    st.session_state.meal_plan[day] = {
                        "Завтрак": mon_plan["Завтрак"].copy(),
                        "Снэк 1": mon_plan["Снэк 1"].copy(),
                        "Обед": mon_plan["Обед"].copy(),
                        "Снэк 2": mon_plan["Снэк 2"].copy(),
                        "Ужин": mon_plan["Ужин"].copy()
                    }
                    db.update_meal_plan_in_db(day, "Завтрак", mon_plan["Завтрак"]["protein"], mon_plan["Завтрак"]["garnish"])
                    db.update_meal_plan_in_db(day, "Снэк 1", mon_plan["Снэк 1"]["snack"])
                    db.update_meal_plan_in_db(day, "Обед", mon_plan["Обед"]["protein"], mon_plan["Обед"]["garnish"])
                    db.update_meal_plan_in_db(day, "Снэк 2", mon_plan["Снэк 2"]["snack"])
                    db.update_meal_plan_in_db(day, "Ужин", mon_plan["Ужин"]["protein"], mon_plan["Ужин"]["garnish"])
                st.rerun()
                
            if st.button(_t('clear_menu_btn'), use_container_width=True):
                for day in days_of_week:
                    st.session_state.meal_plan[day] = {
                        "Завтрак": {"protein": "None", "garnish": "None"},
                        "Снэк 1": {"snack": "None"},
                        "Обед": {"protein": "None", "garnish": "None"},
                        "Снэк 2": {"snack": "None"},
                        "Ужин": {"protein": "None", "garnish": "None"}
                    }
                    
                    db.update_meal_plan_in_db(day, "Завтрак", "None", "None")
                    db.update_meal_plan_in_db(day, "Снэк 1", "None")
                    db.update_meal_plan_in_db(day, "Обед", "None", "None")
                    db.update_meal_plan_in_db(day, "Снэк 2", "None")
                    db.update_meal_plan_in_db(day, "Ужин", "None", "None")
                st.rerun()



# ---- TAB: FOOD RECORDER & LOG ----
with tab_log:
    st.markdown(_t('log_header'))
    
    # 1. Date and Quick Actions
    col_date, col_action_btn = st.columns([1, 1])
    with col_date:
        log_date = st.date_input(_t('log_date_label'), key="food_log_date_input")
        date_str = log_date.strftime("%Y-%m-%d") if log_date else datetime.date.today().strftime("%Y-%m-%d")
    with col_action_btn:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button(_t('log_copy_plan_btn'), use_container_width=True):
            # Clear existing log entries for this date
            for entry in db.get_food_log(date_str):
                db.delete_food_log_entry(entry['id'])
            
            # Map date to weekday
            day_name = log_date.strftime('%A') if log_date else datetime.date.today().strftime('%A')
            plan_for_day = st.session_state.meal_plan.get(day_name, {})
            
            # Log Breakfast
            br = plan_for_day.get("Завтрак", {})
            br_p = br.get("protein", "None")
            br_g = br.get("garnish", "None")
            if br_p != "None":
                m = st.session_state.food_macros.get(br_p, {'protein': 0.0, 'carbs': 0.0, 'fat': 0.0})
                db.add_food_log_entry(date_str, "Завтрак", br_p, "None", float(st.session_state.protein_portion), 0.0, m['protein'], m['carbs'], m['fat'])
            if br_g != "None":
                m = st.session_state.food_macros.get(br_g, {'protein': 0.0, 'carbs': 0.0, 'fat': 0.0})
                db.add_food_log_entry(date_str, "Завтрак", br_g, "None", float(st.session_state.garnish_portion), 0.0, m['protein'], m['carbs'], m['fat'])
            
            # Log Snack 1
            sn1 = plan_for_day.get("Снэк 1", {})
            sn1_f = sn1.get("snack", "None")
            if sn1_f != "None":
                m = st.session_state.food_macros.get(sn1_f, {'protein': 0.0, 'carbs': 0.0, 'fat': 0.0})
                db.add_food_log_entry(date_str, "Снэк 1", sn1_f, "None", float(st.session_state.snack_portion), 0.0, m['protein'], m['carbs'], m['fat'])
            
            # Log Lunch
            lu = plan_for_day.get("Обед", {})
            lu_p = lu.get("protein", "None")
            lu_g = lu.get("garnish", "None")
            if lu_p != "None":
                m = st.session_state.food_macros.get(lu_p, {'protein': 0.0, 'carbs': 0.0, 'fat': 0.0})
                db.add_food_log_entry(date_str, "Обед", lu_p, "None", float(st.session_state.protein_portion), 0.0, m['protein'], m['carbs'], m['fat'])
            if lu_g != "None":
                m = st.session_state.food_macros.get(lu_g, {'protein': 0.0, 'carbs': 0.0, 'fat': 0.0})
                db.add_food_log_entry(date_str, "Обед", lu_g, "None", float(st.session_state.garnish_portion), 0.0, m['protein'], m['carbs'], m['fat'])
                
            # Log Snack 2
            sn2 = plan_for_day.get("Снэк 2", {})
            sn2_f = sn2.get("snack", "None")
            if sn2_f != "None":
                m = st.session_state.food_macros.get(sn2_f, {'protein': 0.0, 'carbs': 0.0, 'fat': 0.0})
                db.add_food_log_entry(date_str, "Снэк 2", sn2_f, "None", float(st.session_state.snack_portion), 0.0, m['protein'], m['carbs'], m['fat'])
                
            # Log Dinner
            di = plan_for_day.get("Ужин", {})
            di_p = di.get("protein", "None")
            di_g = di.get("garnish", "None")
            if di_p != "None":
                m = st.session_state.food_macros.get(di_p, {'protein': 0.0, 'carbs': 0.0, 'fat': 0.0})
                db.add_food_log_entry(date_str, "Ужин", di_p, "None", float(st.session_state.protein_portion), 0.0, m['protein'], m['carbs'], m['fat'])
            if di_g != "None":
                m = st.session_state.food_macros.get(di_g, {'protein': 0.0, 'carbs': 0.0, 'fat': 0.0})
                db.add_food_log_entry(date_str, "Ужин", di_g, "None", float(st.session_state.garnish_portion), 0.0, m['protein'], m['carbs'], m['fat'])
                
            st.success(_t('log_success_msg'))
            st.rerun()

    st.markdown("---")
    
    # 2. Render meal sections
    meal_type_options = ["Завтрак", "Снэк 1", "Обед", "Снэк 2", "Ужин"]
    def translate_meal_type(m):
        if m == "Завтрак": return _t('breakfast')
        if m == "Снэк 1": return _t('snack_1')
        if m == "Обед": return _t('lunch')
        if m == "Снэк 2": return _t('snack_2')
        if m == "Ужин": return _t('dinner')
        return m

    log_entries = db.get_food_log(date_str)
    all_foods = sorted(list(st.session_state.food_macros.keys()))
    
    # Group logs by meal type
    entries_by_meal = {m: [] for m in meal_type_options}
    for entry in log_entries:
        m_type = entry['meal_type']
        if m_type in entries_by_meal:
            entries_by_meal[m_type].append(entry)
            
    day_total_p = 0.0
    day_total_c = 0.0
    day_total_f = 0.0

    for meal_type in meal_type_options:
        with st.container(border=True):
            st.markdown(f"### {translate_meal_type(meal_type)}")
            
            meal_entries = entries_by_meal[meal_type]
            
            # Show list of entries for this meal
            if meal_entries:
                for entry in meal_entries:
                    f_name = entry['food_name']
                    g_name = entry['garnish_name']
                    f_port = entry['food_portion']
                    g_port = entry['garnish_portion']
                    
                    p_val, c_val, f_val = 0.0, 0.0, 0.0
                    
                    # Compute macros
                    p_density = entry.get('protein_density', 0.0)
                    c_density = entry.get('carbs_density', 0.0)
                    f_density = entry.get('fat_density', 0.0)
                    
                    if p_density == 0.0 and c_density == 0.0 and f_density == 0.0:
                        if f_name != "None" and f_name in st.session_state.food_macros:
                            f_macro = st.session_state.food_macros[f_name]
                            p_density = f_macro['protein']
                            c_density = f_macro['carbs']
                            f_density = f_macro['fat']
                            
                    p_val += p_density * f_port / 100.0
                    c_val += c_density * f_port / 100.0
                    f_val += f_density * f_port / 100.0
                        
                    day_total_p += p_val
                    day_total_c += c_val
                    day_total_f += f_val
                    
                    # Row for the food entry
                    col_item_desc, col_item_macros, col_item_del = st.columns([4, 3, 1])
                    with col_item_desc:
                        desc_parts = []
                        if f_name != "None":
                            desc_parts.append(f"{translate_food(f_name)} ({int(f_port)}g)")
                        if g_name != "None":
                            desc_parts.append(f"{translate_food(g_name)} ({int(g_port)}g)")
                        st.write(" + ".join(desc_parts) if desc_parts else "-")
                    with col_item_macros:
                        st.write(f"P: {p_val:.1f}g | C: {c_val:.1f}g | F: {f_val:.1f}g")
                    with col_item_del:
                        if st.button(_t('delete_btn'), key=f"del_log_{entry['id']}", use_container_width=True):
                            db.delete_food_log_entry(entry['id'])
                            st.rerun()
            else:
                st.info("No items logged" if lang == 'en' else "Нет записанных продуктов")
            
            # Inline mini-form to add item to this meal
            category_options = ["Proteins", "Garnish", "Snack", "Salad", "Dressing", "Other", "Custom"]
            category_trans = {
                "Proteins": translations.get("category_display", {}).get("Proteins", "Proteins"),
                "Garnish": translations.get("category_display", {}).get("Garnish", "Garnish"),
                "Snack": translations.get("category_display", {}).get("Snack", "Snack"),
                "Salad": translations.get("category_display", {}).get("Salad", "Salad"),
                "Dressing": translations.get("category_display", {}).get("Dressing", "Dressing"),
                "Other": translations.get("category_display", {}).get("Other", "Other"),
                "Custom": _t('category_custom')
            }
            
            col_add_cat, col_add_food, col_add_portion, col_add_btn = st.columns([2, 3, 2, 2])
            with col_add_cat:
                selected_cat = st.selectbox(
                    _t('log_type_label'),
                    category_options,
                    format_func=lambda x: category_trans.get(x, x),
                    key=f"add_cat_select_{meal_type}",
                    label_visibility="collapsed"
                )
            
            custom_fields_active = (selected_cat == "Custom")
            
            with col_add_food:
                if custom_fields_active:
                    custom_name = st.text_input(
                        _t('custom_name_label'),
                        placeholder=_t('custom_name_label'),
                        key=f"custom_name_input_{meal_type}",
                        label_visibility="collapsed"
                    )
                    food_select = "Custom"
                else:
                    category_map = {
                        "Proteins": st.session_state.proteins_db,
                        "Garnish": st.session_state.garnishes_db,
                        "Snack": st.session_state.snacks_db,
                        "Salad": st.session_state.salads_db,
                        "Dressing": st.session_state.dressings_db,
                        "Other": st.session_state.others_db
                    }
                    cat_items = category_map.get(selected_cat, [])
                    food_select = st.selectbox(
                        _t('log_item_label'),
                        ["None"] + sorted(list(cat_items)),
                        format_func=translate_food,
                        key=f"add_food_select_{meal_type}",
                        label_visibility="collapsed"
                    )
            
            with col_add_portion:
                default_portion = 150.0
                if meal_type in ["Снэк 1", "Снэк 2"]:
                    default_portion = float(st.session_state.snack_portion)
                elif meal_type in ["Завтрак", "Обед", "Ужин"]:
                    if selected_cat == "Garnish":
                        default_portion = float(st.session_state.garnish_portion)
                    else:
                        default_portion = float(st.session_state.protein_portion)
                        
                food_portion = st.number_input(
                    _t('log_portion_g_label'),
                    min_value=0.0,
                    max_value=1000.0,
                    value=default_portion,
                    step=10.0,
                    key=f"add_portion_input_{meal_type}",
                    label_visibility="collapsed"
                )
            
            # If Custom, display a row underneath for macros inputs
            if custom_fields_active:
                st.markdown("<div style='font-size:0.85rem; color:#64748b; margin-bottom:0.2rem;'>Nutrient Densities (g/100g) / Пищевая ценность (г/100г)</div>", unsafe_allow_html=True)
                col_custom_p, col_custom_c, col_custom_f = st.columns(3)
                with col_custom_p:
                    c_prot = st.number_input(_t('custom_protein_label'), min_value=0.0, max_value=100.0, value=10.0, step=0.5, key=f"custom_prot_{meal_type}")
                with col_custom_c:
                    c_carb = st.number_input(_t('custom_carbs_label'), min_value=0.0, max_value=100.0, value=0.0, step=0.5, key=f"custom_carb_{meal_type}")
                with col_custom_f:
                    c_fat = st.number_input(_t('custom_fat_label'), min_value=0.0, max_value=100.0, value=0.0, step=0.5, key=f"custom_fat_{meal_type}")
            elif food_select != "None":
                default_macros = st.session_state.food_macros.get(food_select, {'protein': 0.0, 'carbs': 0.0, 'fat': 0.0})
                st.markdown("<div style='font-size:0.85rem; color:#64748b; margin-bottom:0.2rem;'>Nutrient Densities (g/100g) / Пищевая ценность (г/100г)</div>", unsafe_allow_html=True)
                col_pred_p, col_pred_c, col_pred_f = st.columns(3)
                with col_pred_p:
                    c_prot = st.number_input(_t('custom_protein_label'), min_value=0.0, max_value=100.0, value=float(default_macros['protein']), step=0.5, key=f"pred_prot_{meal_type}_{food_select}")
                with col_pred_c:
                    c_carb = st.number_input(_t('custom_carbs_label'), min_value=0.0, max_value=100.0, value=float(default_macros['carbs']), step=0.5, key=f"pred_carb_{meal_type}_{food_select}")
                with col_pred_f:
                    c_fat = st.number_input(_t('custom_fat_label'), min_value=0.0, max_value=100.0, value=float(default_macros['fat']), step=0.5, key=f"pred_fat_{meal_type}_{food_select}")
            
            with col_add_btn:
                if st.button(_t('log_add_item_btn'), key=f"add_btn_{meal_type}", use_container_width=True, type="secondary"):
                    if custom_fields_active:
                        clean_custom_name = custom_name.strip()
                        if not clean_custom_name:
                            st.error("Please enter a custom name!" if lang == 'en' else "Введите название продукта!")
                        else:
                            # Save custom food to DB
                            db.add_food_to_db(clean_custom_name, "Other", c_prot, c_carb, c_fat)
                            # Update active cache
                            if clean_custom_name not in st.session_state.others_db:
                                st.session_state.others_db.append(clean_custom_name)
                            st.session_state.food_macros[clean_custom_name] = {
                                'protein': c_prot,
                                'carbs': c_carb,
                                'fat': c_fat
                            }
                            # Log entry
                            db.add_food_log_entry(
                                date_str=date_str,
                                meal_type=meal_type,
                                food_name=clean_custom_name,
                                garnish_name="None",
                                food_portion=food_portion,
                                garnish_portion=0.0,
                                protein_density=c_prot,
                                carbs_density=c_carb,
                                fat_density=c_fat
                            )
                            st.success(_t('log_success_msg'))
                            st.rerun()
                    else:
                        if food_select != "None":
                            db.add_food_log_entry(
                                date_str=date_str,
                                meal_type=meal_type,
                                food_name=food_select,
                                garnish_name="None",
                                food_portion=food_portion,
                                garnish_portion=0.0,
                                protein_density=c_prot,
                                carbs_density=c_carb,
                                fat_density=c_fat
                            )
                            st.success(_t('log_success_msg'))
                            st.rerun()

    st.markdown("---")
    
    # 3. Daily Summary Totals
    unit_g = 'г' if lang == 'ru' else 'g'
    st.markdown(f"#### {'Day Totals' if lang == 'en' else 'Итого за день'}")
    col_t1, col_t2, col_t3 = st.columns(3)
    with col_t1:
        st.markdown(f"""
        <div class="card">
            <p class="metric-value">{day_total_p:.1f} {unit_g}</p>
            <p class="metric-label">{'Protein' if lang == 'en' else 'Белки'}</p>
        </div>
        """, unsafe_allow_html=True)
    with col_t2:
        st.markdown(f"""
        <div class="card">
            <p class="metric-value">{day_total_c:.1f} {unit_g}</p>
            <p class="metric-label">{'Carbs' if lang == 'en' else 'Углеводы'}</p>
        </div>
        """, unsafe_allow_html=True)
    with col_t3:
        st.markdown(f"""
        <div class="card">
            <p class="metric-value">{day_total_f:.1f} {unit_g}</p>
            <p class="metric-label">{'Fats' if lang == 'en' else 'Жиры'}</p>
        </div>
        """, unsafe_allow_html=True)

# ---- TAB 3: SHOPPING LIST ----
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
                
        for snack_type in ["Снэк 1", "Снэк 2"]:
            s = st.session_state.meal_plan[day][snack_type]["snack"]
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
                
                checked = st.checkbox(item_label, value=is_checked, key=item_key)
                if checked != is_checked:
                    if checked:
                        st.session_state.checked_groceries.add(item_key)
                        db.set_grocery_checked_state(item_key, True)
                    else:
                        st.session_state.checked_groceries.discard(item_key)
                        db.set_grocery_checked_state(item_key, False)
        
        # Display Garnishes
        if shopping_garnishes:
            has_items = True
            st.markdown(_t('shopping_garnishes_section'))
            for item, weight in shopping_garnishes.items():
                item_label = f"{translate_food(item)} — {weight} {unit_g}"
                item_key = f"chk_garnish_{item}_{weight}"
                is_checked = item_key in st.session_state.checked_groceries
                
                checked = st.checkbox(item_label, value=is_checked, key=item_key)
                if checked != is_checked:
                    if checked:
                        st.session_state.checked_groceries.add(item_key)
                        db.set_grocery_checked_state(item_key, True)
                    else:
                        st.session_state.checked_groceries.discard(item_key)
                        db.set_grocery_checked_state(item_key, False)
                     
        # Display Snacks
        if shopping_snacks:
            has_items = True
            st.markdown(_t('shopping_snacks_section'))
            for item, weight in shopping_snacks.items():
                item_label = f"{translate_food(item)} — {weight} {unit_g}"
                item_key = f"chk_snack_{item}_{weight}"
                is_checked = item_key in st.session_state.checked_groceries
                
                checked = st.checkbox(item_label, value=is_checked, key=item_key)
                if checked != is_checked:
                    if checked:
                        st.session_state.checked_groceries.add(item_key)
                        db.set_grocery_checked_state(item_key, True)
                    else:
                        st.session_state.checked_groceries.discard(item_key)
                        db.set_grocery_checked_state(item_key, False)
                     
        # Display Extras
        if extra_items_list:
            has_items = True
            st.markdown(_t('shopping_extras_section'))
            for i, item in enumerate(extra_items_list):
                item_key = f"chk_extra_{item}_{i}"
                is_checked = item_key in st.session_state.checked_groceries
                
                checked = st.checkbox(item, value=is_checked, key=item_key)
                if checked != is_checked:
                    if checked:
                        st.session_state.checked_groceries.add(item_key)
                        db.set_grocery_checked_state(item_key, True)
                    else:
                        st.session_state.checked_groceries.discard(item_key)
                        db.set_grocery_checked_state(item_key, False)
                        
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
    import datetime
    today = datetime.date.today()
    
    # 1. Daily Intake Analysis Section
    st.markdown("### 📅 " + ("Daily Actual Intake" if lang == 'en' else "Фактическое потребление за день"))
    selected_day = st.date_input("Select Date" if lang == 'en' else "Выберите дату", today, key="stats_daily_date_input")
    day_str = selected_day.strftime("%Y-%m-%d") if selected_day else today.strftime("%Y-%m-%d")
    
    # Fetch actual log entries for this specific day
    daily_logs = db.get_food_log(day_str)
    
    day_total_p = 0.0
    day_total_c = 0.0
    day_total_f = 0.0
    
    for entry in daily_logs:
        f_name = entry['food_name']
        g_name = entry['garnish_name']
        f_port = entry['food_portion']
        g_port = entry['garnish_portion']
        
        p_density = entry.get('protein_density', 0.0)
        c_density = entry.get('carbs_density', 0.0)
        f_density = entry.get('fat_density', 0.0)
        
        if p_density == 0.0 and c_density == 0.0 and f_density == 0.0:
            if f_name != "None" and f_name in st.session_state.food_macros:
                f_macro = st.session_state.food_macros[f_name]
                p_density = f_macro['protein']
                c_density = f_macro['carbs']
                f_density = f_macro['fat']
                
        day_total_p += p_density * f_port / 100.0
        day_total_c += c_density * f_port / 100.0
        day_total_f += f_density * f_port / 100.0
            
        if g_name != "None" and g_name in st.session_state.food_macros:
            g_macro = st.session_state.food_macros[g_name]
            day_total_p += g_macro['protein'] * g_port / 100.0
            day_total_c += g_macro['carbs'] * g_port / 100.0
            day_total_f += g_macro['fat'] * g_port / 100.0
            
    target_protein = st.session_state.target_protein
    target_carbs = st.session_state.target_carbs
    target_fat = st.session_state.target_fat
    unit_g = 'г' if lang == 'ru' else 'g'
    
    progress_p_day = min(1.0, day_total_p / target_protein) if target_protein > 0 else 0.0
    progress_c_day = min(1.0, day_total_c / target_carbs) if target_carbs > 0 else 0.0
    progress_f_day = min(1.0, day_total_f / target_fat) if target_fat > 0 else 0.0
    
    col_dp, col_dc, col_df = st.columns(3)
    
    with col_dp:
        st.subheader("🥩 " + ("Protein" if lang == 'en' else "Белки"))
        st.markdown(f"""
        <div class="card">
            <p class="metric-value">{day_total_p:.1f} {unit_g}</p>
            <p class="metric-label">{"Protein Intake" if lang == 'en' else "Потребление белка"}</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown(f"**Goal: {target_protein}{unit_g} ({progress_p_day*100:.0f}%)**" if lang == 'en' else f"**Цель: {target_protein}{unit_g} ({progress_p_day*100:.0f}%)**")
        st.progress(progress_p_day)
        if day_total_p >= target_protein:
            st.success("🎉 Met goal!" if lang == 'en' else "🎉 Норма достигнута!")
        elif day_total_p >= target_protein * 0.8:
            st.warning("⚠️ Near goal" if lang == 'en' else "⚠️ Около нормы")
        else:
            st.error("🔴 Below goal" if lang == 'en' else "🔴 Ниже нормы")

    with col_dc:
        st.subheader("🌾 " + ("Carbohydrates" if lang == 'en' else "Углеводы"))
        st.markdown(f"""
        <div class="card">
            <p class="metric-value">{day_total_c:.1f} {unit_g}</p>
            <p class="metric-label">{"Carb Intake" if lang == 'en' else "Потребление углеводов"}</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown(f"**Goal: {target_carbs}{unit_g} ({progress_c_day*100:.0f}%)**" if lang == 'en' else f"**Цель: {target_carbs}{unit_g} ({progress_c_day*100:.0f}%)**")
        st.progress(progress_c_day)
        if day_total_c >= target_carbs:
            st.success("🎉 Met goal!" if lang == 'en' else "🎉 Норма достигнута!")
        elif day_total_c >= target_carbs * 0.8:
            st.warning("⚠️ Near goal" if lang == 'en' else "⚠️ Около нормы")
        else:
            st.error("🔴 Below goal" if lang == 'en' else "🔴 Ниже нормы")

    with col_df:
        st.subheader("🧈 " + ("Fats" if lang == 'en' else "Жиры"))
        st.markdown(f"""
        <div class="card">
            <p class="metric-value">{day_total_f:.1f} {unit_g}</p>
            <p class="metric-label">{"Fat Intake" if lang == 'en' else "Потребление жиров"}</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown(f"**Goal: {target_fat}{unit_g} ({progress_f_day*100:.0f}%)**" if lang == 'en' else f"**Цель: {target_fat}{unit_g} ({progress_f_day*100:.0f}%)**")
        st.progress(progress_f_day)
        if day_total_f >= target_fat:
            st.success("🎉 Met goal!" if lang == 'en' else "🎉 Норма достигнута!")
        elif day_total_f >= target_fat * 0.8:
            st.warning("⚠️ Near goal" if lang == 'en' else "⚠️ Около нормы")
        else:
            st.error("🔴 Below goal" if lang == 'en' else "🔴 Ниже нормы")

    st.markdown("---")
    
    # 2. Period Analysis Section
    st.markdown("### 📊 " + ("Period Actual Intake Analysis" if lang == 'en' else "Анализ фактического потребления за период"))
    
    default_start = today - datetime.timedelta(days=6)
    col_start, col_end = st.columns(2)
    with col_start:
        start_date = st.date_input("Start Date" if lang == 'en' else "Начальная дата", default_start, key="stats_start_date_input")
    with col_end:
        end_date = st.date_input("End Date" if lang == 'en' else "Конечная дата", today, key="stats_end_date_input")
        
    start_str = start_date.strftime("%Y-%m-%d") if start_date else default_start.strftime("%Y-%m-%d")
    end_str = end_date.strftime("%Y-%m-%d") if end_date else today.strftime("%Y-%m-%d")
    
    # Fetch actual log entries in range
    logs_in_range = db.get_actual_intake_in_range(start_str, end_str)
    
    # Generate list of all dates in the range to display 0 on empty days
    delta = (end_date - start_date) if (start_date and end_date) else (today - default_start)
    if delta.days >= 0:
        all_dates = [(start_date if start_date else default_start) + datetime.timedelta(days=i) for i in range(delta.days + 1)]
    else:
        all_dates = [start_date if start_date else default_start]
        
    logs_by_date = {d.strftime("%Y-%m-%d"): [] for d in all_dates}
    for entry in logs_in_range:
        e_date = entry['date']
        if e_date in logs_by_date:
            logs_by_date[e_date].append(entry)
            
    total_p = 0.0
    total_c = 0.0
    total_f = 0.0
    daily_macros_data = []
    
    for d_str in sorted(logs_by_date.keys()):
        day_p = 0.0
        day_c = 0.0
        day_f = 0.0
        
        for entry in logs_by_date[d_str]:
            f_name = entry['food_name']
            g_name = entry['garnish_name']
            f_port = entry['food_portion']
            g_port = entry['garnish_portion']
            
            p_density = entry.get('protein_density', 0.0)
            c_density = entry.get('carbs_density', 0.0)
            f_density = entry.get('fat_density', 0.0)
            
            if p_density == 0.0 and c_density == 0.0 and f_density == 0.0:
                if f_name != "None" and f_name in st.session_state.food_macros:
                    f_macro = st.session_state.food_macros[f_name]
                    p_density = f_macro['protein']
                    c_density = f_macro['carbs']
                    f_density = f_macro['fat']
                    
            day_p += p_density * f_port / 100.0
            day_c += c_density * f_port / 100.0
            day_f += f_density * f_port / 100.0
                
            if g_name != "None" and g_name in st.session_state.food_macros:
                g_macro = st.session_state.food_macros[g_name]
                day_p += g_macro['protein'] * g_port / 100.0
                day_c += g_macro['carbs'] * g_port / 100.0
                day_f += g_macro['fat'] * g_port / 100.0
                
        total_p += day_p
        total_c += day_c
        total_f += day_f
        
        # Format date for index display
        daily_macros_data.append({
            _t('day_label_column'): d_str,
            'Protein' if lang == 'en' else 'Белки': round(day_p, 1),
            'Carbs' if lang == 'en' else 'Углеводы': round(day_c, 1),
            'Fats' if lang == 'en' else 'Жиры': round(day_f, 1)
        })
        
    num_days = max(1, len(all_dates))
    avg_daily_p = total_p / num_days
    avg_daily_c = total_c / num_days
    avg_daily_f = total_f / num_days
    
    target_protein = st.session_state.target_protein
    target_carbs = st.session_state.target_carbs
    target_fat = st.session_state.target_fat
    unit_g = 'г' if lang == 'ru' else 'g'
    
    progress_p = min(1.0, avg_daily_p / target_protein) if target_protein > 0 else 0.0
    progress_c = min(1.0, avg_daily_c / target_carbs) if target_carbs > 0 else 0.0
    progress_f = min(1.0, avg_daily_f / target_fat) if target_fat > 0 else 0.0

    # UI Columns for each macro
    col_p, col_c, col_f = st.columns(3)
    
    with col_p:
        st.subheader("🥩 " + ("Protein" if lang == 'en' else "Белки"))
        st.markdown(f"""
        <div class="card">
            <p class="metric-value">{avg_daily_p:.1f} {unit_g}</p>
            <p class="metric-label">{_t('stat_card_avg_protein')}</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown(f"**Goal: {target_protein}{unit_g} ({progress_p*100:.0f}%)**" if lang == 'en' else f"**Цель: {target_protein}{unit_g} ({progress_p*100:.0f}%)**")
        st.progress(progress_p)
        if avg_daily_p >= target_protein:
            st.success(_t('success_goal_msg').format(avg=avg_daily_p, target=target_protein))
        elif avg_daily_p >= target_protein * 0.8:
            st.warning(_t('warning_goal_msg').format(avg=avg_daily_p, percent=progress_p*100, target=target_protein))
        else:
            st.error(_t('error_goal_msg').format(avg=avg_daily_p, target=target_protein))

    with col_c:
        st.subheader("🌾 " + ("Carbohydrates" if lang == 'en' else "Углеводы"))
        st.markdown(f"""
        <div class="card">
            <p class="metric-value">{avg_daily_c:.1f} {unit_g}</p>
            <p class="metric-label">{_t('stat_card_avg_carbs')}</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown(f"**Goal: {target_carbs}{unit_g} ({progress_c*100:.0f}%)**" if lang == 'en' else f"**Цель: {target_carbs}{unit_g} ({progress_c*100:.0f}%)**")
        st.progress(progress_c)
        if avg_daily_c >= target_carbs:
            st.success("🎉 Met goal!" if lang == 'en' else "🎉 Норма достигнута!")
        elif avg_daily_c >= target_carbs * 0.8:
            st.warning("⚠️ Near goal" if lang == 'en' else "⚠️ Около нормы")
        else:
            st.error("🔴 Below goal" if lang == 'en' else "🔴 Ниже нормы")

    with col_f:
        st.subheader("🧈 " + ("Fats" if lang == 'en' else "Жиры"))
        st.markdown(f"""
        <div class="card">
            <p class="metric-value">{avg_daily_f:.1f} {unit_g}</p>
            <p class="metric-label">{_t('stat_card_avg_fats')}</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown(f"**Goal: {target_fat}{unit_g} ({progress_f*100:.0f}%)**" if lang == 'en' else f"**Цель: {target_fat}{unit_g} ({progress_f*100:.0f}%)**")
        st.progress(progress_f)
        if avg_daily_f >= target_fat:
            st.success("🎉 Met goal!" if lang == 'en' else "🎉 Норма достигнута!")
        elif avg_daily_f >= target_fat * 0.8:
            st.warning("⚠️ Near goal" if lang == 'en' else "⚠️ Около нормы")
        else:
            st.error("🔴 Below goal" if lang == 'en' else "🔴 Ниже нормы")

    import altair as alt

    # 1. Weight & GLP-1 Injections Chart
    st.markdown("### " + ("📈 Weight & GLP-1 Injections" if lang == 'en' else "📈 Вес и инъекции GLP-1"))
    
    # Get weight history
    weight_hist = db.get_weight_history()
    weight_by_date = {d: w for d, w in weight_hist}
    
    # Find last weight recorded before start date for forward fill
    last_weight = 0.0
    for d_str, w_val in weight_hist:
        if d_str < start_str:
            last_weight = w_val
        else:
            break
            
    filled_weight_by_date = {}
    for d in all_dates:
        d_str = d.strftime("%Y-%m-%d")
        if d_str in weight_by_date:
            last_weight = weight_by_date[d_str]
        filled_weight_by_date[d_str] = last_weight

    weight_records = []
    for d in all_dates:
        d_str = d.strftime("%Y-%m-%d")
        w_val = filled_weight_by_date.get(d_str, 0.0)
        if w_val > 0:
            weight_records.append({'Date': d_str, 'Weight': w_val})
            
    df_w = pd.DataFrame(weight_records)
    
    # Get injection history
    inj_hist = db.get_injection_history()
    inj_records = []
    for entry in inj_hist:
        d_str = entry[1]
        if start_str <= d_str <= end_str:
            med = entry[2]
            dose = entry[3]
            med_short = med.split(" ")[0] if med else ""
            label = f"{dose} mg"
            tooltip_text = f"{med_short} {dose} mg" if med_short else f"{dose} mg"
            inj_records.append({'Date': d_str, 'Label': label, 'Tooltip': tooltip_text})
            
    df_inj = pd.DataFrame(inj_records)
    
    if not df_w.empty:
        # Weight line layer
        weight_line = alt.Chart(df_w).mark_line(
            color='#3B82F6',
            strokeWidth=3,
            interpolate='monotone'
        ).encode(
            x=alt.X('Date:T', title="Date" if lang == 'en' else "Дата"),
            y=alt.Y('Weight:Q', scale=alt.Scale(zero=False), title="Weight (kg)" if lang == 'en' else "Вес (кг)"),
            tooltip=[
                alt.Tooltip('Date:T', title="Date" if lang == 'en' else "Дата"),
                alt.Tooltip('Weight:Q', title="Weight (kg)" if lang == 'en' else "Вес (кг)", format=".1f")
            ]
        )
        
        # Weight point markers
        weight_points = alt.Chart(df_w).mark_point(
            color='#3B82F6',
            size=40,
            filled=True
        ).encode(
            x=alt.X('Date:T'),
            y=alt.Y('Weight:Q'),
            tooltip=[
                alt.Tooltip('Date:T', title="Date" if lang == 'en' else "Дата"),
                alt.Tooltip('Weight:Q', title="Weight (kg)" if lang == 'en' else "Вес (кг)", format=".1f")
            ]
        )
        
        layers = [weight_line, weight_points]
        
        if not df_inj.empty:
            # Injection event dots on the X-axis (at the bottom)
            inj_dots = alt.Chart(df_inj).mark_point(
                color='#EF4444',
                size=120,
                shape='circle',
                filled=True
            ).encode(
                x=alt.X('Date:T'),
                y=alt.value(280),
                tooltip=[
                    alt.Tooltip('Date:T', title="Date" if lang == 'en' else "Дата"),
                    alt.Tooltip('Tooltip:N', title="Injection" if lang == 'en' else "Инъекция")
                ]
            )
            
            inj_text = alt.Chart(df_inj).mark_text(
                align='center',
                baseline='bottom',
                dy=-10,
                color='#EF4444',
                fontSize=10,
                fontWeight='bold'
            ).encode(
                x=alt.X('Date:T'),
                y=alt.value(280),
                text='Label:N'
            )
            layers.extend([inj_dots, inj_text])
            
        chart_w_inj = alt.layer(*layers).properties(
            height=300
        ).interactive(bind_y=False)
        st.altair_chart(chart_w_inj, use_container_width=True)
    else:
        st.info("No weight logs available in this date range." if lang == 'en' else "Нет данных о весе за этот период.")

    # 2. Proteins Chart
    st.markdown("---")
    st.markdown("### " + ("🥩 Daily Protein Intake" if lang == 'en' else "🥩 Суточное потребление белка"))
    
    p_records = []
    for entry in daily_macros_data:
        p_records.append({
            'Date': entry[_t('day_label_column')],
            'Protein': entry['Protein' if lang == 'en' else 'Белки']
        })
    df_p = pd.DataFrame(p_records)
    
    if not df_p.empty:
        bar_p = alt.Chart(df_p).mark_bar(color='#10B981', opacity=0.85).encode(
            x=alt.X('Date:T', title="Date" if lang == 'en' else "Дата"),
            y=alt.Y('Protein:Q', title="Protein (g)" if lang == 'en' else "Белок (г)"),
            tooltip=[
                alt.Tooltip('Date:T', title="Date" if lang == 'en' else "Дата"),
                alt.Tooltip('Protein:Q', title="Protein (g)" if lang == 'en' else "Белок (г)", format=".1f")
            ]
        )
        
        # Horizontal target rule
        goal_df_p = pd.DataFrame([{'Goal': target_protein}])
        rule_p = alt.Chart(goal_df_p).mark_rule(
            color='#EF4444',
            strokeDash=[5, 5],
            strokeWidth=2
        ).encode(
            y='Goal:Q',
            tooltip=[alt.Tooltip('Goal:Q', title="Goal (g)" if lang == 'en' else "Цель (г)")]
        )
        
        chart_p = alt.layer(bar_p, rule_p).properties(
            height=250
        ).interactive(bind_y=False)
        st.altair_chart(chart_p, use_container_width=True)
    else:
        st.info("No nutrition logs available in this date range." if lang == 'en' else "Нет данных о питании за этот период.")

    # 3. Calories Chart
    st.markdown("---")
    st.markdown("### " + ("🔥 Daily Caloric Consumption" if lang == 'en' else "🔥 Суточное потребление калорий"))
    
    c_records = []
    for entry in daily_macros_data:
        p = entry['Protein' if lang == 'en' else 'Белки']
        c = entry['Carbs' if lang == 'en' else 'Углеводы']
        f = entry['Fats' if lang == 'en' else 'Жиры']
        cals = p * 4.0 + c * 4.0 + f * 9.0
        c_records.append({
            'Date': entry[_t('day_label_column')],
            'Calories': round(cals, 1)
        })
    df_c = pd.DataFrame(c_records)
    target_calories = target_protein * 4.0 + target_carbs * 4.0 + target_fat * 9.0
    
    if not df_c.empty:
        area_c = alt.Chart(df_c).mark_area(
            color='#D946EF',
            opacity=0.2,
            line={'color': '#D946EF', 'width': 3}
        ).encode(
            x=alt.X('Date:T', title="Date" if lang == 'en' else "Дата"),
            y=alt.Y('Calories:Q', title="Calories (kcal)" if lang == 'en' else "Калории (ккал)"),
            tooltip=[
                alt.Tooltip('Date:T', title="Date" if lang == 'en' else "Дата"),
                alt.Tooltip('Calories:Q', title="Calories (kcal)" if lang == 'en' else "Калории (ккал)", format=".1f")
            ]
        )
        
        # Horizontal target rule
        goal_df_c = pd.DataFrame([{'Goal': target_calories}])
        rule_c = alt.Chart(goal_df_c).mark_rule(
            color='#EF4444',
            strokeDash=[5, 5],
            strokeWidth=2
        ).encode(
            y='Goal:Q',
            tooltip=[alt.Tooltip('Goal:Q', title="Goal (kcal)" if lang == 'en' else "Цель (ккал)")]
        )
        
        chart_c = alt.layer(area_c, rule_c).properties(
            height=250
        ).interactive(bind_y=False)
        st.altair_chart(chart_c, use_container_width=True)
    else:
        st.info("No nutrition logs available in this date range." if lang == 'en' else "Нет данных о питании за этот период.")

# ---- TAB 4: WEIGHT TRACKER ----
with tab_weight:
    st.markdown(_t('weight_header'))
    
    # 1. Fetch weight history
    weight_history = db.get_weight_history()
    
    # 2. Form to add new/historical entry
    col_w_form, col_w_stats = st.columns([1, 2])
    
    with col_w_form:
        with st.container(border=True):
            st.markdown("#### " + ("Add / Update Entry" if lang == 'en' else "Добавить / Изменить"))
            
            # Date Picker
            import datetime
            w_date = st.date_input(_t('weight_date_label'), value=datetime.date.today(), key="w_date_input")
            w_date_str = w_date.strftime("%Y-%m-%d") if w_date else datetime.date.today().strftime("%Y-%m-%d")
            
            # Weight Input
            w_val = st.number_input(_t('weight_input_label'), min_value=30.0, max_value=250.0, value=80.0, step=0.1, format="%.1f")
            
            # Save Button
            if st.button(_t('weight_save_btn'), use_container_width=True):
                db.add_weight_entry(w_date_str, w_val)
                st.success("Weight recorded!" if lang == 'en' else "Вес записан!")
                st.rerun()
                
    with col_w_stats:
        if weight_history:
            # Calculate metrics
            current_w = weight_history[-1][1]
            start_w = weight_history[0][1]
            diff_w = current_w - start_w
            
            col_m1, col_m2, col_m3 = st.columns(3)
            with col_m1:
                st.markdown(f"""
                <div class="card">
                    <p class="metric-value">{current_w:.1f} kg</p>
                    <p class="metric-label">{_t('weight_stat_current')}</p>
                </div>
                """, unsafe_allow_html=True)
            with col_m2:
                st.markdown(f"""
                <div class="card">
                    <p class="metric-value">{start_w:.1f} kg</p>
                    <p class="metric-label">{_t('weight_stat_start')}</p>
                </div>
                """, unsafe_allow_html=True)
            with col_m3:
                color_class = "metric-value"
                sign = "+" if diff_w > 0 else ""
                st.markdown(f"""
                <div class="card">
                    <p class="{color_class}">{sign}{diff_w:.1f} kg</p>
                    <p class="metric-label">{_t('weight_stat_diff')}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No weight entries recorded yet." if lang == 'en' else "Записи о весе отсутствуют.")
            
    # 3. Chart and History table
    if weight_history:
        st.markdown(_t('weight_chart_title'))
        df_weight = pd.DataFrame(weight_history, columns=[_t('col_date'), _t('col_weight')])
        st.line_chart(df_weight.set_index(_t('col_date')), y=_t('col_weight'))
        
        # Display history table with delete button for each entry
        st.markdown(_t('weight_history_title'))
        
        for date_str, w_value in reversed(weight_history):
            col_d1, col_d2, col_d3 = st.columns([2, 2, 1])
            with col_d1:
                st.write(date_str)
            with col_d2:
                st.write(f"{w_value:.1f} kg")
            with col_d3:
                if st.button(_t('delete_btn'), key=f"del_w_{date_str}", use_container_width=True):
                    db.delete_weight_entry(date_str)
                    st.rerun()

# ---- TAB 5: GLP-1 INJECTIONS ----
with tab_glp1:
    st.markdown(_t('glp1_header'))
    
    # 1. Fetch injection history
    injection_history = db.get_injection_history()
    
    # 2. Form to log injection
    col_inj_form, col_inj_stats = st.columns([1, 2])
    
    with col_inj_form:
        with st.container(border=True):
            st.markdown("#### " + ("Log New Injection" if lang == 'en' else "Записать инъекцию"))
            
            inj_date = st.date_input(_t('glp1_date_label'), value=datetime.date.today(), key="inj_date_input")
            inj_date_str = inj_date.strftime("%Y-%m-%d") if inj_date else datetime.date.today().strftime("%Y-%m-%d")
            
            # Warning for past dates
            today = datetime.date.today()
            if inj_date and inj_date < today:
                st.warning(_t('glp1_warning_past').format(date=inj_date_str))
                
            # Medication Selection
            medication_brands = [
                "Mounjaro (Tirzepatide)",
                "Ozempic (Semaglutide)",
                "Wegovy (Semaglutide)",
                "Zepbound (Tirzepatide)",
                "Saxenda (Liraglutide)",
                "Victoza (Liraglutide)",
                "Trulicity (Dulaglutide)",
                "Other / Custom"
            ]
            med_selected = st.selectbox(_t('glp1_med_label'), medication_brands)
            
            # Dose suggestions
            default_dose = 2.5
            if "Ozempic" in med_selected or "Wegovy" in med_selected:
                default_dose = 0.25
            elif "Saxenda" in med_selected or "Victoza" in med_selected:
                default_dose = 0.6
            elif "Trulicity" in med_selected:
                default_dose = 0.75
                
            inj_dose = st.number_input(_t('glp1_dose_label'), min_value=0.05, max_value=50.0, value=default_dose, step=0.05, format="%.2f")
            
            # Save Button
            if st.button(_t('glp1_save_btn'), use_container_width=True):
                db.add_injection_entry(inj_date_str, med_selected, inj_dose)
                st.success("Injection recorded!" if lang == 'en' else "Инъекция записана!")
                st.rerun()
                
    with col_inj_stats:
        if injection_history:
            latest_inj = injection_history[0] # (id, date, medication, dose)
            latest_date = datetime.datetime.strptime(latest_inj[1], "%Y-%m-%d").date()
            next_due = latest_date + datetime.timedelta(days=7)
            next_due_str = next_due.strftime("%Y-%m-%d")
            
            col_i1, col_i2 = st.columns(2)
            with col_i1:
                st.markdown(f"""
                <div class="card">
                    <p class="metric-value">{latest_inj[3]:.2f} mg</p>
                    <p class="metric-label">{_t('glp1_latest_injection')} ({latest_inj[2]})</p>
                    <caption style="color:#64748b; font-size:0.8rem; display:block; margin-top:5px;">Date: {latest_inj[1]}</caption>
                </div>
                """, unsafe_allow_html=True)
            with col_i2:
                is_overdue = today > next_due
                overdue_label = "⚠️ OVERDUE" if is_overdue and med_selected not in ["Saxenda (Liraglutide)", "Victoza (Liraglutide)"] else ""
                
                st.markdown(f"""
                <div class="card">
                    <p class="metric-value" style="color: {'#EF4444' if is_overdue and med_selected not in ["Saxenda (Liraglutide)", "Victoza (Liraglutide)"] else '#10B981'};">{next_due_str}</p>
                    <p class="metric-label">{_t('glp1_next_due')} {overdue_label}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No injections logged yet." if lang == 'en' else "Записи об инъекциях отсутствуют.")
            
    # 3. Injection Log Table
    if injection_history:
        st.markdown(_t('glp1_history_title'))
        
        col_th1, col_th2, col_th3, col_th4 = st.columns([2, 3, 2, 1])
        with col_th1:
            st.markdown(f"**{_t('col_date')}**")
        with col_th2:
            st.markdown(f"**{_t('col_medication')}**")
        with col_th3:
            st.markdown(f"**{_t('col_dose')}**")
        with col_th4:
            st.write("")
        st.divider()
            
        for entry_id, date_str, med_name, dose_val in injection_history:
            col_tr1, col_tr2, col_tr3, col_tr4 = st.columns([2, 3, 2, 1])
            with col_tr1:
                st.write(date_str)
            with col_tr2:
                st.write(med_name)
            with col_tr3:
                st.write(f"{dose_val:.2f} mg")
            with col_tr4:
                if st.button(_t('delete_btn'), key=f"del_inj_{entry_id}", use_container_width=True):
                    db.delete_injection_entry(entry_id)
                    st.rerun()

# ---- TAB 7: SETTINGS ----
with tab_settings:
    st.markdown(f"### {_t('profile_header')}")
    
    def save_profile(key, session_key):
        db.update_profile_value(key, st.session_state[session_key])
        
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        st.text_input(_t('login_label'), key="profile_username", on_change=save_profile, args=("username", "profile_username"))
        st.text_input(_t('email_label'), key="profile_email", on_change=save_profile, args=("email", "profile_email"))
    with col_p2:
        gender_options = ["Male", "Female", "Other"]
        gender_trans = {
            "Male": _t('gender_male'),
            "Female": _t('gender_female'),
            "Other": _t('gender_other')
        }
        gender_idx = gender_options.index(st.session_state.profile_gender) if st.session_state.profile_gender in gender_options else 0
        gender_sel = st.selectbox(_t('gender_label'), gender_options, index=gender_idx, format_func=lambda x: gender_trans.get(x, x), key="profile_gender_select")
        if gender_sel != st.session_state.profile_gender:
            st.session_state.profile_gender = gender_sel
            db.update_profile_value("gender", gender_sel)
        
    # Change Password Section
    st.markdown(f"#### {_t('change_pw_header')}")
    col_pw1, col_pw2, col_pw3 = st.columns([3, 3, 2])
    with col_pw1:
        new_pw = st.text_input(_t('new_password_label'), type="password", key="new_password_input")
    with col_pw2:
        confirm_pw = st.text_input(_t('confirm_password_label'), type="password", key="confirm_password_input")
    with col_pw3:
        st.write("<br>", unsafe_allow_html=True)
        if st.button(_t('save_btn'), key="change_password_submit_btn", use_container_width=True):
            if not new_pw:
                st.error(_t('pw_change_empty'))
            elif new_pw != confirm_pw:
                st.error(_t('pw_change_mismatch'))
            else:
                db.change_user_password(new_pw)
                st.success(_t('pw_change_success'))

    st.divider()
    st.markdown(f"### {_t('actions_header')}")
    
    col_act1, col_act2 = st.columns(2)
    with col_act1:
        lang_choices = {"ru": "🇷🇺 Русский", "en": "🇬🇧 English"}
        lang_val = st.selectbox(
            _t('lang_label'), 
            options=list(lang_choices.keys()), 
            format_func=lambda x: lang_choices[x],
            index=0 if lang == 'ru' else 1,
            key="lang_selector"
        )
        if lang_val != st.session_state.lang:
            st.session_state.lang = lang_val
            db.update_setting_value('lang', lang_val)
            st.rerun()
            
        st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
        if st.button(_t('logout_btn'), use_container_width=True):
            st.session_state.clear()
            st.rerun()
            
    with col_act2:
        st.write("")
        st.write("")
        if st.button(_t('add_product_btn'), use_container_width=True, type="primary"):
            add_product_dialog()
            
    st.divider()
    
    # Portions
    st.subheader(_t('portion_header'))
    st.slider(_t('protein_portion_label'), min_value=50, max_value=400, key="protein_portion", on_change=update_portion_setting, args=("protein_portion",), step=10)
    st.slider(_t('garnish_portion_label'), min_value=30, max_value=300, key="garnish_portion", on_change=update_portion_setting, args=("garnish_portion",), step=5)
    st.slider(_t('snack_portion_label'), min_value=10, max_value=150, key="snack_portion", on_change=update_portion_setting, args=("snack_portion",), step=5)
    
    st.divider()
    
    # Targets/Goals
    st.subheader(_t('goals_header'))
    st.slider(_t('target_protein_label'), min_value=50, max_value=250, key="target_protein", on_change=update_portion_setting, args=("target_protein",), step=5)
    st.slider(_t('target_carbs_label'), min_value=50, max_value=400, key="target_carbs", on_change=update_portion_setting, args=("target_carbs",), step=5)
    st.slider(_t('target_fat_label'), min_value=20, max_value=150, key="target_fat", on_change=update_portion_setting, args=("target_fat",), step=5)
    
    st.divider()
    
    # Active pools
    st.subheader("Active Pools Selection" if lang == 'en' else "Выбор пула активных продуктов")
    col_pool1, col_pool2, col_pool3 = st.columns(3)
    with col_pool1:
        st.multiselect(
            _t('select_proteins_label'), 
            options=st.session_state.proteins_db,
            key="active_proteins",
            format_func=translate_food
        )
    with col_pool2:
        st.multiselect(
            _t('select_garnishes_label'), 
            options=st.session_state.garnishes_db,
            key="active_garnishes",
            format_func=translate_food
        )
    with col_pool3:
        st.multiselect(
            _t('select_snacks_label'),
            options=st.session_state.snacks_db,
            key="active_snacks",
            format_func=translate_food
        )
        
    st.divider()
    
    # Extra items
    st.subheader(_t('additional_list_header'))
    st.text_area(_t('additional_list_header'), 
                 placeholder=_t('additional_placeholder'),
                 key="extra_items_input",
                 label_visibility="collapsed")

st.divider()
st.caption(_t('footer_caption'))