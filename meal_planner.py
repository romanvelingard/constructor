import streamlit as st
import pandas as pd
import random

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

# 1. State Management & Initial Database
if 'proteins_db' not in st.session_state:
    st.session_state.proteins_db = {
        'Индейка': 25.0, 'Курица': 24.0, 'Мушт': 21.0, 'Говядина': 26.0, 
        'Печень': 20.0, 'Тунец': 22.0, 'Сардины': 23.0, 'Фасоль': 8.0, 'Творог': 15.0,
        'Тофу': 15.0
    }

if 'garnishes_db' not in st.session_state:
    st.session_state.garnishes_db = ['Гречка', 'Киноа', 'Рис', 'Картофель', 'Паста']

if 'snacks_db' not in st.session_state:
    st.session_state.snacks_db = {
        'Миндаль': 21.0,
        'Кешью': 18.0,
        'Грецкий орех': 15.0
    }

# Active week pool state bindings
if 'active_proteins' not in st.session_state:
    st.session_state.active_proteins = list(st.session_state.proteins_db.keys())[:7]

if 'active_garnishes' not in st.session_state:
    st.session_state.active_garnishes = st.session_state.garnishes_db[:4]

if 'active_snacks' not in st.session_state:
    st.session_state.active_snacks = list(st.session_state.snacks_db.keys())

if 'checked_groceries' not in st.session_state:
    st.session_state.checked_groceries = set()

days_of_week = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]

# Preload/upgrade initial plan
if 'meal_plan' not in st.session_state:
    st.session_state.meal_plan = {
        day: {
            "Обед": {"protein": "Курица", "garnish": "Гречка"},
            "Ужин": {"protein": "Индейка", "garnish": "Рис"},
            "Снэк": {"snack": "Миндаль"}
        } for day in days_of_week
    }
else:
    # Upgrade state structure with Snacks if user has active session
    for day in days_of_week:
        if "Снэк" not in st.session_state.meal_plan[day]:
            st.session_state.meal_plan[day]["Снэк"] = {"snack": "Миндаль"}

# Modal Dialog Function
@st.dialog("Добавить новый продукт")
def add_product_dialog():
    category = st.selectbox("ТИП:", ["Протеины", "Гарнир", "Снэк"])
    name = st.text_input("Название продукта:", placeholder="Например: Лосось, Булгур, Арахис")
    
    # Enable double/float input for protein density
    protein_density = st.number_input(
        "Количество белка (г/100г):", 
        min_value=0.0, 
        max_value=100.0, 
        value=15.0, 
        step=0.5, 
        format="%.1f",
        disabled=(category == "Гарнир")
    )
    
    if st.button("Сохранить в базу", use_container_width=True):
        clean_name = name.strip()
        if clean_name:
            if category == "Протеины":
                st.session_state.proteins_db[clean_name] = protein_density
                if clean_name not in st.session_state.active_proteins:
                    st.session_state.active_proteins.append(clean_name)
                st.success(f"Протеин '{clean_name}' ({protein_density} г белка) успешно добавлен!")
            elif category == "Снэк":
                st.session_state.snacks_db[clean_name] = protein_density
                if clean_name not in st.session_state.active_snacks:
                    st.session_state.active_snacks.append(clean_name)
                st.success(f"Снэк '{clean_name}' ({protein_density} г белка) успешно добавлен!")
            else:
                if clean_name not in st.session_state.garnishes_db:
                    st.session_state.garnishes_db.append(clean_name)
                if clean_name not in st.session_state.active_garnishes:
                    st.session_state.active_garnishes.append(clean_name)
                st.success(f"Гарнир '{clean_name}' успешно добавлен!")
            st.rerun()
        else:
            st.error("Введите название продукта!")

# 2. Sidebar Controls
with st.sidebar:
    st.header("🎯 Действия и Настройки")
    
    # Dialog Trigger Button
    if st.button("➕ Добавить новый продукт", use_container_width=True, type="primary"):
        add_product_dialog()
        
    st.divider()
    
    # Portions
    st.subheader("Размеры порций (сырой вес)")
    protein_portion = st.slider("Размер порции белка (г):", min_value=50, max_value=400, value=150, step=10)
    garnish_portion = st.slider("Размер порции гарнира (г):", min_value=30, max_value=300, value=80, step=5)
    snack_portion = st.slider("Размер порции снэков (г):", min_value=10, max_value=150, value=30, step=5)
    
    st.divider()
    
    st.subheader("Целевые показатели")
    target_protein = st.slider("Цель по белку (г/день):", min_value=50, max_value=250, value=130, step=5)
    
    # Extra shopping list notes
    st.subheader("🛒 Дополнительно в список")
    extra_items_input = st.text_area("Дополнительные товары (через запятую):", 
                                    placeholder="Яйца, огурцы, помидоры, зелень, масло...")

# 3. Header Title
st.markdown("""
<div class="title-container">
    <h1 style="margin:0; font-size:2.5rem; color:#1e293b; font-weight:800;">📅 Premium Food Planner & Shopping List</h1>
    <p style="margin:0.5rem 0 0 0; color:#64748b; font-size:1.1rem;">Планируйте свое меню на неделю, контролируйте норму белка и автоматически получайте список покупок.</p>
</div>
""", unsafe_allow_html=True)

# 4. Multiselect for active week pool (from the database)
col_sel1, col_sel2, col_sel3 = st.columns(3)
with col_sel1:
    selected_proteins = st.multiselect(
        "Выберите доступные протеины на неделю:", 
        options=list(st.session_state.proteins_db.keys()),
        key="active_proteins"
    )
with col_sel2:
    selected_garnishes = st.multiselect(
        "Выберите доступные гарниры на неделю:", 
        options=st.session_state.garnishes_db,
        key="active_garnishes"
    )
with col_sel3:
    selected_snacks = st.multiselect(
        "Выберите доступные снэки на неделю:",
        options=list(st.session_state.snacks_db.keys()),
        key="active_snacks"
    )

# Prepare lists for selection
active_proteins_options = ["Нет"] + st.session_state.active_proteins
active_garnishes_options = ["Нет"] + st.session_state.active_garnishes
active_snacks_options = ["Нет"] + st.session_state.active_snacks

# Main Workspace Tabs
tab_menu, tab_list, tab_stats = st.tabs([
    "📅  Меню на неделю", 
    "🛒 Список покупок", 
    "📊 Аналитика питания"
])

# ---- TAB 1: WEEKLY PLANNER ----
with tab_menu:
    # 7-day schedule grid
    # Let's arrange them nicely in rows
    # Row 1: Monday, Tuesday, Wednesday, Thursday
    # Row 2: Friday, Saturday, Sunday, Actions
    
    col_mon, col_tue, col_wed, col_thu = st.columns(4)
    col_fri, col_sat, col_sun, col_act = st.columns(4)
    
    days_cols = {
        "Понедельник": col_mon,
        "Вторник": col_tue,
        "Среда": col_wed,
        "Четверг": col_thu,
        "Пятница": col_fri,
        "Суббота": col_sat,
        "Воскресенье": col_sun
    }
    
    for day, col in days_cols.items():
        with col:
            with st.container(border=True):
                st.markdown(f"### 📅 {day}")
                
                # Check for lunch selections
                stored_lunch_p = st.session_state.meal_plan[day]["Обед"]["protein"]
                stored_lunch_g = st.session_state.meal_plan[day]["Обед"]["garnish"]
                
                lunch_p_idx = active_proteins_options.index(stored_lunch_p) if stored_lunch_p in active_proteins_options else 0
                lunch_g_idx = active_garnishes_options.index(stored_lunch_g) if stored_lunch_g in active_garnishes_options else 0
                
                st.markdown("**🍲 Обед**")
                lunch_p = st.selectbox(f"Протеин (Обед)##{day}", active_proteins_options, index=lunch_p_idx, label_visibility="collapsed")
                lunch_g = st.selectbox(f"Гарнир (Обед)##{day}", active_garnishes_options, index=lunch_g_idx, label_visibility="collapsed")
                
                # Check for dinner selections
                stored_dinner_p = st.session_state.meal_plan[day]["Ужин"]["protein"]
                stored_dinner_g = st.session_state.meal_plan[day]["Ужин"]["garnish"]
                
                dinner_p_idx = active_proteins_options.index(stored_dinner_p) if stored_dinner_p in active_proteins_options else 0
                dinner_g_idx = active_garnishes_options.index(stored_dinner_g) if stored_dinner_g in active_garnishes_options else 0
                
                st.markdown("**🥗 Ужин**")
                dinner_p = st.selectbox(f"Протеин (Ужин)##{day}", active_proteins_options, index=dinner_p_idx, label_visibility="collapsed")
                dinner_g = st.selectbox(f"Гарнир (Ужин)##{day}", active_garnishes_options, index=dinner_g_idx, label_visibility="collapsed")
                
                # Check for snack selections
                stored_snack_s = st.session_state.meal_plan[day]["Снэк"]["snack"]
                snack_s_idx = active_snacks_options.index(stored_snack_s) if stored_snack_s in active_snacks_options else 0
                
                st.markdown("**🥨 Перекус (Снэк)**")
                snack_s = st.selectbox(f"Снэк (Перекус)##{day}", active_snacks_options, index=snack_s_idx, label_visibility="collapsed")
                
                # Save choice to session state
                st.session_state.meal_plan[day]["Обед"]["protein"] = lunch_p
                st.session_state.meal_plan[day]["Обед"]["garnish"] = lunch_g
                st.session_state.meal_plan[day]["Ужин"]["protein"] = dinner_p
                st.session_state.meal_plan[day]["Ужин"]["garnish"] = dinner_g
                st.session_state.meal_plan[day]["Снэк"]["snack"] = snack_s
                
                # Calculate daily protein content
                day_protein = 0
                for meal_type in ["Обед", "Ужин"]:
                    p = st.session_state.meal_plan[day][meal_type]["protein"]
                    if p != "Нет" and p in st.session_state.proteins_db:
                        day_protein += (protein_portion / 100) * st.session_state.proteins_db[p]
                
                s = st.session_state.meal_plan[day]["Снэк"]["snack"]
                if s != "Нет" and s in st.session_state.snacks_db:
                    day_protein += (snack_portion / 100) * st.session_state.snacks_db[s]
                
                st.markdown(f"<span class='badge badge-protein'>Белок: {day_protein:.1f} г</span>", unsafe_allow_html=True)
                
    # Quick Actions inside col_act
    with col_act:
        with st.container(border=True):
            st.markdown("### ⚡ Быстрые действия")
            
            if st.button("🔄 Заполнить случайно", use_container_width=True):
                for day in days_of_week:
                    st.session_state.meal_plan[day]["Обед"]["protein"] = random.choice(st.session_state.active_proteins) if st.session_state.active_proteins else "Нет"
                    st.session_state.meal_plan[day]["Обед"]["garnish"] = random.choice(st.session_state.active_garnishes) if st.session_state.active_garnishes else "Нет"
                    st.session_state.meal_plan[day]["Ужин"]["protein"] = random.choice(st.session_state.active_proteins) if st.session_state.active_proteins else "Нет"
                    st.session_state.meal_plan[day]["Ужин"]["garnish"] = random.choice(st.session_state.active_garnishes) if st.session_state.active_garnishes else "Нет"
                    st.session_state.meal_plan[day]["Снэк"]["snack"] = random.choice(st.session_state.active_snacks) if st.session_state.active_snacks else "Нет"
                st.rerun()
                
            if st.button("📋 Скопировать Пн на все дни", use_container_width=True):
                mon_plan = st.session_state.meal_plan["Понедельник"]
                for day in days_of_week[1:]:
                    st.session_state.meal_plan[day] = {
                        "Обед": mon_plan["Обед"].copy(),
                        "Ужин": mon_plan["Ужин"].copy(),
                        "Снэк": mon_plan["Снэк"].copy()
                    }
                st.rerun()
                
            if st.button("🗑️ Очистить меню", use_container_width=True):
                for day in days_of_week:
                    st.session_state.meal_plan[day]["Обед"]["protein"] = "Нет"
                    st.session_state.meal_plan[day]["Обед"]["garnish"] = "Нет"
                    st.session_state.meal_plan[day]["Ужин"]["protein"] = "Нет"
                    st.session_state.meal_plan[day]["Ужин"]["garnish"] = "Нет"
                    st.session_state.meal_plan[day]["Снэк"]["snack"] = "Нет"
                st.rerun()

# ---- TAB 2: SHOPPING LIST ----
with tab_list:
    st.markdown("### 🛒 Сводный список покупок на неделю")
    st.write("Суммированный вес продуктов, рассчитанный исходя из выбранного меню и настроек порций:")
    
    # Aggregate quantities
    shopping_proteins = {}
    shopping_garnishes = {}
    shopping_snacks = {}
    
    for day in days_of_week:
        for meal in ["Обед", "Ужин"]:
            p = st.session_state.meal_plan[day][meal]["protein"]
            g = st.session_state.meal_plan[day][meal]["garnish"]
            
            if p != "Нет" and p in st.session_state.proteins_db:
                shopping_proteins[p] = shopping_proteins.get(p, 0) + protein_portion
            if g != "Нет" and g in st.session_state.garnishes_db:
                shopping_garnishes[g] = shopping_garnishes.get(g, 0) + garnish_portion
                
        s = st.session_state.meal_plan[day]["Снэк"]["snack"]
        if s != "Нет" and s in st.session_state.snacks_db:
            shopping_snacks[s] = shopping_snacks.get(s, 0) + snack_portion

    # Parse extra items
    extra_items_list = []
    if extra_items_input:
        extra_items_list = [item.strip() for item in extra_items_input.split(",") if item.strip()]

    # Layout: two columns for display and text copy
    col_check, col_raw = st.columns([2, 1])
    
    with col_check:
        st.markdown("#### ✅ Интерактивный чеклист")
        
        has_items = False
        
        # Display Proteins
        if shopping_proteins:
            has_items = True
            st.markdown("##### 🥩 Протеиновые продукты")
            for item, weight in shopping_proteins.items():
                item_label = f"{item} — {weight} г"
                # Checkbox identity key
                item_key = f"chk_protein_{item}_{weight}"
                is_checked = item_key in st.session_state.checked_groceries
                
                if st.checkbox(item_label, value=is_checked, key=item_key):
                    st.session_state.checked_groceries.add(item_key)
                else:
                    st.session_state.checked_groceries.discard(item_key)
        
        # Display Garnishes
        if shopping_garnishes:
            has_items = True
            st.markdown("##### 🌾 Гарниры")
            for item, weight in shopping_garnishes.items():
                item_label = f"{item} — {weight} г"
                item_key = f"chk_garnish_{item}_{weight}"
                is_checked = item_key in st.session_state.checked_groceries
                
                if st.checkbox(item_label, value=is_checked, key=item_key):
                    st.session_state.checked_groceries.add(item_key)
                else:
                    st.session_state.checked_groceries.discard(item_key)
                    
        # Display Snacks
        if shopping_snacks:
            has_items = True
            st.markdown("##### 🥨 Снэки / Перекусы")
            for item, weight in shopping_snacks.items():
                item_label = f"{item} — {weight} г"
                item_key = f"chk_snack_{item}_{weight}"
                is_checked = item_key in st.session_state.checked_groceries
                
                if st.checkbox(item_label, value=is_checked, key=item_key):
                    st.session_state.checked_groceries.add(item_key)
                else:
                    st.session_state.checked_groceries.discard(item_key)
                    
        # Display Extras
        if extra_items_list:
            has_items = True
            st.markdown("##### 🥗 Дополнительно")
            for i, item in enumerate(extra_items_list):
                item_key = f"chk_extra_{item}_{i}"
                is_checked = item_key in st.session_state.checked_groceries
                
                if st.checkbox(item, value=is_checked, key=item_key):
                    st.session_state.checked_groceries.add(item_key)
                else:
                    st.session_state.checked_groceries.discard(item_key)
                    
        if not has_items:
            st.info("Ваш список покупок пуст. Выберите блюда в меню на неделю!")
            
    with col_raw:
        st.markdown("#### 📋 Текст для копирования")
        # Build text string
        raw_text = "🛒 СПИСОК ПОКУПОК НА НЕДЕЛЮ\n"
        raw_text += "===========================\n\n"
        if shopping_proteins:
            raw_text += "🥩 ПРОТЕИНЫ:\n"
            for item, weight in shopping_proteins.items():
                raw_text += f"- {item}: {weight} г\n"
            raw_text += "\n"
        if shopping_garnishes:
            raw_text += "🌾 GАРНИРЫ:\n"
            for item, weight in shopping_garnishes.items():
                raw_text += f"- {item}: {weight} г\n"
            raw_text += "\n"
        if shopping_snacks:
            raw_text += "🥨 СНЭКИ / ПЕРЕКУСЫ:\n"
            for item, weight in shopping_snacks.items():
                raw_text += f"- {item}: {weight} г\n"
            raw_text += "\n"
        if extra_items_list:
            raw_text += "🥗 ДОПОЛНИТЕЛЬНО:\n"
            for item in extra_items_list:
                raw_text += f"- {item}\n"
            raw_text += "\n"
        
        st.text_area("Скопируйте этот список:", value=raw_text, height=280)
        st.caption("💡 Вы можете легко скопировать этот текст и отправить себе в мессенджер.")

# ---- TAB 3: STATISTICS & ANALYTICS ----
with tab_stats:
    st.markdown("### 📊 Анализ дневной нормы белка")
    
    # Calculations
    total_weekly_p = 0
    daily_protein_data = []
    
    for day in days_of_week:
        day_p = 0
        for meal in ["Обед", "Ужин"]:
            p = st.session_state.meal_plan[day][meal]["protein"]
            if p != "Нет" and p in st.session_state.proteins_db:
                day_p += (protein_portion / 100) * st.session_state.proteins_db[p]
        
        s = st.session_state.meal_plan[day]["Снэк"]["snack"]
        if s != "Нет" and s in st.session_state.snacks_db:
            day_p += (snack_portion / 100) * st.session_state.snacks_db[s]
            
        total_weekly_p += day_p
        daily_protein_data.append({"День": day, "Белок (г)": round(day_p, 1)})
        
    avg_daily_p = total_weekly_p / 7
    progress = min(1.0, avg_daily_p / target_protein) if target_protein > 0 else 0.0
    
    # Metric cards display
    col_stat1, col_stat2, col_stat3 = st.columns(3)
    
    with col_stat1:
        st.markdown(f"""
        <div class="card">
            <p class="metric-value">{avg_daily_p:.1f} г</p>
            <p class="metric-label">Средний белок в день</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col_stat2:
        st.markdown(f"""
        <div class="card">
            <p class="metric-value">{progress*100:.0f}%</p>
            <p class="metric-label">Выполнение цели ({target_protein}г)</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col_stat3:
        st.markdown(f"""
        <div class="card">
            <p class="metric-value">{total_weekly_p:.1f} г</p>
            <p class="metric-label">Всего белка за неделю</p>
        </div>
        """, unsafe_allow_html=True)
        
    # Progress bar and status feedback
    st.markdown("#### Целевой прогресс дневной нормы белка")
    st.progress(progress)
    
    if avg_daily_p >= target_protein:
        st.success(f"🎉 Отлично! Ваше среднее потребление белка ({avg_daily_p:.1f} г) соответствует или превышает вашу цель ({target_protein} г/день)!")
    elif avg_daily_p >= target_protein * 0.8:
        st.warning(f"⚠️ Вы близки к вашей цели! Среднее потребление белка ({avg_daily_p:.1f} г) составляет {progress*100:.0f}% от цели ({target_protein} г/день). Добавьте более концентрированные белковые продукты.")
    else:
        st.error(f"🔴 Дефицит белка. Ваше среднее потребление белка ({avg_daily_p:.1f} г) значительно ниже цели ({target_protein} г/день). Попробуйте увеличить размер порций белка в боковом меню или заменить нежирные белки на более плотные.")
        
    # Chart
    st.markdown("#### Дневное потребление белка по дням недели")
    df_daily = pd.DataFrame(daily_protein_data)
    st.bar_chart(df_daily.set_index("День"))

st.divider()
st.caption("Подготовлено для Roman Velingard")