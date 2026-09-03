import os
import json
import urllib.parse
import streamlit as st
import streamlit.components.v1 as components

# 1. 페이지 기본 설정 (전체 화면 모드)
st.set_page_config(
    page_title="Halfclub Trend AI Curation Dashboard",
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

# 3. 타겟 키워드 리스트 로드 (keywords.json 연동)
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

# 4. URL 쿼리 파라미터 디코딩 및 초기 키워드/탭 판별
qp = st.query_params
raw_kw = qp.get("keyword", "")
if raw_kw:
    raw_kw = urllib.parse.unquote(str(raw_kw)).strip()

if raw_kw and raw_kw in keywords_list:
    initial_kw = raw_kw
else:
    initial_kw = keywords_list[0] if keywords_list else "가디건"

initial_tab = qp.get("tab", "grid")
if initial_tab not in ["grid", "table", "raw", "prompt"]:
    initial_tab = "grid"

initial_keyword_json = json.dumps(initial_kw, ensure_ascii=False)
initial_tab_json = json.dumps(initial_tab, ensure_ascii=False)

# 5. 0.1초 고속 비동기 SPA 자원 HTML/CSS/JS 템플릿
html_content = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Halfclub Trend AI Curation Dashboard</title>
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
        .keyword-list {{
            list-style: none;
            overflow-y: auto;
            flex: 1;
            padding: 8px 0;
        }}
        .keyword-item {{
            padding: 9px 14px;
            margin: 2px 10px;
            font-size: 0.88rem;
            color: #334155;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: space-between;
            border-radius: 8px;
            transition: all 0.15s ease;
        }}
        .keyword-item:hover {{
            background-color: #f1f5f9;
            color: #0f172a;
        }}
        .keyword-item:focus {{
            outline: 2px solid #2563eb;
            outline-offset: -2px;
            background-color: #eff6ff;
            color: #1d4ed8;
        }}
        .keyword-item.active {{
            background-color: #eff6ff;
            color: #2563eb;
            font-weight: 800;
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
            padding: 14px 28px;
            border-bottom: 1px solid #e2e8f0;
            display: flex;
            align-items: center;
            justify-content: space-between;
            background-color: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(8px);
            position: sticky;
            top: 0;
            z-index: 20;
        }}
        .navbar-title {{
            font-size: 1.35rem;
            font-weight: 800;
            color: #0f172a;
            transition: color 0.15s ease;
        }}
        .navbar-title:hover, .navbar-title:hover span {{
            color: #2563eb !important;
        }}
        .dashboard-body {{
            padding: 22px 28px;
            flex: 1;
        }}
        
        /* 헤더 메타 뱃지 */
        .meta-badges {{
            display: flex;
            align-items: center;
            gap: 12px;
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 10px;
            padding: 9px 16px;
            margin-bottom: 20px;
            font-size: 0.82rem;
            color: #64748b;
            font-weight: 600;
            box-shadow: 0 1px 3px rgba(0,0,0,0.02);
            flex-wrap: wrap;
        }}
        
        /* 트렌드 가이드 박스 */
        .guide-card-box {{
            background-color: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            padding: 22px 26px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.03);
            margin-bottom: 22px;
            box-sizing: border-box;
            width: 100%;
        }}
        .guide-card-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 14px;
        }}
        .guide-title {{
            font-size: 1.08rem;
            font-weight: 800;
            color: #0f172a;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .guide-text {{
            font-size: 1.02rem;
            line-height: 1.8;
            color: #1e293b;
            letter-spacing: -0.01em;
            margin-bottom: 16px;
        }}
        .guide-text b,
        .guide-text strong,
        #guideTextBody b,
        #guideTextBody strong,
        .highlight-kw {{
            color: #1d4ed8;
            font-weight: 800;
            background: #eff6ff;
            padding: 1px 6px;
            border-radius: 4px;
            border-bottom: 2px solid #93c5fd;
            display: inline;
        }}
        
        /* 탭 서식 */
        .tab-navigation {{
            display: flex;
            gap: 6px;
            border-bottom: 2px solid #e2e8f0;
            margin-bottom: 22px;
        }}
        .tab-btn {{
            padding: 10px 18px;
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
            background: #f1f5f9;
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

        #tabContentPrompt.tab-content.active {{
            display: flex !important;
            flex-direction: column;
            gap: 20px;
        }}
        
        /* 5열 그리드 카드 배치 */
        .grid-container {{
            display: grid;
            grid-template-columns: repeat(5, 1fr);
            gap: 16px;
        }}
        .product-card {{
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            overflow: hidden;
            background: #ffffff;
            box-shadow: 0 1px 3px rgba(0,0,0,0.03);
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            transition: all 0.22s cubic-bezier(0.16, 1, 0.3, 1);
        }}
        .product-card:hover {{
            transform: translateY(-4px);
            box-shadow: 0 12px 24px -8px rgba(15, 23, 42, 0.12), 0 0 0 1px #3b82f6;
        }}
        .product-img-wrap {{
            position: relative;
            width: 100%;
            aspect-ratio: 1 / 1.15;
            background-color: #f8fafc;
            overflow: hidden;
        }}
        .product-img {{
            width: 100%;
            height: 100%;
            object-fit: cover;
            object-position: top center;
            transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1);
        }}
        .product-card:hover .product-img {{
            transform: scale(1.06);
        }}
        .rank-badge {{
            position: absolute;
            top: 8px;
            left: 8px;
            background: rgba(15, 23, 42, 0.8);
            backdrop-filter: blur(4px);
            color: #ffffff;
            font-size: 11px;
            font-weight: 800;
            padding: 3px 8px;
            border-radius: 6px;
            letter-spacing: 0.5px;
        }}
        .rank-top1 {{
            background: linear-gradient(135deg, #f59e0b, #d97706) !important;
            color: #ffffff !important;
            box-shadow: 0 2px 8px rgba(245, 158, 11, 0.4);
        }}
        .rank-top2, .rank-top3 {{
            background: linear-gradient(135deg, #334155, #1e293b) !important;
            color: #ffffff !important;
        }}
        .product-info {{
            padding: 14px 14px 8px 14px;
        }}
        .brand-name {{
            font-size: 0.78rem;
            color: #64748b;
            font-weight: 700;
            margin-bottom: 4px;
            text-transform: uppercase;
            letter-spacing: 0.2px;
        }}
        .product-name {{
            font-size: 0.88rem;
            font-weight: 600;
            color: #0f172a;
            height: 40px;
            overflow: hidden;
            text-overflow: ellipsis;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            line-height: 1.42;
            margin-bottom: 10px;
        }}
        .price-wrap {{
            display: flex;
            align-items: baseline;
            gap: 6px;
            margin-bottom: 6px;
        }}
        .discount-rate {{
            font-size: 1.05rem;
            color: #f43f5e;
            font-weight: 800;
        }}
        .sale-price {{
            font-size: 1.05rem;
            font-weight: 800;
            color: #0f172a;
        }}
        .normal-price {{
            font-size: 0.78rem;
            color: #94a3b8;
            text-decoration: line-through;
        }}
        .badge-chip-container {{
            display: flex;
            flex-wrap: wrap;
            gap: 4px;
            margin-top: 6px;
        }}
        .badge-chip-item {{
            font-size: 11px;
            padding: 2px 7px;
            border-radius: 5px;
            font-weight: 600;
            display: inline-flex;
            align-items: center;
            gap: 3px;
        }}
        .badge-blue {{ background: #eff6ff; color: #2563eb; border: 1px solid #dbeafe; }}
        .badge-red {{ background: #fef2f2; color: #dc2626; border: 1px solid #fee2e2; }}
        .badge-gray {{ background: #f1f5f9; color: #475569; border: 1px solid #e2e8f0; }}
        .badge-brand {{ background: #ecfdf5; color: #059669; border: 1px solid #a7f3d0; }}
        .badge-media {{ background: #e0f2fe; color: #0369a1; font-weight: 700; border: 1px solid #bae6fd; }}
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
            padding: 12px 14px;
            border-bottom: 1px solid #e2e8f0;
            text-align: left;
        }}
        .data-table td {{
            padding: 12px 14px;
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

        /* JSON 트리 접기/펼치기 전용 스타일 */
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
            padding: 3px 8px;
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
        <!-- 좌측 키워드 사이드바 -->
        <aside class="sidebar">
            <div class="sidebar-header" onclick="goToDefaultPage()" title="기본 페이지로 이동 (새로고침)">
                <div class="sidebar-title">
                    <span>타겟 키워드 목록</span>
                    <span style="font-size:0.75rem; background:#eff6ff; color:#2563eb; padding:2px 8px; border-radius:10px;" id="keywordCountBadge">0</span>
                </div>
            </div>
            <div class="search-box">
                <input type="text" id="keywordSearchInput" class="search-input" placeholder="키워드 검색..."/>
            </div>
            <ul class="keyword-list" id="keywordList"></ul>
        </aside>

        <!-- 우측 메인 대시보드 -->
        <main class="main-content">
            <header class="top-navbar" style="padding-bottom:14px;">
                <div style="display:flex; align-items:center; gap:10px;">
                    <a id="currentKeywordTitleLink" href="{HALFCLUB_WEB_URL}/search/%EA%B0%80%EB%94%94%EA%B1%B4" target="_blank" rel="noopener noreferrer" style="text-decoration:none; color:inherit;" title="하프클럽에서 검색 (새 탭 이동)">
                        <h1 class="navbar-title" id="currentKeywordTitle" style="font-size:1.4rem; font-weight:800; color:#0f172a; margin:0; cursor:pointer; display:flex; align-items:center; gap:6px;">
                            <span id="currentKeywordText">가디건</span>
                            <span style="font-size:0.95rem; color:#64748b; font-weight:normal;">↗</span>
                        </h1>
                    </a>
                    <span style="background:#eff6ff; border:1px solid #dbeafe; color:#1d4ed8; font-size:12px; font-weight:700; padding:3px 12px; border-radius:9999px;">키워드 트렌드 추천</span>
                    <button id="btnCopyUrl" onclick="copyCurrentUrl()" style="background:#f1f5f9; border:1px solid #cbd5e1; color:#475569; font-size:11px; font-weight:700; padding:4px 9px; border-radius:6px; cursor:pointer;" title="현재 키워드 URL 링크 복사">URL 복사</button>
                </div>
                <div style="display:flex; align-items:center; gap:12px; font-size:0.85rem; font-weight:700; color:#334155;">
                    <div style="display:flex; align-items:center; gap:6px;">
                        <span>사이트:</span>
                        <select id="siteCdSelect" style="padding:6px 12px; border-radius:6px; border:1px solid #cbd5e1; background:#ffffff; font-size:0.85rem; font-weight:700; color:#0f172a; outline:none;">
                            <option value="1" selected>1 (하프클럽)</option>
                            <option value="2">2 (보리보리)</option>
                        </select>
                    </div>
                    <div style="display:flex; align-items:center; gap:6px;">
                        <span>조회 수:</span>
                        <input type="number" id="sizeInput" value="50" min="1" max="200" style="width:60px; padding:5px 8px; border-radius:6px; border:1px solid #cbd5e1; background:#ffffff; font-size:0.85rem; font-weight:700; color:#0f172a; text-align:center; outline:none;"/>
                    </div>
                    <button id="btnFetch" style="background:#0b1329; color:#ffffff; border:none; padding:8px 18px; border-radius:6px; font-weight:800; font-size:0.85rem; cursor:pointer; transition:background 0.15s ease;">API 연동 조회</button>
                </div>
            </header>

            <div class="dashboard-body">
                <!-- 메타 메타데이터 뱃지 바 -->
                <div class="meta-badges" id="metaBadgesBar" style="display:flex; align-items:center; gap:10px; margin-bottom:14px; padding:7px 16px;">
                    <div style="display:flex; align-items:center; gap:6px; background:#f8fafc; border:1px solid #e2e8f0; padding:3px 10px; border-radius:6px;">
                        <span style="color:#64748b; font-size:0.75rem;">모델</span>
                        <span style="color:#2563eb; font-weight:800; font-size:0.82rem;" id="llmModelText">-</span>
                    </div>
                    <div style="display:flex; align-items:center; gap:6px; background:#f8fafc; border:1px solid #e2e8f0; padding:3px 10px; border-radius:6px;">
                        <span style="color:#64748b; font-size:0.75rem;">토큰</span>
                        <span style="color:#db2777; font-weight:800; font-size:0.82rem;" id="tokenUsageText">In: 0 / Out: 0 / Cached: 0 (Total: 0)</span>
                    </div>
                    <div style="display:flex; align-items:center; gap:6px; background:#f8fafc; border:1px solid #e2e8f0; padding:3px 10px; border-radius:6px;">
                        <span style="color:#64748b; font-size:0.75rem;">생성일시</span>
                        <span style="color:#334155; font-weight:700; font-size:0.82rem;" id="createDtText">-</span>
                    </div>
                    <div style="display:flex; align-items:center; gap:6px; background:#f8fafc; border:1px solid #e2e8f0; padding:3px 10px; border-radius:6px;">
                        <span style="color:#64748b; font-size:0.75rem;">갱신일시</span>
                        <span style="color:#334155; font-weight:700; font-size:0.82rem;" id="updateDtText">-</span>
                    </div>
                    <!-- 필터링 상태 (오른쪽 끝 정렬) -->
                    <div style="display:flex; align-items:center; gap:6px; background:#f8fafc; border:1px solid #e2e8f0; padding:3px 10px; border-radius:6px; margin-left:auto;">
                        <span style="color:#64748b; font-size:0.75rem; font-weight:700;">필터링</span>
                        <span id="filterBadgesText" style="display:flex; gap:4px;">
                            <span style="background:#ffffff; border:1px solid #cbd5e1; color:#334155; font-weight:700; padding:1px 6px; border-radius:4px; font-size:0.75rem;">카테고리: ON</span>
                            <span style="background:#ffffff; border:1px solid #cbd5e1; color:#334155; font-weight:700; padding:1px 6px; border-radius:4px; font-size:0.75rem;">성별: ON</span>
                        </span>
                    </div>
                </div>

                <!-- AI 트렌드 큐레이션 가이드 카드 -->
                <div class="guide-card-box" id="guideCard">
                    <div class="guide-card-header">
                        <div class="guide-title">AI 트렌드 큐레이션 가이드</div>
                        <div style="display:flex; gap:6px;" id="extractedTagsHeader"></div>
                    </div>

                    <!-- AI 큐레이션 요약 (curation_summary) -->
                    <div id="curationSummaryWrap" style="display:none; background:#f8fafc; border:1px solid #e2e8f0; border-left:3px solid #2563eb; border-radius:6px; padding:8px 12px; margin-bottom:12px; align-items:center; gap:8px;">
                        <span style="font-size:0.75rem; font-weight:800; background:#eff6ff; color:#2563eb; padding:2px 7px; border-radius:4px; flex-shrink:0;">요약</span>
                        <span id="curationSummaryText" style="font-size:0.88rem; font-weight:700; color:#0f172a; line-height:1.5;"></span>
                    </div>

                    <div class="guide-text" id="guideTextBody">데이터를 불러오는 중입니다...</div>
                    <div style="font-size:0.8rem; font-weight:600; color:#64748b; margin-top:8px;" id="extractedBrandsWrap"></div>
                    <div style="font-size:0.8rem; font-weight:600; color:#64748b; margin-top:4px;" id="extractedKeywordsWrap"></div>
                    <div style="font-size:0.8rem; font-weight:600; color:#64748b; margin-top:4px;" id="extractedSearchKeywordsWrap"></div>
                    
                    <!-- 참고 뉴스 기사 (기본 펼침, 클릭 시 접기 토글) -->
                    <div style="margin-top:12px; padding-top:10px; border-top:1px solid #f1f5f9;" id="articlesWrapper">
                        <div style="display:flex; align-items:center; justify-content:space-between; cursor:pointer; user-select:none; padding:4px 0;" onclick="toggleArticlesAccordion()" title="참고 뉴스 목록 접기/펼치기">
                            <div style="font-size:0.8rem; font-weight:700; color:#475569; display:flex; align-items:center; gap:6px;">
                                <span>참고 뉴스 기사</span>
                                <span id="articlesCountBadge" style="font-size:0.72rem; background:#f1f5f9; color:#64748b; padding:1px 6px; border-radius:4px;">0건</span>
                            </div>
                            <span id="articlesToggleIcon" style="font-size:0.75rem; color:#2563eb; font-weight:700;">목록 접기 ▲</span>
                        </div>
                        <div id="articlesListContainer" style="display:block; margin-top:8px;"></div>
                    </div>
                </div>

                <!-- 뷰 탭 네비게이션 -->
                <nav class="tab-navigation">
                    <button class="tab-btn active" id="tabBtnGrid" onclick="switchViewTab('grid')">추천 상품</button>
                    <button class="tab-btn" id="tabBtnTable" onclick="switchViewTab('table')">추천 상품 데이터 확인</button>
                    <button class="tab-btn" id="tabBtnRaw" onclick="switchViewTab('raw')">API JSON 데이터 확인</button>
                    <button class="tab-btn" id="tabBtnPrompt" onclick="switchViewTab('prompt')">LLM 프롬프트</button>
                </nav>

                <!-- 탭 1: 5열 그리드 배치 -->
                <section class="tab-content active" id="tabContentGrid">
                    <div class="grid-container" id="productGridContainer"></div>
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
                                <th>매칭 키워드</th>
                                <th>평점(리뷰)</th>
                                <th>카테고리</th>
                            </tr>
                        </thead>
                        <tbody id="productTableBody"></tbody>
                    </table>
                </section>

                <!-- 탭 3: Raw JSON 데이터 배치 -->
                <section class="tab-content" id="tabContentRaw">
                    <div id="rawJsonContainer"></div>
                </section>

                <!-- 탭 4: LLM 프롬프트 & 산출 상세 인스펙터 -->
                <section class="tab-content" id="tabContentPrompt">
                    <div style="display:flex; flex-direction:column; gap:16px;">
                        <h3 style="font-size:1.05rem; font-weight:800; color:#0f172a; margin-bottom:4px; display:flex; align-items:center; gap:8px;">
                            <span>STAGE 1 : 스타일 트렌드 가이드 작성 프롬프트 & LLM 산출</span>
                        </h3>

                        <!-- 1단계 시스템 프롬프트 카드 -->
                        <div id="cardSysStage1" style="background:#0f172a; border-radius:8px; border:1px solid #1e293b; box-shadow:0 1px 3px rgba(0,0,0,0.2); overflow:hidden;">
                            <div style="display:flex; align-items:center; justify-content:space-between; padding:10px 16px; background:#1e293b; border-bottom:1px solid #334155;">
                                <div style="display:flex; align-items:center; gap:10px;">
                                    <span style="background:#059669; color:#ffffff; font-size:11px; font-weight:800; padding:2px 7px; border-radius:4px; letter-spacing:0.5px;">system_prompt</span>
                                    <span style="font-size:0.83rem; font-weight:700; color:#94a3b8;">LLM 키워드 트렌드 가이드 생성 프롬프트</span>
                                </div>
                                <div style="display:flex; align-items:center; gap:6px;">
                                    <button class="json-ctrl-btn" onclick="expandAllJson('promptSysStage1')">전체 펼치기</button>
                                    <button class="json-ctrl-btn" onclick="collapseAllJson('promptSysStage1')">전체 접기</button>
                                    <button id="btnCopySys1" onclick="copyPromptTextToClipboard('promptSysStage1', 'btnCopySys1')" class="json-ctrl-btn">내용 복사</button>
                                </div>
                            </div>
                            <div style="padding:14px 16px; background:#0f172a; max-height:360px; overflow:auto;">
                                <div id="promptSysStage1" class="json-tree-container"></div>
                            </div>
                        </div>

                        <!-- 1단계 입력 User Prompt 카드 -->
                        <div id="cardUserStage1" style="display:none; background:#0f172a; border-radius:8px; border:1px solid #1e293b; box-shadow:0 1px 3px rgba(0,0,0,0.2); overflow:hidden;">
                            <div style="display:flex; align-items:center; justify-content:space-between; padding:10px 16px; background:#1e293b; border-bottom:1px solid #334155;">
                                <div style="display:flex; align-items:center; gap:10px;">
                                    <span style="background:#059669; color:#ffffff; font-size:11px; font-weight:800; padding:2px 7px; border-radius:4px; letter-spacing:0.5px;">user_prompt</span>
                                    <span style="font-size:0.83rem; font-weight:700; color:#94a3b8;">LLM 키워드 트렌드 가이드 생성 프롬프트 (실 데이터)</span>
                                </div>
                                <div style="display:flex; align-items:center; gap:6px;">
                                    <button class="json-ctrl-btn" onclick="expandAllJson('promptUserStage1')">전체 펼치기</button>
                                    <button class="json-ctrl-btn" onclick="collapseAllJson('promptUserStage1')">전체 접기</button>
                                    <button id="btnCopyUser1" onclick="copyPromptTextToClipboard('promptUserStage1', 'btnCopyUser1')" class="json-ctrl-btn">내용 복사</button>
                                </div>
                            </div>
                            <div style="padding:14px 16px; background:#0f172a; max-height:360px; overflow:auto;">
                                <div id="promptUserStage1" class="json-tree-container"></div>
                            </div>
                        </div>

                        <!-- 1단계 LLM 결과 JSON 카드 -->
                        <div id="cardResultStage1" style="display:none; background:#0f172a; border-radius:8px; border:1px solid #1e293b; box-shadow:0 1px 3px rgba(0,0,0,0.2); overflow:hidden;">
                            <div style="display:flex; align-items:center; justify-content:space-between; padding:10px 16px; background:#1e293b; border-bottom:1px solid #334155;">
                                <div style="display:flex; align-items:center; gap:10px;">
                                    <span style="background:#8b5cf6; color:#ffffff; font-size:11px; font-weight:800; padding:2px 7px; border-radius:4px; letter-spacing:0.5px;">response</span>
                                    <span style="font-size:0.83rem; font-weight:700; color:#94a3b8;">LLM 응답 (JSON 트리 접기/펼치기 가능)</span>
                                </div>
                                <div style="display:flex; align-items:center; gap:6px;">
                                    <button class="json-ctrl-btn" onclick="expandAllJson('promptResultStage1')">전체 펼치기</button>
                                    <button class="json-ctrl-btn" onclick="collapseAllJson('promptResultStage1')">전체 접기</button>
                                    <button id="btnCopyResult1" onclick="copyPromptTextToClipboard('promptResultStage1', 'btnCopyResult1')" class="json-ctrl-btn">내용 복사</button>
                                </div>
                            </div>
                            <div style="padding:14px 16px; background:#0f172a; max-height:360px; overflow:auto;">
                                <div id="promptResultStage1" class="json-tree-container"></div>
                            </div>
                        </div>
                    </div>

                    <div style="display:flex; flex-direction:column; gap:16px; margin-top:10px;">
                        <h3 style="font-size:1.05rem; font-weight:800; color:#0f172a; margin-bottom:4px; display:flex; align-items:center; gap:8px;">
                            <span>STAGE 2 : 상품 큐레이션 및 정렬 프롬프트 & LLM 산출</span>
                        </h3>

                        <!-- 2단계 시스템 프롬프트 카드 -->
                        <div id="cardSysStage2" style="background:#0f172a; border-radius:8px; border:1px solid #1e293b; box-shadow:0 1px 3px rgba(0,0,0,0.2); overflow:hidden;">
                            <div style="display:flex; align-items:center; justify-content:space-between; padding:10px 16px; background:#1e293b; border-bottom:1px solid #334155;">
                                <div style="display:flex; align-items:center; gap:10px;">
                                    <span style="background:#059669; color:#ffffff; font-size:11px; font-weight:800; padding:2px 7px; border-radius:4px; letter-spacing:0.5px;">system_prompt</span>
                                    <span style="font-size:0.83rem; font-weight:700; color:#94a3b8;">LLM 키워드 트렌드 상품 선택 프롬프트</span>
                                </div>
                                <div style="display:flex; align-items:center; gap:6px;">
                                    <button class="json-ctrl-btn" onclick="expandAllJson('promptSysStage2')">전체 펼치기</button>
                                    <button class="json-ctrl-btn" onclick="collapseAllJson('promptSysStage2')">전체 접기</button>
                                    <button id="btnCopySys2" onclick="copyPromptTextToClipboard('promptSysStage2', 'btnCopySys2')" class="json-ctrl-btn">내용 복사</button>
                                </div>
                            </div>
                            <div style="padding:14px 16px; background:#0f172a; max-height:360px; overflow:auto;">
                                <div id="promptSysStage2" class="json-tree-container"></div>
                            </div>
                        </div>

                        <!-- 2단계 입력 User Prompt 카드 -->
                        <div id="cardUserStage2" style="display:none; background:#0f172a; border-radius:8px; border:1px solid #1e293b; box-shadow:0 1px 3px rgba(0,0,0,0.2); overflow:hidden;">
                            <div style="display:flex; align-items:center; justify-content:space-between; padding:10px 16px; background:#1e293b; border-bottom:1px solid #334155;">
                                <div style="display:flex; align-items:center; gap:10px;">
                                    <span style="background:#059669; color:#ffffff; font-size:11px; font-weight:800; padding:2px 7px; border-radius:4px; letter-spacing:0.5px;">user_prompt</span>
                                    <span style="font-size:0.83rem; font-weight:700; color:#94a3b8;">LLM 키워드 트렌드 상품 선택 프롬프트 (실 데이터)</span>
                                </div>
                                <div style="display:flex; align-items:center; gap:6px;">
                                    <button class="json-ctrl-btn" onclick="expandAllJson('promptUserStage2')">전체 펼치기</button>
                                    <button class="json-ctrl-btn" onclick="collapseAllJson('promptUserStage2')">전체 접기</button>
                                    <button id="btnCopyUser2" onclick="copyPromptTextToClipboard('promptUserStage2', 'btnCopyUser2')" class="json-ctrl-btn">내용 복사</button>
                                </div>
                            </div>
                            <div style="padding:14px 16px; background:#0f172a; max-height:360px; overflow:auto;">
                                <div id="promptUserStage2" class="json-tree-container"></div>
                            </div>
                        </div>

                        <!-- 2단계 LLM 결과 JSON 카드 -->
                        <div id="cardResultStage2" style="display:none; background:#0f172a; border-radius:8px; border:1px solid #1e293b; box-shadow:0 1px 3px rgba(0,0,0,0.2); overflow:hidden;">
                            <div style="display:flex; align-items:center; justify-content:space-between; padding:10px 16px; background:#1e293b; border-bottom:1px solid #334155;">
                                <div style="display:flex; align-items:center; gap:10px;">
                                    <span style="background:#8b5cf6; color:#ffffff; font-size:11px; font-weight:800; padding:2px 7px; border-radius:4px; letter-spacing:0.5px;">response</span>
                                    <span style="font-size:0.83rem; font-weight:700; color:#94a3b8;">LLM 응답 (JSON 트리 접기/펼치기 가능)</span>
                                </div>
                                <div style="display:flex; align-items:center; gap:6px;">
                                    <button class="json-ctrl-btn" onclick="expandAllJson('promptResultStage2')">전체 펼치기</button>
                                    <button class="json-ctrl-btn" onclick="collapseAllJson('promptResultStage2')">전체 접기</button>
                                    <button id="btnCopyResult2" onclick="copyPromptTextToClipboard('promptResultStage2', 'btnCopyResult2')" class="json-ctrl-btn">내용 복사</button>
                                </div>
                            </div>
                            <div style="padding:14px 16px; background:#0f172a; max-height:400px; overflow:auto;">
                                <div id="promptResultStage2" class="json-tree-container"></div>
                            </div>
                        </div>
                    </div>
                </section>
            </div>
        </main>
    </div>

    <script>
        // Streamlit secrets 기반 통합 도메인 설정
        const DOMAINS = {{
            HALFCLUB_WEB: "{HALFCLUB_WEB_URL}",
            HALFCLUB_API: "{HALFCLUB_API_URL}",
            HALFCLUB_CDN: "{HALFCLUB_CDN_URL}",
            BORIBORI_WEB: "{BORIBORI_WEB_URL}",
            BORIBORI_API: "{BORIBORI_API_URL}",
            BORIBORI_CDN: "{BORIBORI_CDN_URL}"
        }};

        // 현재 선택된 사이트 기준 웹 기본 도메인 반환 (기본: 하프클럽, siteCd '2': 보리보리)
        function getWebBaseUrl() {{
            const siteCd = document.getElementById('siteCdSelect')?.value || '1';
            return siteCd === '2' ? DOMAINS.BORIBORI_WEB : DOMAINS.HALFCLUB_WEB;
        }}

        // 현재 선택된 사이트 기준 API 기본 도메인 반환 (기본: 하프클럽, siteCd '2': 보리보리)
        function getApiBaseUrl() {{
            const siteCd = document.getElementById('siteCdSelect')?.value || '1';
            return siteCd === '2' ? DOMAINS.BORIBORI_API : DOMAINS.HALFCLUB_API;
        }}

        // 현재 선택된 사이트 기준 이미지 CDN 기본 도메인 반환 (기본: 하프클럽, siteCd '2': 보리보리)
        function getCdnBaseUrl() {{
            const siteCd = document.getElementById('siteCdSelect')?.value || '1';
            return siteCd === '2' ? DOMAINS.BORIBORI_CDN : DOMAINS.HALFCLUB_CDN;
        }}

        // 사이트 기준 통합 검색 URL 생성 헬퍼 함수
        function getSearchUrl(keyword, brandCode = null) {{
            const base = getWebBaseUrl();
            const cleanKw = encodeURIComponent((keyword || '').trim());
            if (brandCode) {{
                return `${{base}}/search/${{cleanKw}}?brandCd=${{encodeURIComponent(brandCode)}}`;
            }}
            return `${{base}}/search/${{cleanKw}}`;
        }}

        // 상품 상세 페이지 이동 URL 생성 헬퍼 함수 (사이트별 분기 지원)
        function getProductDetailUrl(prdNo) {{
            if (!prdNo || prdNo === '-') return '#';
            return `${{getWebBaseUrl()}}/product/${{prdNo}}`;
        }}

        // 상품 이미지 CDN 통합 URL 생성 헬퍼 함수 (사이트별 CDN 분기)
        function getImageUrl(imgPath) {{
            if (!imgPath) return '';
            if (imgPath.startsWith('http://') || imgPath.startsWith('https://')) return imgPath;
            return `${{getCdnBaseUrl()}}/rimg/330x440/contain/${{imgPath}}`;
        }}

        const allKeywords = {keywords_json_str};
        let currentKeyword = {initial_keyword_json};
        let currentTab = {initial_tab_json};
        let currentRawData = null;
        let currentApiUrl = '';
        let displayedKeywords = allKeywords;

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

            const searchInput = document.getElementById('keywordSearchInput');
            if (searchInput) searchInput.value = '';
            renderKeywordList(allKeywords);
            const defaultKw = allKeywords[0] || '가디건';
            switchViewTab('grid', false);
            selectKeyword(defaultKw, true, true);
        }}

        function copyCurrentUrl() {{
            const hostUrl = (window.parent && window.parent.location && window.parent.location.origin) 
                ? (window.parent.location.origin + window.parent.location.pathname)
                : (window.location.origin + window.location.pathname);
            const curUrl = hostUrl + '?keyword=' + encodeURIComponent(currentKeyword) + '&tab=' + encodeURIComponent(currentTab);
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

        function updateUrlQuery(kw, tab) {{
            try {{
                const queryStr = '?keyword=' + encodeURIComponent(kw) + '&tab=' + encodeURIComponent(tab);
                try {{
                    if (window.parent && window.parent.history && window.parent.history.replaceState) {{
                        let targetPath = queryStr;
                        try {{
                            if (window.parent.location && window.parent.location.pathname) {{
                                targetPath = window.parent.location.pathname + queryStr;
                            }}
                        }} catch (e) {{}}
                        window.parent.history.replaceState({{ keyword: kw, tab: tab }}, '', targetPath);
                    }}
                }} catch (e) {{}}

                try {{
                    if (window.top && window.top.history && window.top.history.replaceState) {{
                        let targetPath = queryStr;
                        try {{
                            if (window.top.location && window.top.location.pathname) {{
                                targetPath = window.top.location.pathname + queryStr;
                            }}
                        }} catch (e) {{}}
                        window.top.history.replaceState({{ keyword: kw, tab: tab }}, '', targetPath);
                    }}
                }} catch (e) {{}}

                if (window.history && window.history.replaceState) {{
                    window.history.replaceState({{ keyword: kw, tab: tab }}, '', queryStr);
                }}
            }} catch (e) {{}}
        }}

        function getInitialState() {{
            let kw = {initial_keyword_json};
            let tab = {initial_tab_json};

            try {{
                const searchStr = (window.parent && window.parent.location && window.parent.location.search) ? window.parent.location.search :
                                  (window.top && window.top.location && window.top.location.search) ? window.top.location.search :
                                  window.location.search;
                if (searchStr) {{
                    const params = new URLSearchParams(searchStr);
                    const pKw = params.get('keyword');
                    const pTab = params.get('tab');
                    if (pKw) {{
                        const decodedKw = decodeURIComponent(pKw).trim();
                        if (allKeywords.includes(decodedKw)) kw = decodedKw;
                    }}
                    if (pTab && ['grid', 'table', 'raw', 'prompt'].includes(pTab)) {{
                        tab = pTab;
                    }}
                }}
            }} catch (e) {{}}

            return {{ kw, tab }};
        }}

        if (document.readyState === 'loading') {{
            document.addEventListener('DOMContentLoaded', initApp);
        }} else {{
            initApp();
        }}

        function initApp() {{
            const initState = getInitialState();
            currentKeyword = initState.kw;
            currentTab = initState.tab;

            renderKeywordList(allKeywords);
            setupEventListeners();
            switchViewTab(currentTab, false);
            selectKeyword(currentKeyword, false, false);
            updateUrlQuery(currentKeyword, currentTab);
        }}

        function setupEventListeners() {{
            const searchInput = document.getElementById('keywordSearchInput');
            if (searchInput) {{
                searchInput.addEventListener('input', (e) => {{
                    const q = e.target.value.trim().toLowerCase();
                    const filtered = allKeywords.filter(k => k.toLowerCase().includes(q));
                    renderKeywordList(filtered);
                }});
                searchInput.addEventListener('keydown', (e) => {{
                    if (e.key === 'ArrowDown') {{
                        e.preventDefault();
                        const listContainer = document.getElementById('keywordList');
                        const firstLi = listContainer?.firstElementChild;
                        if (firstLi && displayedKeywords.length > 0) {{
                            firstLi.focus();
                            selectKeyword(displayedKeywords[0]);
                        }}
                    }}
                }});
            }}

            const siteSelect = document.getElementById('siteCdSelect');
            if (siteSelect) {{
                siteSelect.addEventListener('change', () => {{
                    updateHeaderKeyword(currentKeyword);
                    fetchKeywordTrend(currentKeyword);
                }});
            }}

            const btnFetch = document.getElementById('btnFetch');
            if (btnFetch) {{
                btnFetch.addEventListener('click', () => {{
                    fetchKeywordTrend(currentKeyword);
                }});
            }}
        }}

        function switchViewTab(tabName, updateUrl = true) {{
            currentTab = tabName;
            document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));

            if (tabName === 'grid') {{
                document.getElementById('tabBtnGrid').classList.add('active');
                document.getElementById('tabContentGrid').classList.add('active');
            }} else if (tabName === 'table') {{
                document.getElementById('tabBtnTable').classList.add('active');
                document.getElementById('tabContentTable').classList.add('active');
            }} else if (tabName === 'raw') {{
                document.getElementById('tabBtnRaw').classList.add('active');
                document.getElementById('tabContentRaw').classList.add('active');
            }} else if (tabName === 'prompt') {{
                document.getElementById('tabBtnPrompt').classList.add('active');
                document.getElementById('tabContentPrompt').classList.add('active');
            }}

            if (updateUrl) {{
                updateUrlQuery(currentKeyword, currentTab);
            }}
        }}

        function renderKeywordList(keywords) {{
            displayedKeywords = keywords;
            const listContainer = document.getElementById('keywordList');
            const badge = document.getElementById('keywordCountBadge');
            if (badge) badge.textContent = keywords.length;

            listContainer.innerHTML = '';
            keywords.forEach((kw, idx) => {{
                const origIdx = allKeywords.indexOf(kw) + 1;
                const li = document.createElement('li');
                li.className = `keyword-item ${{kw === currentKeyword ? 'active' : ''}}`;
                li.setAttribute('data-kw', kw);
                li.setAttribute('tabindex', '0');
                li.innerHTML = `<span>${{kw}}</span> <span style="font-size:0.75rem; opacity:0.6;">#${{origIdx}}</span>`;
                
                li.addEventListener('click', () => selectKeyword(kw));

                li.addEventListener('keydown', (e) => {{
                    if (e.key === 'ArrowDown') {{
                        e.preventDefault();
                        if (idx + 1 < displayedKeywords.length) {{
                            const nextIdx = idx + 1;
                            const nextLi = listContainer.children[nextIdx];
                            if (nextLi) {{
                                nextLi.focus();
                                selectKeyword(displayedKeywords[nextIdx]);
                            }}
                        }}
                    }} else if (e.key === 'ArrowUp') {{
                        e.preventDefault();
                        if (idx > 0) {{
                            const prevIdx = idx - 1;
                            const prevLi = listContainer.children[prevIdx];
                            if (prevLi) {{
                                prevLi.focus();
                                selectKeyword(displayedKeywords[prevIdx]);
                            }}
                        }} else {{
                            const searchInput = document.getElementById('keywordSearchInput');
                            if (searchInput) searchInput.focus();
                        }}
                    }} else if (e.key === 'Enter' || e.key === ' ') {{
                        e.preventDefault();
                        selectKeyword(kw);
                    }}
                }});

                listContainer.appendChild(li);
            }});
        }}

        function updateHeaderKeyword(kw) {{
            const txtEl = document.getElementById('currentKeywordText');
            if (txtEl) txtEl.textContent = kw;

            const linkEl = document.getElementById('currentKeywordTitleLink');
            if (linkEl) {{
                const siteCd = document.getElementById('siteCdSelect')?.value || '1';
                const siteName = siteCd === '2' ? '보리보리' : '하프클럽';
                linkEl.href = getSearchUrl(kw);
                linkEl.title = `${{siteName}}에서 '${{kw}}' 검색 (새 탭 이동)`;
            }}
        }}

        function selectKeyword(kw, updateUrl = true, resetTab = true) {{
            currentKeyword = kw;
            let activeElem = null;
            document.querySelectorAll('.keyword-item').forEach(item => {{
                if (item.getAttribute('data-kw') === kw) {{
                    item.classList.add('active');
                    activeElem = item;
                }} else {{
                    item.classList.remove('active');
                }}
            }});

            if (activeElem) {{
                activeElem.scrollIntoView({{ block: 'nearest', behavior: 'smooth' }});
            }}

            updateHeaderKeyword(kw);

            if (resetTab) {{
                switchViewTab('grid', false);
            }}

            const mainContent = document.querySelector('.main-content');
            if (mainContent) {{
                mainContent.scrollTop = 0;
            }}

            if (updateUrl) {{
                updateUrlQuery(kw, currentTab);
            }}

            fetchKeywordTrend(kw);
        }}

        function toggleArticlesAccordion() {{
            const container = document.getElementById('articlesListContainer');
            const icon = document.getElementById('articlesToggleIcon');
            if (!container) return;
            const isHidden = container.style.display === 'none' || !container.style.display;
            container.style.display = isHidden ? 'block' : 'none';
            if (icon) {{
                icon.textContent = isHidden ? '목록 접기 ▲' : '목록 펼치기 ▼';
            }}
        }}

        async function fetchKeywordTrend(kw) {{
            const siteCd = document.getElementById('siteCdSelect')?.value || '1';
            const size = document.getElementById('sizeInput')?.value || '50';
            const apiBase = getApiBaseUrl();
            currentApiUrl = `${{apiBase}}/recommend/keyword-trend?llmInfo=true&siteCd=${{siteCd}}&size=${{size}}&keyword=${{encodeURIComponent(kw)}}`;

            try {{
                const res = await fetch(currentApiUrl);
                if (!res.ok) {{
                    throw new Error(`HTTP ${{res.status}}: ${{res.statusText}}`);
                }}
                const contentType = res.headers.get('content-type') || '';
                if (!contentType.includes('application/json')) {{
                    const text = await res.text();
                    throw new Error(`API 응답이 JSON 형식이 아닙니다 (Status: ${{res.status}})\\n호출 URL: ${{currentApiUrl}}\\n응답 내용 앞부분: ${{text.slice(0, 150)}}`);
                }}
                const data = await res.json();
                currentRawData = data;
                renderDashboardData(data, kw);
            }} catch (err) {{
                document.getElementById('guideTextBody').innerHTML = `
                    <div style="color:#ef4444; font-weight:700; font-size:0.85rem; line-height:1.6;">
                        <div>API 호출 실패: ${{escapeHtml(err.message)}}</div>
                        <div style="font-size:0.78rem; color:#94a3b8; margin-top:4px; word-break:break-all;">요청 URL: ${{currentApiUrl}}</div>
                    </div>
                `;

                const gridContainer = document.getElementById('productGridContainer');
                if (gridContainer) {{
                    gridContainer.innerHTML = '<div style="grid-column:1/-1; padding:40px 20px; text-align:center; color:#64748b;">추천 상품 데이터가 없습니다.</div>';
                }}

                const tbody = document.getElementById('productTableBody');
                if (tbody) {{
                    tbody.innerHTML = '<tr><td colspan="10" style="text-align:center; padding:30px; color:#64748b;">추천 상품 데이터가 없습니다.</td></tr>';
                }}
            }}
        }}

        function renderDashboardData(data, kw) {{
            const llmInfo = data.llm_info || {{}};
            const reason = data.noshow_reason || llmInfo.noshow_reason || '';

            const provider = llmInfo.llm_provider || data.llm_provider || '-';
            const model = llmInfo.llm_model || data.llm_model || '-';
            const elemModel = document.getElementById('llmModelText');
            if (elemModel) {{
                elemModel.textContent = (provider === '-' && model === '-') ? '-' : `${{provider}} / ${{model}}`;
            }}

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
                    <span style="background:#ffffff; border:1px solid #e2e8f0; color:#334155; font-weight:700; padding:2px 8px; border-radius:4px; font-size:0.8rem;">카테고리: ${{bCat}}</span>
                    <span style="background:#ffffff; border:1px solid #e2e8f0; color:#334155; font-weight:700; padding:2px 8px; border-radius:4px; font-size:0.8rem;">성별: ${{bGen}}</span>
                `;
            }}

            const createDt = data.create_dt || llmInfo.create_dt || '-';
            const updateDt = data.update_dt || llmInfo.update_dt || '-';
            const elemCreateDt = document.getElementById('createDtText');
            if (elemCreateDt) elemCreateDt.textContent = createDt;
            const elemUpdateDt = document.getElementById('updateDtText');
            if (elemUpdateDt) elemUpdateDt.textContent = updateDt;

            // 큐레이션 요약문 (curation_summary: LLM 2단계 산출물 우선 탐색)
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

            // API 응답 데이터의 guide_text_html을 그대로 단독 표시
            let guideText = data.guide_text_html || '';

            const extKws = data.extracted_keywords || stage1.guide_result?.extracted_keywords || llmInfo.extracted_keywords || [];
            const extSearchKws = data.extracted_search_keywords || stage1.guide_result?.extracted_search_keywords || llmInfo.extracted_search_keywords || [];
            const extBrands = data.extracted_brands || stage1.guide_result?.extracted_brands || llmInfo.extracted_brands || [];

            if (reason) {{
                guideText = `
                    <div style="background:#fff1f2; border:1px solid #fecdd3; color:#9f1239; padding:16px 20px; border-radius:8px; line-height:1.6; margin-bottom:12px;">
                        <div style="font-weight:700; margin-bottom:4px; color:#be123c;">[미표시 사유]</div>
                        <div style="font-size:0.92rem; color:#be123c;">${{reason}}</div>
                    </div>
                ` + (guideText || '');
            }}

            document.getElementById('guideTextBody').innerHTML = guideText || '가이드 문구가 없습니다.';

            const catTag = data.extracted_category || stage1.guide_result?.extracted_category || '기본';
            const genTag = data.extracted_gender || stage1.guide_result?.extracted_gender || '공용';
            const seasonVal = data.extracted_season || stage1.guide_result?.extracted_season || ['사계절'];
            const seasonStr = Array.isArray(seasonVal) ? seasonVal.join(', ') : seasonVal;

            document.getElementById('extractedTagsHeader').innerHTML = `
                <span class="badge-chip-item badge-blue" style="font-weight:700;">카테고리: ${{catTag}}</span>
                <span class="badge-chip-item badge-gray">성별: ${{genTag}}</span>
                <span class="badge-chip-item badge-gray">계절: ${{seasonStr}}</span>
            `;

            const products = data.recommended_products || data.products || data.items || [];

            const brandToCodeMap = {{}};
            products.forEach(p => {{
                const bNm = (p.brandNm || p.brdNm || p.brand || '').trim().toLowerCase();
                const bCd = (p.brandCd || p.brdCd || p.brandCode || '').trim();
                if (bNm && bCd) {{
                    brandToCodeMap[bNm] = bCd;
                }}
            }});
            const v2Brands = data.internal_signals?.v2_brands || data.v2_brands || [];
            v2Brands.forEach(b => {{
                const bNm = (b.name || b.brandNm || '').trim().toLowerCase();
                const bCd = (b.code || b.brdCd || b.brandCd || '').trim();
                if (bNm && bCd) {{
                    brandToCodeMap[bNm] = bCd;
                }}
            }});

            const brandChips = extBrands.map((b, bIdx) => {{
                const bClean = (typeof b === 'object' ? b.name : b).trim();
                const bCode = (typeof b === 'object' && b.code) ? b.code : brandToCodeMap[bClean.toLowerCase()];
                
                const chipId = `brandChip_${{bIdx}}`;
                const searchUrl = bCode ? getSearchUrl(kw, bCode) : getSearchUrl(kw + ' ' + bClean);
                const titleText = bCode ? `브랜드 필터 '${{bClean}}' (${{bCode}}) 적용 검색` : `'${{kw}} ${{bClean}}' 검색`;

                return `<a id="${{chipId}}" href="${{searchUrl}}" target="_blank" rel="noopener noreferrer" class="badge-chip-item badge-brand" style="text-decoration:none; cursor:pointer;" title="${{titleText}}">${{bClean}} ↗</a>`;
            }}).join('');

            const kwChips = extKws.map(k => {{
                const searchUrl = getSearchUrl(kw + ' ' + k);
                return `<a href="${{searchUrl}}" target="_blank" rel="noopener noreferrer" class="badge-chip-item badge-blue" style="text-decoration:none; cursor:pointer;" title="'${{kw}} ${{k}}' 검색">${{k}} ↗</a>`;
            }}).join('');

            const searchKwChips = extSearchKws.map(k => {{
                const searchUrl = getSearchUrl(kw + ' ' + k);
                return `<a href="${{searchUrl}}" target="_blank" rel="noopener noreferrer" class="badge-chip-item badge-purple" style="text-decoration:none; cursor:pointer;" title="'${{kw}} ${{k}}' 검색">${{k}} ↗</a>`;
            }}).join('');

            document.getElementById('extractedBrandsWrap').innerHTML = brandChips ? `
                <div style="display:flex; align-items:flex-start; gap:10px; margin-top:8px;">
                    <span style="width:76px; min-width:76px; flex-shrink:0; font-weight:700; color:#475569; font-size:0.8rem; padding-top:2px;">대상 브랜드:</span>
                    <div style="display:flex; align-items:center; gap:6px; flex-wrap:wrap; flex:1;">${{brandChips}}</div>
                </div>
            ` : '';

            document.getElementById('extractedKeywordsWrap').innerHTML = kwChips ? `
                <div style="display:flex; align-items:flex-start; gap:10px; margin-top:6px;">
                    <span style="width:76px; min-width:76px; flex-shrink:0; font-weight:700; color:#475569; font-size:0.8rem; padding-top:2px;">추출 키워드:</span>
                    <div style="display:flex; align-items:center; gap:6px; flex-wrap:wrap; flex:1;">${{kwChips}}</div>
                </div>
            ` : '';

            document.getElementById('extractedSearchKeywordsWrap').innerHTML = searchKwChips ? `
                <div style="display:flex; align-items:flex-start; gap:10px; margin-top:6px;">
                    <span style="width:76px; min-width:76px; flex-shrink:0; font-weight:700; color:#475569; font-size:0.8rem; padding-top:2px;">검색 키워드:</span>
                    <div style="display:flex; align-items:center; gap:6px; flex-wrap:wrap; flex:1;">${{searchKwChips}}</div>
                </div>
            ` : '';

            const articles = data.keyword_articles || llmInfo.keyword_articles || [];
            const articlesContainer = document.getElementById('articlesListContainer');
            const countBadge = document.getElementById('articlesCountBadge');
            const wrap = document.getElementById('articlesWrapper');
            if (countBadge) {{
                countBadge.textContent = `${{articles.length}}건`;
            }}
            if (articlesContainer) {{
                if (!articles || articles.length === 0) {{
                    if (wrap) wrap.style.display = 'none';
                    articlesContainer.innerHTML = '<div style="font-size:0.75rem; color:#94a3b8; padding:6px 0;">참고 뉴스 기사가 없습니다.</div>';
                }} else {{
                    if (wrap) wrap.style.display = 'block';
                    const artHtml = articles.map(art => {{
                        const linkUrl = art.link || art.url || '#';
                        const sourceName = art.source || art.media || '뉴스';
                        const titleText = art.title || art.text || '제목 없음';
                        const pubDate = art.publish_dt || art.published_date || art.date || '';
                        const hasValidLink = linkUrl && linkUrl !== '#';

                        return `
                            <div style="background:#f8fafc; padding:8px 12px; border-radius:6px; border:1px solid #e2e8f0; display:flex; align-items:center; justify-content:space-between; font-size:0.8rem; margin-bottom:6px;">
                                <div style="display:flex; align-items:center; gap:8px; overflow:hidden;">
                                    <a href="${{linkUrl}}" ${{hasValidLink ? 'target="_blank" rel="noopener noreferrer"' : ''}} style="color:#0f172a; text-decoration:none; font-weight:600; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;" title="${{titleText}}">${{titleText}} <span class="badge-chip-item badge-media">${{sourceName}}</span></a>
                                </div>
                                <div style="display:flex; align-items:center; gap:8px; flex-shrink:0; font-size:0.75rem; color:#64748b;">
                                    ${{pubDate ? `<span>${{pubDate}}</span>` : ''}}
                                    ${{hasValidLink ? `<a href="${{linkUrl}}" target="_blank" rel="noopener noreferrer" style="color:#2563eb; text-decoration:underline; font-weight:600;">원문보기</a>` : ''}}
                                </div>
                            </div>
                        `;
                    }}).join('');
                    articlesContainer.innerHTML = artHtml;
                }}
            }}

            renderProductGrid(products, kw);
            renderProductTable(products, kw);
            renderRawJsonView(data);
            renderPromptInspector(stage1, stage2);
        }}

        function renderProductGrid(products, currentKw) {{
            const container = document.getElementById('productGridContainer');
            if (products.length === 0) {{
                container.innerHTML = '<div style="grid-column:1/-1; padding:20px; text-align:center; color:#64748b;">추천 상품 데이터가 없습니다.</div>';
                return;
            }}

            const kw = currentKw || currentKeyword;
            container.innerHTML = products.map((prd, idx) => {{
                const rank = idx + 1;
                const prdNo = prd.prdNo || prd.product_no || prd.id || '';
                const prdUrl = prd.prd_url || getProductDetailUrl(prdNo);
                const hasPrdUrl = prdUrl && prdUrl !== '#';

                const name = prd.prdNm || prd.name || '상품명 없음';
                const brand = prd.brandNm || prd.brdNm || prd.brand || '브랜드';
                const salePrc = prd.dcPrcApp || prd.selPrc || prd.salePrc || prd.price || 0;
                const nrmPrc = prd.normPrc || prd.nrmPrc || 0;
                const discRt = prd.totRateApp || prd.discRt || 0;
                const rating = prd.reviewStar || prd.avgPoint || 0.0;
                const reviews = prd.reviewQty || prd.revCnt || 0;
                const matchedKws = prd.matched_keywords || [];

                const imgUrl = getImageUrl(prd.appPrdImgUrl || prd.prdImg || '');

                const kwChips = matchedKws.map(k => {{
                    const searchUrl = getSearchUrl(kw + ' ' + k);
                    return `<a href="${{searchUrl}}" target="_blank" rel="noopener noreferrer" class="badge-chip-item badge-blue" style="text-decoration:none; cursor:pointer;" title="'${{kw}} ${{k}}' 검색">${{k}} ↗</a>`;
                }}).join('');
                const badgesHtml = renderBadgesHtml(prd);

                const rankClass = rank === 1 ? 'rank-badge rank-top1' : (rank === 2 ? 'rank-badge rank-top2' : (rank === 3 ? 'rank-badge rank-top3' : 'rank-badge'));
                const rankText = rank === 1 ? 'TOP 1' : (rank <= 3 ? `TOP ${{rank}}` : `#${{rank}}`);

                return `
                    <div class="product-card">
                        <div>
                            <a href="${{prdUrl}}" ${{hasPrdUrl ? 'target="_blank" rel="noopener noreferrer"' : ''}} style="display:block; text-decoration:none; color:inherit;">
                                <div class="product-img-wrap">
                                    <img src="${{imgUrl}}" class="product-img" alt="${{name}}"/>
                                    <span class="${{rankClass}}">${{rankText}}</span>
                                </div>
                                <div class="product-info">
                                    <div class="brand-name">${{brand}}</div>
                                    <div class="product-name" title="${{name}}">${{name}}</div>
                                    <div class="price-wrap">
                                        ${{discRt > 0 ? `<span class="discount-rate">${{discRt}}%</span>` : ''}}
                                        <span class="sale-price">${{salePrc.toLocaleString()}}원</span>
                                        ${{nrmPrc > salePrc ? `<span class="normal-price">${{nrmPrc.toLocaleString()}}원</span>` : ''}}
                                    </div>
                                    ${{reviews > 0 || rating > 0 ? `<div style="font-size:0.75rem; color:#64748b; font-weight:600;">★ ${{rating}} (리뷰 ${{reviews.toLocaleString()}})</div>` : ''}}
                                </div>
                            </a>
                        </div>
                        <div style="padding:0 12px 12px 12px;">
                            <div class="badge-chip-container"><span class="badge-chip-item">키워드:</span>${{kwChips}}</div>
                            ${{badgesHtml}}
                        </div>
                    </div>
                `;
            }}).join('');
        }}

        function renderProductTable(products, currentKw) {{
            const tbody = document.getElementById('productTableBody');
            if (products.length === 0) {{
                tbody.innerHTML = '<tr><td colspan="10" style="text-align:center; padding:20px; color:#64748b;">추천 상품 데이터가 없습니다.</td></tr>';
                return;
            }}

            const kw = currentKw || currentKeyword;
            tbody.innerHTML = products.map((prd, idx) => {{
                const rank = idx + 1;
                const prdNo = prd.prdNo || prd.product_no || prd.id || '-';
                const prdUrl = prd.prd_url || getProductDetailUrl(prdNo);
                const hasPrdUrl = prdUrl && prdUrl !== '#';

                const brand = prd.brandNm || prd.brdNm || prd.brand || '-';
                const name = prd.prdNm || prd.name || '-';
                
                const rawSalePrc = prd.dcPrcApp || prd.selPrc || prd.salePrc || prd.price || 0;
                const rawNrmPrc = prd.normPrc || prd.nrmPrc || 0;
                const rawDiscRt = prd.totRateApp || prd.discRt || 0;

                const salePrc = rawSalePrc ? `${{rawSalePrc.toLocaleString()}}원` : '0원';
                const nrmPrc = rawNrmPrc ? `${{rawNrmPrc.toLocaleString()}}원` : '-';
                const discRt = rawDiscRt ? `${{rawDiscRt}}%` : '-';

                const matchedKws = (prd.matched_keywords || []).map(k => {{
                    const searchUrl = getSearchUrl(kw + ' ' + k);
                    return `<a href="${{searchUrl}}" target="_blank" rel="noopener noreferrer" style="color:#2563eb; text-decoration:none; font-weight:600;">${{k}}</a>`;
                }}).join(', ');
                const rating = prd.reviewStar || prd.avgPoint || 0.0;
                const reviews = prd.reviewQty || prd.revCnt || 0;
                const ratingRev = `${{rating}} (${{reviews}})`;

                const cat = prd.dpCtgrNm2 || prd.dpCtgrNm1 || prd.catNm || '-';

                return `
                    <tr>
                        <td style="font-weight:700;">#${{rank}}</td>
                        <td>${{hasPrdUrl ? `<a href="${{prdUrl}}" target="_blank" rel="noopener noreferrer" style="color:#2563eb; text-decoration:none; font-weight:700;">${{prdNo}} ↗</a>` : prdNo}}</td>
                        <td style="font-weight:600;">${{brand}}</td>
                        <td>${{hasPrdUrl ? `<a href="${{prdUrl}}" target="_blank" rel="noopener noreferrer" style="color:#0f172a; text-decoration:none;">${{name}}</a>` : name}}</td>
                        <td style="font-weight:700; color:#0f172a;">${{salePrc}}</td>
                        <td style="color:#94a3b8; text-decoration:line-through;">${{nrmPrc}}</td>
                        <td style="color:#ef4444; font-weight:700;">${{discRt}}</td>
                        <td>${{matchedKws || '-'}}</td>
                        <td>${{ratingRev}}</td>
                        <td>${{cat}}</td>
                    </tr>
                `;
            }}).join('');
        }}

        let promptResDataMap = {{}};

        function renderPromptInspector(stage1, stage2) {{
            promptResDataMap = {{}};

            const p1Sys = stage1.prompt_info?.system_prompt;
            const cardSys1 = document.getElementById('cardSysStage1');
            const elemSys1 = document.getElementById('promptSysStage1');
            if (p1Sys && elemSys1) {{
                if (cardSys1) cardSys1.style.display = 'block';
                promptResDataMap['promptSysStage1'] = p1Sys;
                elemSys1.innerHTML = renderJsonTree(p1Sys, true);
            }}

            const p1User = stage1.prompt_info?.user_prompt;
            const cardUser1 = document.getElementById('cardUserStage1');
            const elemUser1 = document.getElementById('promptUserStage1');
            if (p1User && elemUser1) {{
                if (cardUser1) cardUser1.style.display = 'block';
                promptResDataMap['promptUserStage1'] = p1User;
                elemUser1.innerHTML = renderJsonTree(p1User, true);
            }} else if (cardUser1) {{
                cardUser1.style.display = 'none';
            }}

            const res1 = stage1.guide_result || stage1.prompt_info?.raw_response;
            const cardRes1 = document.getElementById('cardResultStage1');
            const elemRes1 = document.getElementById('promptResultStage1');
            if (res1 && elemRes1) {{
                if (cardRes1) cardRes1.style.display = 'block';
                promptResDataMap['promptResultStage1'] = res1;
                elemRes1.innerHTML = renderJsonTree(res1, true);
            }} else if (cardRes1) {{
                cardRes1.style.display = 'none';
            }}

            const p2Sys = stage2.prompt_info?.system_prompt;
            const cardSys2 = document.getElementById('cardSysStage2');
            const elemSys2 = document.getElementById('promptSysStage2');
            if (p2Sys && elemSys2) {{
                if (cardSys2) cardSys2.style.display = 'block';
                promptResDataMap['promptSysStage2'] = p2Sys;
                elemSys2.innerHTML = renderJsonTree(p2Sys, true);
            }}

            const p2User = stage2.prompt_info?.user_prompt;
            const cardUser2 = document.getElementById('cardUserStage2');
            const elemUser2 = document.getElementById('promptUserStage2');
            if (p2User && elemUser2) {{
                if (cardUser2) cardUser2.style.display = 'block';
                promptResDataMap['promptUserStage2'] = p2User;
                elemUser2.innerHTML = renderJsonTree(p2User, true);
            }} else if (cardUser2) {{
                cardUser2.style.display = 'none';
            }}

            const res2 = stage2.prompt_info?.raw_response || stage2.llm_response;
            const cardRes2 = document.getElementById('cardResultStage2');
            const elemRes2 = document.getElementById('promptResultStage2');
            if (res2 && elemRes2) {{
                if (cardRes2) cardRes2.style.display = 'block';
                promptResDataMap['promptResultStage2'] = res2;
                elemRes2.innerHTML = renderJsonTree(res2, true);
            }} else if (cardRes2) {{
                cardRes2.style.display = 'none';
            }}
        }}

        // 계층형 JSON 트리 렌더러 (객체/배열 단위 접기/펼치기 및 JSON 문자열 자동 파싱 지원)
        function renderJsonTree(data, isRoot = true) {{
            if (data === null || data === undefined) {{
                return '<span class="json-null">null</span>';
            }}
            if (typeof data === 'boolean') {{
                return `<span class="json-boolean">${{data}}</span>`;
            }}
            if (typeof data === 'number') {{
                return `<span class="json-number">${{data}}</span>`;
            }}
            if (typeof data === 'string') {{
                const trimmed = data.trim();
                if ((trimmed.startsWith('{{') && trimmed.endsWith('}}')) || (trimmed.startsWith('[') && trimmed.endsWith(']'))) {{
                    try {{
                        const parsed = JSON.parse(trimmed);
                        return renderJsonTree(parsed, false);
                    }} catch (e) {{}}
                }}
                if (data.includes(String.fromCharCode(10))) {{
                    return `<pre style="margin:0; font-family:'Consolas', 'Courier New', monospace; font-size:0.83rem; line-height:1.55; white-space:pre-wrap; word-break:break-all; color:#cbd5e1;">${{escapeHtml(data)}}</pre>`;
                }}
                return `<span class="json-string">"${{escapeHtml(data)}}"</span>`;
            }}

            if (Array.isArray(data)) {{
                if (data.length === 0) return '<span class="json-bracket">[]</span>';

                const itemsHtml = data.map((item, idx) => {{
                    const comma = (idx < data.length - 1) ? '<span class="json-comma">,</span>' : '';
                    return `<div class="json-node-row">${{renderJsonTree(item, false)}}${{comma}}</div>`;
                }}).join('');

                return `
                    <span class="json-node-collapsible">
                        <span class="json-toggle" onclick="toggleJsonNode(this)" title="접기/펼치기">▼</span>
                        <span class="json-bracket">[</span>
                        <span class="json-collapsed-text" style="display:none;" onclick="toggleJsonNode(this.previousElementSibling.previousElementSibling)">... ${{data.length}} items </span>
                        <div class="json-children">${{itemsHtml}}</div>
                        <span class="json-bracket">]</span>
                    </span>
                `;
            }}

            if (typeof data === 'object') {{
                const keys = Object.keys(data);
                if (keys.length === 0) return '<span class="json-bracket">{{}}</span>';

                const itemsHtml = keys.map((key, idx) => {{
                    const comma = (idx < keys.length - 1) ? '<span class="json-comma">,</span>' : '';
                    return `
                        <div class="json-node-row">
                            <span class="json-key">"${{escapeHtml(key)}}"</span><span class="json-colon">: </span>${{renderJsonTree(data[key], false)}}${{comma}}
                        </div>
                    `;
                }}).join('');

                return `
                    <span class="json-node-collapsible">
                        <span class="json-toggle" onclick="toggleJsonNode(this)" title="접기/펼치기">▼</span>
                        <span class="json-bracket">{{</span>
                        <span class="json-collapsed-text" style="display:none;" onclick="toggleJsonNode(this.previousElementSibling.previousElementSibling)">... ${{keys.length}} keys </span>
                        <div class="json-children">${{itemsHtml}}</div>
                        <span class="json-bracket">}}</span>
                    </span>
                `;
            }}

            return escapeHtml(String(data));
        }}

        function toggleJsonNode(el) {{
            const parent = el.closest('.json-node-collapsible');
            if (!parent) return;
            const toggleBtn = parent.querySelector(':scope > .json-toggle');
            const collapsedText = parent.querySelector(':scope > .json-collapsed-text');
            const children = parent.querySelector(':scope > .json-children');

            if (!children) return;

            const isCollapsed = children.style.display === 'none';
            if (isCollapsed) {{
                children.style.display = 'block';
                if (toggleBtn) toggleBtn.textContent = '▼';
                if (collapsedText) collapsedText.style.display = 'none';
            }} else {{
                children.style.display = 'none';
                if (toggleBtn) toggleBtn.textContent = '▶';
                if (collapsedText) collapsedText.style.display = 'inline';
            }}
        }}

        function expandAllJson(containerId) {{
            const container = document.getElementById(containerId);
            if (!container) return;
            container.querySelectorAll('.json-node-collapsible').forEach(node => {{
                const toggleBtn = node.querySelector(':scope > .json-toggle');
                const collapsedText = node.querySelector(':scope > .json-collapsed-text');
                const children = node.querySelector(':scope > .json-children');
                if (children) children.style.display = 'block';
                if (toggleBtn) toggleBtn.textContent = '▼';
                if (collapsedText) collapsedText.style.display = 'none';
            }});
        }}

        function collapseAllJson(containerId) {{
            const container = document.getElementById(containerId);
            if (!container) return;
            container.querySelectorAll('.json-node-collapsible').forEach(node => {{
                const toggleBtn = node.querySelector(':scope > .json-toggle');
                const collapsedText = node.querySelector(':scope > .json-collapsed-text');
                const children = node.querySelector(':scope > .json-children');
                if (children) children.style.display = 'none';
                if (toggleBtn) toggleBtn.textContent = '▶';
                if (collapsedText) collapsedText.style.display = 'inline';
            }});
        }}

        function highlightJsonHtml(obj, restoreNewlines = false) {{
            let str = '';
            if (typeof obj === 'string') {{
                try {{
                    const parsed = JSON.parse(obj);
                    str = JSON.stringify(parsed, null, 2);
                }} catch (e) {{
                    str = String(obj);
                }}
            }} else {{
                str = JSON.stringify(obj, null, 2);
            }}

            if (restoreNewlines) {{
                str = str.replace(/\\\\n/g, String.fromCharCode(10));
            }}

            const escaped = escapeHtml(str);
            return escaped.replace(/("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\\s*:)?|\\b(true|false|null)\\b|-?\\d+(?:\\.\\d*)?(?:[eE][+\\-]?\\d+)?)/g, function (match) {{
                let cls = 'json-number';
                if (/^"/.test(match)) {{
                    if (/:$/.test(match)) {{
                        cls = 'json-key';
                    }} else {{
                        cls = 'json-string';
                    }}
                }} else if (/true|false/.test(match)) {{
                    cls = 'json-boolean';
                }} else if (/null/.test(match)) {{
                    cls = 'json-null';
                }}
                return `<span class="${{cls}}">${{match}}</span>`;
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

        function copyPromptTextToClipboard(elemId, btnId) {{
            const btn = document.getElementById(btnId);
            if (!btn) return;
            let textToCopy = '';
            if (promptResDataMap[elemId]) {{
                const val = promptResDataMap[elemId];
                textToCopy = (typeof val === 'string') ? val : JSON.stringify(val, null, 2);
            }} else {{
                const elem = document.getElementById(elemId);
                if (!elem) return;
                textToCopy = elem.innerText || elem.textContent;
            }}

            navigator.clipboard.writeText(textToCopy).then(() => {{
                const origText = btn.textContent;
                btn.textContent = '복사 완료!';
                btn.style.background = '#10b981';
                setTimeout(() => {{
                    btn.textContent = origText;
                    btn.style.background = '#334155';
                }}, 1500);
            }}).catch(err => {{
                alert('복사 실패: ' + err);
            }});
        }}

        function copyRawJsonToClipboard(btnId) {{
            if (!currentRawData) return;
            const btn = document.getElementById(btnId);
            const str = JSON.stringify(currentRawData, null, 2);
            navigator.clipboard.writeText(str).then(() => {{
                btn.textContent = '복사 완료!';
                btn.style.background = '#10b981';
                setTimeout(() => {{
                    btn.textContent = 'JSON 전체 복사';
                    btn.style.background = '#334155';
                }}, 1500);
            }}).catch(err => {{
                alert('복사 실패: ' + err);
            }});
        }}

        function renderRawJsonView(data) {{
            const container = document.getElementById('rawJsonContainer');
            const apiUrl = currentApiUrl;
            const treeHtml = renderJsonTree(data, true);

            const urlCard = `
                <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:8px; padding:12px 16px; margin-bottom:16px; display:flex; align-items:center; justify-content:space-between;">
                    <div style="display:flex; align-items:center; gap:10px; overflow:hidden;">
                        <span style="background:#2563eb; color:#ffffff; font-size:11px; font-weight:800; padding:3px 8px; border-radius:4px;">GET</span>
                        <span style="font-family:monospace; font-size:0.85rem; color:#2563eb; font-weight:700; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">${{apiUrl}}</span>
                    </div>
                </div>
            `;

            const jsonCard = `
                <div style="background:#0f172a; border-radius:8px; border:1px solid #1e293b; box-shadow:0 1px 3px rgba(0,0,0,0.2); overflow:hidden;">
                    <div style="display:flex; align-items:center; justify-content:space-between; padding:10px 16px; background:#1e293b; border-bottom:1px solid #334155;">
                        <div style="display:flex; align-items:center; gap:10px;">
                            <span style="background:#10b981; color:#ffffff; font-size:11px; font-weight:800; padding:2px 7px; border-radius:4px; letter-spacing:0.5px;">200 OK</span>
                            <span style="font-size:0.83rem; font-weight:700; color:#94a3b8;">키워드 트렌드 API 원본 JSON 데이터 (객체/배열 접기/펼치기 가능)</span>
                        </div>
                        <div style="display:flex; align-items:center; gap:6px;">
                            <button class="json-ctrl-btn" onclick="expandAllJson('rawJsonTreeBody')">전체 펼치기</button>
                            <button class="json-ctrl-btn" onclick="collapseAllJson('rawJsonTreeBody')">전체 접기</button>
                            <button id="btnCopyJson" onclick="copyRawJsonToClipboard('btnCopyJson')" class="json-ctrl-btn">JSON 전체 복사</button>
                        </div>
                    </div>
                    <div style="padding:14px 16px; background:#0f172a; max-height:600px; overflow:auto;">
                        <div id="rawJsonTreeBody" class="json-tree-container">${{treeHtml}}</div>
                    </div>
                </div>
            `;

            container.innerHTML = urlCard + jsonCard;
        }}

        function renderBadgesHtml(item) {{
            let htmls = [];
            if (item.badgeImg && typeof item.badgeImg === 'string' && item.badgeImg.trim()) {{
                htmls.push(`<img src="${{item.badgeImg.trim()}}" style="height:17px; vertical-align:middle;" alt="배지"/>`);
            }}
            if (item.eblmImg && typeof item.eblmImg === 'string' && item.eblmImg.trim()) {{
                htmls.push(`<img src="${{item.eblmImg.trim()}}" style="height:17px; vertical-align:middle;" alt="엠블럼"/>`);
            }}

            let icnNms = item.icnNms || [];
            if (icnNms.length === 0 && item.icnNm) {{
                icnNms = item.icnNm.split('@');
            }}

            icnNms.forEach(name => {{
                const clean = String(name).trim();
                if (!clean) return;
                let cls = 'badge-gray';
                if (clean.includes('무료배송')) cls = 'badge-blue';
                else if (clean.includes('온리') || clean.includes('단독')) cls = 'badge-red';
                htmls.push(`<span class="badge-chip-item ${{cls}}">${{clean}}</span>`);
            }});

            if (htmls.length > 0) {{
                return `<div class="badge-chip-container">${{htmls.join(' ')}}</div>`;
            }}
            return '';
        }}
    </script>
</body>
</html>
"""

# Streamlit 원페이지 통합 HTML 서빙 (내부 단일 스크롤 전용)
components.html(html_content, height=1000, scrolling=False)
