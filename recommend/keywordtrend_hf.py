import os
import json
import streamlit as st
import streamlit.components.v1 as components

# 1. 페이지 기본 설정 (전체 화면 모드)
st.set_page_config(
    page_title="Halfclub Trend AI Curation Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. 기본 CSS 덮어쓰기 (Streamlit 상단 헤더/푸터 제거 및 iframe 100% 핏)
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

# 4. URL 쿼리 파라미터 읽기 (초기 접속 / 새로고침 / URL 직접 공유 완벽 지원)
qp = st.query_params
initial_kw = qp.get("keyword", keywords_list[0] if keywords_list else "가디건")
if initial_kw not in keywords_list:
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
        body {{
            background-color: #ffffff;
            color: #0f172a;
            height: 100vh;
            overflow: hidden;
        }}
        .app-container {{
            display: flex;
            height: 100vh;
            width: 100vw;
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
            padding: 9px 18px;
            font-size: 0.88rem;
            color: #334155;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: space-between;
            transition: background 0.12s ease, color 0.12s ease;
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
            font-weight: 700;
            border-left: 3px solid #2563eb;
        }}
        
        /* 우측 메인 대시보드 */
        .main-content {{
            flex: 1;
            display: flex;
            flex-direction: column;
            overflow-y: auto;
            background-color: #ffffff;
        }}
        .top-navbar {{
            padding: 16px 28px;
            border-bottom: 1px solid #e2e8f0;
            display: flex;
            align-items: center;
            justify-content: space-between;
            background-color: #ffffff;
            position: sticky;
            top: 0;
            z-index: 10;
        }}
        .navbar-title {{
            font-size: 1.35rem;
            font-weight: 800;
            color: #0f172a;
        }}
        .dashboard-body {{
            padding: 24px 28px;
            flex: 1;
        }}
        
        /* 헤더 메타 뱃지 */
        .meta-badges {{
            display: flex;
            align-items: center;
            gap: 16px;
            margin-bottom: 18px;
            font-size: 0.83rem;
            color: #64748b;
            font-weight: 600;
        }}
        
        /* 트렌드 가이드 박스 */
        .guide-card-box {{
            background-color: #ffffff;
            border: 1px solid #cbd5e1;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
            margin-bottom: 22px;
        }}
        .guide-card-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 12px;
        }}
        .guide-title {{
            font-size: 1.05rem;
            font-weight: 800;
            color: #0f172a;
        }}
        .guide-text {{
            font-size: 0.93rem;
            line-height: 1.65;
            color: #334155;
            margin-bottom: 14px;
        }}
        .highlight-kw {{
            background-color: #fef08a;
            color: #854d0e;
            padding: 2px 5px;
            border-radius: 4px;
            font-weight: 700;
        }}
        
        /* 탭 서식 */
        .tab-navigation {{
            display: flex;
            gap: 8px;
            border-bottom: 2px solid #e2e8f0;
            margin-bottom: 20px;
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
            transition: color 0.15s ease, border-color 0.15s ease;
        }}
        .tab-btn.active {{
            color: #2563eb;
            border-bottom-color: #2563eb;
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
            border-radius: 8px;
            overflow: hidden;
            background: #ffffff;
            box-shadow: 0 1px 3px rgba(0,0,0,0.04);
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            transition: transform 0.15s ease, box-shadow 0.15s ease;
        }}
        .product-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        }}
        .product-img-wrap {{
            position: relative;
            width: 100%;
            height: 210px;
            background-color: #f1f5f9;
        }}
        .product-img {{
            width: 100%;
            height: 100%;
            object-fit: cover;
        }}
        .rank-badge {{
            position: absolute;
            top: 8px;
            left: 8px;
            background-color: #0f172a;
            color: #ffffff;
            font-size: 11px;
            font-weight: 800;
            padding: 2px 7px;
            border-radius: 4px;
        }}
        .product-info {{
            padding: 12px;
        }}
        .brand-name {{
            font-size: 0.76rem;
            color: #64748b;
            font-weight: 700;
            margin-bottom: 2px;
        }}
        .product-name {{
            font-size: 0.85rem;
            font-weight: 600;
            color: #0f172a;
            height: 38px;
            overflow: hidden;
            text-overflow: ellipsis;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            line-height: 1.35;
            margin-bottom: 8px;
        }}
        .price-wrap {{
            display: flex;
            align-items: baseline;
            gap: 4px;
            margin-bottom: 6px;
        }}
        .sale-price {{
            font-size: 0.95rem;
            font-weight: 800;
            color: #0f172a;
        }}
        .normal-price {{
            font-size: 0.75rem;
            color: #94a3b8;
            text-decoration: line-through;
        }}
        .discount-rate {{
            font-size: 0.75rem;
            color: #ef4444;
            font-weight: 700;
        }}
        .badge-chip-container {{
            display: flex;
            flex-wrap: wrap;
            gap: 4px;
            margin-top: 6px;
        }}
        .badge-chip-item {{
            font-size: 10px;
            padding: 2px 6px;
            border-radius: 4px;
            font-weight: 600;
        }}
        .badge-blue {{ background: #eff6ff; color: #2563eb; }}
        .badge-red {{ background: #fef2f2; color: #dc2626; }}
        .badge-gray {{ background: #f1f5f9; color: #475569; }}
        .badge-brand {{ background: #ecfdf5; color: #059669; border: 1px solid #a7f3d0; }}
        .badge-media {{ background: #e0f2fe; color: #0369a1; font-weight: 700; }}
        
        /* 데이터 테이블 */
        .data-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.84rem;
        }}
        .data-table th {{
            background-color: #f8fafc;
            color: #475569;
            font-weight: 700;
            padding: 10px 12px;
            border-bottom: 1px solid #e2e8f0;
            text-align: left;
        }}
        .data-table td {{
            padding: 10px 12px;
            border-bottom: 1px solid #f1f5f9;
            color: #334155;
        }}
        .data-table tr:hover {{
            background-color: #f8fafc;
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
    </style>
</head>
<body>
    <div class="app-container">
        <!-- 좌측 키워드 사이드바 -->
        <aside class="sidebar">
            <div class="sidebar-header">
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
            <header class="top-navbar" style="display:flex; align-items:center; justify-content:space-between; padding-bottom:14px;">
                <div style="display:flex; align-items:center; gap:10px;">
                    <h1 class="navbar-title" id="currentKeywordTitle" style="font-size:1.4rem; font-weight:800; color:#0f172a; margin:0;">가디건</h1>
                    <span style="background:#eff6ff; border:1px solid #dbeafe; color:#1d4ed8; font-size:12px; font-weight:700; padding:3px 12px; border-radius:9999px;">키워드 트렌드 추천</span>
                    <button id="btnCopyUrl" onclick="copyCurrentUrl()" style="background:#f1f5f9; border:1px solid #cbd5e1; color:#475569; font-size:11px; font-weight:700; padding:3px 8px; border-radius:6px; cursor:pointer;" title="현재 키워드 URL 링크 복사">URL 복사</button>
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
                <div class="meta-badges" id="metaBadgesBar" style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:8px; padding:9px 16px; margin-bottom:18px; display:flex; align-items:center; gap:20px; font-size:0.83rem; font-weight:600; color:#64748b;">
                    <div style="display:flex; align-items:center; gap:6px;">
                        <span>LLM 모델:</span>
                        <span style="background:#eff6ff; border:1px solid #bfdbfe; color:#2563eb; font-weight:700; padding:2px 8px; border-radius:4px; font-size:0.82rem;" id="llmModelText">-</span>
                    </div>
                    <div style="display:flex; align-items:center; gap:6px;">
                        <span>LLM 토큰:</span>
                        <span style="background:#fdf2f8; border:1px solid #fbcfe8; color:#db2777; font-weight:700; padding:2px 8px; border-radius:4px; font-size:0.82rem;" id="tokenUsageText">In: 0 / Out: 0 / Cached: 0 (Total: 0)</span>
                    </div>
                    <div style="display:flex; align-items:center; gap:6px;">
                        <span>필터링 적용:</span>
                        <span id="filterBadgesText" style="display:flex; gap:6px;">
                            <span style="background:#ffffff; border:1px solid #e2e8f0; color:#334155; font-weight:700; padding:2px 8px; border-radius:4px; font-size:0.8rem;">브랜드: ON</span>
                            <span style="background:#ffffff; border:1px solid #e2e8f0; color:#334155; font-weight:700; padding:2px 8px; border-radius:4px; font-size:0.8rem;">카테고리: ON</span>
                            <span style="background:#ffffff; border:1px solid #e2e8f0; color:#334155; font-weight:700; padding:2px 8px; border-radius:4px; font-size:0.8rem;">성별: ON</span>
                        </span>
                    </div>
                    <div style="display:flex; align-items:center; gap:6px;">
                        <span>생성일시:</span>
                        <span style="background:#f1f5f9; border:1px solid #cbd5e1; color:#334155; font-weight:700; padding:2px 8px; border-radius:4px; font-size:0.82rem;" id="createDtText">-</span>
                    </div>
                    <div style="display:flex; align-items:center; gap:6px;">
                        <span>갱신일시:</span>
                        <span style="background:#f1f5f9; border:1px solid #cbd5e1; color:#334155; font-weight:700; padding:2px 8px; border-radius:4px; font-size:0.82rem;" id="updateDtText">-</span>
                    </div>
                </div>

                <!-- AI 트렌드 큐레이션 가이드 카드 -->
                <div class="guide-card-box" id="guideCard">
                    <div class="guide-card-header">
                        <div class="guide-title">AI 트렌드 큐레이션 가이드</div>
                        <div style="display:flex; gap:6px;" id="extractedTagsHeader"></div>
                    </div>
                    <div class="guide-text" id="guideTextBody">데이터를 불러오는 중입니다...</div>
                    <div style="font-size:0.8rem; font-weight:600; color:#64748b; margin-top:8px;" id="extractedBrandsWrap"></div>
                    <div style="font-size:0.8rem; font-weight:600; color:#64748b; margin-top:4px;" id="extractedKeywordsWrap"></div>
                    
                    <!-- 참고 뉴스 기사 5건 목록 -->
                    <div style="margin-top:14px; padding-top:12px; border-top:1px solid #e2e8f0;" id="articlesWrapper">
                        <div style="font-size:0.8rem; font-weight:700; color:#475569; margin-bottom:8px; display:flex; align-items:center; justify-content:space-between;">
                            <span>참고 뉴스 기사 목록</span>
                            <span style="font-size:0.72rem; color:#94a3b8; font-weight:normal;">원문 클릭 이동</span>
                        </div>
                        <div id="articlesListContainer"></div>
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
                                <button id="btnCopySys1" onclick="copyPromptTextToClipboard('promptSysStage1', 'btnCopySys1')" style="background:#334155; color:#f8fafc; border:none; padding:4px 10px; border-radius:4px; font-size:12px; font-weight:600; cursor:pointer;">내용 복사</button>
                            </div>
                            <div style="padding:14px 16px; background:#0f172a; max-height:280px; overflow:auto;">
                                <pre style="margin:0; font-family:'Consolas', 'Courier New', monospace; font-size:0.83rem; line-height:1.55; color:#cbd5e1; white-space:pre-wrap; word-break:break-all;"><code id="promptSysStage1"></code></pre>
                            </div>
                        </div>

                        <!-- 1단계 입력 User Prompt 카드 -->
                        <div id="cardUserStage1" style="display:none; background:#0f172a; border-radius:8px; border:1px solid #1e293b; box-shadow:0 1px 3px rgba(0,0,0,0.2); overflow:hidden;">
                            <div style="display:flex; align-items:center; justify-content:space-between; padding:10px 16px; background:#1e293b; border-bottom:1px solid #334155;">
                                <div style="display:flex; align-items:center; gap:10px;">
                                    <span style="background:#059669; color:#ffffff; font-size:11px; font-weight:800; padding:2px 7px; border-radius:4px; letter-spacing:0.5px;">user_prompt</span>
                                    <span style="font-size:0.83rem; font-weight:700; color:#94a3b8;">LLM 키워드 트렌드 가이드 생성 프롬프트 (실 데이터)</span>
                                </div>
                                <button id="btnCopyUser1" onclick="copyPromptTextToClipboard('promptUserStage1', 'btnCopyUser1')" style="background:#334155; color:#f8fafc; border:none; padding:4px 10px; border-radius:4px; font-size:12px; font-weight:600; cursor:pointer;">내용 복사</button>
                            </div>
                            <div style="padding:14px 16px; background:#0f172a; max-height:360px; overflow:auto;">
                                <pre style="margin:0; font-family:'Consolas', 'Courier New', monospace; font-size:0.83rem; line-height:1.55; white-space:pre-wrap; word-break:break-all;"><code id="promptUserStage1"></code></pre>
                            </div>
                        </div>

                        <!-- 1단계 LLM 결과 JSON 카드 -->
                        <div id="cardResultStage1" style="display:none; background:#0f172a; border-radius:8px; border:1px solid #1e293b; box-shadow:0 1px 3px rgba(0,0,0,0.2); overflow:hidden;">
                            <div style="display:flex; align-items:center; justify-content:space-between; padding:10px 16px; background:#1e293b; border-bottom:1px solid #334155;">
                                <div style="display:flex; align-items:center; gap:10px;">
                                    <span style="background:#8b5cf6; color:#ffffff; font-size:11px; font-weight:800; padding:2px 7px; border-radius:4px; letter-spacing:0.5px;">response</span>
                                    <span style="font-size:0.83rem; font-weight:700; color:#94a3b8;">LLM 응답</span>
                                </div>
                                <button id="btnCopyResult1" onclick="copyPromptTextToClipboard('promptResultStage1', 'btnCopyResult1')" style="background:#334155; color:#f8fafc; border:none; padding:4px 10px; border-radius:4px; font-size:12px; font-weight:600; cursor:pointer;">내용 복사</button>
                            </div>
                            <div style="padding:14px 16px; background:#0f172a; max-height:360px; overflow:auto;">
                                <pre style="margin:0; font-family:'Consolas', 'Courier New', monospace; font-size:0.83rem; line-height:1.55; white-space:pre-wrap; word-break:break-all;"><code id="promptResultStage1"></code></pre>
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
                                <button id="btnCopySys2" onclick="copyPromptTextToClipboard('promptSysStage2', 'btnCopySys2')" style="background:#334155; color:#f8fafc; border:none; padding:4px 10px; border-radius:4px; font-size:12px; font-weight:600; cursor:pointer;">내용 복사</button>
                            </div>
                            <div style="padding:14px 16px; background:#0f172a; max-height:280px; overflow:auto;">
                                <pre style="margin:0; font-family:'Consolas', 'Courier New', monospace; font-size:0.83rem; line-height:1.55; color:#cbd5e1; white-space:pre-wrap; word-break:break-all;"><code id="promptSysStage2"></code></pre>
                            </div>
                        </div>

                        <!-- 2단계 입력 User Prompt 카드 -->
                        <div id="cardUserStage2" style="display:none; background:#0f172a; border-radius:8px; border:1px solid #1e293b; box-shadow:0 1px 3px rgba(0,0,0,0.2); overflow:hidden;">
                            <div style="display:flex; align-items:center; justify-content:space-between; padding:10px 16px; background:#1e293b; border-bottom:1px solid #334155;">
                                <div style="display:flex; align-items:center; gap:10px;">
                                    <span style="background:#059669; color:#ffffff; font-size:11px; font-weight:800; padding:2px 7px; border-radius:4px; letter-spacing:0.5px;">user_prompt</span>
                                    <span style="font-size:0.83rem; font-weight:700; color:#94a3b8;">LLM 키워드 트렌드 상품 선택 프롬프트 (실 데이터)</span>
                                </div>
                                <button id="btnCopyUser2" onclick="copyPromptTextToClipboard('promptUserStage2', 'btnCopyUser2')" style="background:#334155; color:#f8fafc; border:none; padding:4px 10px; border-radius:4px; font-size:12px; font-weight:600; cursor:pointer;">내용 복사</button>
                            </div>
                            <div style="padding:14px 16px; background:#0f172a; max-height:360px; overflow:auto;">
                                <pre style="margin:0; font-family:'Consolas', 'Courier New', monospace; font-size:0.83rem; line-height:1.55; white-space:pre-wrap; word-break:break-all;"><code id="promptUserStage2"></code></pre>
                            </div>
                        </div>

                        <!-- 2단계 LLM 결과 JSON 카드 -->
                        <div id="cardResultStage2" style="display:none; background:#0f172a; border-radius:8px; border:1px solid #1e293b; box-shadow:0 1px 3px rgba(0,0,0,0.2); overflow:hidden;">
                            <div style="display:flex; align-items:center; justify-content:space-between; padding:10px 16px; background:#1e293b; border-bottom:1px solid #334155;">
                                <div style="display:flex; align-items:center; gap:10px;">
                                    <span style="background:#8b5cf6; color:#ffffff; font-size:11px; font-weight:800; padding:2px 7px; border-radius:4px; letter-spacing:0.5px;">response</span>
                                    <span style="font-size:0.83rem; font-weight:700; color:#94a3b8;">LLM 응답</span>
                                </div>
                                <button id="btnCopyResult2" onclick="copyPromptTextToClipboard('promptResultStage2', 'btnCopyResult2')" style="background:#334155; color:#f8fafc; border:none; padding:4px 10px; border-radius:4px; font-size:12px; font-weight:600; cursor:pointer;">내용 복사</button>
                            </div>
                            <div style="padding:14px 16px; background:#0f172a; max-height:400px; overflow:auto;">
                                <pre style="margin:0; font-family:'Consolas', 'Courier New', monospace; font-size:0.83rem; line-height:1.55; white-space:pre-wrap; word-break:break-all;"><code id="promptResultStage2"></code></pre>
                            </div>
                        </div>
                    </div>
                </section>
            </div>
        </main>
    </div>

    <script>
        const allKeywords = {keywords_json_str};
        let currentKeyword = {initial_keyword_json};
        let currentTab = {initial_tab_json};
        let currentRawData = null;
        let currentApiUrl = '';
        let displayedKeywords = allKeywords;

        function copyCurrentUrl() {{
            const curUrl = window.location.origin + window.location.pathname + '?keyword=' + encodeURIComponent(currentKeyword) + '&tab=' + encodeURIComponent(currentTab);
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

        if (document.readyState === 'loading') {{
            document.addEventListener('DOMContentLoaded', initApp);
        }} else {{
            initApp();
        }}

        function initApp() {{
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

        function selectKeyword(kw, updateUrl = true, resetTab = true) {{
            currentKeyword = kw;
            let activeElem = null;
            document.querySelectorAll('.keyword-item').forEach(item => {{
                const txtElem = item.querySelector('span');
                const txt = txtElem ? txtElem.textContent : '';
                if (txt === kw) {{
                    item.classList.add('active');
                    activeElem = item;
                }} else {{
                    item.classList.remove('active');
                }}
            }});

            if (activeElem) {{
                activeElem.scrollIntoView({{ block: 'nearest', behavior: 'smooth' }});
            }}

            document.getElementById('currentKeywordTitle').textContent = kw;

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

        async function fetchKeywordTrend(kw) {{
            const siteCd = document.getElementById('siteCdSelect').value || '1';
            const size = document.getElementById('sizeInput')?.value || '50';
            currentApiUrl = `https://dev-api.halfclub.com/recommend/keyword-trend?llmInfo=true&siteCd=${{siteCd}}&size=${{size}}&keyword=${{encodeURIComponent(kw)}}`;
            const brandFilterUrl = `https://hapix.halfclub.com/searches/v2/product/brand-filter/?keyword=${{encodeURIComponent(kw)}}&isPopular=true&size=100&device=pc`;

            try {{
                const [recRes, brandRes] = await Promise.allSettled([
                    fetch(currentApiUrl),
                    fetch(brandFilterUrl)
                ]);

                if (recRes.status !== 'fulfilled' || !recRes.value.ok) {{
                    throw new Error(`API HTTP Error: ${{recRes.status === 'fulfilled' ? recRes.value.status : recRes.reason}}`);
                }}
                const data = await recRes.value.json();
                currentRawData = data;

                let brandFilterList = [];
                if (brandRes.status === 'fulfilled' && brandRes.value.ok) {{
                    try {{
                        const bData = await brandRes.value.json();
                        brandFilterList = bData?.data?.aggregations?.brand || [];
                    }} catch (e) {{
                        console.warn('Brand filter parse failed:', e);
                    }}
                }}

                renderDashboardData(data, kw, brandFilterList);
            }} catch (err) {{
                document.getElementById('guideTextBody').innerHTML = `
                    <div style="color:#ef4444; font-weight:700; font-size:0.85rem;">API 호출 실패: ${{err.message}}</div>
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

        function renderDashboardData(data, kw, brandFilterList = []) {{
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

            const brandFilter = data.enable_brand_filter ?? llmInfo.enable_brand_filter;
            const catFilter = data.enable_category_filter ?? llmInfo.enable_category_filter;
            const genFilter = data.enable_gender_filter ?? llmInfo.enable_gender_filter;

            const bBrand = brandFilter === true ? 'ON' : 'OFF';
            const bCat = catFilter === true ? 'ON' : 'OFF';
            const bGen = genFilter === true ? 'ON' : 'OFF';

            const elemFilter = document.getElementById('filterBadgesText');
            if (elemFilter) {{
                elemFilter.innerHTML = `
                    <span style="background:#ffffff; border:1px solid #e2e8f0; color:#334155; font-weight:700; padding:2px 8px; border-radius:4px; font-size:0.8rem;">브랜드: ${{bBrand}}</span>
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

            let guideText = data.guide_text || data.guide_text_html || '';
            const extKws = data.extracted_keywords || [];
            const extBrands = data.extracted_brands || [];

            if (extKws.length > 0) {{
                const sortedKws = [...extKws, kw].sort((a, b) => b.length - a.length);
                sortedKws.forEach(k => {{
                    if (k && k.trim()) {{
                        const cleanKw = k.trim().replace(/\\s+/g, '');
                        if (cleanKw) {{
                            let escapedPattern = '';
                            const specialChars = '.*+?^${{}}()|[]\\\\';
                            for (let ci = 0; ci < cleanKw.length; ci++) {{
                                const ch = cleanKw[ci];
                                if (specialChars.indexOf(ch) !== -1) {{
                                    escapedPattern += '\\\\' + ch;
                                }} else {{
                                    escapedPattern += ch;
                                }}
                                if (ci < cleanKw.length - 1) {{
                                    escapedPattern += '\\\\s*';
                                }}
                            }}
                            const reg = new RegExp(`(${{escapedPattern}})`, 'gi');
                            guideText = guideText.replace(reg, '<strong class="highlight-kw">$1</strong>');
                        }}
                    }}
                }});
            }}

            if (reason) {{
                guideText = `
                    <div style="background:#fff1f2; border:1px solid #fecdd3; color:#9f1239; padding:16px 20px; border-radius:8px; line-height:1.6; margin-bottom:12px;">
                        <div style="font-weight:700; margin-bottom:4px; color:#be123c;">[미표시 사유]</div>
                        <div style="font-size:0.92rem; color:#be123c;">${{reason}}</div>
                    </div>
                ` + (guideText || '');
            }}

            document.getElementById('guideTextBody').innerHTML = guideText || '가이드 문구가 없습니다.';

            const catTag = data.extracted_category || '기본';
            const genTag = data.extracted_gender || '공용';
            const seasonVal = data.extracted_season || ['사계절'];
            const seasonStr = Array.isArray(seasonVal) ? seasonVal.join(', ') : seasonVal;

            document.getElementById('extractedTagsHeader').innerHTML = `
                <span class="badge-chip-item badge-gray">카테고리: ${{catTag}}</span>
                <span class="badge-chip-item badge-gray">성별: ${{genTag}}</span>
                <span class="badge-chip-item badge-gray">계절: ${{seasonStr}}</span>
            `;

            const products = data.recommended_products || data.products || data.items || [];

            const brandToCodeMap = {{}};
            brandFilterList.forEach(b => {{
                const bNm = (b.name || b.brandNm || b.key || '').trim();
                const bCd = (b.code || b.brandCd || b.brdCd || '').trim();
                if (bNm && bCd) {{
                    brandToCodeMap[bNm.toLowerCase()] = bCd;
                    brandToCodeMap[bNm] = bCd;
                }}
            }});
            products.forEach(p => {{
                const bNm = (p.brandNm || p.brdNm || p.brand || '').trim();
                const bCd = (p.brandCd || p.brdCd || p.brandCode || '').trim();
                if (bNm && bCd) {{
                    brandToCodeMap[bNm.toLowerCase()] = bCd;
                    brandToCodeMap[bNm] = bCd;
                }}
            }});
            const v2Brands = data.internal_signals?.v2_brands || data.v2_brands || [];
            v2Brands.forEach(b => {{
                const bNm = (b.name || b.brandNm || '').trim();
                const bCd = (b.code || b.brdCd || b.brandCd || '').trim();
                if (bNm && bCd) {{
                    brandToCodeMap[bNm.toLowerCase()] = bCd;
                    brandToCodeMap[bNm] = bCd;
                }}
            }});

            const brandChips = extBrands.map((b, bIdx) => {{
                const bClean = (typeof b === 'object' ? b.name : b).trim();
                let bCode = (typeof b === 'object' && b.code) ? b.code : (brandToCodeMap[bClean.toLowerCase()] || brandToCodeMap[bClean]);
                
                const chipId = `brandChip_${{bIdx}}`;
                const searchUrl = bCode 
                    ? `https://halfclub.com/search/${{encodeURIComponent(kw)}}?brandCd=${{encodeURIComponent(bCode)}}`
                    : `https://halfclub.com/search/${{encodeURIComponent(kw + ' ' + bClean)}}`;
                const titleText = bCode ? `하프클럽 브랜드 필터 '${{bClean}}' (${{bCode}}) 적용 검색` : `하프클럽에서 '${{kw}} ${{bClean}}' 검색`;

                if (!bCode) {{
                    fetch(`https://hapix.halfclub.com/searches/prdList/?keyword=${{encodeURIComponent(bClean)}}&device=pc&limit=0,1&sortSeq=12&isOnlyList=true`)
                        .then(r => r.json())
                        .then(resData => {{
                            const hits = resData?.data?.result?.hits?.hits;
                            if (hits && hits.length > 0) {{
                                const foundCd = hits[0]?._source?.brandCd;
                                if (foundCd) {{
                                    const chipEl = document.getElementById(chipId);
                                    if (chipEl) {{
                                        chipEl.href = `https://halfclub.com/search/${{encodeURIComponent(kw)}}?brandCd=${{encodeURIComponent(foundCd)}}`;
                                        chipEl.title = `하프클럽 브랜드 필터 '${{bClean}}' (${{foundCd}}) 적용 검색`;
                                    }}
                                }}
                            }}
                        }})
                        .catch(() => {{}});
                }}

                return `<a id="${{chipId}}" href="${{searchUrl}}" target="_blank" rel="noopener noreferrer" class="badge-chip-item badge-brand" style="text-decoration:none; cursor:pointer;" title="${{titleText}}">${{bClean}} ↗</a>`;
            }}).join('');

            const kwChips = extKws.map(k => {{
                const searchUrl = `https://halfclub.com/search/${{encodeURIComponent(kw + ' ' + k)}}`;
                return `<a href="${{searchUrl}}" target="_blank" rel="noopener noreferrer" class="badge-chip-item badge-blue" style="text-decoration:none; cursor:pointer;" title="하프클럽에서 '${{kw}} ${{k}}' 검색">${{k}} ↗</a>`;
            }}).join('');

            document.getElementById('extractedBrandsWrap').innerHTML = brandChips ? `
                <div style="display:flex; align-items:center; gap:8px; flex-wrap:wrap;">
                    <span style="flex-shrink:0; font-weight:700;">추출 브랜드:</span>
                    <div style="display:flex; align-items:center; gap:6px; flex-wrap:wrap;">${{brandChips}}</div>
                </div>
            ` : '';

            document.getElementById('extractedKeywordsWrap').innerHTML = kwChips ? `
                <div style="display:flex; align-items:center; gap:8px; flex-wrap:wrap; margin-top:4px;">
                    <span style="flex-shrink:0; font-weight:700;">추출 키워드:</span>
                    <div style="display:flex; align-items:center; gap:6px; flex-wrap:wrap;">${{kwChips}}</div>
                </div>
            ` : '';

            const articles = data.keyword_articles || llmInfo.keyword_articles || [];
            const articlesContainer = document.getElementById('articlesListContainer');
            if (articlesContainer) {{
                if (!articles || articles.length === 0) {{
                    articlesContainer.innerHTML = '<div style="font-size:0.75rem; color:#94a3b8;">참고 뉴스 기사가 없습니다.</div>';
                }} else {{
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
                const prdUrl = prd.prd_url || (prdNo ? `https://halfclub.com/product/${{prdNo}}` : '#');
                const hasPrdUrl = prdUrl && prdUrl !== '#';

                const name = prd.prdNm || prd.name || '상품명 없음';
                const brand = prd.brandNm || prd.brdNm || prd.brand || '브랜드';
                const salePrc = prd.dcPrcApp || prd.selPrc || prd.salePrc || prd.price || 0;
                const nrmPrc = prd.normPrc || prd.nrmPrc || 0;
                const discRt = prd.totRateApp || prd.discRt || 0;
                const rating = prd.reviewStar || prd.avgPoint || 0.0;
                const reviews = prd.reviewQty || prd.revCnt || 0;
                const matchedKws = prd.matched_keywords || [];

                let imgUrl = prd.appPrdImgUrl || prd.prdImg || '';
                if (imgUrl && !imgUrl.startswith('http')) {{
                    imgUrl = `https://cdn2.halfclub.com/rimg/330x440/contain/${{imgUrl}}`;
                }}

                const kwChips = matchedKws.map(k => {{
                    const searchUrl = `https://halfclub.com/search/${{encodeURIComponent(kw + ' ' + k)}}`;
                    return `<a href="${{searchUrl}}" target="_blank" rel="noopener noreferrer" class="badge-chip-item badge-blue" style="text-decoration:none; cursor:pointer;" title="하프클럽에서 '${{kw}} ${{k}}' 검색">${{k}} ↗</a>`;
                }}).join('');
                const badgesHtml = renderBadgesHtml(prd);

                return `
                    <div class="product-card">
                        <div>
                            <a href="${{prdUrl}}" ${{hasPrdUrl ? 'target="_blank" rel="noopener noreferrer"' : ''}} style="display:block; text-decoration:none; color:inherit;">
                                <div class="product-img-wrap">
                                    <img src="${{imgUrl}}" class="product-img" alt="${{name}}"/>
                                    <span class="rank-badge">#${{rank}}</span>
                                </div>
                                <div class="product-info">
                                    <div class="brand-name">${{brand}}</div>
                                    <div class="product-name" title="${{name}}">${{name}}</div>
                                    <div class="price-wrap">
                                        <span class="sale-price">${{salePrc.toLocaleString()}}원</span>
                                        ${{nrmPrc > salePrc ? `<span class="normal-price">${{nrmPrc.toLocaleString()}}원</span>` : ''}}
                                        ${{discRt > 0 ? `<span class="discount-rate">${{discRt}}%</span>` : ''}}
                                    </div>
                                    <div style="font-size:0.72rem; color:#64748b;">평점 ${{rating}} (${{reviews}}개 리뷰)</div>
                                </div>
                            </a>
                        </div>
                        <div style="padding:0 12px 12px 12px;">
                            <div class="badge-chip-container"><span class="badge-chip-item">매칭 키워드:</span>${{kwChips}}</div>
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
                const prdUrl = prd.prd_url || (prdNo !== '-' ? `https://halfclub.com/product/${{prdNo}}` : '#');
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
                    const searchUrl = `https://halfclub.com/search/${{encodeURIComponent(kw + ' ' + k)}}`;
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

        function renderPromptInspector(stage1, stage2) {{
            const p1Sys = stage1.prompt_info?.system_prompt;
            const cardSys1 = document.getElementById('cardSysStage1');
            const elemSys1 = document.getElementById('promptSysStage1');
            if (p1Sys && elemSys1) {{
                if (cardSys1) cardSys1.style.display = 'block';
                elemSys1.innerHTML = highlightJsonHtml(p1Sys, true);
            }}

            const p1User = stage1.prompt_info?.user_prompt;
            const cardUser1 = document.getElementById('cardUserStage1');
            const elemUser1 = document.getElementById('promptUserStage1');
            if (p1User && elemUser1) {{
                if (cardUser1) cardUser1.style.display = 'block';
                elemUser1.innerHTML = highlightJsonHtml(p1User, true);
            }} else if (cardUser1) {{
                cardUser1.style.display = 'none';
            }}

            const res1 = stage1.guide_result || stage1.prompt_info?.raw_response;
            const cardRes1 = document.getElementById('cardResultStage1');
            const elemRes1 = document.getElementById('promptResultStage1');
            if (res1 && elemRes1) {{
                if (cardRes1) cardRes1.style.display = 'block';
                elemRes1.innerHTML = highlightJsonHtml(res1, true);
            }} else if (cardRes1) {{
                cardRes1.style.display = 'none';
            }}

            const p2Sys = stage2.prompt_info?.system_prompt;
            const cardSys2 = document.getElementById('cardSysStage2');
            const elemSys2 = document.getElementById('promptSysStage2');
            if (p2Sys && elemSys2) {{
                if (cardSys2) cardSys2.style.display = 'block';
                elemSys2.innerHTML = highlightJsonHtml(p2Sys, true);
            }}

            const p2User = stage2.prompt_info?.user_prompt;
            const cardUser2 = document.getElementById('cardUserStage2');
            const elemUser2 = document.getElementById('promptUserStage2');
            if (p2User && elemUser2) {{
                if (cardUser2) cardUser2.style.display = 'block';
                elemUser2.innerHTML = highlightJsonHtml(p2User, true);
            }} else if (cardUser2) {{
                cardUser2.style.display = 'none';
            }}

            const res2 = stage2.prompt_info?.raw_response || stage2.llm_response;
            const cardRes2 = document.getElementById('cardResultStage2');
            const elemRes2 = document.getElementById('promptResultStage2');
            if (res2 && elemRes2) {{
                if (cardRes2) cardRes2.style.display = 'block';
                elemRes2.innerHTML = highlightJsonHtml(res2, true);
            }} else if (cardRes2) {{
                cardRes2.style.display = 'none';
            }}
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
            const elem = document.getElementById(elemId);
            const btn = document.getElementById(btnId);
            if (!elem) return;
            const textToCopy = elem.innerText || elem.textContent;
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
            const highlightedJson = highlightJsonHtml(data);

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
                            <span style="font-size:0.83rem; font-weight:700; color:#94a3b8;">키워드 트렌드 API 원본 JSON 데이터</span>
                        </div>
                        <button id="btnCopyJson" onclick="copyRawJsonToClipboard('btnCopyJson')" style="background:#334155; color:#f8fafc; border:none; padding:4px 10px; border-radius:4px; font-size:12px; font-weight:600; cursor:pointer; transition:background 0.15s ease;">JSON 전체 복사</button>
                    </div>
                    <div style="padding:14px 16px; background:#0f172a; max-height:550px; overflow:auto;">
                        <pre style="margin:0; font-family:'Consolas', 'Courier New', monospace; font-size:0.83rem; line-height:1.55; white-space:pre-wrap; word-break:break-all; color:#cbd5e1;"><code>${{highlightedJson}}</code></pre>
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

# Streamlit 원페이지 통합 HTML 서빙 (전체 100vh 뷰포트)
components.html(html_content, height=960, scrolling=True)
