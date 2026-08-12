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

# 기본 CSS 덮어쓰기 (Streamlit 여백 제거 및 프레임 최대화)
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
</style>
""", unsafe_allow_html=True)

# 파일 경로 산출
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KEYWORDS_PATH = os.path.join(BASE_DIR, "keywords.json")

def load_keywords():
    if os.path.exists(KEYWORDS_PATH):
        try:
            with open(KEYWORDS_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
        except Exception as e:
            pass
    return [    "가디건",
    "가방",
    "골프모자",
    "골프백",
    "골프장갑",
    "골프티",
    "골프화",
    "귀걸이",
    "긴바지",
    "긴팔티셔츠",
    "남성가방",
    "남성골프화",
    "남성벨트",
    "넥워머",
    "넥타이",
    "니트",
    "토드백",
    "데님",
    "데님팬츠",
    "드레스",
    "등산화",
    "런닝화",
    "레깅스",
    "레더자켓",
    "레인부츠",
    "로퍼",
    "맨투맨",
    "머플러",
    "모자",
    "목걸이",
    "민소매",
    "민소매티셔츠",
    "반바지",
    "반팔",
    "반팔티셔츠",
    "베스트",
    "벨트",
    "보스턴백",
    "보스톤백",
    "볼캡",
    "부츠",
    "브로치",
    "비니",
    "샌들",
    "서류가방",
    "선글라스",
    "셋업",
    "셔츠",
    "손수건",
    "숄더백",
    "스니커즈",
    "스카프",
    "스커트",
    "스포츠웨어",
    "슬랙스",
    "슬리퍼",
    "슬링백",
    "신발",
    "아우터",
    "양말",
    "에코백",
    "여성가방",
    "여성골프화",
    "여성벨트",
    "오픈토",
    "요가복",
    "우산",
    "우비",
    "운동화",
    "원피스",
    "자켓",
    "바람막이",
    "잠옷",
    "장갑",
    "점퍼",
    "정장",
    "정장자켓",
    "정장팬츠",
    "정장화",
    "조끼",
    "집업",
    "집업티셔츠",
    "코트",
    "크로스백",
    "클러치",
    "오픈토",
    "토트백",
    "트렌치",
    "티셔츠",
    "패딩",
    "귀걸이",
    "목걸이",
    "팔찌",
    "팬츠",
    "펌프스",
    "플랫",
    "하프팬츠",
    "후드",
    "힐",
    "후리스",
    "후드티",
    "스웨터",
    "블라우스",
    "발찌",
    "슈즈",
    "슬링백",
    "양산",
    "지갑",
    "시계",
    "홈웨어",
    "수트",
    "무스탕"]

keywords_list = load_keywords()
keywords_json_str = json.dumps(keywords_list, ensure_ascii=False)

# 불필요한 내부 규칙 문구가 전면 철거된 0.1초 비동기 SPA 자원
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
        /* 좌측 사이드바 (index.html 1:1 라이트 테마) */
        .sidebar {{
            width: 270px;
            background-color: #ffffff;
            border-right: 1px solid #e2e8f0;
            display: flex;
            flex-direction: column;
            padding: 16px;
            flex-shrink: 0;
        }}
        .brand {{
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 16px;
        }}
        .brand-logo {{
            background: linear-gradient(135deg, #4f46e5, #ec4899);
            color: #ffffff;
            font-weight: 800;
            font-size: 1.05rem;
            padding: 6px 10px;
            border-radius: 8px;
        }}
        .brand-text h1 {{
            font-size: 1.05rem;
            font-weight: 800;
            color: #0f172a;
            line-height: 1.2;
        }}
        .brand-text p {{
            font-size: 0.75rem;
            color: #64748b;
        }}
        .search-box {{
            margin-bottom: 12px;
        }}
        .search-box input {{
            width: 100%;
            background-color: #ffffff;
            border: 1px solid #cbd5e1;
            color: #0f172a;
            padding: 9px 12px;
            border-radius: 6px;
            font-size: 0.85rem;
            outline: none;
        }}
        .search-box input:focus {{
            border-color: #2563eb;
            box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.15);
        }}
        .section-header-row {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;
            padding: 4px 0;
        }}
        .section-label {{
            font-size: 0.78rem;
            font-weight: 700;
            color: #64748b;
            text-transform: uppercase;
        }}
        .keyword-count-badge {{
            background: #eff6ff;
            color: #2563eb;
            border: 1px solid #bfdbfe;
            font-size: 0.72rem;
            font-weight: 700;
            padding: 2px 8px;
            border-radius: 10px;
        }}
        .keyword-list {{
            list-style: none;
            overflow-y: auto;
            flex-grow: 1;
            display: flex;
            flex-direction: column;
            gap: 3px;
            padding-right: 4px;
        }}
        .keyword-item {{
            padding: 9px 12px;
            border-radius: 6px;
            font-size: 0.88rem;
            color: #475569;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border: 1px solid transparent;
            transition: all 0.15s ease;
        }}
        .keyword-item:hover {{
            background-color: #f8fafc;
            color: #0f172a;
            border-color: #cbd5e1;
        }}
        .keyword-item.active {{
            background-color: #eff6ff;
            border-color: #bfdbfe;
            color: #2563eb;
            font-weight: 700;
        }}
        
        /* 메인 콘텐츠 구역 */
        .main-content {{
            flex-grow: 1;
            display: flex;
            flex-direction: column;
            overflow: hidden;
            background-color: #f8fafc;
        }}
        
        /* index.html 1:1 동기화 메인 상단 헤더 */
        .top-header {{
            background-color: #ffffff;
            border-bottom: 1px solid #e2e8f0;
            padding: 12px 24px;
            display: flex;
            flex-direction: column;
            gap: 10px;
            box-shadow: 0 1px 2px rgba(0,0,0,0.03);
        }}
        .header-top-row {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            width: 100%;
        }}
        .controls-group {{
            display: flex;
            align-items: center;
            gap: 14px;
        }}
        .control-item {{
            display: flex;
            align-items: center;
            gap: 6px;
            font-size: 0.82rem;
            font-weight: 600;
            color: #334155;
        }}
        .control-item select, .control-item input {{
            background-color: #ffffff;
            border: 1px solid #cbd5e1;
            color: #0f172a;
            padding: 5px 8px;
            border-radius: 6px;
            font-size: 0.82rem;
            outline: none;
            font-weight: 600;
        }}
        .btn-fetch {{
            background-color: #0f172a;
            color: #ffffff;
            border: none;
            padding: 6px 14px;
            border-radius: 6px;
            font-size: 0.82rem;
            font-weight: 700;
            cursor: pointer;
            transition: background 0.2s ease;
        }}
        .btn-fetch:hover {{
            background-color: #334155;
        }}
        .active-title-group {{
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .active-title-group h2 {{
            font-size: 1.3rem;
            font-weight: 800;
            color: #0f172a;
        }}
        
        /* meta-timestamps 뱃지 바 */
        .meta-timestamps {{
            display: flex;
            align-items: center;
            flex-wrap: wrap;
            gap: 16px;
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            padding: 6px 12px;
            border-radius: 6px;
            font-size: 0.78rem;
        }}
        .meta-item {{
            display: flex;
            align-items: center;
            gap: 6px;
        }}
        .meta-label {{
            color: #64748b;
            font-weight: 600;
        }}
        .meta-val {{
            color: #0f172a;
            font-weight: 700;
        }}
        .meta-llm-badge {{
            background: #eff6ff;
            color: #2563eb;
            border: 1px solid #bfdbfe;
            padding: 1px 6px;
            border-radius: 4px;
        }}
        .token-usage-badge {{
            background: #fdf2f8;
            color: #db2777;
            border: 1px solid #fbcfe8;
            padding: 1px 6px;
            border-radius: 4px;
        }}
        .filter-badges-group {{
            display: flex;
            gap: 4px;
        }}
        .filter-badge {{
            background: #ffffff;
            border: 1px solid #cbd5e1;
            color: #334155;
            padding: 1px 5px;
            border-radius: 4px;
            font-size: 0.72rem;
            font-weight: 700;
        }}
        
        /* 대시보드 스크롤 바디 */
        .dashboard-scroll-body {{
            overflow-y: auto;
            padding: 16px 24px;
            display: flex;
            flex-direction: column;
            gap: 14px;
        }}
        
        /* AI 트렌드 가이드 카드 */
        .card {{
            background-color: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 16px;
            box-shadow: 0 1px 2px rgba(0,0,0,0.03);
        }}
        .card-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }}
        .card-header h3 {{
            font-size: 1.0rem;
            font-weight: 800;
            color: #0f172a;
        }}
        .tags-group {{
            display: flex;
            gap: 6px;
        }}
        .tag {{
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 0.75rem;
            font-weight: 700;
            background-color: #f8fafc;
            border: 1px solid #cbd5e1;
            color: #334155;
        }}
        .guide-text-body {{
            font-size: 0.92rem;
            line-height: 1.65;
            color: #1e293b;
            margin-bottom: 10px;
        }}
        .highlight-kw {{
            font-weight: bold;
            color: #854d0e;
            background-color: #fef08a;
            padding: 2px 6px;
            border-radius: 4px;
            border-bottom: 2px solid #eab308;
        }}
        
        /* 메인 뷰 탭 3종 스타일 */
        .view-tabs-header {{
            display: flex;
            border-bottom: 2px solid #cbd5e1;
            margin-bottom: 14px;
            gap: 8px;
        }}
        .tab-btn {{
            background: none;
            border: none;
            padding: 8px 16px;
            font-size: 0.88rem;
            font-weight: 700;
            color: #64748b;
            cursor: pointer;
            border-bottom: 2px solid transparent;
            margin-bottom: -2px;
            transition: all 0.2s ease;
        }}
        .tab-btn:hover {{
            color: #0f172a;
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
        
        /* 5열 상품 카드 그리드 */
        .products-grid {{
            display: grid;
            grid-template-columns: repeat(5, 1fr);
            gap: 14px;
        }}
        @media (max-width: 1400px) {{
            .products-grid {{ grid-template-columns: repeat(4, 1fr); }}
        }}
        @media (max-width: 1100px) {{
            .products-grid {{ grid-template-columns: repeat(3, 1fr); }}
        }}
        
        .product-card {{
            background-color: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            box-shadow: 0 1px 2px rgba(0,0,0,0.04);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }}
        .product-card:hover {{
            transform: translateY(-3px);
            box-shadow: 0 6px 16px rgba(0,0,0,0.08);
        }}
        .card-img-container {{
            width: 100%;
            height: 185px;
            background-color: #f8fafc;
            overflow: hidden;
            position: relative;
        }}
        .card-img-container img {{
            width: 100%;
            height: 100%;
            object-fit: cover;
        }}
        .rank-badge {{
            position: absolute;
            top: 6px;
            left: 6px;
            background-color: rgba(15, 23, 42, 0.75);
            color: #ffffff;
            font-size: 0.72rem;
            font-weight: 700;
            padding: 2px 6px;
            border-radius: 3px;
        }}
        
        .card-info {{
            padding: 11px;
            display: flex;
            flex-direction: column;
            gap: 3px;
        }}
        .badge-chip-container {{
            display: flex;
            flex-wrap: wrap;
            gap: 4px;
            align-items: center;
            height: 22px;
            overflow: hidden;
            margin-bottom: 2px;
        }}
        .badge-chip-item {{
            display: inline-flex;
            align-items: center;
            font-size: 10px;
            font-weight: 700;
            padding: 2px 6px;
            border-radius: 3px;
            color: #ffffff;
            white-space: nowrap;
        }}
        .badge-blue {{ background-color: #2563eb; }}
        .badge-red {{ background-color: #dc2626; }}
        .badge-gray {{ background-color: #64748b; }}
        
        .card-brand {{
            font-size: 0.78rem;
            font-weight: 800;
            color: #2563eb;
            text-transform: uppercase;
        }}
        .card-title {{
            font-size: 0.85rem;
            font-weight: 600;
            color: #0f172a;
            line-height: 1.3;
            height: 2.6em;
            overflow: hidden;
            text-overflow: ellipsis;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
        }}
        .price-row {{
            display: flex;
            align-items: baseline;
            gap: 4px;
            margin-top: 2px;
        }}
        .price-rate {{
            font-size: 0.92rem;
            font-weight: 800;
            color: #dc2626;
        }}
        .price-final {{
            font-size: 1.0rem;
            font-weight: 800;
            color: #0f172a;
        }}
        .price-origin {{
            font-size: 0.75rem;
            color: #94a3b8;
            text-decoration: line-through;
        }}
        .matched-line {{
            font-size: 0.75rem;
            color: #2563eb;
            font-weight: 700;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            margin-top: 1px;
        }}
        .meta-line {{
            font-size: 0.72rem;
            color: #64748b;
        }}
        .btn-dtl {{
            display: block;
            text-align: center;
            background-color: #0f172a;
            color: #ffffff;
            font-size: 0.78rem;
            font-weight: 700;
            padding: 6px 0;
            border-radius: 4px;
            text-decoration: none;
            margin-top: 6px;
            transition: background 0.2s ease;
        }}
        .btn-dtl:hover {{
            background-color: #334155;
        }}

        /* 데이터 테이블 스타일 */
        .data-table-container {{
            background-color: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            overflow-x: auto;
            box-shadow: 0 1px 2px rgba(0,0,0,0.03);
        }}
        .custom-data-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.82rem;
            text-align: left;
        }}
        .custom-data-table th {{
            background-color: #f1f5f9;
            color: #0f172a;
            font-weight: 700;
            padding: 10px 12px;
            border-bottom: 2px solid #cbd5e1;
            white-space: nowrap;
        }}
        .custom-data-table td {{
            padding: 10px 12px;
            border-bottom: 1px solid #e2e8f0;
            color: #334155;
        }}
        .custom-data-table tr:hover {{
            background-color: #f8fafc;
        }}

        /* Raw JSON 복원 스타일 */
        .raw-json-container {{
            background-color: #0f172a;
            color: #38bdf8;
            padding: 16px;
            border-radius: 8px;
            font-family: monospace;
            font-size: 0.82rem;
            overflow-x: auto;
            max-height: 550px;
            line-height: 1.5;
        }}

        .loading-overlay {{
            font-size: 0.95rem;
            color: #64748b;
            padding: 40px;
            text-align: center;
            font-weight: 600;
        }}
    </style>
</head>

<body>
    <div class="app-container">
        <!-- 좌측 사이드바 (index.html 1:1 동기화) -->
        <aside class="sidebar">
            <div class="brand">
                <div class="brand-logo">HF</div>
                <div class="brand-text">
                    <h1>Trend AI</h1>
                    <p>패션 큐레이션 대시보드</p>
                </div>
            </div>

            <div class="search-box">
                <input type="text" id="keywordSearchInput" placeholder="키워드 검색 (예: 가디건)...">
            </div>

            <div class="section-header-row">
                <span class="section-label">트렌드 키워드</span>
                <span class="keyword-count-badge" id="keywordCountBadge">0</span>
            </div>

            <ul class="keyword-list" id="keywordList">
                <!-- JavaScript 비동기 렌더링 -->
            </ul>
        </aside>

        <!-- 메인 콘텐츠 영역 -->
        <main class="main-content">
            <!-- index.html 1:1 동기화 상단 메인 헤더 & meta-timestamps 뱃지 바 -->
            <header class="top-header">
                <div class="header-top-row">
                    <div class="active-title-group">
                        <h2 id="currentKeywordTitle"></h2>
                        <span style="background:#f1f5f9; color:#0f172a; border:1px solid #cbd5e1; padding:3px 9px; border-radius:10px; font-size:12px; font-weight:bold;">키워드 트렌드 추천</span>
                    </div>

                    <div class="controls-group">
                        <div class="control-item">
                            <label for="siteCdSelect">사이트:</label>
                            <select id="siteCdSelect">
                                <option value="1" selected>1 (하프클럽)</option>
                                <option value="2">2 (보리보리)</option>
                            </select>
                        </div>

                        <div class="control-item">
                            <label for="sizeInput">조회 수:</label>
                            <input type="number" id="sizeInput" value="50" min="1" max="100" style="width:70px;">
                        </div>

                        <button type="button" class="btn-fetch" id="btnFetch">API 연동 조회</button>
                    </div>
                </div>

                <!-- meta-timestamps 뱃지 바 -->
                <div class="meta-timestamps">
                    <div class="meta-item">
                        <span class="meta-label">LLM 모델:</span>
                        <span class="meta-val meta-llm-badge" id="llmModelVal">openai / gpt-5.6-luna</span>
                    </div>
                    <div class="meta-item">
                        <span class="meta-label">LLM 토큰:</span>
                        <span class="meta-val token-usage-badge" id="llmTokenUsageVal">In: 7,517 / Out: 3,511 (Total: 11,028)</span>
                    </div>
                    <div class="meta-item">
                        <span class="meta-label">필터링 적용:</span>
                        <div class="filter-badges-group" id="filterBadgesGroup">
                            <span class="filter-badge" id="filterBrandBadge">브랜드: ON</span>
                            <span class="filter-badge" id="filterCategoryBadge">카테고리: OFF</span>
                            <span class="filter-badge" id="filterGenderBadge">성별: OFF</span>
                        </div>
                    </div>
                </div>
            </header>

            <!-- 대시보드 메인 바디 -->
            <div class="dashboard-scroll-body">
                <!-- AI 트렌드 가이드 카드 -->
                <section class="card" id="guideCard" style="display:none;">
                    <div class="card-header">
                        <h3>AI 트렌드 큐레이션 가이드</h3>
                        <div class="tags-group">
                            <span class="tag" id="tagCategory">카테고리: -</span>
                            <span class="tag" id="tagGender">성별: -</span>
                            <span class="tag" id="tagSeason">계절: -</span>
                        </div>
                    </div>
                    <div class="guide-text-body" id="guideTextBody">-</div>
                    <div id="brandsWrapper" style="margin-top:6px; font-size:12px; color:#64748b; font-weight:600;"></div>
                    <div id="keywordsWrapper" style="margin-top:4px; font-size:12px; color:#64748b; font-weight:600;"></div>
                </section>

                <!-- 메인 뷰 탭 3종 (상품 카드 뷰 / 데이터 테이블 뷰 / Raw JSON 뷰) -->
                <section>
                    <div class="view-tabs-header">
                        <button class="tab-btn active" id="tabBtnGrid" onclick="switchViewTab('grid')">상품 카드 뷰 (한 줄 5개)</button>
                        <button class="tab-btn" id="tabBtnTable" onclick="switchViewTab('table')">데이터 테이블 뷰</button>
                        <button class="tab-btn" id="tabBtnRaw" onclick="switchViewTab('raw')">Raw JSON 데이터 뷰</button>
                        <div style="margin-left:auto; align-self:center; font-size:0.8rem; color:#64748b;" id="resultCountInfo">총 0개</div>
                    </div>

                    <!-- 탭 1: 상품 카드 뷰 -->
                    <div class="tab-content active" id="tabContentGrid">
                        <div class="products-grid" id="productsGrid">
                            <div class="loading-overlay">데이터 로딩 중...</div>
                        </div>
                    </div>

                    <!-- 탭 2: 데이터 테이블 뷰 -->
                    <div class="tab-content" id="tabContentTable">
                        <div class="data-table-container" id="productsTableContainer">
                            <div class="loading-overlay">데이터 로딩 중...</div>
                        </div>
                    </div>

                    <!-- 탭 3: Raw JSON 데이터 뷰 (불필요 텍스트 완전 철거) -->
                    <div class="tab-content" id="tabContentRaw">
                        <pre class="raw-json-container" id="rawJsonContainer">로딩 중...</pre>
                    </div>
                </section>
            </div>
        </main>
    </div>

    <!-- 0.1초 비동기(fetch) SPA 애플리케이션 스크립트 -->
    <script>
        const allKeywords = {keywords_json_str};
        let currentKeyword = '';
        let currentRawData = null;

        document.addEventListener('DOMContentLoaded', () => {{
            initApp();
        }});

        function initApp() {{
            renderKeywordList(allKeywords);
            setupEventListeners();
            fetchKeywordTrend(currentKeyword);
        }}

        function setupEventListeners() {{
            // 키워드 실시간 검색
            const searchInput = document.getElementById('keywordSearchInput');
            if (searchInput) {{
                searchInput.addEventListener('input', (e) => {{
                    const q = e.target.value.trim().toLowerCase();
                    const filtered = allKeywords.filter(k => k.toLowerCase().includes(q));
                    renderKeywordList(filtered);
                }});
            }}

            // API 조회 버튼
            const btnFetch = document.getElementById('btnFetch');
            if (btnFetch) {{
                btnFetch.addEventListener('click', () => {{
                    fetchKeywordTrend(currentKeyword);
                }});
            }}
        }}

        function switchViewTab(tabName) {{
            document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));

            if (tabName === 'grid') {{
                document.getElementById('tabBtnGrid').classList.add('active');
                document.getElementById('tabContentGrid').classList.add('active');
            }} else if (tabName === 'table') {{
                document.getElementById('tabBtnTable').classList.add('active');
                document.getElementById('tabContentTable').classList.add('active');
            }} else if (tabName === 'raw') {{
                document.getElementById('tabBtnRaw').classList.add('active');
                document.getElementById('tabContentRaw').classList.add('active');
            }}
        }}

        function renderKeywordList(keywords) {{
            const listContainer = document.getElementById('keywordList');
            const badge = document.getElementById('keywordCountBadge');
            if (badge) badge.textContent = keywords.length;

            listContainer.innerHTML = '';
            keywords.forEach((kw, idx) => {{
                const origIdx = allKeywords.indexOf(kw) + 1;
                const li = document.createElement('li');
                li.className = `keyword-item ${{kw === currentKeyword ? 'active' : ''}}`;
                li.innerHTML = `<span>${{kw}}</span> <span style="font-size:0.75rem; opacity:0.6;">#${{origIdx}}</span>`;
                li.addEventListener('click', () => selectKeyword(kw));
                listContainer.appendChild(li);
            }});
        }}

        function selectKeyword(kw) {{
            currentKeyword = kw;
            document.querySelectorAll('.keyword-item').forEach(item => {{
                const txt = item.querySelector('span').textContent;
                if (txt === kw) item.classList.add('active');
                else item.classList.remove('active');
            }});
            document.getElementById('currentKeywordTitle').textContent = kw;
            fetchKeywordTrend(kw);
        }}

        async function fetchKeywordTrend(kw) {{
            const grid = document.getElementById('productsGrid');
            grid.innerHTML = '<div class="loading-overlay">0.1초 비동기 트렌드 API 요청 중...</div>';

            const siteCd = document.getElementById('siteCdSelect').value;
            const size = document.getElementById('sizeInput').value || 50;

            const apiUrl = `https://dev-api.halfclub.com/recommend/keyword-trend?siteCd=${{siteCd}}&size=${{size}}&keyword=${{encodeURIComponent(kw)}}`;

            try {{
                const resp = await fetch(apiUrl);
                if (!resp.ok) throw new Error('HTTP ' + resp.status);
                const data = await resp.json();
                currentRawData = data;

                renderMetaTimestamps(data);
                renderGuideInfo(data, kw);
                const products = extractProducts(data);
                
                renderProductsGrid(products);
                renderProductsTable(products);
                renderRawJson(data);
            }} catch (err) {{
                console.error(err);
                grid.innerHTML = `<div class="loading-overlay" style="color:#dc2626;">API 호출 실패: ${{err.message}}</div>`;
            }}
        }}

        function renderMetaTimestamps(data) {{
            if (data && data.llm_info) {{
                const info = data.llm_info;
                const modelVal = `${{info.llm_provider || 'openai'}} / ${{info.llm_model || 'gpt-5.6-luna'}}`;
                const reqT = typeof info.total_request_tokens === 'number' ? info.total_request_tokens : 0;
                const resT = typeof info.total_response_tokens === 'number' ? info.total_response_tokens : 0;
                const totT = reqT + resT;
                const tokenVal = `In: ${{reqT.toLocaleString()}} / Out: ${{resT.toLocaleString()}} (Total: ${{totT.toLocaleString()}})`;

                const brandSt = info.enable_brand_filter ? 'ON' : 'OFF';
                const catSt = info.enable_category_filter ? 'ON' : 'OFF';
                const genderSt = info.enable_gender_filter ? 'ON' : 'OFF';

                document.getElementById('llmModelVal').textContent = modelVal;
                document.getElementById('llmTokenUsageVal').textContent = tokenVal;
                document.getElementById('filterBrandBadge').textContent = `브랜드: ${{brandSt}}`;
                document.getElementById('filterCategoryBadge').textContent = `카테고리: ${{catSt}}`;
                document.getElementById('filterGenderBadge').textContent = `성별: ${{genderSt}}`;
            }}
        }}

        function extractProducts(resData) {{
            if (!resData) return [];
            if (Array.isArray(resData.products)) return resData.products;
            if (Array.isArray(resData.data)) return resData.data;
            if (resData.data && Array.isArray(resData.data.products)) return resData.data.products;
            return [];
        }}

        function renderGuideInfo(data, kw) {{
            const guideCard = document.getElementById('guideCard');
            const guideBody = document.getElementById('guideTextBody');
            const rawText = data.guide_text || data.guide_text_html;

            if (rawText) {{
                guideCard.style.display = 'block';
                const extKws = Array.isArray(data.extracted_keywords) ? data.extracted_keywords : [];
                guideBody.innerHTML = formatHighlightedGuideText(rawText, extKws, kw);

                document.getElementById('tagCategory').textContent = `카테고리: ${{data.extracted_category || '기본'}}`;
                document.getElementById('tagGender').textContent = `성별: ${{data.extracted_gender || '공용'}}`;
                
                const season = Array.isArray(data.extracted_season) ? data.extracted_season.join(', ') : (data.extracted_season || '사계절');
                document.getElementById('tagSeason').textContent = `계절: ${{season}}`;

                const extBrands = Array.isArray(data.extracted_brands) ? data.extracted_brands : [];
                const bWrapper = document.getElementById('brandsWrapper');
                if (extBrands.length > 0) {{
                    bWrapper.innerHTML = '추출 브랜드: ' + extBrands.map(b => `<span style="background:#ecfdf5; color:#059669; border:1px solid #a7f3d0; padding:2px 7px; border-radius:10px; font-size:11px; margin-right:4px;">${{b}}</span>`).join('');
                }} else {{
                    bWrapper.innerHTML = '';
                }}

                const kWrapper = document.getElementById('keywordsWrapper');
                if (extKws.length > 0) {{
                    kWrapper.innerHTML = '추출 키워드: ' + extKws.map(k => `<span style="background:#eff6ff; color:#2563eb; border:1px solid #bfdbfe; padding:2px 7px; border-radius:10px; font-size:11px; margin-right:4px;">${{k}}</span>`).join('');
                }} else {{
                    kWrapper.innerHTML = '';
                }}
            }} else {{
                guideCard.style.display = 'none';
            }}
        }}

        function formatHighlightedGuideText(text, extKws, mainKw) {{
            if (!text) return '';
            let kws = [];
            if (mainKw) kws.push(mainKw.trim());
            if (Array.isArray(extKws)) kws.push(...extKws.map(k => String(k).trim()));
            kws = [...new Set(kws.filter(k => k.length > 0))];
            if (kws.length === 0) return text;
            kws.sort((a, b) => b.length - a.length);
            const escaped = kws.map(k => k.replace(/[.*+?^${{}}()|[\\]\\\\]/g, '\\\\$&'));
            const pattern = new RegExp(`(${{escaped.join('|')}})`, 'gi');
            return text.replace(pattern, '<strong class="highlight-kw">$1</strong>');
        }}

        function renderProductsGrid(products) {{
            const grid = document.getElementById('productsGrid');
            const info = document.getElementById('resultCountInfo');
            info.textContent = `총 ${{products.length}}개`;

            if (products.length === 0) {{
                grid.innerHTML = '<div class="loading-overlay">조회된 상품이 없습니다.</div>';
                return;
            }}

            grid.innerHTML = '';
            products.forEach((item, idx) => {{
                let imgUrl = item.appPrdImgUrl || item.prdImg || '';
                if (imgUrl && typeof imgUrl === 'string' && !imgUrl.startsWith('http')) {{
                    imgUrl = `https://cdn2.halfclub.com/rimg/330x440/contain/${{imgUrl}}`;
                }}

                const badgesHtml = renderBadgesHtml(item);
                const brand = item.brandNm || '브랜드 없음';
                const prdNm = item.prdNm || '상품명 없음';

                const normPrc = item.normPrc || 0;
                const selPrc = item.selPrc || 0;
                const dcPrc = item.dcPrcPc || selPrc;
                const totRate = item.totRatePc || 0;

                let priceHtml = '';
                if (totRate > 0) {{
                    priceHtml += `<span class="price-rate">${{totRate}}%</span> `;
                }}
                priceHtml += `<span class="price-final">${{dcPrc.toLocaleString()}}원</span>`;
                if (normPrc > dcPrc) {{
                    priceHtml += ` <span class="price-origin">${{normPrc.toLocaleString()}}원</span>`;
                }}

                const star = item.reviewStar || 0;
                const reviewQty = item.reviewQty || 0;
                const reviewStr = reviewQty ? `평점 ${{star.toFixed(1)}} (${{reviewQty}})` : '리뷰 없음';

                const matchedKws = Array.isArray(item.matched_keywords) ? item.matched_keywords.join(', ') : '없음';
                const score = item.score || 0;

                const c1 = item.dpCtgrNm1 || '';
                const c2 = item.dpCtgrNm2 || '';
                const c3 = item.dpCtgrNm3 || '';
                const ctgrStr = [c1, c2, c3].filter(Boolean).join(' > ');

                const dtlUrl = item.appPrdDtlUrl || `https://dev.halfclub.com/product/${{item.prdNo}}`;

                const card = document.createElement('div');
                card.className = 'product-card';
                card.innerHTML = `
                    <div class="card-img-container">
                        <span class="rank-badge">#${{idx + 1}}</span>
                        <img src="${{imgUrl}}" alt="${{prdNm}}"/>
                    </div>
                    <div class="card-info">
                        ${{badgesHtml}}
                        <div class="card-brand">${{brand}}</div>
                        <div class="card-title" title="${{prdNm}}">${{prdNm}}</div>
                        <div class="price-row">${{priceHtml}}</div>
                        <div class="matched-line">매칭: ${{matchedKws}}</div>
                        <div class="meta-line">${{reviewStr}} | 점수 ${{score}}</div>
                        <div class="meta-line" style="white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">${{ctgrStr}}</div>
                        <a href="${{dtlUrl}}" target="_blank" class="btn-dtl">상품 상세보기</a>
                    </div>
                `;
                grid.appendChild(card);
            }});
        }}

        function renderProductsTable(products) {{
            const container = document.getElementById('productsTableContainer');
            if (products.length === 0) {{
                container.innerHTML = '<div class="loading-overlay">표시할 테이블 데이터가 없습니다.</div>';
                return;
            }}

            let rowsHtml = products.map((item, idx) => {{
                const brand = item.brandNm || '-';
                const prdNm = item.prdNm || '-';
                const prdNo = item.prdNo || '-';
                const selPrc = item.selPrc || item.dcPrcPc || 0;
                const normPrc = item.normPrc || 0;
                const totRate = item.totRatePc || 0;
                const matchedKws = Array.isArray(item.matched_keywords) ? item.matched_keywords.join(', ') : '-';
                const star = item.reviewStar ? item.reviewStar.toFixed(1) : '-';
                const reviewQty = item.reviewQty || 0;
                const c1 = item.dpCtgrNm1 || '';
                const c2 = item.dpCtgrNm2 || '';
                const ctgrStr = [c1, c2].filter(Boolean).join(' > ') || '-';
                const dtlUrl = item.appPrdDtlUrl || `https://dev.halfclub.com/product/${{prdNo}}`;

                return `
                    <tr>
                        <td><b>#${{idx + 1}}</b></td>
                        <td>${{prdNo}}</td>
                        <td><span style="color:#2563eb; font-weight:700;">${{brand}}</span></td>
                        <td><a href="${{dtlUrl}}" target="_blank" style="color:#0f172a; text-decoration:none; font-weight:600;">${{prdNm}}</a></td>
                        <td><b style="color:#0f172a;">${{selPrc.toLocaleString()}}원</b></td>
                        <td><span style="color:#94a3b8; text-decoration:line-through;">${{normPrc.toLocaleString()}}원</span></td>
                        <td><b style="color:#dc2626;">${{totRate}}%</b></td>
                        <td><span style="color:#2563eb; font-weight:600;">${{matchedKws}}</span></td>
                        <td>${{star}} (${{reviewQty}})</td>
                        <td>${{ctgrStr}}</td>
                    </tr>
                `;
            }}).join('');

            container.innerHTML = `
                <table class="custom-data-table">
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
                    <tbody>
                        ${{rowsHtml}}
                    </tbody>
                </table>
            `;
        }}

        function renderRawJson(data) {{
            const container = document.getElementById('rawJsonContainer');
            if (!data) {{
                container.textContent = 'JSON 데이터가 없습니다.';
                return;
            }}
            container.textContent = JSON.stringify(data, null, 2);
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
components.html(html_content, height=940, scrolling=True)
