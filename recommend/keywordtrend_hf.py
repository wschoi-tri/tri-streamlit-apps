import os
import json
import streamlit as st
import streamlit.components.v1 as components

# 페이지 기본 설정 (전체 화면 모드)
st.set_page_config(
    page_title="Halfclub Trend AI Curation Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 기본 CSS 덮어쓰기 (Streamlit 상단 헤더/푸터 제거 및 전체 화면 최대화)
st.markdown("""
<style>
    .stAppHeader {display: none !important;}
    footer {display: none !important;}
    #MainMenu {visibility: hidden;}
    .block-container {
        padding-top: 0rem !important;
        padding-bottom: 0rem !important;
        padding-left: 0rem !important;
        padding-right: 0rem !important;
        max-width: 100% !important;
    }
    iframe {
        border: none !important;
        width: 100% !important;
        height: 100vh !important;
    }
</style>
""", unsafe_allow_html=True)

# 타겟 키워드 리스트 로드 (keywords.json 연동)
def load_keywords():
    kw_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "keywords.json")
    if os.path.exists(kw_path):
        try:
            with open(kw_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return [
        "가디건", "가방", "골프모자", "골프백", "골프장갑", "골프티", "골프화", "귀걸이", "긴바지", "긴팔티셔츠",
        "남성가방", "남성골프화", "남성벨트", "넥워머", "넥타이", "니트", "토드백", "데님", "데님팬츠", "드레스",
        "등산화", "런닝화", "레깅스", "레더자켓", "레인부츠", "로퍼", "맨투맨", "머플러", "모자", "목걸이",
        "민소매", "민소매티셔츠", "반바지", "반팔", "반팔티셔츠", "베스트", "벨트", "보스턴백", "보스톤백", "볼캡",
        "부츠", "브로치", "비니", "샌들", "서류가방", "선글라스", "셋업", "셔츠", "손수건", "숄더백",
        "스니커즈", "스카프", "스커트", "스포츠웨어", "슬랙스", "슬리퍼", "슬링백", "신발", "아우터", "양말",
        "에코백", "여성가방", "여성골프화", "여성벨트", "오픈토", "요가복", "우산", "우비", "운동화", "원피스",
        "자켓", "바람막이", "잠옷", "장갑", "점퍼", "정장", "정장자켓", "정장팬츠", "정장화", "조끼",
        "집업", "집업티셔츠", "코트", "크로스백", "클러치", "토트백", "트렌치", "티셔츠", "패딩", "팔찌",
        "팬츠", "펌프스", "플랫", "하프팬츠", "후드", "힐", "후리스", "후드티", "스웨터", "블라우스",
        "발찌", "슈즈", "양산", "지갑", "시계", "홈웨어", "수트", "무스탕"
    ]

keywords_list = load_keywords()

# URL 쿼리 파라미터 읽기 (초기 진입 / 새로고침 / 외부 링크 접속 지원)
qp = st.query_params
initial_kw = qp.get("keyword", keywords_list[0] if keywords_list else "가디건")
if initial_kw not in keywords_list:
    initial_kw = keywords_list[0] if keywords_list else "가디건"

initial_tab = qp.get("tab", "grid")
if initial_tab not in ["grid", "table", "raw", "prompt"]:
    initial_tab = "grid"

# Streamlit 양방향 커스텀 컴포넌트 선언
component_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "component")
_trend_dashboard_component = components.declare_component(
    "trend_dashboard_component",
    path=component_dir
)

# 컴포넌트 렌더링 및 프론트엔드 변경 이벤트 수신
comp_state = _trend_dashboard_component(
    keywords=keywords_list,
    initialKeyword=initial_kw,
    initialTab=initial_tab,
    default={"keyword": initial_kw, "tab": initial_tab}
)

# 프론트엔드에서 키워드/탭 변경 시 Streamlit Cloud 상단 주소창 URL 실시간 동기화
if comp_state and isinstance(comp_state, dict):
    selected_kw = comp_state.get("keyword")
    selected_tab = comp_state.get("tab")

    if selected_kw:
        need_update = False
        if st.query_params.get("keyword") != selected_kw:
            st.query_params["keyword"] = selected_kw
            need_update = True
        if selected_tab and st.query_params.get("tab") != selected_tab:
            st.query_params["tab"] = selected_tab
            need_update = True
