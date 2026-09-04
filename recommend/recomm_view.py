import os
import json
import urllib.parse
import streamlit as st
import streamlit.components.v1 as components

# 1. 페이지 기본 설정 (전체 화면 모드)
st.set_page_config(
    page_title="전체 추천 서비스 확인",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. 기본 CSS 덮어쓰기 (Streamlit 기본 여백/헤더 완전 제거 및 뷰포트 100% 풀스크린)
st.markdown("""
<style>
    header[data-testid="stHeader"], div[data-testid="stToolbar"], div[data-testid="stDecoration"], .stAppHeader, footer, #MainMenu {
        display: none !important;
        visibility: hidden !important;
    }
    html, body, .stApp, section.main, .main, .block-container, div[data-testid="stBlockContainer"], div[data-testid="stCustomComponentV1"] {
        padding: 0 !important;
        margin: 0 !important;
        max-width: 100% !important;
        width: 100% !important;
        height: 100% !important;
        overflow: hidden !important;
        background-color: #f8fafc !important;
    }
    iframe {
        position: fixed !important;
        top: 0 !important;
        left: 0 !important;
        width: 100vw !important;
        height: 100vh !important;
        border: none !important;
        margin: 0 !important;
        padding: 0 !important;
        display: block !important;
        z-index: 99999 !important;
    }
</style>
""", unsafe_allow_html=True)

# 2-1. Streamlit 시크릿 (.streamlit/secrets.toml) 도메인 로드 (기본값 금지 원칙 준수)
try:
    domains_conf = st.secrets["domains"]
    HALFCLUB_WEB_URL = str(domains_conf["halfclub_web"]).rstrip("/")
    HALFCLUB_API_URL = str(domains_conf["halfclub_api"]).rstrip("/")
    HALFCLUB_CDN_URL = str(domains_conf["halfclub_cdn"]).rstrip("/")
    HALFCLUB_PRD_URL = str(domains_conf["halfclub_prd"]).rstrip("/")
    BORIBORI_WEB_URL = str(domains_conf["boribori_web"]).rstrip("/")
    BORIBORI_API_URL = str(domains_conf["boribori_api"]).rstrip("/")
    BORIBORI_CDN_URL = str(domains_conf["boribori_cdn"]).rstrip("/")
    BORIBORI_PRD_URL = str(domains_conf["boribori_prd"]).rstrip("/")
except Exception as e:
    raise ValueError(f".streamlit/secrets.toml 내 [domains] 섹션 및 필수 도메인 키가 누락되었습니다: {e}")

# 3. 실제 서비스 중인 추천 API 모델 목록 (LF 모델 2종 및 키워드 트렌드 포함 총 9종)
ML_TYPES = [
    {"id": "home", "name": "홈 개인화", "desc": "FORYOU 종합 맞춤", "endpoint": "/recommend/home"},
    {"id": "similaritem", "name": "유사 상품", "desc": "속성/메타 유사도", "endpoint": "/recommend/similaritem"},
    {"id": "viewtogether", "name": "함께 본 상품", "desc": "동시 조회 기반", "endpoint": "/recommend/viewtogether"},
    {"id": "buytogether", "name": "함께 구매한 상품", "desc": "동시 구매 기반", "endpoint": "/recommend/buytogether"},
    {"id": "similar-image", "name": "유사 이미지", "desc": "비전 임베딩 유사도", "endpoint": "/recommend/similar-image"},
    {"id": "recommendforyou", "name": "개인화 추천", "desc": "다중 히스토리 맞춤", "endpoint": "/recommend/recommendforyou"},
    {"id": "lf", "name": "LF 개인화", "desc": "LF 계열 종합 맞춤", "endpoint": "/recommend/lf", "siteOnly": "1"},
    {"id": "lfsimilaritem", "name": "LF 유사 상품", "desc": "LF 계열 유사도", "endpoint": "/recommend/lfsimilaritem", "siteOnly": "1"},
    {"id": "keyword-trend", "name": "키워드 트렌드", "desc": "AI 트렌드 큐레이션", "endpoint": "/recommend/keyword-trend"}
]

# 3-1. 키워드 트렌드 타겟 키워드 리스트 로드
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
keywords_json_str = json.dumps(keywords_list, ensure_ascii=False)

# 4. URL 쿼리 파라미터 디코딩 및 상태 설정 (하드코딩 초기값 완전 제거)
qp = st.query_params
raw_site = qp.get("siteCd", "1")
if raw_site not in ["1", "2"]:
    raw_site = "1"

raw_type = qp.get("mlType", "home")
valid_type_ids = [m["id"] for m in ML_TYPES]
if raw_type not in valid_type_ids:
    raw_type = "home"

raw_prd = qp.get("prdNo", "")
if raw_prd:
    raw_prd = urllib.parse.unquote(str(raw_prd)).strip()
else:
    raw_prd = ""  # [사용자 요청] 과거 상품번호 하드코딩 초기값 완전 제거

raw_kw = qp.get("keyword", "")
if raw_kw:
    raw_kw = urllib.parse.unquote(str(raw_kw)).strip()
if not raw_kw:
    raw_kw = keywords_list[0] if keywords_list else "가디건"

raw_k = qp.get("k", "50")
if not raw_k.isdigit() or int(raw_k) <= 0:
    raw_k = "50"

raw_basket = qp.get("basketPrdNo", "")
raw_wish = qp.get("wishPrdNo", "")
raw_mem = qp.get("memNo", "")
raw_self = qp.get("selfYn", "false")
raw_selected_seed = qp.get("seedPrdNo", "")

raw_tab = qp.get("tab", "grid")
if raw_tab not in ["grid", "table", "raw", "prompt"]:
    raw_tab = "grid"

ml_types_json = json.dumps(ML_TYPES, ensure_ascii=False)
initial_site_json = json.dumps(raw_site, ensure_ascii=False)
initial_type_json = json.dumps(raw_type, ensure_ascii=False)
initial_prd_json = json.dumps(raw_prd, ensure_ascii=False)
initial_keyword_json = json.dumps(raw_kw, ensure_ascii=False)
initial_k_json = json.dumps(raw_k, ensure_ascii=False)
initial_basket_json = json.dumps(raw_basket, ensure_ascii=False)
initial_wish_json = json.dumps(raw_wish, ensure_ascii=False)
initial_mem_json = json.dumps(raw_mem, ensure_ascii=False)
initial_self_json = json.dumps(raw_self, ensure_ascii=False)
initial_selected_seed_json = json.dumps(raw_selected_seed, ensure_ascii=False)
initial_tab_json = json.dumps(raw_tab, ensure_ascii=False)

# 5. 풀스크린 일체형(Top-Down) HTML/CSS/JS 템플릿
html_content = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Recomm Service Dashboard</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;600;700;800&family=Outfit:wght@500;700;800&display=swap" rel="stylesheet">
    <style>
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: 'Noto Sans KR', -apple-system, BlinkMacSystemFont, sans-serif;
        }}
        html, body {{
            background-color: #f8fafc;
            color: #0f172a;
            height: 100%;
            width: 100%;
            margin: 0;
            padding: 0;
            overflow-x: hidden;
            overflow-y: auto;
        }}
        .app-wrapper {{
            display: flex;
            flex-direction: column;
            min-height: 1250px;
            width: 100%;
            padding: 14px 20px 40px 20px;
            max-width: 1920px;
            margin: 0 auto;
        }}

        /* 1단: 최상단 글로벌 통합 네비게이션 헤더 (1줄 고정 레이아웃) */
        .top-global-header {{
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 10px;
            padding: 8px 14px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 10px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.03);
            margin-bottom: 12px;
            flex-wrap: nowrap;
            overflow-x: auto;
            white-space: nowrap;
        }}
        .header-left-cluster {{
            display: flex;
            align-items: center;
            gap: 8px;
            flex-wrap: nowrap;
            flex-shrink: 0;
        }}
        .site-switch-group {{
            display: flex;
            background: #f1f5f9;
            padding: 3px;
            border-radius: 8px;
            gap: 2px;
            flex-shrink: 0;
        }}
        .site-btn {{
            border: none;
            padding: 5px 12px;
            border-radius: 6px;
            font-size: 0.83rem;
            font-weight: 800;
            color: #64748b;
            background: transparent;
            cursor: pointer;
            transition: all 0.15s ease;
            white-space: nowrap;
        }}
        .site-btn.active {{
            background: #ffffff;
            color: #0f172a;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        .v-divider {{
            width: 1px;
            height: 22px;
            background-color: #cbd5e1;
            flex-shrink: 0;
            margin: 0 2px;
        }}
        .model-tabs-group {{
            display: flex;
            background: #f1f5f9;
            padding: 3px;
            border-radius: 8px;
            gap: 2px;
            flex-wrap: nowrap;
            flex-shrink: 0;
        }}
        .model-tab-btn {{
            border: none;
            padding: 5px 10px;
            border-radius: 6px;
            font-size: 0.81rem;
            font-weight: 700;
            color: #475569;
            background: transparent;
            cursor: pointer;
            transition: all 0.15s ease;
            display: inline-flex;
            align-items: center;
            white-space: nowrap;
            flex-shrink: 0;
        }}
        .model-tab-btn:hover {{
            color: #0f172a;
            background: rgba(255, 255, 255, 0.6);
        }}
        .model-tab-btn.active {{
            background: #2563eb;
            color: #ffffff;
            font-weight: 800;
            box-shadow: 0 1px 3px rgba(37,99,235,0.25);
        }}
        
        .header-right-cluster {{
            display: flex;
            align-items: center;
            gap: 8px;
            flex-shrink: 0;
            flex-wrap: nowrap;
            margin-left: auto;
        }}
        .k-input-box {{
            display: flex;
            align-items: center;
            gap: 4px;
            font-size: 0.8rem;
            font-weight: 700;
            color: #475569;
            white-space: nowrap;
            flex-shrink: 0;
        }}
        .k-input {{
            width: 44px;
            padding: 3px 5px;
            border: 1px solid #cbd5e1;
            border-radius: 6px;
            text-align: center;
            font-size: 0.8rem;
            font-weight: 800;
            outline: none;
        }}
        .btn-copy-url {{
            background: #f1f5f9;
            border: 1px solid #cbd5e1;
            color: #475569;
            font-size: 0.78rem;
            font-weight: 700;
            padding: 4px 9px;
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.15s ease;
            white-space: nowrap;
            flex-shrink: 0;
        }}
        .btn-copy-url:hover {{
            background: #e2e8f0;
            color: #0f172a;
        }}
        .status-badge {{
            font-size: 0.78rem;
            font-weight: 800;
            padding: 4px 8px;
            border-radius: 6px;
            background: #ecfdf5;
            color: #059669;
            border: 1px solid #a7f3d0;
            white-space: nowrap;
            flex-shrink: 0;
        }}

        /* 2단: 추천 기준 상품 설정 및 대상 정보 일체형 카드 */
        .criterion-panel {{
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            padding: 14px 18px;
            display: grid;
            grid-template-columns: 340px 1fr;
            gap: 20px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.03);
            margin-bottom: 14px;
            box-sizing: border-box;
            width: 100%;
        }}
        .target-preview-box {{
            width: 340px;
            min-width: 340px;
            max-width: 340px;
            box-sizing: border-box;
            flex-shrink: 0;
            border-right: 1px solid #f1f5f9;
            padding-right: 18px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            overflow: hidden;
        }}
        .target-header-row {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 8px;
        }}
        .target-panel-title {{
            font-size: 0.88rem;
            font-weight: 800;
            color: #0f172a;
            display: flex;
            align-items: center;
            gap: 6px;
        }}
        .target-item-card {{
            display: flex;
            gap: 12px;
            align-items: center;
            min-width: 0;
            width: 100%;
        }}
        .target-thumb-wrap {{
            width: 72px;
            height: 86px;
            border-radius: 6px;
            overflow: hidden;
            background: #f1f5f9;
            border: 1px solid #e2e8f0;
            flex-shrink: 0;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .target-thumb {{
            width: 100%;
            height: 100%;
            object-fit: cover;
        }}
        .target-meta-details {{
            display: flex;
            flex-direction: column;
            gap: 2px;
            min-width: 0;
            flex: 1;
            overflow: hidden;
        }}
        .target-brand-row {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 6px;
        }}
        .target-brand {{
            font-size: 0.74rem;
            font-weight: 700;
            color: #64748b;
        }}
        .target-selacnt {{
            font-size: 0.7rem;
            font-weight: 600;
            color: #2563eb;
            background: #eff6ff;
            padding: 1px 5px;
            border-radius: 3px;
        }}
        .target-name {{
            font-size: 0.86rem;
            font-weight: 700;
            color: #0f172a;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            line-height: 1.35;
            display: block;
            width: 100%;
            min-width: 0;
        }}
        .target-price-row {{
            display: flex;
            align-items: baseline;
            gap: 5px;
            margin-top: 2px;
        }}
        .target-dc-price {{
            font-size: 0.95rem;
            font-weight: 800;
            color: #0f172a;
        }}
        .target-rate {{
            font-size: 0.82rem;
            font-weight: 800;
            color: #f43f5e;
        }}
        .target-cat-path {{
            font-size: 0.73rem;
            color: #64748b;
            font-weight: 500;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            margin-top: 2px;
        }}
        .multi-chips-row {{
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            gap: 4px;
            margin-top: 8px;
            padding-top: 6px;
            border-top: 1px dotted #e2e8f0;
            max-height: none;
            overflow: visible;
        }}
        .prd-chip {{
            font-size: 10px;
            font-weight: 700;
            padding: 2px 6px;
            border-radius: 4px;
            background: #eff6ff;
            color: #2563eb;
            border: 1px solid #dbeafe;
            cursor: pointer;
            transition: all 0.15s ease;
        }}
        .prd-chip:hover {{
            background: #fee2e2;
            color: #ef4444;
            border-color: #fca5a5;
        }}
        .chip-clear-all {{
            background: #f1f5f9;
            color: #ef4444;
            border-color: #fecaca;
            font-weight: 800;
        }}
        .chip-clear-all:hover {{
            background: #ef4444;
            color: #ffffff;
            border-color: #ef4444;
        }}

        /* 우측: 기준 상품 선택기 */
        .selector-controls-box {{
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            gap: 8px;
            min-width: 0;
        }}
        .selector-top-row {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 12px;
            flex-wrap: wrap;
        }}
        .input-fields-cluster {{
            display: flex;
            align-items: center;
            gap: 6px;
            flex-wrap: wrap;
        }}
        .primary-prd-input {{
            padding: 5px 8px;
            border: 1px solid #cbd5e1;
            border-radius: 6px;
            font-size: 0.82rem;
            font-weight: 600;
            color: #0f172a;
            outline: none;
            width: 140px;
        }}
        .home-extra-input {{
            padding: 5px 7px;
            border: 1px solid #cbd5e1;
            border-radius: 6px;
            font-size: 0.78rem;
            font-weight: 600;
            color: #0f172a;
            outline: none;
            width: 105px;
        }}
        .btn-query {{
            background: #0f172a;
            color: #ffffff;
            border: none;
            padding: 5px 14px;
            border-radius: 6px;
            font-size: 0.82rem;
            font-weight: 800;
            cursor: pointer;
            transition: background 0.15s ease;
        }}
        .btn-query:hover {{
            background: #2563eb;
        }}
        .btn-clear {{
            background: #ffffff;
            color: #ef4444;
            border: 1px solid #fca5a5;
            padding: 5px 10px;
            border-radius: 6px;
            font-size: 0.8rem;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.15s ease;
        }}
        .btn-clear:hover {{
            background: #fef2f2;
            border-color: #ef4444;
        }}
        .seed-instruction-text {{
            font-size: 0.75rem;
            color: #64748b;
            font-weight: 600;
        }}
        .seed-grid-row {{
            display: grid;
            grid-template-columns: repeat(12, 1fr);
            gap: 6px;
            overflow-x: auto;
            padding: 4px 2px;
        }}
        .seed-mini-card {{
            border: 1px solid #e2e8f0;
            border-radius: 6px;
            overflow: hidden;
            background: #ffffff;
            cursor: pointer;
            display: flex;
            flex-direction: column;
            align-items: center;
            text-align: center;
            padding: 3px;
            transition: border-color 0.15s ease, box-shadow 0.15s ease, background-color 0.15s ease;
            position: relative;
            user-select: none;
        }}
        .seed-mini-card:hover {{
            border-color: #64748b;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.08);
        }}
        .seed-mini-card.active {{
            border-color: #2563eb;
            background: #eff6ff;
            box-shadow: 0 0 0 2px rgba(37,99,235,0.3);
        }}
        .seed-mini-rank {{
            position: absolute;
            top: 4px;
            left: 4px;
            background: rgba(15, 23, 42, 0.78);
            color: #ffffff;
            font-size: 9.5px;
            font-weight: 800;
            padding: 1.5px 4.5px;
            border-radius: 3px;
            line-height: 1.1;
            z-index: 2;
            letter-spacing: -0.2px;
            box-shadow: 0 1px 2px rgba(0,0,0,0.3);
            pointer-events: none;
        }}
        .seed-mini-rank.top-rank {{
            background: #ea580c;
        }}
        .best-link-btn {{
            display: inline-flex;
            align-items: center;
            gap: 3px;
            font-size: 0.72rem;
            font-weight: 700;
            color: #2563eb;
            background: #eff6ff;
            border: 1px solid #bfdbfe;
            border-radius: 4px;
            padding: 1.5px 7px;
            text-decoration: none;
            transition: all 0.15s ease;
        }}
        .best-link-btn:hover {{
            background: #dbeafe;
            border-color: #93c5fd;
            color: #1d4ed8;
        }}
        .seed-mini-badge {{
            position: absolute;
            top: 4px;
            right: 4px;
            background: #2563eb;
            color: #ffffff;
            font-size: 9px;
            font-weight: 800;
            padding: 1px 3px;
            border-radius: 3px;
            display: none;
        }}
        .seed-mini-card.active .seed-mini-badge {{
            display: block;
        }}
        .seed-mini-img {{
            width: 100%;
            aspect-ratio: 1 / 1.1;
            object-fit: cover;
            border-radius: 3px;
            background-color: #f8fafc;
        }}
        .seed-mini-cat {{
            font-size: 0.68rem;
            font-weight: 700;
            color: #0f172a;
            margin-top: 2px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            width: 100%;
        }}
        .seed-mini-prdno {{
            font-size: 0.62rem;
            color: #64748b;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            width: 100%;
        }}

        /* home / lf API 전용: 홈 추천 탭 바 */
        .home-seed-tabs-section {{
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 10px;
            padding: 10px 14px;
            margin-bottom: 12px;
            box-shadow: 0 1px 2px rgba(0,0,0,0.02);
        }}
        .home-seed-tabs-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 8px;
        }}
        .home-seed-tabs-title {{
            font-size: 0.84rem;
            font-weight: 800;
            color: #0f172a;
            display: flex;
            align-items: center;
            gap: 6px;
        }}
        .home-seed-cards-container {{
            display: flex;
            gap: 8px;
            overflow-x: auto;
            padding-bottom: 2px;
        }}
        .home-seed-card {{
            width: 110px;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 5px;
            background: #ffffff;
            cursor: pointer;
            display: flex;
            flex-direction: column;
            align-items: center;
            text-align: center;
            flex-shrink: 0;
            transition: all 0.15s ease;
            position: relative;
        }}
        .home-seed-card:hover {{
            border-color: #94a3b8;
            transform: translateY(-2px);
        }}
        .home-seed-card.active {{
            border-color: #2563eb;
            background: #eff6ff;
            box-shadow: 0 0 0 2px rgba(37,99,235,0.3);
        }}
        .home-foryou-card {{
            width: 110px;
            height: 124px;
            border: 1px solid #cbd5e1;
            border-radius: 8px;
            background: #f8fafc;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            flex-shrink: 0;
            transition: all 0.15s ease;
        }}
        .home-foryou-card:hover {{
            border-color: #2563eb;
            background: #eff6ff;
        }}
        .home-foryou-card.active {{
            border-color: #2563eb;
            background: #2563eb;
            color: #ffffff !important;
            box-shadow: 0 2px 6px rgba(37,99,235,0.3);
        }}
        .home-foryou-card.active .foryou-title, .home-foryou-card.active .foryou-desc {{
            color: #ffffff !important;
        }}
        .foryou-title {{
            font-size: 1rem;
            font-weight: 800;
            color: #0f172a;
        }}
        .foryou-desc {{
            font-size: 0.72rem;
            font-weight: 600;
            color: #64748b;
            margin-top: 2px;
        }}
        .home-seed-card-img {{
            width: 100%;
            height: 75px;
            object-fit: cover;
            border-radius: 4px;
            background: #f1f5f9;
        }}
        .home-seed-type-tag {{
            font-size: 9px;
            font-weight: 800;
            padding: 1px 5px;
            border-radius: 3px;
            margin-top: 4px;
        }}
        .tag-recent {{ background: #eff6ff; color: #2563eb; }}
        .tag-basket {{ background: #fdf2f8; color: #db2777; }}
        .tag-wish {{ background: #fef2f2; color: #ef4444; }}

        /* 3단: 추천 결과 메인 뷰 (최소 높이 확보로 탭 전환 시 흔들림 방지) */
        .results-section {{
            display: flex;
            flex-direction: column;
            flex: 1;
            min-height: 850px;
        }}
        /* 3단: 추천 결과 메인 탭 바 (호출 API 전면 배치 및 스크롤바 원천 차단) */
        .results-tab-bar {{
            display: flex;
            align-items: center;
            justify-content: flex-start;
            gap: 12px;
            border-bottom: 2px solid #e2e8f0;
            margin-bottom: 12px;
            padding-bottom: 0;
            flex-wrap: nowrap;
            overflow: visible;
            white-space: nowrap;
        }}
        .results-tab-bar::-webkit-scrollbar {{
            display: none;
            width: 0;
            height: 0;
        }}
        .active-api-badge-box {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            background: #eff6ff;
            border: 1px solid #bfdbfe;
            padding: 4px 10px;
            border-radius: 6px;
            flex-shrink: 0;
        }}
        .active-api-label {{
            font-size: 0.72rem;
            font-weight: 800;
            color: #1d4ed8;
            background: #dbeafe;
            padding: 2px 6px;
            border-radius: 4px;
            white-space: nowrap;
        }}
        .active-api-info-text {{
            font-size: 0.82rem;
            font-weight: 700;
            color: #1e40af;
            font-family: monospace, -apple-system, BlinkMacSystemFont, sans-serif;
            white-space: nowrap;
        }}
        .kw-search-link-btn {{
            display: inline-flex;
            align-items: center;
            gap: 3px;
            font-size: 0.72rem;
            font-weight: 700;
            color: #2563eb;
            background: #ffffff;
            border: 1px solid #bfdbfe;
            border-radius: 4px;
            padding: 2px 8px;
            text-decoration: none;
            transition: all 0.15s ease;
            white-space: nowrap;
            flex-shrink: 0;
        }}
        .kw-search-link-btn:hover {{
            background: #eff6ff;
            border-color: #93c5fd;
            color: #1d4ed8;
        }}
        .v-divider-tab {{
            width: 1px;
            height: 20px;
            background-color: #cbd5e1;
            flex-shrink: 0;
        }}
        .tab-btn-cluster {{
            display: flex;
            gap: 4px;
            flex-shrink: 0;
        }}
        .result-tab-btn {{
            padding: 7px 14px;
            font-size: 0.88rem;
            font-weight: 700;
            color: #64748b;
            background: none;
            border: none;
            cursor: pointer;
            border-bottom: 2px solid transparent;
            margin-bottom: -2px;
            transition: all 0.15s ease;
            white-space: nowrap;
        }}
        .result-tab-btn:hover {{ color: #0f172a; }}
        .result-tab-btn.active {{
            color: #2563eb;
            border-bottom-color: #2563eb;
            font-weight: 800;
        }}

        .tab-pane {{
            display: none;
            min-height: 780px;
        }}
        .tab-pane.active {{
            display: block;
            min-height: 780px;
        }}

        /* 10열 그리드 */
        .grid-10-container {{
            display: grid;
            grid-template-columns: repeat(10, 1fr);
            gap: 10px;
            min-height: 400px;
        }}
        .product-card {{
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            overflow: hidden;
            background: #ffffff;
            box-shadow: 0 1px 2px rgba(0,0,0,0.02);
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            transition: border-color 0.15s ease, box-shadow 0.15s ease;
            position: relative;
        }}
        .product-card:hover {{
            border-color: #94a3b8;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.06);
        }}
        /* [내가 본] 선택 상품 강조 카드 스타일 */
        .product-card.card-origin {{
            border: 2px solid #ef4444 !important;
            background: #fff5f5 !important;
            box-shadow: 0 4px 12px rgba(239, 68, 68, 0.18) !important;
        }}
        .product-img-wrap {{
            position: relative;
            width: 100%;
            aspect-ratio: 1 / 1;
            background-color: #f8fafc;
            overflow: hidden;
        }}
        .product-img {{
            width: 100%;
            height: 100%;
            object-fit: cover;
            object-position: center;
            transition: transform 0.2s ease;
        }}
        .product-card:hover .product-img {{
            transform: scale(1.04);
        }}
        .rank-badge {{
            position: absolute;
            top: 5px;
            left: 5px;
            background: rgba(15, 23, 42, 0.85);
            backdrop-filter: blur(4px);
            color: #ffffff;
            font-size: 10px;
            font-weight: 800;
            padding: 2px 5px;
            border-radius: 4px;
            z-index: 2;
        }}
        .rank-top1 {{
            background: linear-gradient(135deg, #f59e0b, #d97706) !important;
            box-shadow: 0 2px 6px rgba(245, 158, 11, 0.4);
        }}
        .rank-top2, .rank-top3 {{
            background: linear-gradient(135deg, #334155, #1e293b) !important;
        }}
        .origin-badge {{
            position: absolute;
            top: 5px;
            right: 5px;
            background: #ef4444;
            color: #ffffff;
            font-size: 10px;
            font-weight: 800;
            padding: 2px 6px;
            border-radius: 4px;
            z-index: 2;
            box-shadow: 0 2px 4px rgba(239,68,68,0.3);
        }}
        .product-info {{
            padding: 8px;
        }}
        .product-brand-row {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 4px;
            margin-bottom: 2px;
        }}
        .brand-name {{
            font-size: 0.72rem;
            color: #64748b;
            font-weight: 700;
            text-transform: uppercase;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            flex: 1;
            min-width: 0;
        }}
        .product-card-prdno {{
            font-size: 0.65rem;
            font-weight: 700;
            color: #2563eb;
            background: #eff6ff;
            border: 1px solid #dbeafe;
            padding: 1px 4px;
            border-radius: 3px;
            font-family: monospace, -apple-system, BlinkMacSystemFont, sans-serif;
            white-space: nowrap;
            flex-shrink: 0;
            line-height: 1.3;
        }}
        .product-name {{
            font-size: 0.78rem;
            font-weight: 600;
            color: #0f172a;
            height: 34px;
            overflow: hidden;
            text-overflow: ellipsis;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            line-height: 1.35;
            margin-bottom: 6px;
        }}
        .price-wrap {{
            display: flex;
            align-items: baseline;
            gap: 4px;
            margin-bottom: 4px;
            flex-wrap: wrap;
        }}
        .discount-rate {{
            font-size: 0.88rem;
            color: #f43f5e;
            font-weight: 800;
        }}
        .sale-price {{
            font-size: 0.88rem;
            font-weight: 800;
            color: #0f172a;
        }}
        .normal-price {{
            font-size: 0.7rem;
            color: #94a3b8;
            text-decoration: line-through;
        }}
        .badge-chip-container {{
            display: flex;
            flex-wrap: wrap;
            gap: 3px;
            margin-top: 4px;
        }}
        .badge-chip-item {{
            font-size: 10px;
            padding: 1px 5px;
            border-radius: 4px;
            font-weight: 600;
            display: inline-flex;
            align-items: center;
            gap: 2px;
        }}
        .badge-blue {{ background: #eff6ff; color: #2563eb; border: 1px solid #dbeafe; }}
        .badge-amber {{ background: #fffbeb; color: #d97706; border: 1px solid #fef3c7; }}
        .badge-gray {{ background: #f1f5f9; color: #475569; border: 1px solid #e2e8f0; }}
        .badge-red {{ background: #fef2f2; color: #ef4444; border: 1px solid #fecaca; }}
        .badge-purple {{ background: #f5f3ff; color: #7c3aed; border: 1px solid #ddd6fe; }}
        .badge-emerald {{ background: #ecfdf5; color: #059669; border: 1px solid #a7f3d0; }}
        .badge-cyan {{ background: #ecfeff; color: #0891b2; border: 1px solid #cffafe; }}

        /* 데이터 테이블 */
        .data-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.85rem;
            background: #ffffff;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 1px 3px rgba(0,0,0,0.02);
            border: 1px solid #e2e8f0;
        }}
        .data-table th {{
            background-color: #f8fafc;
            color: #475569;
            font-weight: 700;
            padding: 11px 14px;
            border-bottom: 1px solid #e2e8f0;
            text-align: left;
        }}
        .data-table td {{
            padding: 10px 14px;
            border-bottom: 1px solid #f1f5f9;
            color: #334155;
            vertical-align: middle;
        }}
        .data-table tr:hover {{ background-color: #f8fafc; }}

        /* 슬림 스크롤바 */
        ::-webkit-scrollbar {{ width: 6px; height: 6px; }}
        ::-webkit-scrollbar-track {{ background: transparent; }}
        ::-webkit-scrollbar-thumb {{ background: #cbd5e1; border-radius: 3px; }}
        ::-webkit-scrollbar-thumb:hover {{ background: #94a3b8; }}

        /* JSON 트리 */
        .json-key {{ color: #38bdf8 !important; font-weight: 700; }}
        .json-string {{ color: #4ade80 !important; }}
        .json-number {{ color: #fb923c !important; font-weight: 700; }}
        .json-boolean {{ color: #c084fc !important; font-weight: 700; }}
        .json-null {{ color: #f43f5e !important; font-weight: 700; }}
        .json-toggle {{ cursor: pointer; user-select: none; display: inline-block; width: 13px; font-size: 9px; color: #94a3b8; }}
        .json-bracket {{ color: #cbd5e1; font-weight: bold; }}
        .json-children {{ padding-left: 18px; border-left: 1px dotted #334155; margin-left: 4px; }}
        .json-node-row {{ line-height: 1.55; word-break: break-all; }}
        .json-ctrl-btn {{
            background: #334155;
            color: #f8fafc;
            border: none;
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: 600;
            cursor: pointer;
        }}
        .json-ctrl-btn:hover {{ background: #475569; }}

        /* 키워드 트렌드 전용 2단 패널 */
        .keyword-trend-panel {{
            display: flex;
            flex-direction: column;
            gap: 8px;
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 10px;
            padding: 10px 14px;
            margin-bottom: 12px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.03);
        }}
        .kw-controls-row {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 12px;
            flex-wrap: nowrap;
        }}
        .kw-input-cluster {{
            display: flex;
            align-items: center;
            gap: 6px;
            flex: 1;
            min-width: 0;
        }}
        .primary-kw-input {{
            width: 140px;
            padding: 4px 8px;
            font-size: 0.82rem;
            font-weight: 700;
            border: 1px solid #cbd5e1;
            border-radius: 5px;
            color: #0f172a;
            outline: none;
        }}
        .primary-kw-input:focus {{
            border-color: #2563eb;
            box-shadow: 0 0 0 2px rgba(37,99,235,0.12);
        }}
        .kw-filter-input {{
            width: 130px;
            padding: 4px 8px;
            font-size: 0.78rem;
            border: 1px solid #e2e8f0;
            border-radius: 5px;
            color: #475569;
            outline: none;
        }}
        .kw-filter-input:focus {{
            border-color: #94a3b8;
        }}
        .llm-meta-cluster {{
            display: flex;
            align-items: center;
            gap: 8px;
            flex-shrink: 0;
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            padding: 3px 10px;
            border-radius: 6px;
            font-size: 0.74rem;
        }}
        .llm-meta-item {{
            display: flex;
            align-items: center;
            gap: 4px;
        }}
        .llm-meta-label {{
            color: #64748b;
            font-weight: 700;
        }}
        .llm-meta-val {{
            color: #0f172a;
            font-weight: 600;
        }}
        .kw-chips-container {{
            display: flex;
            align-items: center;
            gap: 5px;
            overflow-x: auto;
            padding: 2px 0 4px 0;
            white-space: nowrap;
            scrollbar-width: thin;
        }}
        .kw-chips-container:focus {{
            outline: none;
        }}
        .kw-chip {{
            display: inline-flex;
            align-items: center;
            padding: 3px 9px;
            border-radius: 14px;
            font-size: 0.76rem;
            font-weight: 600;
            color: #475569;
            background: #f1f5f9;
            border: 1px solid #e2e8f0;
            cursor: pointer;
            transition: all 0.12s ease;
            user-select: none;
            flex-shrink: 0;
        }}
        .kw-chip:hover {{
            background: #e2e8f0;
            color: #0f172a;
        }}
        .kw-chip.active {{
            background: #2563eb;
            color: #ffffff;
            border-color: #2563eb;
            font-weight: 700;
            box-shadow: 0 1px 3px rgba(37,99,235,0.25);
        }}
        .kw-ai-content-card {{
            display: flex;
            flex-direction: column;
            gap: 8px;
            border-top: 1px dashed #e2e8f0;
            padding-top: 8px;
        }}
        .curation-summary-wrap {{
            display: flex;
            align-items: center;
            gap: 8px;
            background: linear-gradient(90deg, #eff6ff 0%, #f0fdf4 100%);
            border: 1px solid #bfdbfe;
            border-radius: 6px;
            padding: 6px 12px;
        }}
        .curation-summary-badge {{
            font-size: 0.72rem;
            font-weight: 800;
            color: #1d4ed8;
            background: #dbeafe;
            padding: 2px 6px;
            border-radius: 4px;
            flex-shrink: 0;
        }}
        .curation-summary-text {{
            font-size: 0.82rem;
            font-weight: 700;
            color: #0f172a;
            line-height: 1.4;
        }}
        .guide-text-section {{
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 6px;
            padding: 8px 12px;
        }}
        .guide-header-row {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 4px;
            gap: 8px;
        }}
        .guide-title {{
            font-size: 0.75rem;
            font-weight: 800;
            color: #475569;
        }}
        .extracted-tags-header {{
            display: flex;
            align-items: center;
            gap: 4px;
            flex-wrap: wrap;
        }}
        .guide-text-body {{
            font-size: 0.84rem;
            line-height: 1.6;
            color: #1e293b;
        }}
        .guide-text-body b,
        .guide-text-body strong {{
            color: #1d4ed8;
            font-weight: 800;
            background: #eff6ff;
            padding: 1px 4px;
            border-radius: 3px;
        }}
        .extracted-signals-box {{
            display: flex;
            flex-direction: column;
            gap: 4px;
            font-size: 0.78rem;
        }}
        .badge-brand {{
            background: #eff6ff;
            color: #2563eb;
            border: 1px solid #bfdbfe;
            font-weight: 700;
        }}
        .badge-brand:hover {{
            background: #dbeafe;
        }}
        .badge-media {{
            background: #f1f5f9;
            color: #475569;
            border: 1px solid #e2e8f0;
        }}
        .articles-wrapper {{
            border: 1px solid #e2e8f0;
            border-radius: 6px;
            overflow: hidden;
            margin-top: 2px;
        }}
        .articles-header-btn {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 6px 12px;
            background: #f8fafc;
            cursor: pointer;
            user-select: none;
        }}
        .articles-header-btn:hover {{
            background: #f1f5f9;
        }}
        .articles-list-container {{
            padding: 8px 12px;
            background: #ffffff;
            border-top: 1px solid #e2e8f0;
            max-height: none;
            overflow: visible;
        }}
    </style>
</head>
<body>
    <div class="app-wrapper">
        <!-- 1단: 최상단 글로벌 통합 네비게이션 헤더 -->
        <header class="top-global-header">
            <div class="header-left-cluster">
                <div class="site-switch-group">
                    <button id="btnSiteHalf" class="site-btn active" onclick="changeSite('1')">하프클럽</button>
                    <button id="btnSiteBori" class="site-btn" onclick="changeSite('2')">보리보리</button>
                </div>
                <div class="v-divider"></div>
                <div class="model-tabs-group" id="modelTabsGroup"></div>
            </div>

            <div class="header-right-cluster">
                <div class="k-input-box">
                    <span>k:</span>
                    <input type="number" id="sizeInput" class="k-input" value="50" min="1" max="200"/>
                </div>
                <button id="btnCopyUrl" class="btn-copy-url" onclick="copyCurrentUrl()">URL 복사</button>
                <div id="statusBadge" class="status-badge">대기 중...</div>
            </div>
        </header>

        <!-- 2단: 추천 기준 상품 설정 및 대상 정보 일체형 카드 -->
        <section class="criterion-panel" id="criterionPanel">
            <div class="target-preview-box">
                <div>
                    <div class="target-header-row">
                        <div class="target-panel-title">
                            <span>추천 기준 대상 상품</span>
                            <span id="targetCountBadge" style="font-size:10px; font-weight:800; background:#eff6ff; color:#2563eb; padding:1px 6px; border-radius:4px;">0개</span>
                        </div>
                        <a id="targetMallLink" href="#" target="_blank" rel="noopener noreferrer" style="text-decoration:none; color:#2563eb; font-size:0.75rem; font-weight:700; display:none;" title="쇼핑몰 상세 새 탭 열기">쇼핑몰 이동 ↗</a>
                    </div>
                    <div class="target-item-card">
                        <div class="target-thumb-wrap" id="targetThumbWrap">
                            <span style="font-size:0.7rem; color:#94a3b8;">선택 없음</span>
                        </div>
                        <div class="target-meta-details">
                            <div class="target-brand-row">
                                <span class="target-brand" id="targetBrandText">선택된 상품 없음</span>
                                <span class="target-selacnt" id="targetSelAcntBadge" style="display:none;"></span>
                            </div>
                            <span class="target-name" id="targetNameText" title="상품명">기준 상품을 선택하거나 상품번호를 입력하세요.</span>
                            <div class="target-price-row">
                                <span class="target-dc-price" id="targetPriceText">-</span>
                                <span class="target-rate" id="targetRateText"></span>
                            </div>
                            <span class="target-cat-path" id="targetCatPath">실시간 베스트 상품을 클릭하여 기준 상품을 지정할 수 있습니다.</span>
                        </div>
                    </div>
                </div>
                <div class="multi-chips-row" id="multiChipsContainer" style="display:none;"></div>
            </div>

            <div class="selector-controls-box">
                <div class="selector-top-row">
                    <div class="input-fields-cluster">
                        <span style="font-size:0.8rem; font-weight:700; color:#475569;">상품번호:</span>
                        <input type="text" id="directPrdInput" class="primary-prd-input" placeholder="단일 or 쉼표 다중"/>

                        <!-- [선택 해제] 버튼 -->
                        <button class="btn-clear" onclick="clearSelectedPrd()" title="선택된 기준 상품 모두 해제">선택 해제</button>

                        <!-- home / lf 전용 필드 -->
                        <div id="homeFieldsWrap" style="display:none; align-items:center; gap:5px;">
                            <input type="text" id="basketPrdInput" class="home-extra-input" placeholder="장바구니 prdNo"/>
                            <input type="text" id="wishPrdInput" class="home-extra-input" placeholder="좋아요 prdNo"/>
                            <input type="text" id="memNoInput" class="home-extra-input" style="width:80px;" placeholder="회원 memNo"/>
                            <label style="display:flex; align-items:center; gap:3px; font-size:0.78rem; font-weight:700; color:#475569; cursor:pointer;">
                                <input type="checkbox" id="selfYnCheck"/>
                                <span>휴리스틱</span>
                            </label>
                        </div>

                        <button class="btn-query" onclick="triggerFetch()">조회</button>
                    </div>

                    <div class="seed-instruction-text" id="seedStatusWrap" style="display:flex; align-items:center; gap:6px; flex-wrap:wrap;">
                        <span id="seedStatusText">실시간 베스트 12개</span>
                        <a id="bestPageLink" href="https://www.halfclub.com/best" target="_blank" rel="noopener noreferrer" class="best-link-btn" title="해당 사이트 실시간 베스트 상품 페이지 새창 열기">베스트 바로가기 ↗</a>
                        <span style="color:#94a3b8; font-size:0.75rem;">(클릭: 선택 / Ctrl+클릭: 다중선택)</span>
                    </div>
                </div>

                <div class="seed-grid-row" id="seedGridContainer"></div>
            </div>
        </section>

        <!-- 2단 B: 키워드 트렌드 AI 큐레이션 전용 패널 (keyword-trend 선택 시 표출) -->
        <section class="keyword-trend-panel" id="keywordTrendPanel" style="display:none;">
            <!-- 키워드 컨트롤러 및 LLM 메타 바 -->
            <div class="kw-controls-row">
                <div class="kw-input-cluster">
                    <span style="font-size:0.82rem; font-weight:700; color:#334155; flex-shrink:0;">트렌드 키워드:</span>
                    <input type="text" id="directKwInput" class="primary-kw-input" placeholder="키워드 입력"/>
                    <button class="btn-query" onclick="triggerKeywordFetch()">조회</button>
                    <a id="kwDirectSearchLink" href="#" target="_blank" rel="noopener noreferrer" class="best-link-btn" style="display:inline-flex;" title="선택된 키워드로 쇼핑몰 검색 결과 새창 열기">검색 바로가기 ↗</a>
                    <input type="text" id="kwFilterInput" class="kw-filter-input" placeholder="키워드 목록 필터..." oninput="filterKeywordsList(this.value)"/>
                    <span style="font-size:0.72rem; color:#64748b; font-weight:600; margin-left:2px;" title="키보드 방향키로 이전/다음 키워드를 즉시 탐색할 수 있습니다.">(← → 키로 탐색)</span>
                </div>

                <div class="llm-meta-cluster">
                    <div class="llm-meta-item" title="적용된 LLM Provider 및 모델">
                        <span class="llm-meta-label">LLM:</span>
                        <span class="llm-meta-val" id="llmModelText">-</span>
                    </div>
                    <div class="llm-meta-item" title="LLM 토큰 사용량">
                        <span class="llm-meta-label">토큰:</span>
                        <span class="llm-meta-val" id="tokenUsageText">-</span>
                    </div>
                    <div class="llm-meta-item" title="카테고리/성별 필터링 상태">
                        <span class="llm-meta-label">필터:</span>
                        <span id="filterBadgesText" style="display:inline-flex; gap:4px;">-</span>
                    </div>
                    <div class="llm-meta-item" title="큐레이션 생성/수정 일시">
                        <span class="llm-meta-label">일시:</span>
                        <span class="llm-meta-val" id="createDtText">-</span>
                    </div>
                </div>
            </div>

            <!-- 타겟 키워드 칩 스트립 -->
            <div class="kw-chips-container" id="kwChipsContainer" tabindex="0" title="좌우 방향키(←, →)로 키워드를 탐색할 수 있습니다."></div>

            <!-- AI 큐레이션 가이드, 신호 칩, 뉴스 기사 및 최종 요약 카드 -->
            <div class="kw-ai-content-card">
                <!-- 가이드 텍스트 & 추출 태그 영역 -->
                <div class="guide-text-section">
                    <div class="guide-header-row">
                        <span class="guide-title">스타일 트렌드 가이드 문구</span>
                        <div class="extracted-tags-header" id="extractedTagsHeader"></div>
                    </div>
                    <div class="guide-text-body" id="guideTextBody">키워드를 선택하거나 조회하세요.</div>
                </div>

                <!-- 추출 브랜드 / 키워드 / 검색 키워드 칩 영역 -->
                <div class="extracted-signals-box">
                    <div id="extractedBrandsWrap"></div>
                    <div id="extractedKeywordsWrap"></div>
                    <div id="extractedSearchKeywordsWrap"></div>
                </div>

                <!-- 참고 뉴스 기사 아코디언 -->
                <div class="articles-wrapper" id="articlesWrapper" style="display:none;">
                    <div class="articles-header-btn" onclick="toggleArticlesAccordion()">
                        <div style="display:flex; align-items:center; gap:8px;">
                            <span style="font-weight:700; color:#334155; font-size:0.85rem;">참고 뉴스 기사</span>
                            <span class="badge-chip-item badge-blue" id="articlesCountBadge">0건</span>
                        </div>
                        <span id="articlesToggleIcon" style="font-size:0.8rem; color:#64748b; font-weight:700;">목록 접기 ▲</span>
                    </div>
                    <div class="articles-list-container" id="articlesListContainer"></div>
                </div>

                <!-- 큐레이션 요약문 (뉴스 기사 아래에 최종 결론 및 요약으로 배치) -->
                <div class="curation-summary-wrap" id="curationSummaryWrap" style="display:none;">
                    <span class="curation-summary-badge">AI 큐레이션 요약</span>
                    <span class="curation-summary-text" id="curationSummaryText"></span>
                </div>
            </div>
        </section>

        <!-- [recomm_home_hf.py 복원] home / lf API 전용: 추천 탭 및 시드 상품 목록 바 -->
        <section class="home-seed-tabs-section" id="homeSeedTabsSection" style="display:none;">
            <div class="home-seed-tabs-header">
                <div class="home-seed-tabs-title">
                    <span>행동 시드 상품 연계 탭</span>
                    <span id="activeSeedStatus" style="font-size:0.75rem; font-weight:700; color:#2563eb; background:#eff6ff; padding:2px 8px; border-radius:4px;">전체 맞춤 추천 (FORYOU)</span>
                </div>
                <span style="font-size:0.75rem; color:#64748b;">시드 카드를 클릭하면 대상 상품 카드와 하단 유사 상품이 즉시 연동됩니다.</span>
            </div>
            <div class="home-seed-cards-container" id="homeSeedCardsContainer"></div>
        </section>

        <!-- 3단: 추천 결과 메인 뷰 (100% 가로 폭) -->
        <main class="results-section">
            <div class="results-tab-bar">
                <div class="active-api-badge-box" title="현재 호출된 추천 API 엔드포인트">
                    <span class="active-api-label">호출 API</span>
                    <span class="active-api-info-text" id="activeApiUrlSnippet">-</span>
                    <a id="kwSearchPageLink" href="#" target="_blank" rel="noopener noreferrer" class="kw-search-link-btn" style="display:none;" title="선택된 키워드로 쇼핑몰 검색 결과 새창 열기">검색 ↗</a>
                </div>
                <div class="v-divider-tab"></div>
                <div class="tab-btn-cluster">
                    <button class="result-tab-btn active" id="tabBtnGrid" onclick="switchViewTab('grid')">추천 상품 그리드</button>
                    <button class="result-tab-btn" id="tabBtnTable" onclick="switchViewTab('table')">추천 상품 데이터 확인</button>
                    <button class="result-tab-btn" id="tabBtnRaw" onclick="switchViewTab('raw')">API JSON 데이터 확인</button>
                    <button class="result-tab-btn" id="tabBtnPrompt" onclick="switchViewTab('prompt')" style="display:none;">프롬프트 메타 정보</button>
                </div>
            </div>

            <section class="tab-pane active" id="tabContentGrid">
                <div class="grid-10-container" id="productGridContainer">
                    <div style="grid-column:1/-1; padding:60px 20px; text-align:center; color:#64748b;">기준 상품을 선택하면 추천 데이터가 표출됩니다.</div>
                </div>
            </section>

            <section class="tab-pane" id="tabContentTable">
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>순번</th>
                            <th>구분</th>
                            <th>상품번호</th>
                            <th>브랜드</th>
                            <th>상품명</th>
                            <th>협력사(selAcntNo)</th>
                            <th>판매가</th>
                            <th>정가</th>
                            <th>할인율</th>
                            <th>추천 스코어</th>
                            <th>ES 스코어</th>
                            <th>카테고리</th>
                        </tr>
                    </thead>
                    <tbody id="productTableBody">
                        <tr><td colspan="12" style="text-align:center; padding:30px; color:#64748b;">데이터를 불러오는 중입니다...</td></tr>
                    </tbody>
                </table>
            </section>

            <section class="tab-pane" id="tabContentRaw">
                <div style="background:#0f172a; border-radius:8px; border:1px solid #1e293b; overflow:hidden;">
                    <div style="display:flex; align-items:center; justify-content:space-between; padding:10px 16px; background:#1e293b; border-bottom:1px solid #334155;">
                        <span id="calledApiUrlFull" style="font-size:0.83rem; font-weight:600; color:#94a3b8; font-family:monospace; word-break:break-all;">-</span>
                        <div style="display:flex; align-items:center; gap:6px; flex-shrink:0;">
                            <button class="json-ctrl-btn" onclick="openApiUrlInNewTab()">새 창 열기 ↗</button>
                            <button class="json-ctrl-btn" onclick="copyApiUrlToClipboard()">URL 복사</button>
                            <button class="json-ctrl-btn" onclick="expandAllJson('rawJsonBody')">전체 펼치기</button>
                            <button class="json-ctrl-btn" onclick="collapseAllJson('rawJsonBody')">전체 접기</button>
                            <button id="btnCopyJson" class="json-ctrl-btn" onclick="copyJsonTextToClipboard()">내용 복사</button>
                        </div>
                    </div>
                    <div style="padding:14px 16px; background:#0f172a; overflow:visible;">
                        <div id="rawJsonBody"></div>
                    </div>
                </div>
            </section>

            <!-- 탭 4: LLM 프롬프트 & 산출 상세 인스펙터 (keyword-trend 전용) -->
            <section class="tab-pane" id="tabContentPrompt">
                <div style="display:flex; flex-direction:column; gap:16px;">
                    <h3 style="font-size:0.95rem; font-weight:800; color:#0f172a; margin-bottom:2px; display:flex; align-items:center; gap:8px;">
                        <span>STAGE 1 : 스타일 트렌드 가이드 작성 프롬프트 & LLM 산출</span>
                    </h3>

                    <!-- 1단계 시스템 프롬프트 카드 -->
                    <div id="cardSysStage1" style="background:#0f172a; border-radius:8px; border:1px solid #1e293b; box-shadow:0 1px 3px rgba(0,0,0,0.2); overflow:hidden;">
                        <div style="display:flex; align-items:center; justify-content:space-between; padding:8px 14px; background:#1e293b; border-bottom:1px solid #334155;">
                            <div style="display:flex; align-items:center; gap:10px;">
                                <span style="background:#059669; color:#ffffff; font-size:11px; font-weight:800; padding:2px 7px; border-radius:4px;">system_prompt</span>
                                <span style="font-size:0.8rem; font-weight:700; color:#94a3b8;">LLM 키워드 트렌드 가이드 생성 프롬프트</span>
                            </div>
                            <div style="display:flex; align-items:center; gap:6px;">
                                <button class="json-ctrl-btn" onclick="expandAllJson('promptSysStage1')">전체 펼치기</button>
                                <button class="json-ctrl-btn" onclick="collapseAllJson('promptSysStage1')">전체 접기</button>
                                <button id="btnCopySys1" onclick="copyPromptTextToClipboard('promptSysStage1', 'btnCopySys1')" class="json-ctrl-btn">내용 복사</button>
                            </div>
                        </div>
                        <div style="padding:12px 14px; background:#0f172a; overflow:visible;">
                            <div id="promptSysStage1" class="json-tree-container"></div>
                        </div>
                    </div>

                    <!-- 1단계 입력 User Prompt 카드 -->
                    <div id="cardUserStage1" style="display:none; background:#0f172a; border-radius:8px; border:1px solid #1e293b; box-shadow:0 1px 3px rgba(0,0,0,0.2); overflow:hidden;">
                        <div style="display:flex; align-items:center; justify-content:space-between; padding:8px 14px; background:#1e293b; border-bottom:1px solid #334155;">
                            <div style="display:flex; align-items:center; gap:10px;">
                                <span style="background:#059669; color:#ffffff; font-size:11px; font-weight:800; padding:2px 7px; border-radius:4px;">user_prompt</span>
                                <span style="font-size:0.8rem; font-weight:700; color:#94a3b8;">LLM 키워드 트렌드 가이드 생성 프롬프트 (실 데이터)</span>
                            </div>
                            <div style="display:flex; align-items:center; gap:6px;">
                                <button class="json-ctrl-btn" onclick="expandAllJson('promptUserStage1')">전체 펼치기</button>
                                <button class="json-ctrl-btn" onclick="collapseAllJson('promptUserStage1')">전체 접기</button>
                                <button id="btnCopyUser1" onclick="copyPromptTextToClipboard('promptUserStage1', 'btnCopyUser1')" class="json-ctrl-btn">내용 복사</button>
                            </div>
                        </div>
                        <div style="padding:12px 14px; background:#0f172a; overflow:visible;">
                            <div id="promptUserStage1" class="json-tree-container"></div>
                        </div>
                    </div>

                    <!-- 1단계 LLM 결과 JSON 카드 -->
                    <div id="cardResultStage1" style="display:none; background:#0f172a; border-radius:8px; border:1px solid #1e293b; box-shadow:0 1px 3px rgba(0,0,0,0.2); overflow:hidden;">
                        <div style="display:flex; align-items:center; justify-content:space-between; padding:8px 14px; background:#1e293b; border-bottom:1px solid #334155;">
                            <div style="display:flex; align-items:center; gap:10px;">
                                <span style="background:#8b5cf6; color:#ffffff; font-size:11px; font-weight:800; padding:2px 7px; border-radius:4px;">response</span>
                                <span style="font-size:0.8rem; font-weight:700; color:#94a3b8;">LLM 응답 (JSON 트리 접기/펼치기 가능)</span>
                            </div>
                            <div style="display:flex; align-items:center; gap:6px;">
                                <button class="json-ctrl-btn" onclick="expandAllJson('promptResultStage1')">전체 펼치기</button>
                                <button class="json-ctrl-btn" onclick="collapseAllJson('promptResultStage1')">전체 접기</button>
                                <button id="btnCopyResult1" onclick="copyPromptTextToClipboard('promptResultStage1', 'btnCopyResult1')" class="json-ctrl-btn">내용 복사</button>
                            </div>
                        </div>
                        <div style="padding:12px 14px; background:#0f172a; overflow:visible;">
                            <div id="promptResultStage1" class="json-tree-container"></div>
                        </div>
                    </div>
                </div>

                <div style="display:flex; flex-direction:column; gap:16px; margin-top:14px;">
                    <h3 style="font-size:0.95rem; font-weight:800; color:#0f172a; margin-bottom:2px; display:flex; align-items:center; gap:8px;">
                        <span>STAGE 2 : 상품 큐레이션 및 정렬 프롬프트 & LLM 산출</span>
                    </h3>

                    <!-- 2단계 시스템 프롬프트 카드 -->
                    <div id="cardSysStage2" style="background:#0f172a; border-radius:8px; border:1px solid #1e293b; box-shadow:0 1px 3px rgba(0,0,0,0.2); overflow:hidden;">
                        <div style="display:flex; align-items:center; justify-content:space-between; padding:8px 14px; background:#1e293b; border-bottom:1px solid #334155;">
                            <div style="display:flex; align-items:center; gap:10px;">
                                <span style="background:#059669; color:#ffffff; font-size:11px; font-weight:800; padding:2px 7px; border-radius:4px;">system_prompt</span>
                                <span style="font-size:0.8rem; font-weight:700; color:#94a3b8;">LLM 키워드 트렌드 상품 선택 프롬프트</span>
                            </div>
                            <div style="display:flex; align-items:center; gap:6px;">
                                <button class="json-ctrl-btn" onclick="expandAllJson('promptSysStage2')">전체 펼치기</button>
                                <button class="json-ctrl-btn" onclick="collapseAllJson('promptSysStage2')">전체 접기</button>
                                <button id="btnCopySys2" onclick="copyPromptTextToClipboard('promptSysStage2', 'btnCopySys2')" class="json-ctrl-btn">내용 복사</button>
                            </div>
                        </div>
                        <div style="padding:12px 14px; background:#0f172a; overflow:visible;">
                            <div id="promptSysStage2" class="json-tree-container"></div>
                        </div>
                    </div>

                    <!-- 2단계 입력 User Prompt 카드 -->
                    <div id="cardUserStage2" style="display:none; background:#0f172a; border-radius:8px; border:1px solid #1e293b; box-shadow:0 1px 3px rgba(0,0,0,0.2); overflow:hidden;">
                        <div style="display:flex; align-items:center; justify-content:space-between; padding:8px 14px; background:#1e293b; border-bottom:1px solid #334155;">
                            <div style="display:flex; align-items:center; gap:10px;">
                                <span style="background:#059669; color:#ffffff; font-size:11px; font-weight:800; padding:2px 7px; border-radius:4px;">user_prompt</span>
                                <span style="font-size:0.8rem; font-weight:700; color:#94a3b8;">LLM 키워드 트렌드 상품 선택 프롬프트 (실 데이터)</span>
                            </div>
                            <div style="display:flex; align-items:center; gap:6px;">
                                <button class="json-ctrl-btn" onclick="expandAllJson('promptUserStage2')">전체 펼치기</button>
                                <button class="json-ctrl-btn" onclick="collapseAllJson('promptUserStage2')">전체 접기</button>
                                <button id="btnCopyUser2" onclick="copyPromptTextToClipboard('promptUserStage2', 'btnCopyUser2')" class="json-ctrl-btn">내용 복사</button>
                            </div>
                        </div>
                        <div style="padding:12px 14px; background:#0f172a; overflow:visible;">
                            <div id="promptUserStage2" class="json-tree-container"></div>
                        </div>
                    </div>

                    <!-- 2단계 LLM 결과 JSON 카드 -->
                    <div id="cardResultStage2" style="display:none; background:#0f172a; border-radius:8px; border:1px solid #1e293b; box-shadow:0 1px 3px rgba(0,0,0,0.2); overflow:hidden;">
                        <div style="display:flex; align-items:center; justify-content:space-between; padding:8px 14px; background:#1e293b; border-bottom:1px solid #334155;">
                            <div style="display:flex; align-items:center; gap:10px;">
                                <span style="background:#8b5cf6; color:#ffffff; font-size:11px; font-weight:800; padding:2px 7px; border-radius:4px;">response</span>
                                <span style="font-size:0.8rem; font-weight:700; color:#94a3b8;">LLM 응답 (JSON 트리 접기/펼치기 가능)</span>
                            </div>
                            <div style="display:flex; align-items:center; gap:6px;">
                                <button class="json-ctrl-btn" onclick="expandAllJson('promptResultStage2')">전체 펼치기</button>
                                <button class="json-ctrl-btn" onclick="collapseAllJson('promptResultStage2')">전체 접기</button>
                                <button id="btnCopyResult2" onclick="copyPromptTextToClipboard('promptResultStage2', 'btnCopyResult2')" class="json-ctrl-btn">내용 복사</button>
                            </div>
                        </div>
                        <div style="padding:12px 14px; background:#0f172a; overflow:visible;">
                            <div id="promptResultStage2" class="json-tree-container"></div>
                        </div>
                    </div>
                </div>
            </section>
        </main>
    </div>

    <script>
        const DOMAINS = {{
            HALFCLUB_WEB: "{HALFCLUB_WEB_URL}",
            HALFCLUB_API: "{HALFCLUB_API_URL}",
            HALFCLUB_CDN: "{HALFCLUB_CDN_URL}",
            HALFCLUB_PRD: "{HALFCLUB_PRD_URL}",
            BORIBORI_WEB: "{BORIBORI_WEB_URL}",
            BORIBORI_API: "{BORIBORI_API_URL}",
            BORIBORI_CDN: "{BORIBORI_CDN_URL}",
            BORIBORI_PRD: "{BORIBORI_PRD_URL}"
        }};

        const ML_TYPES_LIST = {ml_types_json};
        const KEYWORDS_LIST = {keywords_json_str};

        let currentSiteCd = {initial_site_json};
        let currentMlType = {initial_type_json};
        let currentPrdNo = {initial_prd_json};
        let currentKeyword = {initial_keyword_json};
        let currentK = {initial_k_json};
        let currentBasket = {initial_basket_json};
        let currentWish = {initial_wish_json};
        let currentMem = {initial_mem_json};
        let currentSelfYn = {initial_self_json} === 'true';
        let currentSelectedSeed = {initial_selected_seed_json};
        let currentTab = {initial_tab_json};

        let currentRawData = null;
        let currentApiUrl = '';
        let currentSeedProducts = [];
        let homeExtractedSeeds = [];
        let homeOriginalResults = [];
        let promptResDataMap = {{}};
        let recommendFlowTimer = null;
        let recommendRequestId = 0;
        let targetProductRequestId = 0;

        function debouncedExecuteRecommendFlow(delay = 150) {{
            if (recommendFlowTimer) clearTimeout(recommendFlowTimer);
            recommendFlowTimer = setTimeout(() => {{
                recommendFlowTimer = null;
                executeRecommendFlow();
            }}, delay);
        }}

        function getWebBaseUrl() {{
            return currentSiteCd === '2' ? DOMAINS.BORIBORI_WEB : DOMAINS.HALFCLUB_WEB;
        }}

        function getApiBaseUrl() {{
            return currentSiteCd === '2' ? DOMAINS.BORIBORI_API : DOMAINS.HALFCLUB_API;
        }}

        function getCdnBaseUrl() {{
            return currentSiteCd === '2' ? DOMAINS.BORIBORI_CDN : DOMAINS.HALFCLUB_CDN;
        }}

        function getPrdBaseUrl() {{
            return currentSiteCd === '2' ? DOMAINS.BORIBORI_PRD : DOMAINS.HALFCLUB_PRD;
        }}

        function getProductDetailUrl(prdNo) {{
            if (!prdNo || prdNo === '-') return '#';
            return `${{getPrdBaseUrl()}}/product/${{prdNo}}`;
        }}

        function getBestPageUrl() {{
            return currentSiteCd === '2' 
                ? 'https://m.boribori.co.kr/home/best' 
                : 'https://www.halfclub.com/best';
        }}

        function updateBestPageLink() {{
            const link = document.getElementById('bestPageLink');
            if (link) {{
                link.href = getBestPageUrl();
                link.textContent = currentSiteCd === '2' ? '보리보리 베스트 ↗' : '하프클럽 베스트 ↗';
                link.title = `${{currentSiteCd === '2' ? '보리보리' : '하프클럽'}} 실시간 베스트 상품 페이지 새창 열기`;
            }}
        }}

        function getKeywordSearchUrl(kw) {{
            const targetKw = encodeURIComponent(kw || currentKeyword || '');
            const base = getWebBaseUrl();
            return `${{base}}/search/${{targetKw}}`;
        }}

        function updateKeywordSearchLinks() {{
            const url = getKeywordSearchUrl(currentKeyword);
            const isKwModel = currentMlType === 'keyword-trend';
            const kwText = currentKeyword || '키워드';

            const link1 = document.getElementById('kwSearchPageLink');
            if (link1) {{
                link1.href = url;
                link1.textContent = `'${{kwText}}' 검색 ↗`;
                link1.title = `${{currentSiteCd === '2' ? '보리보리' : '하프클럽'}}에서 '${{kwText}}' 검색 결과 새창 열기`;
                link1.style.display = isKwModel ? 'inline-flex' : 'none';
            }}
            const link2 = document.getElementById('kwDirectSearchLink');
            if (link2) {{
                link2.href = url;
                link2.textContent = `'${{kwText}}' 검색 바로가기 ↗`;
                link2.title = `${{currentSiteCd === '2' ? '보리보리' : '하프클럽'}}에서 '${{kwText}}' 검색 결과 새창 열기`;
            }}
        }}

        function getImageUrl(imgPath) {{
            if (!imgPath) return '';
            if (imgPath.startsWith('http://') || imgPath.startsWith('https://')) return imgPath;
            return `${{getCdnBaseUrl()}}/rimg/330x440/contain/${{imgPath}}`;
        }}

        function getSelectedPrdList() {{
            if (!currentPrdNo) return [];
            return currentPrdNo.split(',').map(s => s.trim()).filter(Boolean);
        }}

        function isSeedCompatibleModel() {{
            return currentMlType === 'home' || currentMlType === 'lf';
        }}

        function updateUrlQuery() {{
            try {{
                let queryStr = `?siteCd=${{encodeURIComponent(currentSiteCd)}}&mlType=${{encodeURIComponent(currentMlType)}}&k=${{encodeURIComponent(currentK)}}&tab=${{encodeURIComponent(currentTab)}}`;
                if (currentMlType === 'keyword-trend') {{
                    queryStr += `&keyword=${{encodeURIComponent(currentKeyword)}}`;
                }} else {{
                    queryStr += `&prdNo=${{encodeURIComponent(currentPrdNo)}}&basketPrdNo=${{encodeURIComponent(currentBasket)}}&wishPrdNo=${{encodeURIComponent(currentWish)}}&memNo=${{encodeURIComponent(currentMem)}}&selfYn=${{currentSelfYn}}&seedPrdNo=${{encodeURIComponent(currentSelectedSeed)}}`;
                }}

                try {{
                    if (window.parent && window.parent.history && window.parent.history.replaceState) {{
                        let targetPath = queryStr;
                        if (window.parent.location && window.parent.location.pathname) {{
                            targetPath = window.parent.location.pathname + queryStr;
                        }}
                        window.parent.history.replaceState({{}}, '', targetPath);
                    }}
                }} catch (e) {{}}
                try {{
                    if (window.top && window.top.history && window.top.history.replaceState) {{
                        let targetPath = queryStr;
                        if (window.top.location && window.top.location.pathname) {{
                            targetPath = window.top.location.pathname + queryStr;
                        }}
                        window.top.history.replaceState({{}}, '', targetPath);
                    }}
                }} catch (e) {{}}
                if (window.history && window.history.replaceState) {{
                    window.history.replaceState({{}}, '', queryStr);
                }}
            }} catch (e) {{}}
        }}

        function copyCurrentUrl() {{
            const hostUrl = (window.parent && window.parent.location && window.parent.location.origin) 
                ? (window.parent.location.origin + window.parent.location.pathname)
                : (window.location.origin + window.location.pathname);
            let curUrl = `${{hostUrl}}?siteCd=${{encodeURIComponent(currentSiteCd)}}&mlType=${{encodeURIComponent(currentMlType)}}&k=${{encodeURIComponent(currentK)}}&tab=${{encodeURIComponent(currentTab)}}`;
            if (currentMlType === 'keyword-trend') {{
                curUrl += `&keyword=${{encodeURIComponent(currentKeyword)}}`;
            }} else {{
                curUrl += `&prdNo=${{encodeURIComponent(currentPrdNo)}}&basketPrdNo=${{encodeURIComponent(currentBasket)}}&wishPrdNo=${{encodeURIComponent(currentWish)}}&memNo=${{encodeURIComponent(currentMem)}}&selfYn=${{currentSelfYn}}&seedPrdNo=${{encodeURIComponent(currentSelectedSeed)}}`;
            }}

            navigator.clipboard.writeText(curUrl).then(() => {{
                const btn = document.getElementById('btnCopyUrl');
                if (btn) {{
                    const orig = btn.textContent;
                    btn.textContent = '복사완료!';
                    btn.style.background = '#dcfce7';
                    btn.style.color = '#15803d';
                    setTimeout(() => {{
                        btn.textContent = orig;
                        btn.style.background = '#f1f5f9';
                        btn.style.color = '#475569';
                    }}, 1500);
                }}
            }}).catch(() => {{
                alert('URL: ' + curUrl);
            }});
        }}

        function initApp() {{
            renderModelTabs();
            updateSiteButtons();
            updateBestPageLink();
            updateKeywordSearchLinks();

            const directInput = document.getElementById('directPrdInput');
            if (directInput) directInput.value = currentPrdNo;

            const kwInput = document.getElementById('directKwInput');
            if (kwInput) kwInput.value = currentKeyword;

            const sizeInput = document.getElementById('sizeInput');
            if (sizeInput) sizeInput.value = currentK;

            const basketInput = document.getElementById('basketPrdInput');
            if (basketInput) basketInput.value = currentBasket;

            const wishInput = document.getElementById('wishPrdInput');
            if (wishInput) wishInput.value = currentWish;

            const memInput = document.getElementById('memNoInput');
            if (memInput) memInput.value = currentMem;

            const selfCheck = document.getElementById('selfYnCheck');
            if (selfCheck) selfCheck.checked = currentSelfYn;

            updateHomeFieldsVisibility();
            updatePanelVisibility();
            switchViewTab(currentTab, false);
            setupEventListeners();
            loadBestProducts(currentSiteCd);
        }}

        function updatePanelVisibility() {{
            const criterionPanel = document.getElementById('criterionPanel');
            const kwPanel = document.getElementById('keywordTrendPanel');
            const promptTabBtn = document.getElementById('tabBtnPrompt');
            const seedTabsSection = document.getElementById('homeSeedTabsSection');

            if (currentMlType === 'keyword-trend') {{
                if (criterionPanel) criterionPanel.style.display = 'none';
                if (seedTabsSection) seedTabsSection.style.display = 'none';
                if (kwPanel) kwPanel.style.display = 'flex';
                if (promptTabBtn) promptTabBtn.style.display = 'inline-block';
                renderKeywordChips();
                const kwInput = document.getElementById('directKwInput');
                if (kwInput) kwInput.value = currentKeyword;
            }} else {{
                if (criterionPanel) criterionPanel.style.display = 'grid';
                if (kwPanel) kwPanel.style.display = 'none';
                if (promptTabBtn) promptTabBtn.style.display = 'none';
                if (currentTab === 'prompt') {{
                    switchViewTab('grid');
                }}
            }}
            updateKeywordSearchLinks();
        }}

        function renderModelTabs() {{
            const group = document.getElementById('modelTabsGroup');
            if (!group) return;

            const availableModels = ML_TYPES_LIST.filter(m => {{
                if (m.siteOnly && m.siteOnly !== currentSiteCd) return false;
                return true;
            }});

            if (!availableModels.some(m => m.id === currentMlType)) {{
                currentMlType = 'home';
            }}

            group.innerHTML = availableModels.map(m => `
                <button class="model-tab-btn ${{m.id === currentMlType ? 'active' : ''}}" onclick="selectMlType('${{m.id}}')" title="${{m.name}} (${{m.id}}: ${{m.endpoint}})">
                    ${{m.name}}
                </button>
            `).join('');
        }}

        function selectMlType(typeId) {{
            currentMlType = typeId;
            currentSelectedSeed = "";
            renderModelTabs();
            updateHomeFieldsVisibility();
            updatePanelVisibility();
            executeRecommendFlow();
        }}

        function updateSiteButtons() {{
            const btnHalf = document.getElementById('btnSiteHalf');
            const btnBori = document.getElementById('btnSiteBori');
            if (btnHalf && btnBori) {{
                if (currentSiteCd === '2') {{
                    btnHalf.classList.remove('active');
                    btnBori.classList.add('active');
                }} else {{
                    btnHalf.classList.add('active');
                    btnBori.classList.remove('active');
                }}
            }}
        }}

        function changeSite(newSiteCd) {{
            if (currentSiteCd === newSiteCd) return;
            currentSiteCd = newSiteCd;

            currentPrdNo = "";
            currentSelectedSeed = "";
            currentBasket = "";
            currentWish = "";
            currentMem = "";
            currentSelfYn = false;
            currentRawData = null;
            homeExtractedSeeds = [];
            homeOriginalResults = [];
            currentSeedProducts = [];

            const directInput = document.getElementById('directPrdInput');
            if (directInput) directInput.value = "";
            const basketInput = document.getElementById('basketPrdInput');
            if (basketInput) basketInput.value = "";
            const wishInput = document.getElementById('wishPrdInput');
            if (wishInput) wishInput.value = "";
            const memInput = document.getElementById('memNoInput');
            if (memInput) memInput.value = "";
            const selfCheck = document.getElementById('selfYnCheck');
            if (selfCheck) selfCheck.checked = false;

            const container = document.getElementById('seedGridContainer');
            if (container) {{
                const siteName = currentSiteCd === '2' ? '보리보리' : '하프클럽';
                container.innerHTML = `<div style="grid-column:1/-1; padding:24px 12px; text-align:center; color:#64748b; font-size:0.83rem; font-weight:600;">${{siteName}} 실시간 베스트 상품을 불러오는 중입니다...</div>`;
            }}
            const seedStatus = document.getElementById('seedStatusText');
            if (seedStatus) {{
                seedStatus.textContent = '실시간 베스트 12개 로딩 중...';
                seedStatus.style.color = '#64748b';
            }}

            const brandEl = document.getElementById('targetBrandText');
            if (brandEl) brandEl.textContent = '조회 중...';
            const nameEl = document.getElementById('targetPrdNmText');
            if (nameEl) nameEl.textContent = '새 사이트 베스트 상품으로 전환 중...';
            const priceEl = document.getElementById('targetDcPrice');
            if (priceEl) priceEl.textContent = '-';
            const prdNoEl = document.getElementById('targetPrdNoText');
            if (prdNoEl) prdNoEl.textContent = '-';
            const imgWrap = document.getElementById('targetThumbWrap');
            if (imgWrap) imgWrap.innerHTML = '<span style="font-size:0.75rem; color:#94a3b8;">Loading...</span>';

            updateSiteButtons();
            updateBestPageLink();
            renderModelTabs();
            updateHomeFieldsVisibility();
            updatePanelVisibility();

            const homeTabs = document.getElementById('homeSeedTabsSection');
            if (homeTabs) homeTabs.style.display = 'none';
            const homeTabsWrap = document.getElementById('homeSeedTabsWrap');
            if (homeTabsWrap) homeTabsWrap.innerHTML = '';

            const snippetEl = document.getElementById('activeApiUrlSnippet');
            if (snippetEl) snippetEl.textContent = '-';
            const fullApiEl = document.getElementById('calledApiUrlFull');
            if (fullApiEl) fullApiEl.textContent = '-';

            updateUrlQuery();

            if (currentMlType === 'keyword-trend') {{
                executeRecommendFlow();
            }} else {{
                loadBestProducts(currentSiteCd, true);
            }}
        }}

        function updateHomeFieldsVisibility() {{
            const homeWrap = document.getElementById('homeFieldsWrap');
            const homeTabs = document.getElementById('homeSeedTabsSection');
            const isSeedModel = isSeedCompatibleModel();
            if (homeWrap) homeWrap.style.display = isSeedModel ? 'flex' : 'none';
            if (homeTabs) homeTabs.style.display = isSeedModel ? 'block' : 'none';
        }}

        function setupEventListeners() {{
            const directInput = document.getElementById('directPrdInput');
            if (directInput) {{
                directInput.addEventListener('keydown', (e) => {{
                    if (e.key === 'Enter') triggerFetch();
                }});
            }}
            const directKwInput = document.getElementById('directKwInput');
            if (directKwInput) {{
                directKwInput.addEventListener('keydown', (e) => {{
                    if (e.key === 'Enter') triggerKeywordFetch();
                }});
            }}
            const sizeInput = document.getElementById('sizeInput');
            if (sizeInput) {{
                sizeInput.addEventListener('change', () => {{
                    currentK = sizeInput.value;
                    executeRecommendFlow();
                }});
            }}

            window.addEventListener('keydown', (e) => {{
                if (currentMlType !== 'keyword-trend') return;

                const activeTag = document.activeElement ? document.activeElement.tagName.toUpperCase() : '';
                if (activeTag === 'INPUT' || activeTag === 'TEXTAREA') {{
                    if (document.activeElement?.id === 'kwFilterInput' && e.key === 'ArrowDown') {{
                        const chipsContainer = document.getElementById('kwChipsContainer');
                        if (chipsContainer) chipsContainer.focus();
                        e.preventDefault();
                    }}
                    return;
                }}

                if (e.key === 'ArrowRight') {{
                    if (handleKeywordArrowNavigation('next')) e.preventDefault();
                }} else if (e.key === 'ArrowLeft') {{
                    if (handleKeywordArrowNavigation('prev')) e.preventDefault();
                }}
            }});

            const chipsContainer = document.getElementById('kwChipsContainer');
            if (chipsContainer) {{
                chipsContainer.addEventListener('keydown', (e) => {{
                    if (e.key === 'ArrowRight') {{
                        if (handleKeywordArrowNavigation('next')) e.preventDefault();
                    }} else if (e.key === 'ArrowLeft') {{
                        if (handleKeywordArrowNavigation('prev')) e.preventDefault();
                    }}
                }});
            }}
        }}

        async function loadBestProducts(siteCd, isSiteChange = false) {{
            const seedStatus = document.getElementById('seedStatusText');
            if (seedStatus) {{
                seedStatus.textContent = '실시간 베스트 12개 로딩 중...';
                seedStatus.style.color = '#64748b';
            }}
            updateBestPageLink();

            const bestUrl = siteCd === '1' 
                ? 'https://hapix.halfclub.com/searches/best/?offset=0&limit=200&dealYn=N&interval=24&countryCd=001&langCd=001&siteCd=1&deviceCd=001&device=pc&mandM=halfclub'
                : 'https://apix.boribori.co.kr/searches/best/?dealYn=N&interval=24&siteCd=2&limit=0,200&countryCd=001&langCd=001&deviceCd=001&mandM=b_boribori';

            try {{
                const res = await fetch(bestUrl);
                if (!res.ok) throw new Error(`HTTP ${{res.status}}`);
                const data = await res.json();

                let hits = [];
                if (data?.data?.result?.hits?.hits) hits = data.data.result.hits.hits;
                else if (data?.data?.result?.hits) hits = data.data.result.hits;
                else if (Array.isArray(data?.data)) hits = data.data;
                else if (Array.isArray(data)) hits = data;

                const products = [];
                const seenCategories = new Set();

                for (let i = 0; i < hits.length; i++) {{
                    if (products.length >= 12) break;
                    const hit = hits[i];
                    const source = hit._source || hit;
                    const prdNo = String(source.prdNo || source.prd_no || '');
                    let dpCtgrNm1 = source.dpCtgrNm1 || '';
                    if (dpCtgrNm1.includes('@')) dpCtgrNm1 = dpCtgrNm1.split('@')[0].trim();
                    if (!dpCtgrNm1) continue;

                    if (prdNo && !seenCategories.has(dpCtgrNm1)) {{
                        seenCategories.add(dpCtgrNm1);
                        products.push({{
                            prd_nm: dpCtgrNm1,
                            full_name: dpCtgrNm1,
                            prd_no: prdNo,
                            prd_img: source.appPrdImgUrl || source.prdImg || '',
                            actual_prd_nm: source.prdNm || `상품${{i+1}}`,
                            sel_acnt_no: source.selAcntNo || source.sel_acnt_no || '',
                            best_rank: i + 1
                        }});
                    }}
                }}

                if (products.length > 0) {{
                    currentSeedProducts = products;
                    if (seedStatus) {{
                        seedStatus.textContent = '실시간 베스트 12개';
                        seedStatus.style.color = '#475569';
                    }}

                    if (isSiteChange || (!currentPrdNo && currentMlType !== 'keyword-trend')) {{
                        currentPrdNo = String(products[0].prd_no);
                        const directInput = document.getElementById('directPrdInput');
                        if (directInput) directInput.value = currentPrdNo;
                        loadTargetProductInfo(currentPrdNo);
                    }}
                }} else {{
                    throw new Error('데이터 없음');
                }}
            }} catch (e) {{
                currentSeedProducts = [];
                if (seedStatus) {{
                    seedStatus.textContent = '서버 연결이 안됩니다';
                    seedStatus.style.color = '#ef4444';
                }}
                const container = document.getElementById('seedGridContainer');
                if (container) {{
                    container.innerHTML = '<div style="grid-column:1/-1; padding:18px; text-align:center; color:#ef4444; font-weight:700; font-size:0.83rem;">서버 연결이 안됩니다 (실시간 베스트 상품 조회 실패)</div>';
                }}
            }}

            renderSeedGrid(true);
            executeRecommendFlow();
        }}

        function updateTargetMiniSummary(prdNoStr) {{
            const prdList = (prdNoStr || '').split(',').map(s => s.trim()).filter(Boolean);
            const firstPrd = prdList[0] || '';

            const countBadge = document.getElementById('targetCountBadge');
            if (countBadge) {{
                if (prdList.length > 1) {{
                    countBadge.textContent = `외 ${{prdList.length - 1}}개`;
                    countBadge.style.display = 'inline-block';
                }} else {{
                    countBadge.style.display = 'none';
                }}
            }}

            const prdNoEl = document.getElementById('targetPrdNoText');
            if (prdNoEl) prdNoEl.textContent = firstPrd || '-';

            const mallLink = document.getElementById('targetMallLink');
            if (mallLink) {{
                if (firstPrd) {{
                    mallLink.href = getProductDetailUrl(firstPrd);
                    mallLink.style.display = 'inline';
                }} else {{
                    mallLink.href = '#';
                    mallLink.style.display = 'none';
                }}
            }}

            const multiContainer = document.getElementById('multiChipsContainer');
            if (multiContainer) {{
                if (prdList.length > 1) {{
                    multiContainer.style.display = 'flex';
                    let chipsHtml = prdList.map(p => `
                        <span class="prd-chip" onclick="removeSelectedPrd('${{p}}')" title="클릭 시 선택 제외">
                            #${{p}} ✕
                        </span>
                    `).join('');
                    chipsHtml += `<span class="prd-chip chip-clear-all" onclick="clearSelectedPrd()" title="모든 선택 상품 해제">전체 해제 ✕</span>`;
                    multiContainer.innerHTML = chipsHtml;
                }} else if (prdList.length === 1) {{
                    multiContainer.style.display = 'flex';
                    multiContainer.innerHTML = `
                        <span class="prd-chip" onclick="removeSelectedPrd('${{firstPrd}}')" title="클릭 시 선택 해제">
                            #${{firstPrd}} ✕
                        </span>
                        <span class="prd-chip chip-clear-all" onclick="clearSelectedPrd()" title="선택 해제">해제 ✕</span>
                    `;
                }} else {{
                    multiContainer.style.display = 'none';
                    multiContainer.innerHTML = '';
                }}
            }}
        }}

        function renderSeedGrid(forceRebuild = false) {{
            const container = document.getElementById('seedGridContainer');
            if (!container || currentSeedProducts.length === 0) return;

            const selectedList = getSelectedPrdList();
            const existingCards = container.querySelectorAll('.seed-mini-card');

            // 기존 카드 개수와 상품 번호가 정확히 일치할 때만 active 클래스 토글 (그 외는 무조건 전체 DOM 재구축)
            const canReuseDom = !forceRebuild && existingCards.length === currentSeedProducts.length &&
                Array.from(existingCards).every((card, idx) => card.getAttribute('data-prdno') === String(currentSeedProducts[idx]?.prd_no));

            if (canReuseDom) {{
                existingCards.forEach((card, idx) => {{
                    const p = currentSeedProducts[idx];
                    if (p) {{
                        const isSelected = selectedList.includes(p.prd_no);
                        card.classList.toggle('active', isSelected);
                    }}
                }});
                return;
            }}

            container.innerHTML = currentSeedProducts.map((p, idx) => {{
                const isSelected = selectedList.includes(p.prd_no);
                const fullImg = getImageUrl(p.prd_img);
                const rankNum = p.best_rank !== undefined ? p.best_rank : (idx + 1);
                const isTopRank = rankNum <= 3;
                return `
                    <div class="seed-mini-card ${{isSelected ? 'active' : ''}}" data-prdno="${{p.prd_no}}" onclick="handleSeedCardClick('${{p.prd_no}}', event)" title="${{p.full_name || p.prd_nm}} (${{rankNum}}위, #${{p.prd_no}})">
                        <span class="seed-mini-rank ${{isTopRank ? 'top-rank' : ''}}">${{rankNum}}위</span>
                        <span class="seed-mini-badge">V</span>
                        <img src="${{fullImg || 'data:image/svg+xml,%3Csvg xmlns=\\'http://www.w3.org/2000/svg\\' width=\\'100\\' height=\\'100\\'%3E%3Crect width=\\'100\\' height=\\'100\\' fill=\\'%23f1f5f9\\'/ %3E%3C/svg%3E'}}" class="seed-mini-img" alt="${{p.prd_nm}}" loading="lazy"/>
                        <span class="seed-mini-cat">${{p.prd_nm}}</span>
                        <span class="seed-mini-prdno">#${{p.prd_no}}</span>
                    </div>
                `;
            }}).join('');
        }}


        function handleSeedCardClick(prdNo, event) {{
            if (event) {{
                event.preventDefault();
                event.stopPropagation();
            }}

            prdNo = String(prdNo).trim();
            let selectedList = getSelectedPrdList();
            const isMultiKey = event && (event.ctrlKey || event.metaKey || event.shiftKey);

            if (isMultiKey) {{
                if (selectedList.includes(prdNo)) {{
                    selectedList = selectedList.filter(p => p !== prdNo);
                }} else {{
                    selectedList.push(prdNo);
                }}
                currentPrdNo = selectedList.join(',');
            }} else {{
                currentPrdNo = prdNo;
            }}

            const directInput = document.getElementById('directPrdInput');
            if (directInput) directInput.value = currentPrdNo;

            currentSelectedSeed = "";
            renderSeedGrid();
            updateTargetMiniSummary(currentPrdNo);

            if (isMultiKey) {{
                debouncedExecuteRecommendFlow(150);
            }} else {{
                executeRecommendFlow();
            }}
        }}

        function removeSelectedPrd(prdNo) {{
            let selectedList = getSelectedPrdList();
            selectedList = selectedList.filter(p => p !== prdNo);
            currentPrdNo = selectedList.join(',');

            const directInput = document.getElementById('directPrdInput');
            if (directInput) directInput.value = currentPrdNo;

            renderSeedGrid();
            updateTargetMiniSummary(currentPrdNo);

            if (currentPrdNo) {{
                debouncedExecuteRecommendFlow(100);
            }} else {{
                clearSelectedPrd();
            }}
        }}

        function clearSelectedPrd() {{
            currentPrdNo = "";
            currentSelectedSeed = "";

            const directInput = document.getElementById('directPrdInput');
            if (directInput) directInput.value = "";

            renderSeedGrid();
            renderTargetProductCardEmpty();
            updateUrlQuery();

            if (isSeedCompatibleModel()) {{
                fetchRecommendationApi();
            }} else {{
                renderEmptyResultsNotice('기준 상품이 선택되지 않았습니다. 상품번호를 입력하거나 아래 실시간 베스트 상품을 선택하세요.');
            }}
        }}

        function renderTargetProductCardEmpty() {{
            const countBadge = document.getElementById('targetCountBadge');
            if (countBadge) countBadge.textContent = '0개';

            const mallLink = document.getElementById('targetMallLink');
            if (mallLink) {{
                mallLink.href = '#';
                mallLink.style.display = 'none';
            }}

            const multiContainer = document.getElementById('multiChipsContainer');
            if (multiContainer) {{
                multiContainer.style.display = 'none';
                multiContainer.innerHTML = '';
            }}

            const imgWrap = document.getElementById('targetThumbWrap');
            if (imgWrap) imgWrap.innerHTML = '<span style="font-size:0.7rem; color:#94a3b8;">선택 없음</span>';

            const brandEl = document.getElementById('targetBrandText');
            if (brandEl) brandEl.textContent = '선택된 상품 없음';

            const selAcntBadge = document.getElementById('targetSelAcntBadge');
            if (selAcntBadge) selAcntBadge.style.display = 'none';

            const nameEl = document.getElementById('targetNameText');
            if (nameEl) {{
                nameEl.textContent = '기준 상품을 선택하거나 상품번호를 입력하세요.';
                nameEl.title = '기준 상품을 선택하거나 상품번호를 입력하세요.';
                nameEl.style.color = '#0f172a';
            }}

            const priceEl = document.getElementById('targetPriceText');
            if (priceEl) priceEl.textContent = '-';

            const rateEl = document.getElementById('targetRateText');
            if (rateEl) rateEl.textContent = '';

            const catEl = document.getElementById('targetCatPath');
            if (catEl) catEl.textContent = '실시간 베스트 상품을 클릭하여 기준 상품을 지정할 수 있습니다.';
        }}

        function renderTargetProductCardError(prdNo) {{
            const countBadge = document.getElementById('targetCountBadge');
            if (countBadge) countBadge.textContent = '조회 실패';

            const mallLink = document.getElementById('targetMallLink');
            if (mallLink) mallLink.style.display = 'none';

            const imgWrap = document.getElementById('targetThumbWrap');
            if (imgWrap) imgWrap.innerHTML = '<span style="font-size:0.7rem; color:#ef4444; font-weight:700;">오류</span>';

            const brandEl = document.getElementById('targetBrandText');
            if (brandEl) brandEl.textContent = '연결 실패';

            const selAcntBadge = document.getElementById('targetSelAcntBadge');
            if (selAcntBadge) selAcntBadge.style.display = 'none';

            const nameEl = document.getElementById('targetNameText');
            if (nameEl) {{
                nameEl.innerHTML = '<span style="color:#ef4444; font-weight:700;">서버 연결이 안됩니다</span>';
                nameEl.title = '서버 연결이 안됩니다';
            }}

            const priceEl = document.getElementById('targetPriceText');
            if (priceEl) priceEl.textContent = '-';

            const rateEl = document.getElementById('targetRateText');
            if (rateEl) rateEl.textContent = '';

            const catEl = document.getElementById('targetCatPath');
            if (catEl) catEl.textContent = `상품번호 #${{prdNo}}의 상세 정보를 서버에서 가져올 수 없습니다.`;
        }}

        function renderEmptyResultsNotice(message) {{
            const statusEl = document.getElementById('statusBadge');
            if (statusEl) {{
                statusEl.textContent = '대기 중';
                statusEl.style.color = '#64748b';
                statusEl.style.background = '#f1f5f9';
                statusEl.style.borderColor = '#cbd5e1';
            }}

            const snippetEl = document.getElementById('activeApiUrlSnippet');
            if (snippetEl) snippetEl.textContent = `기준 상품 선택 대기`;

            const fullUrlEl = document.getElementById('calledApiUrlFull');
            if (fullUrlEl) fullUrlEl.textContent = '-';

            document.getElementById('productGridContainer').innerHTML = `
                <div style="grid-column:1/-1; padding:60px 20px; text-align:center; color:#64748b; font-size:0.95rem; font-weight:600;">
                    ${{escapeHtml(message)}}
                </div>
            `;

            document.getElementById('productTableBody').innerHTML = `
                <tr><td colspan="12" style="text-align:center; padding:30px; color:#64748b;">${{escapeHtml(message)}}</td></tr>
            `;

            renderRawJsonView({{ message: message, status: "WAITING_FOR_INPUT" }});
        }}

        function triggerFetch() {{
            const directInput = document.getElementById('directPrdInput');
            if (directInput) currentPrdNo = directInput.value.trim();

            const sizeInput = document.getElementById('sizeInput');
            if (sizeInput && sizeInput.value) currentK = sizeInput.value;

            const basketInput = document.getElementById('basketPrdInput');
            if (basketInput) currentBasket = basketInput.value.trim();

            const wishInput = document.getElementById('wishPrdInput');
            if (wishInput) currentWish = wishInput.value.trim();

            const memInput = document.getElementById('memNoInput');
            if (memInput) currentMem = memInput.value.trim();

            const selfCheck = document.getElementById('selfYnCheck');
            if (selfCheck) currentSelfYn = selfCheck.checked;

            currentSelectedSeed = "";
            renderSeedGrid();
            executeRecommendFlow();
        }}

        function switchViewTab(tabName, updateUrl = true) {{
            currentTab = tabName;
            document.querySelectorAll('.result-tab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.tab-pane').forEach(c => c.classList.remove('active'));

            if (tabName === 'grid') {{
                document.getElementById('tabBtnGrid')?.classList.add('active');
                document.getElementById('tabContentGrid')?.classList.add('active');
            }} else if (tabName === 'table') {{
                document.getElementById('tabBtnTable')?.classList.add('active');
                document.getElementById('tabContentTable')?.classList.add('active');
            }} else if (tabName === 'raw') {{
                document.getElementById('tabBtnRaw')?.classList.add('active');
                document.getElementById('tabContentRaw')?.classList.add('active');
            }} else if (tabName === 'prompt') {{
                document.getElementById('tabBtnPrompt')?.classList.add('active');
                document.getElementById('tabContentPrompt')?.classList.add('active');
            }}

            if (updateUrl) updateUrlQuery();
        }}

        async function executeRecommendFlow() {{
            updateUrlQuery();

            if (currentMlType === 'keyword-trend') {{
                await fetchRecommendationApi();
                return;
            }}

            const activePrdToLoad = (isSeedCompatibleModel() && currentSelectedSeed) ? currentSelectedSeed : currentPrdNo;
            if (activePrdToLoad) {{
                loadTargetProductInfo(activePrdToLoad);
            }} else {{
                renderTargetProductCardEmpty();
            }}

            if (currentPrdNo || isSeedCompatibleModel()) {{
                await fetchRecommendationApi();
            }} else {{
                renderEmptyResultsNotice('기준 상품이 선택되지 않았습니다. 상품번호를 입력하거나 아래 실시간 베스트 상품을 선택하세요.');
            }}
        }}

        async function loadTargetProductInfo(prdNoStr) {{
            const curReqId = ++targetProductRequestId;
            const prdList = (prdNoStr || '').split(',').map(s => s.trim()).filter(Boolean);
            const firstPrd = prdList[0] || '';

            updateTargetMiniSummary(prdNoStr);

            if (!firstPrd) return;

            const searchBase = currentSiteCd === '2' ? 'https://apix.boribori.co.kr' : 'https://hapix.halfclub.com';
            const searchUrl = `${{searchBase}}/searches/prdList/?keyword=${{encodeURIComponent(firstPrd)}}&siteCd=${{currentSiteCd}}&device=mc`;

            try {{
                const res = await fetch(searchUrl);
                if (curReqId !== targetProductRequestId) return;
                if (!res.ok) throw new Error(`HTTP ${{res.status}}`);
                const data = await res.json();
                if (curReqId !== targetProductRequestId) return;

                const hits = data?.data?.result?.hits?.hits || [];
                if (hits.length > 0) {{
                    const src = hits[0]._source || hits[0];
                    renderTargetProductCard(src, firstPrd);
                }} else {{
                    const seedItem = currentSeedProducts.find(p => String(p.prd_no) === String(firstPrd));
                    if (seedItem) {{
                        renderTargetProductCard({{
                            prdNm: seedItem.actual_prd_nm || seedItem.full_name || seedItem.prd_nm,
                            brandNm: seedItem.prd_nm || '베스트',
                            appPrdImgUrl: seedItem.prd_img,
                            selAcntNo: seedItem.sel_acnt_no,
                            prdNo: seedItem.prd_no
                        }}, firstPrd);
                    }} else {{
                        renderTargetProductCardError(firstPrd);
                    }}
                }}
            }} catch (e) {{
                if (curReqId === targetProductRequestId) {{
                    const seedItem = currentSeedProducts.find(p => String(p.prd_no) === String(firstPrd));
                    if (seedItem) {{
                        renderTargetProductCard({{
                            prdNm: seedItem.actual_prd_nm || seedItem.full_name || seedItem.prd_nm,
                            brandNm: seedItem.prd_nm || '베스트',
                            appPrdImgUrl: seedItem.prd_img,
                            selAcntNo: seedItem.sel_acnt_no,
                            prdNo: seedItem.prd_no
                        }}, firstPrd);
                    }} else {{
                        renderTargetProductCardError(firstPrd);
                    }}
                }}
            }}
        }}

        function renderTargetProductCard(src, firstPrd = '') {{
            const name = src.prdNm || '상품명 미확인';
            const brand = src.brandNm || src.brdNm || '브랜드 미확인';
            const dcPrice = src.dcPrcMc || src.dcPrcApp || src.selPrc || src.price || 0;
            const normPrice = src.normPrc || 0;
            const imgPath = src.appPrdImgUrl || src.prdImg || '';
            const fullImg = getImageUrl(imgPath);
            const targetUrl = getProductDetailUrl(firstPrd || src.prdNo);
            const selAcnt = src.selAcntNo || src.sel_acnt_no || '';

            const c1 = src.dpCtgrNm1 || '';
            const c2 = src.dpCtgrNm2 || '';
            const c3 = src.dpCtgrNm3 || '';
            const catPath = [c1, c2, c3].filter(Boolean).join(' > ');

            const mallLink = document.getElementById('targetMallLink');
            if (mallLink) {{
                mallLink.href = targetUrl;
                mallLink.style.display = 'inline';
            }}

            const imgWrap = document.getElementById('targetThumbWrap');
            if (imgWrap) {{
                imgWrap.innerHTML = fullImg 
                    ? `<a href="${{targetUrl}}" target="_blank" rel="noopener noreferrer"><img src="${{fullImg}}" class="target-thumb" alt="${{name}}"/></a>`
                    : '<span style="font-size:0.7rem; color:#94a3b8;">No Image</span>';
            }}

            const brandEl = document.getElementById('targetBrandText');
            if (brandEl) brandEl.textContent = brand;

            const selAcntBadge = document.getElementById('targetSelAcntBadge');
            if (selAcntBadge) {{
                if (selAcnt) {{
                    selAcntBadge.textContent = `협력사:${{selAcnt}}`;
                    selAcntBadge.style.display = 'inline-block';
                    selAcntBadge.title = `판매자(협력사) 번호: ${{selAcnt}}`;
                }} else {{
                    selAcntBadge.style.display = 'none';
                }}
            }}

            const nameEl = document.getElementById('targetNameText');
            if (nameEl) {{
                nameEl.innerHTML = `<a href="${{targetUrl}}" target="_blank" rel="noopener noreferrer" style="text-decoration:none; color:inherit;">${{name}}</a>`;
                nameEl.title = name;
            }}

            const priceEl = document.getElementById('targetPriceText');
            if (priceEl) priceEl.textContent = `${{Number(dcPrice).toLocaleString()}} 원`;

            const rateEl = document.getElementById('targetRateText');
            if (rateEl) {{
                if (normPrice > dcPrice && normPrice > 0) {{
                    const rate = Math.round((normPrice - dcPrice) / normPrice * 100);
                    rateEl.textContent = `${{rate}}%`;
                }} else {{
                    rateEl.textContent = '';
                }}
            }}

            const catEl = document.getElementById('targetCatPath');
            if (catEl) {{
                catEl.textContent = catPath || '카테고리 정보 없음';
                catEl.title = catPath;
            }}
        }}

        async function fetchRecommendationApi() {{
            const curReqId = ++recommendRequestId;
            const startTime = performance.now();
            const apiBase = getApiBaseUrl();
            const statusEl = document.getElementById('statusBadge');
            if (statusEl) {{
                statusEl.textContent = '조회 중...';
                statusEl.style.color = '#2563eb';
                statusEl.style.background = '#eff6ff';
                statusEl.style.borderColor = '#dbeafe';
            }}
            updateKeywordSearchLinks();

            const endpoint = currentMlType;
            if (currentMlType === 'keyword-trend') {{
                currentApiUrl = `${{apiBase}}/recommend/keyword-trend?llmInfo=true&siteCd=${{currentSiteCd}}&size=${{currentK}}&keyword=${{encodeURIComponent(currentKeyword)}}`;
            }} else {{
                const params = new URLSearchParams();
                params.append('siteCd', currentSiteCd);
                params.append('size', currentK);

                const prdList = getSelectedPrdList();

                if (isSeedCompatibleModel()) {{
                    params.append('deviceCd', '001');
                    if (currentSelfYn) params.append('selfYn', 'true');
                    prdList.forEach(p => params.append('prdNo', p));

                    if (currentBasket) {{
                        currentBasket.split(',').map(s => s.trim()).filter(Boolean).forEach(b => params.append('basketPrdNo', b));
                    }}
                    if (currentWish) {{
                        currentWish.split(',').map(s => s.trim()).filter(Boolean).forEach(w => params.append('wishPrdNo', w));
                    }}
                    if (currentMem) {{
                        currentMem.split(',').map(s => s.trim()).filter(Boolean).forEach(m => params.append('memNo', m));
                    }}
                }} else {{
                    prdList.forEach(p => params.append('prdNo', p));
                }}

                if (currentMlType === 'similaritem' || currentMlType === 'lfsimilaritem') {{
                    params.append('randomYn', 'false');
                }}

                currentApiUrl = `${{apiBase}}/recommend/${{endpoint}}?${{params.toString()}}`;
            }}

            const activeModelObj = ML_TYPES_LIST.find(m => m.id === currentMlType);
            const modelTitle = activeModelObj ? activeModelObj.name : currentMlType;
            const snippetEl = document.getElementById('activeApiUrlSnippet');
            if (snippetEl) {{
                const extraInfo = currentMlType === 'keyword-trend' ? `키워드: '${{currentKeyword}}'` : `${{currentK}}개`;
                snippetEl.textContent = `${{modelTitle}} (/recommend/${{endpoint}}) · ${{extraInfo}}`;
            }}

            const fullUrlEl = document.getElementById('calledApiUrlFull');
            if (fullUrlEl) fullUrlEl.textContent = currentApiUrl;

            try {{
                const res = await fetch(currentApiUrl);
                const duration = Math.round(performance.now() - startTime);

                if (!res.ok) throw new Error(`HTTP ${{res.status}}: ${{res.statusText}}`);

                const data = await res.json();
                if (curReqId !== recommendRequestId) return;
                currentRawData = data;

                if (statusEl) {{
                    statusEl.textContent = `200 OK (${{duration}}ms)`;
                    statusEl.style.color = '#059669';
                    statusEl.style.background = '#ecfdf5';
                    statusEl.style.borderColor = '#a7f3d0';
                }}

                if (currentMlType === 'keyword-trend') {{
                    handleKeywordTrendSuccessResponse(data, currentKeyword);
                }} else {{
                    handleApiSuccessResponse(data);
                }}
            }} catch (err) {{
                if (curReqId !== recommendRequestId) return;
                const duration = Math.round(performance.now() - startTime);
                if (statusEl) {{
                    statusEl.textContent = `서버 연결이 안됩니다 (${{duration}}ms)`;
                    statusEl.style.color = '#ef4444';
                    statusEl.style.background = '#fef2f2';
                    statusEl.style.borderColor = '#fecaca';
                }}

                document.getElementById('productGridContainer').innerHTML = `
                    <div style="grid-column:1/-1; padding:60px 20px; text-align:center; color:#ef4444; font-weight:700;">
                        <div style="font-size:1.1rem; margin-bottom:8px;">서버 연결이 안됩니다</div>
                        <div style="font-size:0.85rem; color:#64748b;">${{escapeHtml(err.message)}}</div>
                        <div style="font-size:0.8rem; color:#94a3b8; margin-top:6px; word-break:break-all;">${{currentApiUrl}}</div>
                    </div>
                `;

                document.getElementById('productTableBody').innerHTML = `
                    <tr><td colspan="12" style="text-align:center; padding:30px; color:#ef4444; font-weight:700;">서버 연결이 안됩니다 (${{escapeHtml(err.message)}})</td></tr>
                `;

                renderRawJsonView({{ error: "서버 연결이 안됩니다", detail: err.message, requested_url: currentApiUrl }});
            }}
        }}

        function handleKeywordTrendSuccessResponse(data, kw) {{
            const llmInfo = data.llm_info || {{}};
            const reason = data.noshow_reason || llmInfo.noshow_reason || '';

            const provider = llmInfo.llm_provider || data.llm_provider || '-';
            const model = llmInfo.llm_model || data.llm_model || '-';
            const elemModel = document.getElementById('llmModelText');
            if (elemModel) elemModel.textContent = (provider === '-' && model === '-') ? '-' : `${{provider}} / ${{model}}`;

            const stage1 = llmInfo.stage1_guide_generation || {{}};
            const stage2 = llmInfo.stage2_product_selection || {{}};

            const usage1 = stage1.prompt_info?.token_usage || llmInfo.stage1_token_usage || {{}};
            const usage2 = stage2.prompt_info?.token_usage || llmInfo.stage2_token_usage || {{}};

            const reqTokens = (usage1.request_tokens || 0) + (usage2.request_tokens || 0) || (llmInfo.total_request_tokens || 0);
            const resTokens = (usage1.response_tokens || 0) + (usage2.response_tokens || 0) || (llmInfo.total_response_tokens || 0);
            const cachedTokens = (usage1.cached_tokens || 0) + (usage2.cached_tokens || 0);
            const totTokens = (usage1.total_tokens || 0) + (usage2.total_tokens || 0) || (reqTokens + resTokens);

            const elemTokenUsage = document.getElementById('tokenUsageText');
            if (elemTokenUsage) {{
                if (totTokens > 0 || reqTokens > 0) {{
                    elemTokenUsage.textContent = `In: ${{reqTokens.toLocaleString()}} / Out: ${{resTokens.toLocaleString()}} / Cached: ${{cachedTokens.toLocaleString()}} (Total: ${{totTokens.toLocaleString()}})`;
                }} else {{
                    elemTokenUsage.textContent = '-';
                }}
            }}

            const catFilter = data.enable_category_filter ?? llmInfo.enable_category_filter;
            const genFilter = data.enable_gender_filter ?? llmInfo.enable_gender_filter;
            const bCat = catFilter === true ? 'ON' : 'OFF';
            const bGen = genFilter === true ? 'ON' : 'OFF';
            const elemFilter = document.getElementById('filterBadgesText');
            if (elemFilter) {{
                elemFilter.innerHTML = `
                    <span style="background:#ffffff; border:1px solid #cbd5e1; color:#334155; font-weight:700; padding:1px 5px; border-radius:3px; font-size:0.7rem;">카테고리: ${{bCat}}</span>
                    <span style="background:#ffffff; border:1px solid #cbd5e1; color:#334155; font-weight:700; padding:1px 5px; border-radius:3px; font-size:0.7rem;">성별: ${{bGen}}</span>
                `;
            }}

            const createDt = data.create_dt || llmInfo.create_dt || '-';
            const elemCreateDt = document.getElementById('createDtText');
            if (elemCreateDt) elemCreateDt.textContent = createDt;

            // 큐레이션 요약문
            const curationSummary = stage2.llm_response?.curation_summary ||
                                   stage2.curation_summary ||
                                   data.curation_summary ||
                                   llmInfo.curation_summary ||
                                   stage1.guide_result?.curation_summary ||
                                   '';
            const summaryWrap = document.getElementById('curationSummaryWrap');
            const summaryText = document.getElementById('curationSummaryText');
            if (summaryWrap && summaryText) {{
                if (curationSummary && curationSummary.trim()) {{
                    summaryText.textContent = curationSummary.trim();
                    summaryWrap.style.display = 'flex';
                }} else {{
                    summaryWrap.style.display = 'none';
                }}
            }}

            // 스타일 가이드 문구
            let guideText = data.guide_text_html || '';
            if (reason) {{
                guideText = `
                    <div style="background:#fff1f2; border:1px solid #fecdd3; color:#9f1239; padding:8px 12px; border-radius:6px; line-height:1.5; margin-bottom:8px;">
                        <span style="font-weight:800; color:#be123c;">[미표시 사유] </span>${{escapeHtml(reason)}}
                    </div>
                ` + (guideText || '');
            }}
            const guideEl = document.getElementById('guideTextBody');
            if (guideEl) guideEl.innerHTML = guideText || '가이드 문구가 없습니다.';

            // 추출 태그
            const catTag = data.extracted_category || stage1.guide_result?.extracted_category || '기본';
            const genTag = data.extracted_gender || stage1.guide_result?.extracted_gender || '공용';
            const seasonVal = data.extracted_season || stage1.guide_result?.extracted_season || ['사계절'];
            const seasonStr = Array.isArray(seasonVal) ? seasonVal.join(', ') : seasonVal;
            const tagsEl = document.getElementById('extractedTagsHeader');
            if (tagsEl) {{
                tagsEl.innerHTML = `
                    <span class="badge-chip-item badge-blue" style="font-weight:700;">카테고리: ${{catTag}}</span>
                    <span class="badge-chip-item badge-gray">성별: ${{genTag}}</span>
                    <span class="badge-chip-item badge-gray">계절: ${{seasonStr}}</span>
                `;
            }}

            // 브랜드, 키워드 칩
            const extBrands = data.extracted_brands || stage1.guide_result?.extracted_brands || llmInfo.extracted_brands || [];
            const extKws = data.extracted_keywords || stage1.guide_result?.extracted_keywords || llmInfo.extracted_keywords || [];
            const extSearchKws = data.extracted_search_keywords || stage1.guide_result?.extracted_search_keywords || llmInfo.extracted_search_keywords || [];

            const brandChips = extBrands.map((b, bIdx) => {{
                const bClean = (typeof b === 'object' ? b.name : b).trim();
                const searchUrl = getKeywordSearchUrl(bClean);
                return `<a href="${{searchUrl}}" target="_blank" rel="noopener noreferrer" class="badge-chip-item badge-brand" style="text-decoration:none; cursor:pointer;" title="'${{bClean}}' 검색">${{bClean}} ↗</a>`;
            }}).join('');

            const kwChips = extKws.map(k => {{
                const kClean = String(k).trim();
                const searchUrl = getKeywordSearchUrl(kClean);
                return `<a href="${{searchUrl}}" target="_blank" rel="noopener noreferrer" class="badge-chip-item badge-blue" style="text-decoration:none; cursor:pointer;" title="'${{kClean}}' 검색">${{kClean}} ↗</a>`;
            }}).join('');

            const searchKwChips = extSearchKws.map(k => {{
                const kClean = String(k).trim();
                const searchUrl = getKeywordSearchUrl(kClean);
                return `<a href="${{searchUrl}}" target="_blank" rel="noopener noreferrer" class="badge-chip-item badge-purple" style="text-decoration:none; cursor:pointer;" title="'${{kClean}}' 검색">${{kClean}} ↗</a>`;
            }}).join('');

            const bWrap = document.getElementById('extractedBrandsWrap');
            if (bWrap) {{
                bWrap.innerHTML = brandChips ? `
                    <div style="display:flex; align-items:center; gap:8px; margin-top:4px;">
                        <span style="font-weight:700; color:#64748b; font-size:0.74rem; flex-shrink:0;">대상 브랜드:</span>
                        <div style="display:flex; align-items:center; gap:4px; flex-wrap:wrap;">${{brandChips}}</div>
                    </div>
                ` : '';
            }}

            const kWrap = document.getElementById('extractedKeywordsWrap');
            if (kWrap) {{
                kWrap.innerHTML = kwChips ? `
                    <div style="display:flex; align-items:center; gap:8px; margin-top:4px;">
                        <span style="font-weight:700; color:#64748b; font-size:0.74rem; flex-shrink:0;">추출 키워드:</span>
                        <div style="display:flex; align-items:center; gap:4px; flex-wrap:wrap;">${{kwChips}}</div>
                    </div>
                ` : '';
            }}

            const skWrap = document.getElementById('extractedSearchKeywordsWrap');
            if (skWrap) {{
                skWrap.innerHTML = searchKwChips ? `
                    <div style="display:flex; align-items:center; gap:8px; margin-top:4px;">
                        <span style="font-weight:700; color:#64748b; font-size:0.74rem; flex-shrink:0;">검색 키워드:</span>
                        <div style="display:flex; align-items:center; gap:4px; flex-wrap:wrap;">${{searchKwChips}}</div>
                    </div>
                ` : '';
            }}

            // 참고 뉴스 기사
            const articles = data.keyword_articles || llmInfo.keyword_articles || [];
            const articlesContainer = document.getElementById('articlesListContainer');
            const countBadge = document.getElementById('articlesCountBadge');
            const wrap = document.getElementById('articlesWrapper');
            if (countBadge) countBadge.textContent = `${{articles.length}}건`;
            if (articlesContainer) {{
                if (!articles || articles.length === 0) {{
                    if (wrap) wrap.style.display = 'none';
                    articlesContainer.innerHTML = '<div style="font-size:0.75rem; color:#94a3b8; padding:4px 0;">참고 뉴스 기사가 없습니다.</div>';
                }} else {{
                    if (wrap) wrap.style.display = 'block';
                    articlesContainer.innerHTML = articles.map(art => {{
                        const linkUrl = art.link || art.url || '#';
                        const sourceName = art.source || art.media || '뉴스';
                        const titleText = art.title || art.text || '제목 없음';
                        const pubDate = art.publish_dt || art.published_date || art.date || '';
                        const hasValidLink = linkUrl && linkUrl !== '#';

                        return `
                            <div style="background:#f8fafc; padding:6px 10px; border-radius:5px; border:1px solid #e2e8f0; display:flex; align-items:center; justify-content:space-between; font-size:0.78rem; margin-bottom:4px;">
                                <div style="display:flex; align-items:center; gap:6px; overflow:hidden;">
                                    <a href="${{linkUrl}}" ${{hasValidLink ? 'target="_blank" rel="noopener noreferrer"' : ''}} style="color:#0f172a; text-decoration:none; font-weight:600; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;" title="${{titleText}}">${{titleText}} <span class="badge-chip-item badge-media">${{sourceName}}</span></a>
                                </div>
                                <div style="display:flex; align-items:center; gap:6px; flex-shrink:0; font-size:0.72rem; color:#64748b;">
                                    ${{pubDate ? `<span>${{pubDate}}</span>` : ''}}
                                    ${{hasValidLink ? `<a href="${{linkUrl}}" target="_blank" rel="noopener noreferrer" style="color:#2563eb; text-decoration:underline; font-weight:600;">원문보기</a>` : ''}}
                                </div>
                            </div>
                        `;
                    }}).join('');
                }}
            }}

            // 프롬프트 인스펙터 렌더링
            renderPromptInspector(stage1, stage2);

            // 추천 상품 렌더링
            const products = data.recommended_products || data.products || data.items || data.result || [];
            renderDashboardResults(products, false);
        }}

        function renderKeywordChips(filterText = '') {{
            const container = document.getElementById('kwChipsContainer');
            if (!container) return;

            const q = (filterText || '').trim().toLowerCase();
            const filtered = q ? KEYWORDS_LIST.filter(k => k.toLowerCase().includes(q)) : KEYWORDS_LIST;

            container.innerHTML = filtered.map(kw => `
                <span class="kw-chip ${{kw === currentKeyword ? 'active' : ''}}" onclick="selectKeyword('${{kw}}')">
                    ${{kw}}
                </span>
            `).join('');

            const activeChip = container.querySelector('.kw-chip.active');
            if (activeChip) activeChip.scrollIntoView({{ behavior: 'smooth', block: 'nearest', inline: 'center' }});
        }}

        function selectKeyword(kw) {{
            currentKeyword = String(kw).trim();
            const input = document.getElementById('directKwInput');
            if (input) input.value = currentKeyword;
            renderKeywordChips(document.getElementById('kwFilterInput')?.value || '');
            updateUrlQuery();
            fetchRecommendationApi();
        }}

        function triggerKeywordFetch() {{
            const input = document.getElementById('directKwInput');
            if (input && input.value.trim()) {{
                currentKeyword = input.value.trim();
            }}
            renderKeywordChips(document.getElementById('kwFilterInput')?.value || '');
            updateUrlQuery();
            fetchRecommendationApi();
        }}

        function filterKeywordsList(q) {{
            renderKeywordChips(q);
        }}

        function handleKeywordArrowNavigation(direction) {{
            if (currentMlType !== 'keyword-trend') return false;

            const filterInput = document.getElementById('kwFilterInput');
            const q = (filterInput?.value || '').trim().toLowerCase();
            const list = q ? KEYWORDS_LIST.filter(k => k.toLowerCase().includes(q)) : KEYWORDS_LIST;
            if (!list || list.length === 0) return false;

            let idx = list.indexOf(currentKeyword);
            if (direction === 'next') {{
                if (idx === -1) idx = 0;
                else idx = (idx + 1) % list.length;
            }} else if (direction === 'prev') {{
                if (idx === -1) idx = list.length - 1;
                else idx = (idx - 1 + list.length) % list.length;
            }}
            selectKeyword(list[idx]);
            return true;
        }}

        function toggleArticlesAccordion() {{
            const container = document.getElementById('articlesListContainer');
            const icon = document.getElementById('articlesToggleIcon');
            if (!container) return;
            const isHidden = container.style.display === 'none';
            container.style.display = isHidden ? 'block' : 'none';
            if (icon) {{
                icon.textContent = isHidden ? '목록 접기 ▲' : '목록 펼치기 ▼';
            }}
        }}

        function renderPromptInspector(stage1, stage2) {{
            promptResDataMap = {{}};

            const p1Sys = stage1.prompt_info?.system_prompt;
            const cardSys1 = document.getElementById('cardSysStage1');
            const elemSys1 = document.getElementById('promptSysStage1');
            if (p1Sys && elemSys1) {{
                if (cardSys1) cardSys1.style.display = 'block';
                promptResDataMap['promptSysStage1'] = p1Sys;
                elemSys1.innerHTML = '';
                elemSys1.appendChild(createJsonTree(p1Sys, true, true));
            }}

            const p1User = stage1.prompt_info?.user_prompt;
            const cardUser1 = document.getElementById('cardUserStage1');
            const elemUser1 = document.getElementById('promptUserStage1');
            if (p1User && elemUser1) {{
                if (cardUser1) cardUser1.style.display = 'block';
                promptResDataMap['promptUserStage1'] = p1User;
                elemUser1.innerHTML = '';
                elemUser1.appendChild(createJsonTree(p1User, true, true));
            }} else if (cardUser1) {{
                cardUser1.style.display = 'none';
            }}

            const res1 = stage1.guide_result || stage1.prompt_info?.raw_response;
            const cardRes1 = document.getElementById('cardResultStage1');
            const elemRes1 = document.getElementById('promptResultStage1');
            if (res1 && elemRes1) {{
                if (cardRes1) cardRes1.style.display = 'block';
                promptResDataMap['promptResultStage1'] = res1;
                elemRes1.innerHTML = '';
                elemRes1.appendChild(createJsonTree(res1, true, true));
            }} else if (cardRes1) {{
                cardRes1.style.display = 'none';
            }}

            const p2Sys = stage2.prompt_info?.system_prompt;
            const cardSys2 = document.getElementById('cardSysStage2');
            const elemSys2 = document.getElementById('promptSysStage2');
            if (p2Sys && elemSys2) {{
                if (cardSys2) cardSys2.style.display = 'block';
                promptResDataMap['promptSysStage2'] = p2Sys;
                elemSys2.innerHTML = '';
                elemSys2.appendChild(createJsonTree(p2Sys, true, true));
            }}

            const p2User = stage2.prompt_info?.user_prompt;
            const cardUser2 = document.getElementById('cardUserStage2');
            const elemUser2 = document.getElementById('promptUserStage2');
            if (p2User && elemUser2) {{
                if (cardUser2) cardUser2.style.display = 'block';
                promptResDataMap['promptUserStage2'] = p2User;
                elemUser2.innerHTML = '';
                elemUser2.appendChild(createJsonTree(p2User, true, true));
            }} else if (cardUser2) {{
                cardUser2.style.display = 'none';
            }}

            const res2 = stage2.prompt_info?.raw_response || stage2.llm_response;
            const cardRes2 = document.getElementById('cardResultStage2');
            const elemRes2 = document.getElementById('promptResultStage2');
            if (res2 && elemRes2) {{
                if (cardRes2) cardRes2.style.display = 'block';
                promptResDataMap['promptResultStage2'] = res2;
                elemRes2.innerHTML = '';
                elemRes2.appendChild(createJsonTree(res2, true, true));
            }} else if (cardRes2) {{
                cardRes2.style.display = 'none';
            }}
        }}

        function copyPromptTextToClipboard(containerId, btnId) {{
            const data = promptResDataMap[containerId];
            if (!data) return;
            const textToCopy = typeof data === 'string' ? data : JSON.stringify(data, null, 2);
            navigator.clipboard.writeText(textToCopy).then(() => {{
                const btn = document.getElementById(btnId);
                if (btn) {{
                    const orig = btn.textContent;
                    btn.textContent = '복사완료!';
                    btn.style.background = '#059669';
                    setTimeout(() => {{
                        btn.textContent = orig;
                        btn.style.background = '#334155';
                    }}, 1500);
                }}
            }}).catch(() => {{
                alert('복사 실패');
            }});
        }}

        function handleApiSuccessResponse(data) {{
            let products = [];
            homeExtractedSeeds = [];

            if (Array.isArray(data)) {{
                products = data;
            }} else if (data && typeof data === 'object') {{
                products = data.result || data.data || data.items || data.results || [];
                if (!Array.isArray(products) && typeof products === 'object') products = [products];

                if (data.seed) {{
                    if (Array.isArray(data.seed)) homeExtractedSeeds = data.seed;
                    else if (data.seed.result && Array.isArray(data.seed.result)) homeExtractedSeeds = data.seed.result;
                    else if (typeof data.seed === 'object') {{
                        const list = [];
                        for (let k of ['recent', 'basket', 'wish', 'result', 'items']) {{
                            if (Array.isArray(data.seed[k])) list.push(...data.seed[k]);
                        }}
                        if (list.length > 0) homeExtractedSeeds = list;
                    }}
                }}
            }}

            homeOriginalResults = products;

            if (isSeedCompatibleModel()) {{
                document.getElementById('homeSeedTabsSection').style.display = 'block';
                renderHomeSeedTabs(homeExtractedSeeds);

                if (currentSelectedSeed) {{
                    fetchSimilarItemForSeed(currentSelectedSeed);
                    return;
                }}
            }} else {{
                document.getElementById('homeSeedTabsSection').style.display = 'none';
            }}

            renderDashboardResults(products, false);
        }}

        function renderHomeSeedTabs(seeds) {{
            const container = document.getElementById('homeSeedCardsContainer');
            if (!container) return;

            const isForyouActive = !currentSelectedSeed;

            let html = `
                <div class="home-foryou-card ${{isForyouActive ? 'active' : ''}}" onclick="selectHomeSeedTab('')" title="전체 맞춤 추천 (FORYOU)">
                    <span style="font-size:12px; font-weight:800; color:${{isForyouActive ? '#ffffff' : '#64748b'}}; margin-bottom:2px;">Index 0</span>
                    <span class="foryou-title">FORYOU</span>
                    <span class="foryou-desc">종합 추천</span>
                </div>
            `;

            seeds.forEach((seed, idx) => {{
                const pNo = String(seed.prdNo || seed.prd_no || '');
                if (!pNo) return;

                const isCardActive = currentSelectedSeed === pNo;
                const seedType = seed.seed || 'seed';
                const tagMap = {{ 'recent': ['최근본', 'tag-recent'], 'basket': ['장바구니', 'tag-basket'], 'wish': ['좋아요', 'tag-wish'] }};
                const tagInfo = tagMap[seedType] || [seedType, 'tag-recent'];
                const brand = seed.brandNm || '';
                const img = getImageUrl(seed.appPrdImgUrl || seed.prdImg || seed.prd_img || '');

                html += `
                    <div class="home-seed-card ${{isCardActive ? 'active' : ''}}" onclick="selectHomeSeedTab('${{pNo}}')" title="${{brand}} #${{pNo}}">
                        <span style="font-size:10px; font-weight:700; color:#64748b;">Index ${{idx + 1}}</span>
                        <img src="${{img || 'data:image/svg+xml,%3Csvg xmlns=\\'http://www.w3.org/2000/svg\\' width=\\'100\\' height=\\'100\\'%3E%3Crect width=\\'100\\' height=\\'100\\' fill=\\'%23f1f5f9\\'/ %3E%3C/svg%3E'}}" class="home-seed-card-img" alt="${{pNo}}" loading="lazy"/>
                        <span class="home-seed-type-tag ${{tagInfo[1]}}">${{tagInfo[0]}}</span>
                        <span style="font-size:0.68rem; font-weight:700; color:#0f172a; margin-top:3px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; width:100%;">${{brand || `#${{pNo}}`}}</span>
                    </div>
                `;
            }});

            container.innerHTML = html;
        }}

        function selectHomeSeedTab(seedPrdNo) {{
            currentSelectedSeed = String(seedPrdNo).trim();
            updateUrlQuery();
            renderHomeSeedTabs(homeExtractedSeeds);

            const activeText = document.getElementById('activeSeedStatus');
            if (activeText) {{
                activeText.textContent = currentSelectedSeed 
                    ? `선택된 시드 상품 #${{currentSelectedSeed}} 기준 유사 상품`
                    : '전체 맞춤 추천 (FORYOU)';
            }}

            if (!currentSelectedSeed) {{
                if (currentPrdNo) {{
                    loadTargetProductInfo(currentPrdNo);
                }} else {{
                    renderTargetProductCardEmpty();
                }}

                // [사용자 요청] 홈개인화에서 Index0 FORYOU 선택 시 API 재조회 수행
                fetchRecommendationApi();
            }} else {{
                loadTargetProductInfo(currentSelectedSeed);
                fetchSimilarItemForSeed(currentSelectedSeed);
            }}
        }}

        async function fetchSimilarItemForSeed(seedPrdNo) {{
            const curReqId = ++recommendRequestId;
            const startTime = performance.now();
            const apiBase = getApiBaseUrl();
            const statusEl = document.getElementById('statusBadge');
            if (statusEl) {{
                statusEl.textContent = `시드 #${{seedPrdNo}} 조회 중...`;
                statusEl.style.color = '#2563eb';
            }}

            const simEndpoint = currentMlType === 'lf' ? 'lfsimilaritem' : 'similaritem';
            const simTitle = currentMlType === 'lf' ? 'LF 유사 상품' : '유사 상품';
            const snippetEl = document.getElementById('activeApiUrlSnippet');
            if (snippetEl) snippetEl.textContent = `시드 #${{seedPrdNo}} (${{simTitle}}: /recommend/${{simEndpoint}}) · ${{currentK}}개`;

            const similarUrl = `${{apiBase}}/recommend/${{simEndpoint}}?siteCd=${{currentSiteCd}}&size=${{currentK}}&prdNo=${{seedPrdNo}}&originPrdYn=true&randomYn=false`;
            const fullUrlEl = document.getElementById('calledApiUrlFull');
            if (fullUrlEl) fullUrlEl.textContent = similarUrl;

            try {{
                const res = await fetch(similarUrl);
                const duration = Math.round(performance.now() - startTime);

                if (!res.ok) throw new Error(`HTTP ${{res.status}}`);
                const data = await res.json();
                if (curReqId !== recommendRequestId) return;
                currentRawData = data;

                if (statusEl) {{
                    statusEl.textContent = `200 OK (${{duration}}ms)`;
                    statusEl.style.color = '#059669';
                }}

                let results = [];
                if (Array.isArray(data)) results = data;
                else if (data && typeof data === 'object') {{
                    results = data.result || data.data || data.items || [];
                }}

                const exists = results.some(r => String(r.prdNo || r.prd_no) === String(seedPrdNo));
                if (!exists) {{
                    const seedObj = homeExtractedSeeds.find(s => String(s.prdNo || s.prd_no) === String(seedPrdNo));
                    if (seedObj) {{
                        results.unshift({{
                            ...seedObj,
                            rcm_prd_no: seedPrdNo,
                            is_origin_forced: true
                        }});
                    }}
                }}

                renderDashboardResults(results, true, seedPrdNo);
            }} catch (e) {{
                if (curReqId !== recommendRequestId) return;
                if (statusEl) statusEl.textContent = '서버 연결이 안됩니다';
                alert(`서버 연결이 안됩니다 (${{e.message}})`);
            }}
        }}

        function renderDashboardResults(products, isSimilarMode = false, seedPrdNo = '') {{
            renderProductGrid(products, isSimilarMode, seedPrdNo);
            renderProductTable(products, isSimilarMode, seedPrdNo);
            renderRawJsonView(currentRawData);
        }}

        function renderProductGrid(products, isSimilarMode = false, seedPrdNo = '') {{
            const container = document.getElementById('productGridContainer');
            if (!container) return;

            if (!products || products.length === 0) {{
                container.innerHTML = '<div style="grid-column:1/-1; padding:60px 20px; text-align:center; color:#64748b;">추천 결과 데이터가 없습니다.</div>';
                return;
            }}

            container.innerHTML = products.map((prd, idx) => {{
                const rank = idx + 1;
                const prdNo = String(prd.prdNo || prd.prd_no || prd.id || '');
                const prdUrl = getProductDetailUrl(prdNo);
                const name = prd.prdNm || prd.prd_nm || prd.name || '상품명 미확인';
                const brand = prd.brandNm || prd.brand_nm || prd.brdNm || '브랜드';
                const salePrc = prd.dcPrcMc || prd.dcPrcApp || prd.selPrc || prd.salePrc || prd.price || 0;
                const normPrc = prd.normPrc || prd.nrmPrc || 0;
                const discRt = prd.totRateApp || prd.discRt || (normPrc > salePrc && normPrc > 0 ? Math.round((normPrc - salePrc) / normPrc * 100) : 0);
                const score = prd.score !== undefined && prd.score !== '' ? Number(prd.score) : null;
                const esScore = prd.esscore !== undefined && prd.esscore !== '' ? Number(prd.esscore) : null;
                const imgPath = prd.appPrdImgUrl || prd.prd_img || prd.prdImg || '';
                const imgUrl = getImageUrl(imgPath);
                const selAcnt = prd.selAcntNo || prd.sel_acnt_no || '';

                const c1 = prd.dpCtgrNm1 || prd.category || '';
                const seedVal = prd.seed || '';
                const seedLabelMap = {{ 'recent': '최근본', 'basket': '장바구니', 'wish': '좋아요' }};
                const seedLabel = seedLabelMap[seedVal] || seedVal;

                const isOriginPrd = (isSimilarMode && seedPrdNo && prdNo === String(seedPrdNo)) || 
                                    (prd.is_origin_forced === true) || 
                                    (prd.rcm_prd_no && String(prd.rcm_prd_no) === prdNo);

                let typeLabel = '';
                if (prd.type === 'self') typeLabel = '베스트';
                else if (prd.type === 'DB') typeLabel = '휴리스틱';

                const rankClass = rank === 1 ? 'rank-badge rank-top1' : (rank === 2 ? 'rank-badge rank-top2' : (rank === 3 ? 'rank-badge rank-top3' : 'rank-badge'));
                const rankText = isOriginPrd ? '선택' : (rank <= 3 ? `TOP ${{rank}}` : `#${{rank}}`);

                return `
                    <div class="product-card ${{isOriginPrd ? 'card-origin' : ''}}">
                        <div class="product-img-wrap">
                            <span class="${{rankClass}}">${{rankText}}</span>
                            ${{isOriginPrd ? '<span class="origin-badge">[ 내가 본 ]</span>' : ''}}
                            <a href="${{prdUrl}}" target="_blank" rel="noopener noreferrer" style="display:block; width:100%; height:100%;">
                                <img src="${{imgUrl || 'data:image/svg+xml,%3Csvg xmlns=\\'http://www.w3.org/2000/svg\\' width=\\'100\\' height=\\'100\\'%3E%3Crect width=\\'100\\' height=\\'100\\' fill=\\'%23f1f5f9\\'/ %3E%3C/svg%3E'}}" class="product-img" alt="${{escapeHtml(name)}}" loading="lazy"/>
                            </a>
                        </div>
                        <div class="product-info">
                            <div class="product-brand-row">
                                <span class="brand-name" title="${{escapeHtml(brand)}}">${{brand}}</span>
                                <span class="product-card-prdno" title="상품번호: ${{prdNo}} (클릭 시 상세 이동)">
                                    <a href="${{prdUrl}}" target="_blank" rel="noopener noreferrer" style="text-decoration:none; color:inherit;">#${{prdNo}}</a>
                                </span>
                            </div>
                            <div class="product-name" title="${{escapeHtml(name)}}">
                                <a href="${{prdUrl}}" target="_blank" rel="noopener noreferrer" style="text-decoration:none; color:inherit;">
                                    ${{name}}
                                </a>
                            </div>
                            <div class="price-wrap">
                                ${{discRt > 0 ? `<span class="discount-rate">${{discRt}}%</span>` : ''}}
                                <span class="sale-price">${{Number(salePrc).toLocaleString()}}원</span>
                                ${{normPrc > salePrc ? `<span class="normal-price">${{Number(normPrc).toLocaleString()}}원</span>` : ''}}
                            </div>
                            <div class="badge-chip-container">
                                ${{isOriginPrd ? '<span class="badge-chip-item badge-red">내가 본 상품</span>' : ''}}
                                ${{typeLabel ? `<span class="badge-chip-item badge-emerald">${{typeLabel}}</span>` : ''}}
                                ${{selAcnt ? `<span class="badge-chip-item badge-cyan" title="협력사(판매자) 번호">협력사:${{selAcnt}}</span>` : ''}}
                                ${{score !== null && !isNaN(score) ? `<span class="badge-chip-item badge-blue" title="추천 스코어">추천: ${{score.toFixed(3)}}</span>` : ''}}
                                ${{esScore !== null && !isNaN(esScore) ? `<span class="badge-chip-item badge-amber" title="ES 스코어">ES: ${{esScore.toFixed(2)}}</span>` : ''}}
                                ${{seedLabel ? `<span class="badge-chip-item badge-purple" title="시드 출처">${{seedLabel}}</span>` : ''}}
                                ${{prd.rcm_prd_no && !isOriginPrd ? `<span class="badge-chip-item badge-gray" title="추천 대상">기준:#${{prd.rcm_prd_no}}</span>` : ''}}
                                ${{c1 ? `<span class="badge-chip-item badge-gray">${{c1}}</span>` : ''}}
                            </div>
                        </div>
                    </div>
                `;
            }}).join('');
        }}

        function renderProductTable(products, isSimilarMode = false, seedPrdNo = '') {{
            const tbody = document.getElementById('productTableBody');
            if (!tbody) return;

            if (!products || products.length === 0) {{
                tbody.innerHTML = '<tr><td colspan="12" style="text-align:center; padding:30px; color:#64748b;">추천 상품 데이터가 없습니다.</td></tr>';
                return;
            }}

            tbody.innerHTML = products.map((prd, idx) => {{
                const rank = idx + 1;
                const prdNo = String(prd.prdNo || prd.prd_no || prd.id || '-');
                const prdUrl = getProductDetailUrl(prdNo);
                const name = prd.prdNm || prd.prd_nm || prd.name || '-';
                const brand = prd.brandNm || prd.brand_nm || prd.brdNm || '-';
                const selAcnt = prd.selAcntNo || prd.sel_acnt_no || '-';
                const salePrc = prd.dcPrcMc || prd.dcPrcApp || prd.selPrc || prd.salePrc || prd.price || 0;
                const normPrc = prd.normPrc || prd.nrmPrc || 0;
                const discRt = prd.totRateApp || prd.discRt || (normPrc > salePrc && normPrc > 0 ? Math.round((normPrc - salePrc) / normPrc * 100) : 0);
                const score = prd.score !== undefined && prd.score !== '' && !isNaN(Number(prd.score)) ? Number(prd.score).toFixed(4) : '-';
                const esScore = prd.esscore !== undefined && prd.esscore !== '' && !isNaN(Number(prd.esscore)) ? Number(prd.esscore).toFixed(4) : '-';
                const c1 = prd.dpCtgrNm1 || prd.category || '-';

                const isOriginPrd = (isSimilarMode && seedPrdNo && prdNo === String(seedPrdNo)) || 
                                    (prd.is_origin_forced === true) || 
                                    (prd.rcm_prd_no && String(prd.rcm_prd_no) === prdNo);

                return `
                    <tr style="${{isOriginPrd ? 'background-color:#fff1f2;' : ''}}">
                        <td style="font-weight:700; color:#64748b;">${{rank}}</td>
                        <td>${{isOriginPrd ? '<span class="badge-chip-item badge-red">[내가본]</span>' : '<span class="badge-chip-item badge-blue">추천</span>'}}</td>
                        <td><a href="${{prdUrl}}" target="_blank" rel="noopener noreferrer" style="color:#2563eb; font-weight:700; text-decoration:none;">${{prdNo}} ↗</a></td>
                        <td style="font-weight:600;">${{brand}}</td>
                        <td style="max-width:240px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;" title="${{escapeHtml(name)}}">${{name}}</td>
                        <td style="font-weight:700; color:#0891b2;">${{selAcnt}}</td>
                        <td style="font-weight:700; color:#0f172a;">${{Number(salePrc).toLocaleString()}}원</td>
                        <td style="color:#94a3b8; text-decoration:line-through;">${{normPrc > 0 ? Number(normPrc).toLocaleString() + '원' : '-'}}</td>
                        <td style="font-weight:800; color:#f43f5e;">${{discRt > 0 ? discRt + '%' : '-'}}</td>
                        <td style="font-weight:700; color:#2563eb;">${{score}}</td>
                        <td style="color:#64748b;">${{esScore}}</td>
                        <td><span class="badge-chip-item badge-gray">${{c1}}</span></td>
                    </tr>
                `;
            }}).join('');
        }}

        function renderRawJsonView(data) {{
            const container = document.getElementById('rawJsonBody');
            if (!container) return;
            container.innerHTML = '';
            container.appendChild(createJsonTree(data, true, true));
        }}

        function createJsonTree(value, isRoot = false, defaultCollapsed = true) {{
            if (value === null) {{
                const s = document.createElement('span');
                s.className = 'json-null';
                s.textContent = 'null';
                return s;
            }}
            if (typeof value === 'boolean') {{
                const s = document.createElement('span');
                s.className = 'json-boolean';
                s.textContent = value ? 'true' : 'false';
                return s;
            }}
            if (typeof value === 'number') {{
                const s = document.createElement('span');
                s.className = 'json-number';
                s.textContent = String(value);
                return s;
            }}
            if (typeof value === 'string') {{
                const s = document.createElement('span');
                s.className = 'json-string';
                s.textContent = JSON.stringify(value);
                return s;
            }}

            const isArray = Array.isArray(value);
            const openBracket = isArray ? '[' : '{{';
            const closeBracket = isArray ? ']' : '}}';
            const keys = Object.keys(value);

            const wrap = document.createElement('div');
            if (keys.length === 0) {{
                wrap.innerHTML = `<span class="json-bracket">${{openBracket}}${{closeBracket}}</span>`;
                return wrap;
            }}

            const headerRow = document.createElement('span');
            headerRow.className = 'json-node-row';

            const toggle = document.createElement('span');
            toggle.className = 'json-toggle';
            toggle.textContent = defaultCollapsed ? '▶' : '▼';
            headerRow.appendChild(toggle);

            const openSpan = document.createElement('span');
            openSpan.className = 'json-bracket';
            openSpan.textContent = openBracket;
            headerRow.appendChild(openSpan);

            const childrenContainer = document.createElement('div');
            childrenContainer.className = 'json-children';
            if (defaultCollapsed) {{
                childrenContainer.style.display = 'none';
            }}

            keys.forEach((key, idx) => {{
                const row = document.createElement('div');
                row.className = 'json-node-row';

                if (!isArray) {{
                    const kSpan = document.createElement('span');
                    kSpan.className = 'json-key';
                    kSpan.textContent = `"${{key}}"`;
                    row.appendChild(kSpan);

                    const colon = document.createElement('span');
                    colon.style.color = '#94a3b8';
                    colon.textContent = ': ';
                    row.appendChild(colon);
                }}

                row.appendChild(createJsonTree(value[key], false, defaultCollapsed));

                if (idx < keys.length - 1) {{
                    const comma = document.createElement('span');
                    comma.style.color = '#64748b';
                    comma.textContent = ',';
                    row.appendChild(comma);
                }}

                childrenContainer.appendChild(row);
            }});

            const footerRow = document.createElement('div');
            footerRow.className = 'json-node-row';
            const closeSpan = document.createElement('span');
            closeSpan.className = 'json-bracket';
            closeSpan.textContent = closeBracket;
            footerRow.appendChild(closeSpan);

            function toggleNode() {{
                const isHidden = childrenContainer.style.display === 'none';
                childrenContainer.style.display = isHidden ? 'block' : 'none';
                toggle.textContent = isHidden ? '▼' : '▶';
            }}

            toggle.addEventListener('click', toggleNode);

            wrap.appendChild(headerRow);
            wrap.appendChild(childrenContainer);
            wrap.appendChild(footerRow);

            return wrap;
        }}

        function expandAllJson(containerId) {{
            const el = document.getElementById(containerId);
            if (!el) return;
            el.querySelectorAll('.json-children').forEach(c => c.style.display = 'block');
            el.querySelectorAll('.json-toggle').forEach(tg => tg.textContent = '▼');
        }}

        function collapseAllJson(containerId) {{
            const el = document.getElementById(containerId);
            if (!el) return;
            el.querySelectorAll('.json-children').forEach(c => c.style.display = 'none');
            el.querySelectorAll('.json-toggle').forEach(tg => tg.textContent = '▶');
        }}

        function openApiUrlInNewTab() {{
            if (currentApiUrl) window.open(currentApiUrl, '_blank', 'noopener,noreferrer');
        }}

        function copyApiUrlToClipboard() {{
            if (!currentApiUrl) return;
            navigator.clipboard.writeText(currentApiUrl).then(() => {{
                alert('API URL 복사 완료');
            }}).catch(() => {{
                prompt('API URL 복사:', currentApiUrl);
            }});
        }}

        function copyJsonTextToClipboard() {{
            if (!currentRawData) return;
            const str = JSON.stringify(currentRawData, null, 2);
            navigator.clipboard.writeText(str).then(() => {{
                const btn = document.getElementById('btnCopyJson');
                if (btn) {{
                    const orig = btn.textContent;
                    btn.textContent = '복사완료!';
                    setTimeout(() => {{ btn.textContent = orig; }}, 1500);
                }}
            }}).catch(() => {{
                alert('JSON 복사 실패');
            }});
        }}

        function escapeHtml(str) {{
            if (!str) return '';
            return String(str)
                .replace(/&/g, '&amp;')
                .replace(/</g, '&lt;')
                .replace(/>/g, '&gt;')
                .replace(/"/g, '&quot;')
                .replace(/'/g, '&#039;');
        }}

        if (document.readyState === 'loading') {{
            document.addEventListener('DOMContentLoaded', initApp);
        }} else {{
            initApp();
        }}
    </script>
</body>
</html>
"""

# 6. Streamlit 컴포넌트 렌더링 (풀스크린 뷰포트)
components.html(html_content, height=1250, scrolling=False)
