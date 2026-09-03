import os
import json
import urllib.parse
import streamlit as st
import streamlit.components.v1 as components

# 1. 페이지 기본 설정 (전체 화면 모드)
st.set_page_config(
    page_title="AI Recomm Service Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. 기본 CSS 덮어쓰기 (Streamlit 사방 여백 완전 제거 및 뷰포트 100% 풀스크린 고정)
st.markdown("""
<style>
    /* 1. Streamlit 헤더, 툴바, 풋터 일체 은폐 */
    header[data-testid="stHeader"], div[data-testid="stToolbar"], div[data-testid="stDecoration"], .stAppHeader, footer, #MainMenu {
        display: none !important;
        visibility: hidden !important;
    }
    /* 2. Streamlit 루트 앱 및 메인 컨테이너 사방 여백 완전 제거 */
    html, body, .stApp, section.main, .main, .block-container, div[data-testid="stBlockContainer"], div[data-testid="stCustomComponentV1"] {
        padding: 0 !important;
        margin: 0 !important;
        max-width: 100% !important;
        width: 100% !important;
        height: 100% !important;
        overflow: hidden !important;
        background-color: #ffffff !important;
    }
    /* 3. iframe을 브라우저 뷰포트 전체(100vw x 100vh)로 강제 고정하여 사방 여백 완전 제거 */
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
    BORIBORI_WEB_URL = str(domains_conf["boribori_web"]).rstrip("/")
    BORIBORI_API_URL = str(domains_conf["boribori_api"]).rstrip("/")
    BORIBORI_CDN_URL = str(domains_conf["boribori_cdn"]).rstrip("/")
except Exception as e:
    raise ValueError(f".streamlit/secrets.toml 내 [domains] 섹션 및 필수 도메인 키가 누락되었습니다: {e}")

# 3. 기본 시드 상품(베스트 상품) 데이터 정의 (하프클럽 & 보리보리)
SEED_PRODUCTS = {
    "1": [
        {"prd_no": "380118214", "prd_nm": "여성의류", "full_name": "여성의류 베스트", "category": "여성의류", "brand_nm": "모조에스핀", "img_url": ""},
        {"prd_no": "402544118", "prd_nm": "남성의류", "full_name": "남성의류 베스트", "category": "남성의류", "brand_nm": "헤지스", "img_url": ""},
        {"prd_no": "379859455", "prd_nm": "신발", "full_name": "신발 베스트", "category": "신발", "brand_nm": "나이키", "img_url": ""},
        {"prd_no": "393954850", "prd_nm": "가방", "full_name": "가방 베스트", "category": "가방", "brand_nm": "닥스", "img_url": ""},
        {"prd_no": "391016367", "prd_nm": "스포츠", "full_name": "스포츠 베스트", "category": "스포츠", "brand_nm": "아디다스", "img_url": ""},
        {"prd_no": "380115991", "prd_nm": "액세서리", "full_name": "액세서리 베스트", "category": "액세서리", "brand_nm": "골든듀", "img_url": ""},
        {"prd_no": "377519208", "prd_nm": "골프웨어", "full_name": "골프웨어 베스트", "category": "골프", "brand_nm": "캘러웨이", "img_url": ""},
        {"prd_no": "383412091", "prd_nm": "아우터", "full_name": "아우터 베스트", "category": "여성의류", "brand_nm": "온앤온", "img_url": ""},
        {"prd_no": "390124890", "prd_nm": "원피스", "full_name": "원피스 베스트", "category": "여성의류", "brand_nm": "샤틴", "img_url": ""},
        {"prd_no": "385901234", "prd_nm": "슬랙스", "full_name": "슬랙스 베스트", "category": "남성의류", "brand_nm": "지오지아", "img_url": ""},
        {"prd_no": "388712345", "prd_nm": "스니커즈", "full_name": "스니커즈 베스트", "category": "신발", "brand_nm": "뉴발란스", "img_url": ""},
        {"prd_no": "391234567", "prd_nm": "이너웨어", "full_name": "이너웨어 베스트", "category": "언더웨어", "brand_nm": "비너스", "img_url": ""}
    ],
    "2": [
        {"prd_no": "380118214", "prd_nm": "베이비의류", "full_name": "베이비의류 베스트", "category": "베이비", "brand_nm": "모이몰른", "img_url": ""},
        {"prd_no": "402544118", "prd_nm": "키즈의류", "full_name": "키즈의류 베스트", "category": "키즈", "brand_nm": "닥스키즈", "img_url": ""},
        {"prd_no": "379859455", "prd_nm": "주니어의류", "full_name": "주니어의류 베스트", "category": "주니어", "brand_nm": "뉴에라키즈", "img_url": ""},
        {"prd_no": "393954850", "prd_nm": "유아신발", "full_name": "유아신발 베스트", "category": "신발", "brand_nm": "아디다스키즈", "img_url": ""},
        {"prd_no": "391016367", "prd_nm": "아동가방", "full_name": "아동가방 베스트", "category": "가방/잡화", "brand_nm": "휠라키즈", "img_url": ""},
        {"prd_no": "380115991", "prd_nm": "출산/육아용품", "full_name": "출산/육아용품 베스트", "category": "육아용품", "brand_nm": "블루래빗", "img_url": ""}
    ]
}

# 4. 추천 모델 서비스 목록 정의
ML_TYPES = [
    {"id": "similaritem", "name": "유사 상품 (similarItem)", "desc": "상품 간 속성 및 임베딩 기반 유사 추천"},
    {"id": "viewtogether", "name": "함께 본 상품 (viewTogether)", "desc": "동일 세션/사용자가 함께 조회한 상품"},
    {"id": "buytogether", "name": "함께 구매한 상품 (buyTogether)", "desc": "동일 장바구니/주문서 함께 구매 상품"},
    {"id": "similar-image", "name": "유사 이미지 상품 (similarImage)", "desc": "비전 임베딩 기반 시각적 유사 상품"},
    {"id": "recommendforyou", "name": "개인화 추천 (recommendForYou)", "desc": "다중 상품 히스토리 기반 맞춤 추천"},
    {"id": "multiSimilarItem", "name": "유사 상품 조합 (multiSimilarItem)", "desc": "다중 상품 입력 기반 결합 유사도"},
    {"id": "meanSimilarItem", "name": "평균 유사 상품 (meanSimilarItem)", "desc": "다중 상품 벡터 평균 기반 유사 추천"},
    {"id": "meanSimilarItemView", "name": "평균 유사 상품 조회 (meanSimilarItemView)", "desc": "조회 이력 벡터 평균 기반 유사 추천"},
    {"id": "meanSimilarItemBuy", "name": "평균 유사 상품 구매 (meanSimilarItemBuy)", "desc": "구매 이력 벡터 평균 기반 유사 추천"}
]

# 5. URL 쿼리 파라미터 디코딩 및 초기 상태 설정
qp = st.query_params
raw_site = qp.get("siteCd", "1")
if raw_site not in ["1", "2"]:
    raw_site = "1"

raw_type = qp.get("mlType", "similaritem")
valid_type_ids = [m["id"] for m in ML_TYPES]
if raw_type not in valid_type_ids:
    raw_type = "similaritem"

raw_prd = qp.get("prdNo", "")
if raw_prd:
    raw_prd = urllib.parse.unquote(str(raw_prd)).strip()
else:
    default_seeds = SEED_PRODUCTS.get(raw_site, [])
    raw_prd = default_seeds[0]["prd_no"] if default_seeds else "380118214"

raw_k = qp.get("k", "50")
if not raw_k.isdigit() or int(raw_k) <= 0:
    raw_k = "50"

raw_age = qp.get("age", "")
raw_gender = qp.get("gender", "")
raw_tab = qp.get("tab", "grid")
if raw_tab not in ["grid", "table", "raw"]:
    raw_tab = "grid"

seed_products_json = json.dumps(SEED_PRODUCTS, ensure_ascii=False)
ml_types_json = json.dumps(ML_TYPES, ensure_ascii=False)
initial_site_json = json.dumps(raw_site, ensure_ascii=False)
initial_type_json = json.dumps(raw_type, ensure_ascii=False)
initial_prd_json = json.dumps(raw_prd, ensure_ascii=False)
initial_k_json = json.dumps(raw_k, ensure_ascii=False)
initial_age_json = json.dumps(raw_age, ensure_ascii=False)
initial_gender_json = json.dumps(raw_gender, ensure_ascii=False)
initial_tab_json = json.dumps(raw_tab, ensure_ascii=False)

# 6. SPA 통합 HTML/CSS/JS 템플릿
html_content = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Recomm Service Dashboard</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;600;700;800&family=Outfit:wght@400;600;700;800&display=swap" rel="stylesheet">
    <style>
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: 'Noto Sans KR', -apple-system, BlinkMacSystemFont, sans-serif;
        }}
        html, body {{
            background-color: #ffffff;
            color: #0f172a;
            height: 100%;
            width: 100%;
            margin: 0;
            padding: 0;
            overflow: hidden;
        }}
        .app-container {{
            display: flex;
            height: 100vh;
            width: 100%;
            overflow: hidden;
        }}
        /* 좌측 사이드바 */
        .sidebar {{
            width: 270px;
            background-color: #ffffff;
            border-right: 1px solid #e2e8f0;
            display: flex;
            flex-direction: column;
            flex-shrink: 0;
        }}
        .sidebar-header {{
            padding: 16px 18px;
            border-bottom: 1px solid #e2e8f0;
            cursor: pointer;
            transition: background-color 0.15s ease;
            user-select: none;
        }}
        .sidebar-header:hover {{
            background-color: #f8fafc;
        }}
        .sidebar-title {{
            font-size: 1.05rem;
            font-weight: 800;
            color: #0f172a;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}
        .search-box {{
            padding: 12px 18px;
            border-bottom: 1px solid #f1f5f9;
        }}
        .search-input {{
            width: 100%;
            padding: 8px 12px;
            border: 1px solid #cbd5e1;
            border-radius: 6px;
            font-size: 0.85rem;
            outline: none;
            transition: border-color 0.15s ease;
        }}
        .search-input:focus {{
            border-color: #2563eb;
        }}
        .seed-list {{
            list-style: none;
            overflow-y: auto;
            flex: 1;
            padding: 8px 0;
        }}
        .seed-item {{
            padding: 8px 14px;
            margin: 2px 10px;
            font-size: 0.86rem;
            color: #334155;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: space-between;
            border-radius: 8px;
            transition: all 0.15s ease;
            gap: 8px;
        }}
        .seed-item:hover {{
            background-color: #f1f5f9;
            color: #0f172a;
        }}
        .seed-item:focus {{
            outline: 2px solid #2563eb;
            outline-offset: -2px;
            background-color: #eff6ff;
            color: #1d4ed8;
        }}
        .seed-item.active {{
            background-color: #eff6ff;
            color: #2563eb;
            font-weight: 800;
            border-left: 3px solid #2563eb;
        }}
        
        /* 우측 메인 대시보드 */
        .main-content {{
            flex: 1;
            display: flex;
            flex-direction: column;
            overflow-y: auto;
            background-color: #f8fafc;
        }}
        .top-navbar {{
            padding: 12px 28px;
            border-bottom: 1px solid #e2e8f0;
            display: flex;
            align-items: center;
            justify-content: space-between;
            background-color: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(8px);
            position: sticky;
            top: 0;
            z-index: 20;
            gap: 16px;
            flex-wrap: wrap;
        }}
        .navbar-title {{
            font-size: 1.25rem;
            font-weight: 800;
            color: #0f172a;
            transition: color 0.15s ease;
            display: flex;
            align-items: center;
            gap: 6px;
        }}
        .navbar-title:hover, .navbar-title:hover span {{
            color: #2563eb !important;
        }}
        .dashboard-body {{
            padding: 20px 28px;
            flex: 1;
        }}
        
        /* 헤더 메타 뱃지 */
        .meta-badges {{
            display: flex;
            align-items: center;
            gap: 10px;
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 10px;
            padding: 8px 16px;
            margin-bottom: 16px;
            font-size: 0.82rem;
            color: #64748b;
            font-weight: 600;
            box-shadow: 0 1px 3px rgba(0,0,0,0.02);
            flex-wrap: wrap;
        }}
        
        /* 추천 대상 상품 카드 */
        .target-card-box {{
            background-color: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            padding: 18px 24px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.03);
            margin-bottom: 18px;
            box-sizing: border-box;
            width: 100%;
        }}
        .target-card-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 12px;
            padding-bottom: 8px;
            border-bottom: 1px solid #f1f5f9;
        }}
        .target-title {{
            font-size: 1.02rem;
            font-weight: 800;
            color: #0f172a;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .target-content-body {{
            display: flex;
            gap: 18px;
            align-items: center;
        }}
        .target-img-wrap {{
            width: 80px;
            height: 96px;
            border-radius: 8px;
            overflow: hidden;
            background-color: #f1f5f9;
            flex-shrink: 0;
            border: 1px solid #e2e8f0;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .target-img {{
            width: 100%;
            height: 100%;
            object-fit: cover;
        }}
        .target-info-wrap {{
            display: flex;
            flex-direction: column;
            gap: 5px;
            flex: 1;
            min-width: 0;
        }}
        
        /* 탭 서식 */
        .tab-navigation {{
            display: flex;
            gap: 6px;
            border-bottom: 2px solid #e2e8f0;
            margin-bottom: 14px;
        }}
        .tab-btn {{
            padding: 9px 18px;
            font-size: 0.92rem;
            font-weight: 700;
            color: #64748b;
            background: none;
            border: none;
            cursor: pointer;
            border-bottom: 3px solid transparent;
            margin-bottom: -2px;
            border-radius: 6px 6px 0 0;
            transition: all 0.15s ease;
        }}
        .tab-btn:hover {{
            color: #0f172a;
            background: transparent;
        }}
        .tab-btn.active {{
            color: #2563eb;
            border-bottom-color: #2563eb;
            background: transparent;
        }}
        .tab-content {{
            display: none;
        }}
        .tab-content.active {{
            display: block;
        }}
        
        /* 10열 그리드 카드 배치 */
        .grid-container {{
            display: grid;
            grid-template-columns: repeat(10, 1fr);
            gap: 10px;
        }}
        .product-card {{
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            overflow: hidden;
            background: #ffffff;
            box-shadow: 0 1px 2px rgba(0,0,0,0.03);
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            transition: border-color 0.15s ease, box-shadow 0.15s ease;
        }}
        .product-card:hover {{
            border-color: #94a3b8;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.06);
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
            background: rgba(15, 23, 42, 0.82);
            backdrop-filter: blur(4px);
            color: #ffffff;
            font-size: 10px;
            font-weight: 800;
            padding: 2px 5px;
            border-radius: 4px;
            letter-spacing: 0.2px;
            z-index: 2;
        }}
        .rank-top1 {{
            background: linear-gradient(135deg, #f59e0b, #d97706) !important;
            color: #ffffff !important;
            box-shadow: 0 2px 6px rgba(245, 158, 11, 0.4);
        }}
        .rank-top2, .rank-top3 {{
            background: linear-gradient(135deg, #334155, #1e293b) !important;
            color: #ffffff !important;
        }}
        .product-info {{
            padding: 8px 8px 6px 8px;
        }}
        .brand-name {{
            font-size: 0.72rem;
            color: #64748b;
            font-weight: 700;
            margin-bottom: 2px;
            text-transform: uppercase;
            letter-spacing: 0.1px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
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
        .badge-brand {{ background: #ecfdf5; color: #059669; border: 1px solid #a7f3d0; }}
        .badge-purple {{ background: #f5f3ff; color: #7c3aed; border: 1px solid #ddd6fe; }}
        
        /* 데이터 테이블 */
        .data-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.85rem;
            background: #ffffff;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 1px 3px rgba(0,0,0,0.03);
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
        .data-table tr:hover {{
            background-color: #f8fafc;
        }}

        /* 슬림 스크롤바 */
        ::-webkit-scrollbar {{
            width: 6px;
            height: 6px;
        }}
        ::-webkit-scrollbar-track {{
            background: transparent;
        }}
        ::-webkit-scrollbar-thumb {{
            background: #cbd5e1;
            border-radius: 3px;
        }}
        ::-webkit-scrollbar-thumb:hover {{
            background: #94a3b8;
        }}
        
        pre, code, pre code {{
            color: #f8fafc !important;
            font-family: 'Consolas', 'Courier New', monospace;
            font-size: 0.84rem;
            line-height: 1.6;
        }}
        .json-key {{ color: #38bdf8 !important; font-weight: 700; }}
        .json-string {{ color: #4ade80 !important; }}
        .json-number {{ color: #fb923c !important; font-weight: 700; }}
        .json-boolean {{ color: #c084fc !important; font-weight: 700; }}
        .json-null {{ color: #f43f5e !important; font-weight: 700; }}

        /* JSON 트리 전용 스타일 */
        .json-node-collapsible {{
            display: inline;
        }}
        .json-toggle {{
            cursor: pointer;
            user-select: none;
            display: inline-block;
            width: 13px;
            font-size: 9px;
            color: #94a3b8;
            vertical-align: middle;
            transition: color 0.15s ease;
        }}
        .json-toggle:hover {{
            color: #38bdf8;
        }}
        .json-bracket {{
            color: #cbd5e1;
            font-weight: bold;
        }}
        .json-colon {{
            color: #94a3b8;
        }}
        .json-comma {{
            color: #64748b;
        }}
        .json-children {{
            padding-left: 18px;
            border-left: 1px dotted #334155;
            margin-left: 4px;
        }}
        .json-node-row {{
            line-height: 1.55;
            word-break: break-all;
        }}
        .json-collapsed-text {{
            background: #1e293b;
            color: #94a3b8;
            font-size: 0.72rem;
            padding: 1px 6px;
            border-radius: 4px;
            border: 1px solid #334155;
            cursor: pointer;
            user-select: none;
            margin: 0 3px;
        }}
        .json-collapsed-text:hover {{
            background: #334155;
            color: #f8fafc;
        }}
        .json-ctrl-btn {{
            background: #334155;
            color: #f8fafc;
            border: none;
            padding: 4px 9px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: 600;
            cursor: pointer;
            transition: background 0.15s ease;
        }}
        .json-ctrl-btn:hover {{
            background: #475569;
        }}
    </style>
</head>
<body>
    <div class="app-container">
        <!-- 좌측 사이드바: 추천 시드 상품 목록 -->
        <aside class="sidebar">
            <div class="sidebar-header" onclick="goToDefaultPage()" title="기본 페이지로 리셋">
                <div class="sidebar-title">
                    <span>추천 시드 상품</span>
                    <span style="font-size:0.75rem; background:#eff6ff; color:#2563eb; padding:2px 8px; border-radius:10px;" id="seedCountBadge">0</span>
                </div>
            </div>
            <div class="search-box">
                <input type="text" id="seedSearchInput" class="search-input" placeholder="상품명/카테고리 검색..."/>
            </div>
            <ul class="seed-list" id="seedList"></ul>
        </aside>

        <!-- 우측 메인 대시보드 -->
        <main class="main-content">
            <header class="top-navbar">
                <div style="display:flex; align-items:center; gap:10px; min-width:240px;">
                    <a id="currentPrdTitleLink" href="#" target="_blank" rel="noopener noreferrer" style="text-decoration:none; color:inherit;" title="쇼핑몰 상세 페이지 새 탭 열기">
                        <h1 class="navbar-title" id="currentPrdTitle">
                            <span id="currentPrdText">상품 선택 대기</span>
                            <span style="font-size:0.95rem; color:#64748b; font-weight:normal;">↗</span>
                        </h1>
                    </a>
                    <span id="navMlTypeBadge" style="background:#eff6ff; border:1px solid #dbeafe; color:#1d4ed8; font-size:12px; font-weight:700; padding:3px 10px; border-radius:9999px; white-space:nowrap;">유사 상품</span>
                    <button id="btnCopyUrl" onclick="copyCurrentUrl()" style="background:#f1f5f9; border:1px solid #cbd5e1; color:#475569; font-size:11px; font-weight:700; padding:4px 9px; border-radius:6px; cursor:pointer;" title="현재 상태 URL 링크 복사">URL 복사</button>
                </div>

                <div style="display:flex; align-items:center; gap:10px; font-size:0.84rem; font-weight:700; color:#334155; flex-wrap:wrap;">
                    <!-- 사이트 선택 -->
                    <div style="display:flex; align-items:center; gap:5px;">
                        <span>사이트:</span>
                        <select id="siteCdSelect" style="padding:5px 9px; border-radius:6px; border:1px solid #cbd5e1; background:#ffffff; font-size:0.84rem; font-weight:700; color:#0f172a; outline:none;">
                            <option value="1">1 (하프클럽)</option>
                            <option value="2">2 (보리보리)</option>
                        </select>
                    </div>

                    <!-- 추천 모델 선택 -->
                    <div style="display:flex; align-items:center; gap:5px;">
                        <span>추천 유형:</span>
                        <select id="mlTypeSelect" style="padding:5px 9px; border-radius:6px; border:1px solid #cbd5e1; background:#ffffff; font-size:0.84rem; font-weight:700; color:#0f172a; outline:none; max-width:200px;"></select>
                    </div>

                    <!-- 상품 번호 직접 입력 -->
                    <div style="display:flex; align-items:center; gap:5px;">
                        <span>상품번호:</span>
                        <input type="text" id="directPrdInput" placeholder="단일 or 쉼표구분 다중" style="width:140px; padding:5px 8px; border-radius:6px; border:1px solid #cbd5e1; background:#ffffff; font-size:0.84rem; font-weight:600; color:#0f172a; outline:none;" title="상품번호 직접 입력 (예: 380118214,402544118)"/>
                    </div>

                    <!-- 연령/성별 필터 -->
                    <div style="display:flex; align-items:center; gap:4px;">
                        <select id="ageSelect" style="padding:5px 7px; border-radius:6px; border:1px solid #cbd5e1; background:#ffffff; font-size:0.82rem; font-weight:600; color:#0f172a; outline:none;">
                            <option value="">연령: 전체</option>
                            <option value="01">40대 미만</option>
                            <option value="02">40대 이상</option>
                        </select>
                        <select id="genderSelect" style="padding:5px 7px; border-radius:6px; border:1px solid #cbd5e1; background:#ffffff; font-size:0.82rem; font-weight:600; color:#0f172a; outline:none;">
                            <option value="">성별: 전체</option>
                            <option value="01">남성</option>
                            <option value="02">여성</option>
                        </select>
                    </div>

                    <!-- 조회 수 k -->
                    <div style="display:flex; align-items:center; gap:4px;">
                        <span>k:</span>
                        <input type="number" id="sizeInput" value="50" min="1" max="200" style="width:52px; padding:5px 6px; border-radius:6px; border:1px solid #cbd5e1; background:#ffffff; font-size:0.84rem; font-weight:700; color:#0f172a; text-align:center; outline:none;"/>
                    </div>

                    <!-- 조회 버튼 -->
                    <button id="btnFetch" onclick="triggerFetch()" style="background:#0b1329; color:#ffffff; border:none; padding:7px 16px; border-radius:6px; font-weight:800; font-size:0.85rem; cursor:pointer; transition:background 0.15s ease;">API 연동 조회</button>
                </div>
            </header>

            <div class="dashboard-body">
                <!-- 메타 메타데이터 뱃지 바 -->
                <div class="meta-badges" id="metaBadgesBar">
                    <div style="display:flex; align-items:center; gap:6px; background:#f8fafc; border:1px solid #e2e8f0; padding:3px 10px; border-radius:6px;">
                        <span style="color:#64748b; font-size:0.75rem;">사이트</span>
                        <span style="color:#2563eb; font-weight:800; font-size:0.82rem;" id="metaSiteText">하프클럽</span>
                    </div>
                    <div style="display:flex; align-items:center; gap:6px; background:#f8fafc; border:1px solid #e2e8f0; padding:3px 10px; border-radius:6px;">
                        <span style="color:#64748b; font-size:0.75rem;">추천 모델</span>
                        <span style="color:#0f172a; font-weight:800; font-size:0.82rem;" id="metaMlTypeText">-</span>
                    </div>
                    <div style="display:flex; align-items:center; gap:6px; background:#f8fafc; border:1px solid #e2e8f0; padding:3px 10px; border-radius:6px;">
                        <span style="color:#64748b; font-size:0.75rem;">대상 상품번호</span>
                        <span style="color:#db2777; font-weight:800; font-size:0.82rem;" id="metaPrdNoText">-</span>
                    </div>
                    <div style="display:flex; align-items:center; gap:6px; background:#f8fafc; border:1px solid #e2e8f0; padding:3px 10px; border-radius:6px;">
                        <span style="color:#64748b; font-size:0.75rem;">필터 조건</span>
                        <span style="color:#334155; font-weight:700; font-size:0.82rem;" id="metaConditionText">연령: 전체 / 성별: 전체</span>
                    </div>
                    <div style="display:flex; align-items:center; gap:6px; background:#f8fafc; border:1px solid #e2e8f0; padding:3px 10px; border-radius:6px;">
                        <span style="color:#64748b; font-size:0.75rem;">조회 수</span>
                        <span style="color:#334155; font-weight:700; font-size:0.82rem;" id="metaKText">50개</span>
                    </div>
                    <div style="display:flex; align-items:center; gap:6px; background:#f8fafc; border:1px solid #e2e8f0; padding:3px 10px; border-radius:6px; margin-left:auto;">
                        <span style="color:#64748b; font-size:0.75rem;">응답 상태</span>
                        <span style="color:#059669; font-weight:800; font-size:0.82rem;" id="metaStatusText">-</span>
                    </div>
                </div>

                <!-- 추천 대상 상품 상세 정보 카드 -->
                <div class="target-card-box" id="targetCard">
                    <div class="target-card-header">
                        <div class="target-title">추천 대상 상품 정보</div>
                        <div style="display:flex; gap:6px;" id="targetTagsHeader"></div>
                    </div>
                    <div class="target-content-body" id="targetContentBody">
                        <div class="target-img-wrap" id="targetImgWrap">
                            <span style="font-size:0.72rem; color:#94a3b8;">이미지 로딩</span>
                        </div>
                        <div class="target-info-wrap">
                            <div style="font-size:0.82rem; font-weight:700; color:#64748b;" id="targetBrandText">-</div>
                            <div style="font-size:1.02rem; font-weight:800; color:#0f172a; line-height:1.4;" id="targetNameText">상품 정보를 조회 중입니다...</div>
                            <div style="display:flex; align-items:baseline; gap:6px; margin-top:2px;">
                                <span style="font-size:1.05rem; font-weight:800; color:#0f172a;" id="targetPriceText">- 원</span>
                                <span style="font-size:0.82rem; color:#94a3b8; text-decoration:line-through;" id="targetNormPriceText"></span>
                                <span style="font-size:0.85rem; font-weight:800; color:#f43f5e;" id="targetDiscRateText"></span>
                            </div>
                            <div style="font-size:0.8rem; color:#64748b; font-weight:600; margin-top:4px;" id="targetCategoryPath"></div>
                        </div>
                    </div>
                    <!-- 다중 대상 상품 칩 목록 (개인화 추천 등) -->
                    <div id="multiTargetChipsWrap" style="display:none; margin-top:10px; padding-top:8px; border-top:1px solid #f1f5f9;">
                        <div style="font-size:0.78rem; font-weight:700; color:#475569; margin-bottom:6px;">다중 대상 상품 목록:</div>
                        <div id="multiTargetChipsContainer" style="display:flex; flex-wrap:wrap; gap:6px;"></div>
                    </div>
                </div>

                <!-- 뷰 탭 네비게이션 -->
                <nav class="tab-navigation">
                    <button class="tab-btn active" id="tabBtnGrid" onclick="switchViewTab('grid')">추천 상품</button>
                    <button class="tab-btn" id="tabBtnTable" onclick="switchViewTab('table')">추천 상품 데이터 확인</button>
                    <button class="tab-btn" id="tabBtnRaw" onclick="switchViewTab('raw')">API JSON 데이터 확인</button>
                </nav>

                <!-- 탭 1: 10열 그리드 배치 -->
                <section class="tab-content active" id="tabContentGrid">
                    <div class="grid-container" id="productGridContainer">
                        <div style="grid-column:1/-1; padding:40px 20px; text-align:center; color:#64748b;">추천 상품 데이터를 불러오는 중입니다...</div>
                    </div>
                </section>

                <!-- 탭 2: 데이터 테이블 배치 -->
                <section class="tab-content" id="tabContentTable">
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>순번</th>
                                <th>상품번호</th>
                                <th>브랜드</th>
                                <th>상품명</th>
                                <th>판매가</th>
                                <th>정가</th>
                                <th>할인율</th>
                                <th>추천 스코어</th>
                                <th>ES 스코어</th>
                                <th>카테고리</th>
                            </tr>
                        </thead>
                        <tbody id="productTableBody">
                            <tr><td colspan="10" style="text-align:center; padding:30px; color:#64748b;">데이터를 불러오는 중입니다...</td></tr>
                        </tbody>
                    </table>
                </section>

                <!-- 탭 3: Raw JSON 데이터 배치 -->
                <section class="tab-content" id="tabContentRaw">
                    <div id="rawJsonContainer">
                        <div style="background:#0f172a; border-radius:8px; border:1px solid #1e293b; box-shadow:0 1px 3px rgba(0,0,0,0.2); overflow:hidden;">
                            <div style="display:flex; align-items:center; justify-content:space-between; padding:10px 16px; background:#1e293b; border-bottom:1px solid #334155;">
                                <div style="display:flex; align-items:center; gap:8px; overflow:hidden;">
                                    <span style="background:#0284c7; color:#ffffff; font-size:11px; font-weight:800; padding:2px 7px; border-radius:4px;">API URL</span>
                                    <span id="calledApiUrlText" style="font-size:0.83rem; font-weight:600; color:#94a3b8; word-break:break-all;">-</span>
                                </div>
                                <div style="display:flex; align-items:center; gap:6px; flex-shrink:0;">
                                    <button class="json-ctrl-btn" onclick="openApiUrlInNewTab()">새 창 열기 ↗</button>
                                    <button class="json-ctrl-btn" onclick="copyApiUrlToClipboard()">URL 복사</button>
                                </div>
                            </div>
                            <div style="display:flex; align-items:center; justify-content:space-between; padding:8px 16px; background:#1e293b; border-bottom:1px solid #334155;">
                                <span style="font-size:0.8rem; font-weight:700; color:#cbd5e1;">Response JSON</span>
                                <div style="display:flex; align-items:center; gap:6px;">
                                    <button class="json-ctrl-btn" onclick="expandAllJson('rawJsonBody')">전체 펼치기</button>
                                    <button class="json-ctrl-btn" onclick="collapseAllJson('rawJsonBody')">전체 접기</button>
                                    <button id="btnCopyJson" class="json-ctrl-btn" onclick="copyJsonTextToClipboard()">내용 복사</button>
                                </div>
                            </div>
                            <div style="padding:14px 16px; background:#0f172a; max-height:600px; overflow:auto;">
                                <div id="rawJsonBody" class="json-tree-container"></div>
                            </div>
                        </div>
                    </div>
                </section>
            </div>
        </main>
    </div>

    <script>
        const DOMAINS = {{
            HALFCLUB_WEB: "{HALFCLUB_WEB_URL}",
            HALFCLUB_API: "{HALFCLUB_API_URL}",
            HALFCLUB_CDN: "{HALFCLUB_CDN_URL}",
            BORIBORI_WEB: "{BORIBORI_WEB_URL}",
            BORIBORI_API: "{BORIBORI_API_URL}",
            BORIBORI_CDN: "{BORIBORI_CDN_URL}"
        }};

        const SEED_DATA = {seed_products_json};
        const ML_TYPES_LIST = {ml_types_json};

        let currentSiteCd = {initial_site_json};
        let currentMlType = {initial_type_json};
        let currentPrdNo = {initial_prd_json};
        let currentK = {initial_k_json};
        let currentAge = {initial_age_json};
        let currentGender = {initial_gender_json};
        let currentTab = {initial_tab_json};

        let currentRawData = null;
        let currentApiUrl = '';
        let displayedSeeds = [];

        function getWebBaseUrl() {{
            return currentSiteCd === '2' ? DOMAINS.BORIBORI_WEB : DOMAINS.HALFCLUB_WEB;
        }}

        function getApiBaseUrl() {{
            return currentSiteCd === '2' ? DOMAINS.BORIBORI_API : DOMAINS.HALFCLUB_API;
        }}

        function getCdnBaseUrl() {{
            return currentSiteCd === '2' ? DOMAINS.BORIBORI_CDN : DOMAINS.HALFCLUB_CDN;
        }}

        function getProductDetailUrl(prdNo) {{
            if (!prdNo || prdNo === '-') return '#';
            return `${{getWebBaseUrl()}}/product/${{prdNo}}`;
        }}

        function getImageUrl(imgPath) {{
            if (!imgPath) return '';
            if (imgPath.startsWith('http://') || imgPath.startsWith('https://')) return imgPath;
            return `${{getCdnBaseUrl()}}/rimg/330x440/contain/${{imgPath}}`;
        }}

        function goToDefaultPage() {{
            try {{
                if (window.top && window.top.location) {{
                    window.top.location.href = window.top.location.origin + window.top.location.pathname;
                    return;
                }}
            }} catch (e) {{}}
            try {{
                if (window.parent && window.parent.location) {{
                    window.parent.location.href = window.parent.location.origin + window.parent.location.pathname;
                    return;
                }}
            }} catch (e) {{}}
            location.reload();
        }}

        function copyCurrentUrl() {{
            const hostUrl = (window.parent && window.parent.location && window.parent.location.origin) 
                ? (window.parent.location.origin + window.parent.location.pathname)
                : (window.location.origin + window.location.pathname);
            const curUrl = `${{hostUrl}}?siteCd=${{encodeURIComponent(currentSiteCd)}}&mlType=${{encodeURIComponent(currentMlType)}}&prdNo=${{encodeURIComponent(currentPrdNo)}}&k=${{encodeURIComponent(currentK)}}&age=${{encodeURIComponent(currentAge)}}&gender=${{encodeURIComponent(currentGender)}}&tab=${{encodeURIComponent(currentTab)}}`;
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

        function updateUrlQuery() {{
            try {{
                const queryStr = `?siteCd=${{encodeURIComponent(currentSiteCd)}}&mlType=${{encodeURIComponent(currentMlType)}}&prdNo=${{encodeURIComponent(currentPrdNo)}}&k=${{encodeURIComponent(currentK)}}&age=${{encodeURIComponent(currentAge)}}&gender=${{encodeURIComponent(currentGender)}}&tab=${{encodeURIComponent(currentTab)}}`;
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

        function initApp() {{
            // 사이트 셀렉트 설정
            const siteSelect = document.getElementById('siteCdSelect');
            if (siteSelect) siteSelect.value = currentSiteCd;

            // 추천 모델 셀렉트박스 채우기
            const mlSelect = document.getElementById('mlTypeSelect');
            if (mlSelect) {{
                mlSelect.innerHTML = ML_TYPES_LIST.map(m => `<option value="${{m.id}}">${{m.name}}</option>`).join('');
                mlSelect.value = currentMlType;
            }}

            // 필터 설정
            const directInput = document.getElementById('directPrdInput');
            if (directInput) directInput.value = currentPrdNo;

            const ageSelect = document.getElementById('ageSelect');
            if (ageSelect) ageSelect.value = currentAge;

            const genderSelect = document.getElementById('genderSelect');
            if (genderSelect) genderSelect.value = currentGender;

            const sizeInput = document.getElementById('sizeInput');
            if (sizeInput) sizeInput.value = currentK;

            // 시드 상품 목록 렌더링
            renderSeedList();

            // 탭 초기화
            switchViewTab(currentTab, false);

            // 이벤트 리스너 등록
            setupEventListeners();

            // 초기 데이터 조회
            executeRecommendFlow();
        }}

        function setupEventListeners() {{
            // 검색 필터링
            const searchInput = document.getElementById('seedSearchInput');
            if (searchInput) {{
                searchInput.addEventListener('input', (e) => {{
                    const q = e.target.value.trim().toLowerCase();
                    const allSeeds = SEED_DATA[currentSiteCd] || [];
                    const filtered = allSeeds.filter(s => 
                        (s.prd_nm && s.prd_nm.toLowerCase().includes(q)) ||
                        (s.full_name && s.full_name.toLowerCase().includes(q)) ||
                        (s.category && s.category.toLowerCase().includes(q)) ||
                        (s.prd_no && s.prd_no.includes(q))
                    );
                    renderSeedList(filtered);
                }});
            }}

            // 사이트 전환 이벤트
            const siteSelect = document.getElementById('siteCdSelect');
            if (siteSelect) {{
                siteSelect.addEventListener('change', (e) => {{
                    currentSiteCd = e.target.value;
                    const seeds = SEED_DATA[currentSiteCd] || [];
                    if (seeds.length > 0) {{
                        currentPrdNo = seeds[0].prd_no;
                        const directInput = document.getElementById('directPrdInput');
                        if (directInput) directInput.value = currentPrdNo;
                    }}
                    renderSeedList();
                    executeRecommendFlow();
                }});
            }}

            // 추천 모델 전환 이벤트
            const mlSelect = document.getElementById('mlTypeSelect');
            if (mlSelect) {{
                mlSelect.addEventListener('change', (e) => {{
                    currentMlType = e.target.value;
                    executeRecommendFlow();
                }});
            }}

            // 직접 입력 Enter 이벤트
            const directInput = document.getElementById('directPrdInput');
            if (directInput) {{
                directInput.addEventListener('keydown', (e) => {{
                    if (e.key === 'Enter') {{
                        triggerFetch();
                    }}
                }});
            }}
        }}

        function renderSeedList(seedsToRender = null) {{
            const list = seedsToRender || SEED_DATA[currentSiteCd] || [];
            displayedSeeds = list;
            const container = document.getElementById('seedList');
            const badge = document.getElementById('seedCountBadge');
            if (badge) badge.textContent = list.length;
            if (!container) return;

            container.innerHTML = '';
            list.forEach((item, idx) => {{
                const li = document.createElement('li');
                const isSelected = item.prd_no === currentPrdNo;
                li.className = `seed-item ${{isSelected ? 'active' : ''}}`;
                li.setAttribute('data-prd-no', item.prd_no);
                li.setAttribute('tabindex', '0');

                const name = item.prd_nm || item.category || '상품';
                const no = item.prd_no;

                li.innerHTML = `
                    <div style="display:flex; align-items:center; gap:8px; overflow:hidden;">
                        <span style="font-weight:700;">${{name}}</span>
                        <span style="font-size:0.75rem; color:#64748b;">#${{no}}</span>
                    </div>
                    <span style="font-size:0.72rem; color:#94a3b8;">${{item.category || ''}}</span>
                `;

                li.addEventListener('click', () => {{
                    selectSeedProduct(item.prd_no);
                }});

                li.addEventListener('keydown', (e) => {{
                    if (e.key === 'ArrowDown') {{
                        e.preventDefault();
                        if (idx + 1 < displayedSeeds.length) {{
                            const nextLi = container.children[idx + 1];
                            if (nextLi) {{
                                nextLi.focus();
                                selectSeedProduct(displayedSeeds[idx + 1].prd_no);
                            }}
                        }}
                    }} else if (e.key === 'ArrowUp') {{
                        e.preventDefault();
                        if (idx > 0) {{
                            const prevLi = container.children[idx - 1];
                            if (prevLi) {{
                                prevLi.focus();
                                selectSeedProduct(displayedSeeds[idx - 1].prd_no);
                            }}
                        }} else {{
                            document.getElementById('seedSearchInput')?.focus();
                        }}
                    }} else if (e.key === 'Enter' || e.key === ' ') {{
                        e.preventDefault();
                        selectSeedProduct(item.prd_no);
                    }}
                }});

                container.appendChild(li);
            }});
        }}

        function selectSeedProduct(prdNo) {{
            currentPrdNo = String(prdNo).trim();
            const directInput = document.getElementById('directPrdInput');
            if (directInput) directInput.value = currentPrdNo;

            document.querySelectorAll('.seed-item').forEach(el => {{
                if (el.getAttribute('data-prd-no') === currentPrdNo) {{
                    el.classList.add('active');
                    el.scrollIntoView({{ block: 'nearest', behavior: 'smooth' }});
                }} else {{
                    el.classList.remove('active');
                }}
            }});

            executeRecommendFlow();
        }}

        function triggerFetch() {{
            const directInput = document.getElementById('directPrdInput');
            if (directInput && directInput.value.trim()) {{
                currentPrdNo = directInput.value.trim();
            }}
            const siteSelect = document.getElementById('siteCdSelect');
            if (siteSelect) currentSiteCd = siteSelect.value;

            const mlSelect = document.getElementById('mlTypeSelect');
            if (mlSelect) currentMlType = mlSelect.value;

            const ageSelect = document.getElementById('ageSelect');
            if (ageSelect) currentAge = ageSelect.value;

            const genderSelect = document.getElementById('genderSelect');
            if (genderSelect) currentGender = genderSelect.value;

            const sizeInput = document.getElementById('sizeInput');
            if (sizeInput && sizeInput.value) currentK = sizeInput.value;

            executeRecommendFlow();
        }}

        function switchViewTab(tabName, updateUrl = true) {{
            currentTab = tabName;
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));

            if (tabName === 'grid') {{
                document.getElementById('tabBtnGrid')?.classList.add('active');
                document.getElementById('tabContentGrid')?.classList.add('active');
            }} else if (tabName === 'table') {{
                document.getElementById('tabBtnTable')?.classList.add('active');
                document.getElementById('tabContentTable')?.classList.add('active');
            }} else if (tabName === 'raw') {{
                document.getElementById('tabBtnRaw')?.classList.add('active');
                document.getElementById('tabContentRaw')?.classList.add('active');
            }}

            if (updateUrl) updateUrlQuery();
        }}

        async function executeRecommendFlow() {{
            updateUrlQuery();
            updateMetaHeaderInfo();

            // 1. 대상 상품 정보 비동기 로드
            loadTargetProductInfo(currentPrdNo);

            // 2. 추천 API 호출
            await fetchRecommendationApi();
        }}

        function updateMetaHeaderInfo() {{
            const siteName = currentSiteCd === '2' ? '보리보리' : '하프클럽';
            const metaSite = document.getElementById('metaSiteText');
            if (metaSite) metaSite.textContent = siteName;

            const mlObj = ML_TYPES_LIST.find(m => m.id === currentMlType);
            const mlName = mlObj ? mlObj.name : currentMlType;
            const metaMl = document.getElementById('metaMlTypeText');
            if (metaMl) metaMl.textContent = mlName;

            const navBadge = document.getElementById('navMlTypeBadge');
            if (navBadge) navBadge.textContent = mlName.split('(')[0].trim();

            const metaPrd = document.getElementById('metaPrdNoText');
            if (metaPrd) metaPrd.textContent = currentPrdNo;

            const ageTxt = currentAge === '01' ? '40대 미만' : (currentAge === '02' ? '40대 이상' : '전체');
            const genTxt = currentGender === '01' ? '남성' : (currentGender === '02' ? '여성' : '전체');
            const metaCond = document.getElementById('metaConditionText');
            if (metaCond) metaCond.textContent = `연령: ${{ageTxt}} / 성별: ${{genTxt}}`;

            const metaK = document.getElementById('metaKText');
            if (metaK) metaK.textContent = `${{currentK}}개`;

            const navTitle = document.getElementById('currentPrdText');
            if (navTitle) navTitle.textContent = `상품번호 ${{currentPrdNo}}`;

            const navLink = document.getElementById('currentPrdTitleLink');
            if (navLink) {{
                const firstPrd = currentPrdNo.split(',')[0].trim();
                navLink.href = getProductDetailUrl(firstPrd);
            }}
        }}

        async function loadTargetProductInfo(prdNoStr) {{
            const prdList = prdNoStr.split(',').map(s => s.trim()).filter(Boolean);
            const firstPrd = prdList[0] || '';

            // 다중 상품 칩 처리
            const multiWrap = document.getElementById('multiTargetChipsWrap');
            const multiContainer = document.getElementById('multiTargetChipsContainer');
            if (multiWrap && multiContainer) {{
                if (prdList.length > 1) {{
                    multiWrap.style.display = 'block';
                    multiContainer.innerHTML = prdList.map(p => `
                        <span class="badge-chip-item badge-blue" style="cursor:pointer;" onclick="selectSeedProduct('${{p}}')">
                            #${{p}} ↗
                        </span>
                    `).join('');
                }} else {{
                    multiWrap.style.display = 'none';
                    multiContainer.innerHTML = '';
                }}
            }}

            if (!firstPrd) return;

            // 검색 API를 통해 첫 번째 대상 상품의 상세 정보 가져오기
            const searchBase = currentSiteCd === '2' ? 'https://apix.boribori.co.kr' : 'https://hapix.halfclub.com';
            const searchUrl = `${{searchBase}}/searches/prdList/?keyword=${{encodeURIComponent(firstPrd)}}&siteCd=${{currentSiteCd}}&device=mc`;

            try {{
                const res = await fetch(searchUrl);
                if (!res.ok) throw new Error(`HTTP ${{res.status}}`);
                const data = await res.json();
                const hits = data?.data?.result?.hits?.hits || [];
                if (hits.length > 0) {{
                    const src = hits[0]._source || hits[0];
                    renderTargetProductCard(src);
                }} else {{
                    renderTargetProductCardFallback(firstPrd);
                }}
            }} catch (e) {{
                renderTargetProductCardFallback(firstPrd);
            }}
        }}

        function renderTargetProductCard(src) {{
            const name = src.prdNm || '상품명 미확인';
            const brand = src.brandNm || src.brdNm || '브랜드 미확인';
            const dcPrice = src.dcPrcMc || src.dcPrcApp || src.selPrc || src.price || 0;
            const normPrice = src.normPrc || 0;
            const imgPath = src.appPrdImgUrl || src.prdImg || '';
            const fullImg = getImageUrl(imgPath);

            const c1 = src.dpCtgrNm1 || '';
            const c2 = src.dpCtgrNm2 || '';
            const c3 = src.dpCtgrNm3 || '';
            const catPath = [c1, c2, c3].filter(Boolean).join(' > ');

            const imgWrap = document.getElementById('targetImgWrap');
            if (imgWrap) {{
                imgWrap.innerHTML = fullImg ? `<img src="${{fullImg}}" class="target-img" alt="${{name}}"/>` : '<span style="font-size:0.72rem; color:#94a3b8;">No Image</span>';
            }}

            const brandEl = document.getElementById('targetBrandText');
            if (brandEl) brandEl.textContent = brand;

            const nameEl = document.getElementById('targetNameText');
            if (nameEl) nameEl.textContent = name;

            const navTitle = document.getElementById('currentPrdText');
            if (navTitle) navTitle.textContent = `${{brand}} - ${{name}}`;

            const priceEl = document.getElementById('targetPriceText');
            if (priceEl) priceEl.textContent = `${{Number(dcPrice).toLocaleString()}} 원`;

            const normEl = document.getElementById('targetNormPriceText');
            if (normEl) normEl.textContent = normPrice > dcPrice ? `${{Number(normPrice).toLocaleString()}} 원` : '';

            const discEl = document.getElementById('targetDiscRateText');
            if (discEl) {{
                if (normPrice > dcPrice && normPrice > 0) {{
                    const rate = Math.round((normPrice - dcPrice) / normPrice * 100);
                    discEl.textContent = `${{rate}}%`;
                }} else {{
                    discEl.textContent = '';
                }}
            }}

            const catEl = document.getElementById('targetCategoryPath');
            if (catEl) catEl.textContent = catPath ? `카테고리: ${{catPath}}` : '';

            const tagsHeader = document.getElementById('targetTagsHeader');
            if (tagsHeader) {{
                tagsHeader.innerHTML = `
                    <span class="badge-chip-item badge-brand">브랜드: ${{brand}}</span>
                    ${{c1 ? `<span class="badge-chip-item badge-blue">${{c1}}</span>` : ''}}
                `;
            }}
        }}

        function renderTargetProductCardFallback(prdNo) {{
            const imgWrap = document.getElementById('targetImgWrap');
            if (imgWrap) {{
                imgWrap.innerHTML = `<span style="font-size:0.72rem; color:#94a3b8;">#${{prdNo}}</span>`;
            }}
            const brandEl = document.getElementById('targetBrandText');
            if (brandEl) brandEl.textContent = '상품 상세';

            const nameEl = document.getElementById('targetNameText');
            if (nameEl) nameEl.textContent = `상품번호 #${{prdNo}} (API 직접 조회)`;

            const priceEl = document.getElementById('targetPriceText');
            if (priceEl) priceEl.textContent = '-';

            const normEl = document.getElementById('targetNormPriceText');
            if (normEl) normEl.textContent = '';

            const discEl = document.getElementById('targetDiscRateText');
            if (discEl) discEl.textContent = '';

            const catEl = document.getElementById('targetCategoryPath');
            if (catEl) catEl.textContent = '';

            const tagsHeader = document.getElementById('targetTagsHeader');
            if (tagsHeader) tagsHeader.innerHTML = '';
        }}

        async function fetchRecommendationApi() {{
            const startTime = performance.now();
            const apiBase = getApiBaseUrl();
            const statusEl = document.getElementById('metaStatusText');
            if (statusEl) {{
                statusEl.textContent = '조회 중...';
                statusEl.style.color = '#2563eb';
            }}

            // 엔드포인트 및 파라미터 구성
            let endpoint = currentMlType;
            if ((currentMlType === 'viewtogether' || currentMlType === 'buytogether') && (currentAge || currentGender)) {{
                endpoint = currentMlType === 'viewtogether' ? 'viewuser' : 'buyuser';
            }}

            const params = new URLSearchParams();
            params.append('siteCd', currentSiteCd);
            params.append('size', currentK);

            const prdList = currentPrdNo.split(',').map(s => s.trim()).filter(Boolean);

            if (['recommendforyou', 'multiSimilarItem', 'meanSimilarItem', 'meanSimilarItemView', 'meanSimilarItemBuy'].includes(currentMlType)) {{
                prdList.forEach(p => params.append('prdNo', p));
            }} else {{
                params.append('prdNo', prdList[0] || '380118214');
            }}

            if (currentAge) params.append('age', currentAge);
            if (currentGender) params.append('gender', currentGender);
            if (currentMlType === 'similaritem' || currentMlType === 'multiSimilarItem') {{
                params.append('randomYn', 'false');
            }}

            currentApiUrl = `${{apiBase}}/recommend/${{endpoint}}?${{params.toString()}}`;

            const urlText = document.getElementById('calledApiUrlText');
            if (urlText) urlText.textContent = currentApiUrl;

            try {{
                const res = await fetch(currentApiUrl);
                const duration = Math.round(performance.now() - startTime);

                if (!res.ok) {{
                    throw new Error(`HTTP ${{res.status}}: ${{res.statusText}}`);
                }}

                const data = await res.json();
                currentRawData = data;

                if (statusEl) {{
                    statusEl.textContent = `200 OK (${{duration}}ms)`;
                    statusEl.style.color = '#059669';
                }}

                renderDashboardResults(data);
            }} catch (err) {{
                const duration = Math.round(performance.now() - startTime);
                if (statusEl) {{
                    statusEl.textContent = `실패 (${{duration}}ms)`;
                    statusEl.style.color = '#ef4444';
                }}

                document.getElementById('productGridContainer').innerHTML = `
                    <div style="grid-column:1/-1; padding:40px 20px; text-align:center; color:#ef4444; font-weight:700;">
                        <div>API 호출에 실패하였습니다: ${{escapeHtml(err.message)}}</div>
                        <div style="font-size:0.8rem; color:#94a3b8; margin-top:6px; word-break:break-all;">요청 URL: ${{currentApiUrl}}</div>
                    </div>
                `;

                document.getElementById('productTableBody').innerHTML = `
                    <tr><td colspan="10" style="text-align:center; padding:30px; color:#ef4444;">API 호출 실패: ${{escapeHtml(err.message)}}</td></tr>
                `;

                renderRawJsonView({{ error: err.message, requested_url: currentApiUrl }});
            }}
        }}

        function renderDashboardResults(data) {{
            let products = [];
            if (Array.isArray(data)) {{
                products = data;
            }} else if (data && typeof data === 'object') {{
                products = data.result || data.data || data.items || data.results || [];
                if (!Array.isArray(products) && typeof products === 'object') {{
                    products = [products];
                }}
            }}

            renderProductGrid(products);
            renderProductTable(products);
            renderRawJsonView(data);
        }}

        function renderProductGrid(products) {{
            const container = document.getElementById('productGridContainer');
            if (!container) return;

            if (!products || products.length === 0) {{
                container.innerHTML = '<div style="grid-column:1/-1; padding:40px 20px; text-align:center; color:#64748b;">추천 상품 결과가 없습니다.</div>';
                return;
            }}

            container.innerHTML = products.map((prd, idx) => {{
                const rank = idx + 1;
                const prdNo = prd.prdNo || prd.prd_no || prd.id || '';
                const prdUrl = getProductDetailUrl(prdNo);
                const name = prd.prdNm || prd.prd_nm || prd.name || '상품명 미확인';
                const brand = prd.brandNm || prd.brand_nm || prd.brdNm || '브랜드';
                const salePrc = prd.dcPrcMc || prd.dcPrcApp || prd.selPrc || prd.salePrc || prd.price || 0;
                const normPrc = prd.normPrc || prd.nrmPrc || 0;
                const discRt = prd.totRateApp || prd.discRt || (normPrc > salePrc && normPrc > 0 ? Math.round((normPrc - salePrc) / normPrc * 100) : 0);
                const score = prd.score !== undefined ? Number(prd.score) : null;
                const esScore = prd.esscore !== undefined ? Number(prd.esscore) : null;
                const imgPath = prd.appPrdImgUrl || prd.prd_img || prd.prdImg || '';
                const imgUrl = getImageUrl(imgPath);

                const c1 = prd.dpCtgrNm1 || prd.category || '';

                const rankClass = rank === 1 ? 'rank-badge rank-top1' : (rank === 2 ? 'rank-badge rank-top2' : (rank === 3 ? 'rank-badge rank-top3' : 'rank-badge'));
                const rankText = rank <= 3 ? `TOP ${{rank}}` : `#${{rank}}`;

                return `
                    <div class="product-card">
                        <div class="product-img-wrap">
                            <span class="${{rankClass}}">${{rankText}}</span>
                            <a href="${{prdUrl}}" target="_blank" rel="noopener noreferrer" style="display:block; width:100%; height:100%;">
                                <img src="${{imgUrl || 'data:image/svg+xml,%3Csvg xmlns=\\'http://www.w3.org/2000/svg\\' width=\\'100\\' height=\\'100\\'%3E%3Crect width=\\'100\\' height=\\'100\\' fill=\\'%23f1f5f9\\'/ %3E%3C/svg%3E'}}" class="product-img" alt="${{escapeHtml(name)}}" loading="lazy"/>
                            </a>
                        </div>
                        <div class="product-info">
                            <div class="brand-name" title="${{escapeHtml(brand)}}">${{brand}}</div>
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
                                ${{score !== null ? `<span class="badge-chip-item badge-blue" title="추천 스코어">추천: ${{score.toFixed(3)}}</span>` : ''}}
                                ${{esScore !== null ? `<span class="badge-chip-item badge-amber" title="ES 스코어">ES: ${{esScore.toFixed(2)}}</span>` : ''}}
                                ${{c1 ? `<span class="badge-chip-item badge-gray">${{c1}}</span>` : ''}}
                            </div>
                        </div>
                    </div>
                `;
            }}).join('');
        }}

        function renderProductTable(products) {{
            const tbody = document.getElementById('productTableBody');
            if (!tbody) return;

            if (!products || products.length === 0) {{
                tbody.innerHTML = '<tr><td colspan="10" style="text-align:center; padding:30px; color:#64748b;">추천 상품 데이터가 없습니다.</td></tr>';
                return;
            }}

            tbody.innerHTML = products.map((prd, idx) => {{
                const rank = idx + 1;
                const prdNo = prd.prdNo || prd.prd_no || prd.id || '-';
                const prdUrl = getProductDetailUrl(prdNo);
                const name = prd.prdNm || prd.prd_nm || prd.name || '-';
                const brand = prd.brandNm || prd.brand_nm || prd.brdNm || '-';
                const salePrc = prd.dcPrcMc || prd.dcPrcApp || prd.selPrc || prd.salePrc || prd.price || 0;
                const normPrc = prd.normPrc || prd.nrmPrc || 0;
                const discRt = prd.totRateApp || prd.discRt || (normPrc > salePrc && normPrc > 0 ? Math.round((normPrc - salePrc) / normPrc * 100) : 0);
                const score = prd.score !== undefined ? Number(prd.score).toFixed(4) : '-';
                const esScore = prd.esscore !== undefined ? Number(prd.esscore).toFixed(4) : '-';
                const c1 = prd.dpCtgrNm1 || prd.category || '-';

                return `
                    <tr>
                        <td style="font-weight:700; color:#64748b;">${{rank}}</td>
                        <td><a href="${{prdUrl}}" target="_blank" rel="noopener noreferrer" style="color:#2563eb; font-weight:700; text-decoration:none;">${{prdNo}} ↗</a></td>
                        <td style="font-weight:600;">${{brand}}</td>
                        <td style="max-width:280px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;" title="${{escapeHtml(name)}}">${{name}}</td>
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
            container.appendChild(createJsonTree(data, true));
        }}

        function createJsonTree(value, isRoot = false) {{
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
            wrap.className = 'json-node-collapsible';

            if (keys.length === 0) {{
                wrap.innerHTML = `<span class="json-bracket">${{openBracket}}${{closeBracket}}</span>`;
                return wrap;
            }}

            const headerRow = document.createElement('span');
            headerRow.className = 'json-node-row';

            const toggle = document.createElement('span');
            toggle.className = 'json-toggle';
            toggle.textContent = '▼';
            headerRow.appendChild(toggle);

            const openSpan = document.createElement('span');
            openSpan.className = 'json-bracket';
            openSpan.textContent = openBracket;
            headerRow.appendChild(openSpan);

            const collapsedSummary = document.createElement('span');
            collapsedSummary.className = 'json-collapsed-text';
            collapsedSummary.style.display = 'none';
            collapsedSummary.textContent = isArray ? `... ${{keys.length}} items ...` : `... ${{keys.length}} keys ...`;
            headerRow.appendChild(collapsedSummary);

            const childrenContainer = document.createElement('div');
            childrenContainer.className = 'json-children';

            keys.forEach((key, idx) => {{
                const row = document.createElement('div');
                row.className = 'json-node-row';

                if (!isArray) {{
                    const kSpan = document.createElement('span');
                    kSpan.className = 'json-key';
                    kSpan.textContent = `"${{key}}"`;
                    row.appendChild(kSpan);

                    const colon = document.createElement('span');
                    colon.className = 'json-colon';
                    colon.textContent = ': ';
                    row.appendChild(colon);
                }}

                row.appendChild(createJsonTree(value[key]));

                if (idx < keys.length - 1) {{
                    const comma = document.createElement('span');
                    comma.className = 'json-comma';
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
                footerRow.style.display = isHidden ? 'block' : 'none';
                collapsedSummary.style.display = isHidden ? 'none' : 'inline';
                toggle.textContent = isHidden ? '▼' : '▶';
            }}

            toggle.addEventListener('click', toggleNode);
            collapsedSummary.addEventListener('click', toggleNode);

            wrap.appendChild(headerRow);
            wrap.appendChild(childrenContainer);
            wrap.appendChild(footerRow);

            return wrap;
        }}

        function expandAllJson(containerId) {{
            const el = document.getElementById(containerId);
            if (!el) return;
            el.querySelectorAll('.json-children').forEach(c => c.style.display = 'block');
            el.querySelectorAll('.json-node-row').forEach(r => r.style.display = 'block');
            el.querySelectorAll('.json-collapsed-text').forEach(t => t.style.display = 'none');
            el.querySelectorAll('.json-toggle').forEach(tg => tg.textContent = '▼');
        }}

        function collapseAllJson(containerId) {{
            const el = document.getElementById(containerId);
            if (!el) return;
            el.querySelectorAll('.json-children').forEach(c => c.style.display = 'none');
            el.querySelectorAll('.json-collapsed-text').forEach(t => t.style.display = 'inline');
            el.querySelectorAll('.json-toggle').forEach(tg => tg.textContent = '▶');
        }}

        function openApiUrlInNewTab() {{
            if (currentApiUrl) {{
                window.open(currentApiUrl, '_blank', 'noopener,noreferrer');
            }}
        }}

        function copyApiUrlToClipboard() {{
            if (!currentApiUrl) return;
            navigator.clipboard.writeText(currentApiUrl).then(() => {{
                alert('API URL이 클립보드에 복사되었습니다.');
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
                alert('JSON 내용 복사에 실패했습니다.');
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

# 7. Streamlit 컴포넌트 렌더링 (사방 여백 완전 제거 및 풀스크린 뷰포트)
components.html(html_content, height=1000, scrolling=False)
