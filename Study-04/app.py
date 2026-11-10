from datetime import datetime
import hashlib
import json
import sqlite3

import streamlit as st

from api import generate_recipes, list_models, prepare_image, recognize
import storage

PAGES = {"대시보드": "🏠 대시보드", "재료 인식": "📷 재료 인식", "레시피 생성": "🍽️ 레시피 생성", "나의 레시피": "📚 나의 레시피", "프로필": "👤 프로필", "추천": "🎯 추천"}
CUISINES = ["한식", "양식", "중식", "일식", "간식", "상관없음"]
DIFFICULTIES = ["쉬움", "보통", "어려움"]
DIETS = ["채식", "비건", "글루텐 프리", "유제품 제외", "견과류 제외", "저염식"]


def navigate(page):
    st.session_state.nav = PAGES[page]


def clear_photo():
    for key in ("photo_preview", "photo_id", "result", "ingredients", "recipe_draft"):
        st.session_state.pop(key, None)


def brand():
    st.markdown('''<h1 class="brand"><svg aria-hidden="true" width="42" height="42" viewBox="0 0 44 44" xmlns="http://www.w3.org/2000/svg"><path d="M29 29L39 39" stroke="#59477b" stroke-width="7" stroke-linecap="round"/><circle cx="19" cy="19" r="17" fill="#59477b"/><path d="M11 13C15 8 20 11 24 12C31 15 27 25 21 26C14 28 7 22 11 13Z" fill="#fffaf2"/><circle cx="19" cy="18" r="5" fill="#f9d34e"/></svg>FridgeChef</h1>''', unsafe_allow_html=True)


def login_page():
    brand()
    st.subheader("AI 기반 맞춤형 레시피 추천 시스템")
    _, center, _ = st.columns([1, 2, 1])
    with center:
        login, signup = st.tabs(["로그인", "회원가입"])
        with login, st.form("login_form"):
            st.subheader("로그인")
            email = st.text_input("이메일", placeholder="your@email.com", key="login_email")
            password = st.text_input("비밀번호", type="password", key="login_password")
            left, right = st.columns(2)
            submitted = left.form_submit_button("로그인", type="primary", width="stretch")
            demo = right.form_submit_button("데모 계정", width="stretch")
            if submitted or demo:
                user_id = "demo1" if demo else storage.authenticate(email, password)
                if user_id:
                    st.session_state.user_id = user_id
                    st.session_state.nav = PAGES["대시보드"]
                    st.rerun()
                st.error("이메일 또는 비밀번호를 확인해 주세요.")
        with signup, st.form("signup_form"):
            st.subheader("회원가입")
            name = st.text_input("이름", max_chars=50, key="signup_name")
            email = st.text_input("이메일", key="signup_email")
            password = st.text_input("비밀번호", type="password", help="8~128자", key="signup_password")
            confirmation = st.text_input("비밀번호 확인", type="password", key="signup_confirmation")
            if st.form_submit_button("회원가입", type="primary", width="stretch"):
                if password != confirmation:
                    st.error("비밀번호가 일치하지 않습니다.")
                else:
                    try:
                        storage.register_user(email, password, name)
                        st.success("회원가입이 완료되었습니다. 로그인 탭에서 로그인해 주세요.")
                    except ValueError as error:
                        st.error(str(error))
        st.caption("교재 실습용 로컬 계정입니다. 실제 서비스에서 쓰는 비밀번호나 개인정보는 입력하지 마세요.")
        with st.expander("테스트 계정 안내"):
            st.write("demo@example.com / demo1234")
            st.write("demo2@example.com / demo1234")
            st.caption("데모 계정의 저장 목록은 공개된 실습 데이터입니다.")


def api_sidebar(user_id):
    with st.sidebar:
        st.subheader("ℹ️ 정보")
        st.info("냉장고 사진을 업로드하면 AI가 자동으로 재료를 인식합니다.\n\n지원 형식: JPG, PNG\n\n최대 크기: 10MB")
        settings = st.expander("⚙️ API 연결 설정", expanded=not st.session_state.get("models"))
        with settings:
            api_key = st.text_input("새 API 키", type="password", help="현재 세션에서만 사용하며 파일로 저장하지 않습니다.").strip()
            fingerprint = hashlib.sha256(api_key.encode()).hexdigest()
            if st.session_state.get("key_fingerprint") != fingerprint:
                for key in ("models", "model", "recipe_model"):
                    st.session_state.pop(key, None)
                st.session_state.key_fingerprint = fingerprint
            st.markdown("[학교 API 키 발급 안내](https://docs.factchat.kr/docs/mnuaibootcamp/api-gateway/getting-started/authentication)")
            consent = st.checkbox("사진·재료·취향을 FactChat과 선택한 모델 제공사로 전송하는 데 동의합니다. 계정 크레딧이 차감될 수 있습니다.", key="api_consent")
        if st.button("🔌 API 연결 테스트", disabled=not api_key):
            try:
                with st.spinner("연결을 확인하고 있어요…"):
                    st.session_state.models = list_models(api_key, claude_only=False)
                st.success("API 연결 성공")
            except ValueError as error:
                st.error(str(error))
        models = st.session_state.get("models", [])
        with settings:
            image_model = st.selectbox("사진 인식 모델 (Claude)", [m for m in models if m.startswith("claude-")], index=None, placeholder="모델을 선택하세요", key="model")
            recipe_model = st.selectbox("레시피 생성 모델", models, index=None, placeholder="DeepSeek 또는 Claude 등 선택", key="recipe_model")
            st.caption("학교용 FactChat을 사용합니다. 다른 모델로 자동 전환하지 않습니다.")
        st.divider()
        st.subheader("📊 데이터베이스")
        st.metric("저장된 레시피", storage.stats(user_id)["saved"])
        if st.session_state.get("recent"):
            st.subheader("📜 최근 기록")
            for entry in st.session_state.recent:
                st.caption(entry)
    return api_key, image_model, recipe_model, consent


def image_page(api_key, model, consent):
    st.header("냉장고 사진에서 재료 인식")
    left, right = st.columns(2, gap="medium")
    with left:
        st.subheader("📷 이미지 업로드")
        photo = st.file_uploader("냉장고 사진을 선택하세요", type=["jpg", "jpeg", "png"], key="photo_upload", on_change=clear_photo)
        if photo is not None:
            raw = photo.getvalue()
            photo_id = hashlib.sha256(raw).hexdigest()
            if photo_id != st.session_state.get("photo_id"):
                st.session_state.pop("result", None)
                st.session_state.pop("ingredients", None)
                st.session_state.pop("recipe_draft", None)
                st.session_state.pop("photo_preview", None)
                st.session_state.photo_id = photo_id
            try:
                prepared = prepare_image(raw)
                st.session_state.photo_preview = prepared
                st.image(prepared, caption="업로드된 이미지")
                st.success("✅ 이미지 업로드 완료")
            except ValueError as error:
                st.error(str(error))
        elif st.session_state.get("photo_preview"):
            st.image(st.session_state.photo_preview, caption="업로드된 이미지")
        else:
            st.caption("JPG 또는 PNG, 최대 10MB")
        prepared = st.session_state.get("photo_preview")
        if st.button("🔍 재료 인식 시작", type="primary", width="stretch", disabled=not (api_key and model and prepared and consent)):
            try:
                with st.spinner("AI가 냉장고 재료를 분석하고 있어요…"):
                    result = recognize(api_key, model, prepared)
                st.session_state.result = {"text": result, "model": model}
                st.session_state.ingredients = result
                st.session_state.pop("recipe_draft", None)
                recent = st.session_state.get("recent", [])
                st.session_state.recent = [datetime.now().strftime("%H:%M") + " · 재료 인식 완료", *recent][:3]
            except ValueError as error:
                st.error(str(error))
    with right:
        st.subheader("📋 인식된 재료")
        if "result" in st.session_state:
            st.markdown(st.session_state.result["text"])
            st.caption("AI가 잘못 인식할 수 있습니다. 실제 재료를 확인하세요. 사진으로 신선도나 섭취 안전성을 판단할 수 없습니다.")
        else:
            st.info("이미지를 업로드하고 '재료 인식 시작' 버튼을 클릭하세요.")
    if st.session_state.get("result") or st.session_state.get("recipe_draft"):
        with st.expander("✏️ 재료 편집", expanded=False):
            edit_ingredients()
        st.button("🍽️ 이 재료로 레시피 생성", type="primary", on_click=navigate, args=("레시피 생성",))


def edit_ingredients():
    draft = st.session_state.get("recipe_draft", {})
    if "ingredients" not in st.session_state:
        st.session_state.ingredients = draft.get("ingredients", st.session_state.get("result", {}).get("text", ""))
    ingredients = st.text_area("사용할 재료", key="ingredients", height=150, max_chars=5000, help="인식 결과를 수정·추가·삭제하고, 불확실한 재료는 지워 주세요. 사진 없이 직접 입력해도 됩니다.")
    st.session_state.recipe_draft = {**draft, "ingredients": ingredients}
    return ingredients


def show_recipe(recipe):
    st.write(f"난이도: {recipe['difficulty']}")
    st.write(f"조리시간: {recipe['minutes']}분")
    st.write(f"인분: {recipe.get('servings', 4)}인분")
    calories = recipe.get("calories")
    st.write(f"칼로리: {calories}kcal / 1인분 (AI 추정)" if calories is not None else "칼로리: 제공되지 않음")
    st.markdown("**재료:**")
    for item in recipe["ingredients"]:
        st.write(f"• {item['name']}: {item['amount']}")
    if recipe["extra_ingredients"]:
        st.markdown("**추가로 필요한 재료:**")
        for item in recipe["extra_ingredients"]:
            st.write(f"• {item['name']}: {item['amount']}")
    st.markdown("**조리법:**")
    for number, step in enumerate(recipe["steps"], 1):
        st.write(f"{number}. {step}")


def recipe_page(api_key, model, consent, user_id):
    st.header("🍽️ 레시피 생성")
    with st.expander("사용 가능한 재료 보기", expanded=not st.session_state.get("result") and not st.session_state.get("recipe_draft")):
        ingredients = edit_ingredients()
    st.subheader("레시피 설정")
    draft = st.session_state.get("recipe_draft", {})
    defaults = {"difficulty": "보통", "max_minutes": 30, "servings": 4, "cuisine": "한식", "diets": []}
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = draft.get(key, value)
    c1, c2, c3 = st.columns(3)
    difficulty = c1.select_slider("난이도", DIFFICULTIES, key="difficulty")
    max_minutes = c2.slider("최대 조리 시간(분)", 5, 120, step=5, key="max_minutes")
    servings = c3.number_input("인분", min_value=1, max_value=12, step=1, key="servings")
    c1, c2 = st.columns(2)
    cuisine = c1.selectbox("요리 종류", CUISINES, key="cuisine")
    diets = c2.multiselect("식단 제한", DIETS, key="diets", placeholder="Choose options")
    st.session_state.recipe_draft = {"ingredients": ingredients, "difficulty": difficulty, "max_minutes": max_minutes, "servings": servings, "cuisine": cuisine, "diets": diets}
    preferences = storage.profile(user_id)["preferences"]
    signature = (ingredients, cuisine, difficulty, preferences, model, max_minutes, servings, tuple(diets))
    if preferences:
        st.caption(f"프로필 반영: {preferences}")
    if not (api_key and model and consent):
        st.caption("왼쪽 API 연결 설정에서 키·모델을 선택하고 전송 안내를 확인하세요.")
    if st.button("🔍 레시피 생성", type="primary", width="stretch", disabled=not (api_key and model and ingredients.strip() and consent)):
        try:
            with st.spinner("재료와 설정에 맞는 레시피를 생성하고 있어요…"):
                recipes = generate_recipes(api_key, model, ingredients, cuisine, difficulty, preferences, max_minutes=max_minutes, servings=servings, dietary_restrictions=diets)
            st.session_state.generated = recipes
            st.session_state.recipe_signature = signature
            st.session_state.generation = st.session_state.get("generation", 0) + 1
            st.session_state.save_feedback = {}
        except ValueError as error:
            st.error(str(error))
    recipes = st.session_state.get("generated", [])
    if not recipes:
        return
    if signature != st.session_state.get("recipe_signature"):
        st.warning("아래 결과는 이전 조건으로 생성했습니다. 변경 사항을 반영하려면 다시 생성하세요.")
    st.caption("AI 제안입니다. 알레르기 유발 재료와 충분한 가열 여부를 직접 확인하세요.")
    with st.expander("🔎 레시피 검색 및 필터"):
        search = st.text_input("요리명 검색")
        left, right = st.columns(2)
        cuisine_filter = left.selectbox("요리 종류 필터", ["전체"] + CUISINES)
        difficulty_filter = right.selectbox("난이도 필터", ["전체"] + DIFFICULTIES)
    shown = 0
    for index, recipe in enumerate(recipes):
        if search.casefold() not in recipe["title"].casefold() or (cuisine_filter != "전체" and recipe["cuisine"] != cuisine_filter) or (difficulty_filter != "전체" and recipe["difficulty"] != difficulty_filter):
            continue
        shown += 1
        with st.expander(f"{index + 1}. {recipe['title']}", expanded=index == 0):
            left, right = st.columns([3, 1])
            with left:
                show_recipe(recipe)
            with right:
                if recipe.get("match_score") is not None:
                    st.metric("매칭 점수", f"{recipe['match_score']}%")
                    st.caption("보유 재료 비율")
                key = f"generated_{st.session_state.get('generation', 0)}_{index}"
                if st.button("💾 저장", key=f"save_{key}"):
                    folder = st.session_state.get(f"folder_{key}", "기본")
                    saved = storage.save_recipe(user_id, recipe, folder)
                    st.session_state.setdefault("save_feedback", {})[key] = saved
                    st.rerun()
                feedback = st.session_state.get("save_feedback", {})
                if key in feedback:
                    if feedback[key]:
                        st.success("레시피가 저장되었습니다!")
                    else:
                        st.info("이미 저장한 레시피입니다.")
                st.download_button("📄 JSON 내보내기", json.dumps(recipe, ensure_ascii=False, indent=2), file_name="recipe.json", mime="application/json", key=f"download_{key}")
                with st.expander("저장 폴더"):
                    st.text_input("폴더 이름", value="기본", max_chars=50, key=f"folder_{key}")
    if not shown:
        st.info("검색·필터 조건에 맞는 레시피가 없습니다.")


def saved_page(user_id):
    st.header("📚 나의 레시피")
    rows = storage.saved_recipes(user_id)
    folders = sorted({"기본"} | {row["folder"] for row in rows})
    folder_filter = st.selectbox("폴더 선택", ["전체"] + folders, index=1)
    with st.expander("🔎 저장한 레시피 검색"):
        search = st.text_input("저장한 요리 검색")
    shown = 0
    for row in rows:
        recipe = row["recipe"]
        if search.casefold() not in recipe["title"].casefold() or (folder_filter != "전체" and row["folder"] != folder_filter):
            continue
        shown += 1
        with st.expander(recipe["title"]):
            left, right = st.columns([3, 1])
            with left:
                show_recipe(recipe)
            with right:
                recipe_id = row["id"]
                st.caption(f"요리한 횟수: {row['cooked']}회")
                if st.button("🍳 요리 완료 +1", key=f"cook_{recipe_id}"):
                    storage.mark_cooked(user_id, recipe_id)
                    st.rerun()
                rating = st.select_slider("평점", options=list(range(6)), value=row["rating"], format_func=lambda value: "미평가" if value == 0 else f"{value} ⭐", key=f"rating_{recipe_id}")
                if st.button("평점 저장", key=f"rate_{recipe_id}"):
                    storage.rate_recipe(user_id, recipe_id, rating)
                    st.rerun()
                folder = st.text_input("폴더 이름", value=row["folder"], max_chars=50, key=f"move_folder_{recipe_id}")
                if st.button("폴더 이동", key=f"move_{recipe_id}"):
                    storage.move_recipe(user_id, recipe_id, folder)
                    st.rerun()
                confirmed = st.checkbox(f"‘{recipe['title']}’ 저장본 삭제 확인", key=f"confirm_delete_{recipe_id}")
                if st.button("저장본 삭제", disabled=not confirmed, key=f"delete_{recipe_id}"):
                    storage.delete_recipe(user_id, recipe_id)
                    st.rerun()
    if not shown:
        st.info("저장된 레시피가 없습니다." if not rows else "검색·폴더 조건에 맞는 레시피가 없습니다.")


def dashboard_page(user_id):
    st.header("📊 나의 요리 대시보드")
    values = storage.stats(user_id)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("저장한 레시피", f"{values['saved']}개", delta=f"+{values['weekly_saved']} 최근 7일")
    c2.metric("요리한 횟수", f"{values['cooked']}회")
    c3.metric("평균 평점", f"{values['rating']} ⭐" if values["rating"] is not None else "— ⭐")
    c4.metric("레시피 폴더", f"{values['folders']}개")
    st.subheader("📈 통계")
    left, right = st.columns(2)
    with left:
        st.markdown("**자주 사용하는 재료**")
        if values["ingredients"]:
            st.bar_chart({"재료": [name for name, _ in values["ingredients"]], "레시피 수": [count for _, count in values["ingredients"]]}, x="재료", y="레시피 수", horizontal=True)
            st.caption("저장된 레시피에 포함된 보유 재료 기준")
        else:
            st.info("레시피를 저장하면 재료 분석이 표시됩니다.")
    with right:
        st.markdown("**최근 저장한 레시피**")
        rows = storage.saved_recipes(user_id)[:3]
        for row in rows:
            st.write(f"• {row['recipe']['title']}")
        if not rows:
            st.caption("아직 저장한 레시피가 없습니다.")
        st.button("📚 나의 레시피 보기", on_click=navigate, args=("나의 레시피",))
    st.divider()
    st.button("📷 냉장고 사진으로 시작하기", type="primary", on_click=navigate, args=("재료 인식",))


def profile_page(user_id):
    st.header("👤 프로필")
    current = storage.profile(user_id)
    with st.form("profile_form"):
        name = st.text_input("이름", value=current["name"], max_chars=50)
        preferences = st.text_area("요리 취향·제외할 재료", value=current["preferences"], max_chars=1000, help="예: 매운맛 적게, 땅콩 제외. AI 결과를 직접 확인하세요.")
        if st.form_submit_button("프로필 저장", type="primary"):
            storage.update_profile(user_id, name, preferences)
            st.success("프로필을 저장했습니다. 다음 레시피 생성부터 반영합니다.")
    st.caption("교재 실습용 로컬 프로필입니다. 실제 개인정보는 입력하지 마세요.")


def recommendation_page(user_id):
    st.header("🎯 맞춤 추천")
    preferences = storage.profile(user_id)["preferences"]
    if preferences:
        st.info(f"나의 요리 취향: {preferences}")
    rows = sorted(storage.saved_recipes(user_id), key=lambda row: (row["rating"], row["cooked"]), reverse=True)[:3]
    st.write("저장한 레시피 중 평점과 요리 횟수가 높은 요리를 다시 골라보세요.")
    for row in rows:
        with st.expander(row["recipe"]["title"]):
            show_recipe(row["recipe"])
    if not rows:
        st.info("아직 저장한 레시피가 없습니다. 재료와 프로필 취향을 반영한 새 레시피를 만들어 보세요.")
    st.button("🍽️ 새 맞춤 레시피 생성", type="primary", on_click=navigate, args=("레시피 생성",))


st.set_page_config(page_title="FridgeChef", page_icon="🍳", layout="wide", initial_sidebar_state="collapsed")
st.markdown("""<style>
.block-container {max-width:1200px;padding-top:2.5rem;padding-bottom:3rem;}
h1 {font-size:2.5rem!important;letter-spacing:-.025em;}
.brand {display:flex;align-items:center;gap:.65rem;}
h2 {font-size:1.8rem!important;} h3 {font-size:1.35rem!important;}
[data-testid="stTabs"] [role="tablist"] {gap:1.15rem;}
[data-testid="stTabs"] [role="tab"] {padding-left:0;padding-right:0;font-size:.9rem;}
[data-testid="stExpander"] {border-radius:5px;}
[data-testid="stExpander"] details > summary {background:#f5f6f9;}
[data-testid="stMetricValue"] {font-size:1.8rem;}
[data-testid="stSidebar"] {background:#f1f2f6;}
</style>""", unsafe_allow_html=True)
try:
    storage.init_db()
    if "user_id" not in st.session_state:
        login_page()
        st.stop()
    user_id = st.session_state.user_id
    title, user, logout = st.columns([2, 1, 1], vertical_alignment="center")
    with title:
        brand()
    user.write(f"👤 {storage.profile(user_id)['name']}")
    if logout.button("로그아웃", width="stretch"):
        st.session_state.clear()
        st.rerun()
    api_key, image_model, recipe_model, consent = api_sidebar(user_id)
    if st.session_state.get("nav") not in PAGES.values():
        st.session_state.nav = PAGES["대시보드"]
    tabs = st.tabs(list(PAGES.values()), key="nav", on_change="rerun")
    for name, tab in zip(PAGES, tabs):
        if not tab.open:
            continue
        with tab:
            if name == "대시보드":
                dashboard_page(user_id)
            elif name == "재료 인식":
                image_page(api_key, image_model, consent)
            elif name == "레시피 생성":
                recipe_page(api_key, recipe_model, consent, user_id)
            elif name == "나의 레시피":
                saved_page(user_id)
            elif name == "프로필":
                profile_page(user_id)
            else:
                recommendation_page(user_id)
    st.divider()
    st.caption("FridgeChef | AI 기반 맞춤형 레시피 추천 시스템")
except sqlite3.Error:
    st.error("저장소 작업에 실패했습니다. 기존 데이터는 유지됩니다. 앱 폴더의 쓰기 권한을 확인하고 다시 시도해 주세요.")
except ValueError as error:
    st.error(str(error))
