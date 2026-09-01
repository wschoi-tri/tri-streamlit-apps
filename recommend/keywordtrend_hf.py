import os
import re
import json
import urllib.parse
import urllib.request
import streamlit as st

# 1. 페이지 기본 설정 (와이드 레이아웃)
st.set_page_config(
    page_title="Halfclub Trend AI Curation Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. 전역 CSS 스타일 (고유의 세련된 UI 1:1 완벽 적용)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;600;700;800&family=Outfit:wght@400;600;700;800&display=swap');
    
    * {
        font-family: 'Noto Sans KR', -apple-system, BlinkMacSystemFont, sans-serif;
        box-sizing: border-box;
    }
    
    .block-container {
        padding-top: 1.2rem !important;
        padding-bottom: 2rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        max-width: 100% !important;
    }
    #MainMenu, footer, header {visibility: hidden;}

    /* 좌측 사이드바 스타일링 */
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e2e8f0;
        padding-top: 1rem;
    }
    [data-testid="stSidebar"] .block-container {
        padding: 0 1rem !important;
    }

    .sidebar-header-box {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 6px 4px 12px 4px;
        border-bottom: 1px solid #e2e8f0;
        margin-bottom: 12px;
    }
    .sidebar-header-title {
        font-size: 1.05rem;
        font-weight: 800;
        color: #0f172a;
    }
    .sidebar-count-badge {
        font-size: 0.75rem;
        background: #eff6ff;
        color: #2563eb;
        font-weight: 700;
        padding: 2px 8px;
        border-radius: 10px;
    }

    /* 키워드 목록 A 링크 (순번 뱃지 & 호버 & 활성화 스타일) */
    .kw-link-list {
        display: flex;
        flex-direction: column;
        gap: 2px;
        max-height: calc(100vh - 160px);
        overflow-y: auto;
        padding-right: 4px;
    }
    .kw-link-item {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 8px 12px;
        font-size: 0.88rem;
        color: #334155;
        text-decoration: none;
        border-radius: 6px;
        transition: background 0.12s ease, color 0.12s ease;
    }
    .kw-link-item:hover {
        background-color: #f1f5f9;
        color: #0f172a;
    }
    .kw-link-item.active {
        background-color: #eff6ff;
        color: #2563eb;
        font-weight: 800;
        border-left: 3px solid #2563eb;
    }
    .kw-rank-num {
        font-size: 0.75rem;
        opacity: 0.6;
        font-weight: normal;
    }
    .kw-link-item.active .kw-rank-num {
        opacity: 0.9;
        font-weight: 700;
    }

    /* 상단 메타 뱃지 바 */
    .meta-badges-bar {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 10px 16px;
        margin-bottom: 18px;
        display: flex;
        align-items: center;
        gap: 18px;
        font-size: 0.83rem;
        font-weight: 600;
        color: #64748b;
        flex-wrap: wrap;
    }
    .meta-chip-blue {
        background: #eff6ff;
        border: 1px solid #bfdbfe;
        color: #2563eb;
        font-weight: 700;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.82rem;
    }
    .meta-chip-pink {
        background: #fdf2f8;
        border: 1px solid #fbcfe8;
        color: #db2777;
        font-weight: 700;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.82rem;
    }
    .meta-chip-white {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        color: #334155;
        font-weight: 700;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.8rem;
    }
    .meta-chip-gray {
        background: #f1f5f9;
        border: 1px solid #cbd5e1;
        color: #334155;
        font-weight: 700;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.82rem;
    }

    /* 트렌드 가이드 카드 */
    .guide-card-box {
        background-color: #ffffff;
        border: 1px solid #cbd5e1;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        margin-bottom: 22px;
    }
    .guide-card-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 12px;
    }
    .guide-title {
        font-size: 1.05rem;
        font-weight: 800;
        color: #0f172a;
    }
    .guide-text {
        font-size: 0.93rem;
        line-height: 1.65;
        color: #334155;
        margin-bottom: 14px;
    }
    .highlight-kw {
        background-color: #fef08a;
        color: #854d0e;
        padding: 2px 5px;
        border-radius: 4px;
        font-weight: 700;
    }

    /* 뱃지 칩 */
    .badge-chip-item {
        font-size: 10px;
        padding: 2px 6px;
        border-radius: 4px;
        font-weight: 600;
        display: inline-block;
        text-decoration: none;
    }
    .badge-blue { background: #eff6ff; color: #2563eb; }
    .badge-red { background: #fef2f2; color: #dc2626; }
    .badge-gray { background: #f1f5f9; color: #475569; }
    .badge-brand { background: #ecfdf5; color: #059669; border: 1px solid #a7f3d0; }
    .badge-media { background: #e0f2fe; color: #0369a1; font-weight: 700; }

    /* 5열 그리드 카드 */
    .product-card {
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        overflow: hidden;
        background: #ffffff;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        height: 100%;
        transition: transform 0.15s ease, box-shadow 0.15s ease;
        margin-bottom: 16px;
    }
    .product-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }
    .product-img-wrap {
        position: relative;
        width: 100%;
        height: 210px;
        background-color: #f1f5f9;
    }
    .product-img {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }
    .rank-badge {
        position: absolute;
        top: 8px;
        left: 8px;
        background-color: #0f172a;
        color: #ffffff;
        font-size: 11px;
        font-weight: 800;
        padding: 2px 7px;
        border-radius: 4px;
    }
    .product-info {
        padding: 12px;
    }
    .brand-name {
        font-size: 0.76rem;
        color: #64748b;
        font-weight: 700;
        margin-bottom: 2px;
    }
    .product-name {
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
    }
    .price-wrap {
        display: flex;
        align-items: baseline;
        gap: 4px;
        margin-bottom: 6px;
    }
    .sale-price {
        font-size: 0.95rem;
        font-weight: 800;
        color: #0f172a;
    }
    .normal-price {
        font-size: 0.75rem;
        color: #94a3b8;
        text-decoration: line-through;
    }
    .discount-rate {
        font-size: 0.75rem;
        color: #ef4444;
        font-weight: 700;
    }
    .badge-chip-container {
        display: flex;
        flex-wrap: wrap;
        gap: 4px;
        margin-top: 6px;
    }

    /* 테이블 스타일 */
    .data-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.84rem;
    }
    .data-table th {
        background-color: #f8fafc;
        color: #475569;
        font-weight: 700;
        padding: 10px 12px;
        border-bottom: 1px solid #e2e8f0;
        text-align: left;
    }
    .data-table td {
        padding: 10px 12px;
        border-bottom: 1px solid #f1f5f9;
        color: #334155;
    }
    .data-table tr:hover {
        background-color: #f8fafc;
    }
</style>
""", unsafe_allow_html=True)

# 3. 타겟 키워드 리스트 로드
@st.cache_data(show_spinner=False)
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

# 4. URL 쿼리 파라미터 읽기 (한글 디코딩 지원)
qp = st.query_params
raw_kw = qp.get("keyword", "")
if raw_kw:
    raw_kw = urllib.parse.unquote(str(raw_kw)).strip()

if raw_kw and raw_kw in keywords_list:
    current_kw = raw_kw
else:
    current_kw = keywords_list[0] if keywords_list else "가디건"

url_site = qp.get("siteCd", "1")
if url_site not in ["1", "2"]:
    url_site = "1"

url_size = int(qp.get("size", "50")) if qp.get("size", "50").isdigit() else 50

# 5. API 캐시 호출 함수
@st.cache_data(ttl=600, show_spinner=False)
def fetch_api_data(kw: str, site_cd: str, size: int):
    rec_url = f"https://dev-api.halfclub.com/recommend/keyword-trend?llmInfo=true&siteCd={site_cd}&size={size}&keyword={urllib.parse.quote(kw)}"
    brand_url = f"https://hapix.halfclub.com/searches/v2/product/brand-filter/?keyword={urllib.parse.quote(kw)}&isPopular=true&size=100&device=pc"

    rec_data = {}
    brand_filter_list = []

    try:
        req = urllib.request.Request(rec_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            if resp.status == 200:
                rec_data = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        rec_data = {"error": str(e)}

    try:
        req_b = urllib.request.Request(brand_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req_b, timeout=6) as resp_b:
            if resp_b.status == 200:
                b_json = json.loads(resp_b.read().decode("utf-8"))
                brand_filter_list = b_json.get("data", {}).get("aggregations", {}).get("brand", [])
    except Exception:
        pass

    return rec_data, brand_filter_list, rec_url

# 6. 좌측 사이드바 구성 (순번 뱃지 & 실시간 검색 & URL 네비게이션)
st.sidebar.markdown(f"""
<div class="sidebar-header-box">
    <span class="sidebar-header-title">타겟 키워드 목록</span>
    <span class="sidebar-count-badge">{len(keywords_list)}</span>
</div>
""", unsafe_allow_html=True)

kw_search = st.sidebar.text_input("키워드 검색", placeholder="키워드 검색...", label_visibility="collapsed")
filtered_kws = [k for k in keywords_list if kw_search.strip().lower() in k.lower()] if kw_search.strip() else keywords_list

link_items = []
for k in filtered_kws:
    orig_idx = keywords_list.index(k) + 1
    is_active = "active" if k == current_kw else ""
    k_url = f"/?keyword={urllib.parse.quote(k)}&siteCd={url_site}&size={url_size}"
    link_items.append(f'<a href="{k_url}" target="_self" class="kw-link-item {is_active}"><span>{k}</span><span class="kw-rank-num">#{orig_idx}</span></a>')

st.sidebar.markdown(f'<div class="kw-link-list">{"".join(link_items)}</div>', unsafe_allow_html=True)

# 7. 우측 상단 헤더 바
col_title, col_ctrl = st.columns([6, 4])
with col_title:
    st.markdown(f"""
    <div style="display:flex; align-items:center; gap:10px; padding:4px 0;">
        <h1 style="font-size:1.4rem; font-weight:800; color:#0f172a; margin:0; display:inline-block;">{current_kw}</h1>
        <span style="background:#eff6ff; border:1px solid #dbeafe; color:#1d4ed8; font-size:12px; font-weight:700; padding:3px 12px; border-radius:9999px;">키워드 트렌드 추천</span>
    </div>
    """, unsafe_allow_html=True)

with col_ctrl:
    c_site, c_size, c_btn = st.columns([4, 3, 3])
    with c_site:
        site_choice = st.selectbox("사이트", ["1 (하프클럽)", "2 (보리보리)"], index=0 if url_site == "1" else 1, label_visibility="collapsed")
        site_cd = "1" if "1" in site_choice else "2"
    with c_size:
        req_size = st.number_input("조회 수", min_value=1, max_value=200, value=url_size, step=10, label_visibility="collapsed")
    with c_btn:
        btn_refresh = st.button("API 연동 조회", type="primary", use_container_width=True)

if btn_refresh:
    st.cache_data.clear()

# 8. API 데이터 로드
data, brand_filter_list, current_api_url = fetch_api_data(current_kw, site_cd, req_size)

if "error" in data:
    st.error(f"API 호출 실패: {data.get('error')}")
    st.stop()

# 9. 메타 정보 추출
llm_info = data.get("llm_info", {})
reason = data.get("noshow_reason") or llm_info.get("noshow_reason") or ""

provider = llm_info.get("llm_provider") or data.get("llm_provider") or "-"
model = llm_info.get("llm_model") or data.get("llm_model") or "-"
model_str = f"{provider} / {model}" if provider != "-" or model != "-" else "-"

stage1 = llm_info.get("stage1_guide_generation", {})
stage2 = llm_info.get("stage2_product_selection", {})
usage1 = stage1.get("prompt_info", {}).get("token_usage", {}) or llm_info.get("stage1_token_usage", {})
usage2 = stage2.get("prompt_info", {}).get("token_usage", {}) or llm_info.get("stage2_token_usage", {})

req_tokens = (usage1.get("request_tokens", 0) or 0) + (usage2.get("request_tokens", 0) or 0) or (llm_info.get("total_request_tokens", 0) or 0)
res_tokens = (usage1.get("response_tokens", 0) or 0) + (usage2.get("response_tokens", 0) or 0) or (llm_info.get("total_response_tokens", 0) or 0)
cached_tokens = (usage1.get("cached_tokens", 0) or 0) + (usage2.get("cached_tokens", 0) or 0)
tot_tokens = (usage1.get("total_tokens", 0) or 0) + (usage2.get("total_tokens", 0) or 0) or (req_tokens + res_tokens)

token_str = f"In: {req_tokens:,} / Out: {res_tokens:,} / Cached: {cached_tokens:,} (Total: {tot_tokens:,})" if tot_tokens > 0 or req_tokens > 0 else "-"

b_brand = "ON" if (data.get("enable_brand_filter") if data.get("enable_brand_filter") is not None else llm_info.get("enable_brand_filter")) is not False else "OFF"
b_cat = "ON" if (data.get("enable_category_filter") if data.get("enable_category_filter") is not None else llm_info.get("enable_category_filter")) is not False else "OFF"
b_gen = "ON" if (data.get("enable_gender_filter") if data.get("enable_gender_filter") is not None else llm_info.get("enable_gender_filter")) is not False else "OFF"

create_dt = data.get("create_dt") or llm_info.get("create_dt") or "-"
update_dt = data.get("update_dt") or llm_info.get("update_dt") or "-"

# 10. 상단 메타 뱃지 바 렌더링
st.markdown(f"""
<div class="meta-badges-bar">
    <div style="display:flex; align-items:center; gap:6px;">
        <span>LLM 모델:</span>
        <span class="meta-chip-blue">{model_str}</span>
    </div>
    <div style="display:flex; align-items:center; gap:6px;">
        <span>LLM 토큰:</span>
        <span class="meta-chip-pink">{token_str}</span>
    </div>
    <div style="display:flex; align-items:center; gap:6px;">
        <span>필터링 적용:</span>
        <span style="display:flex; gap:6px;">
            <span class="meta-chip-white">브랜드: {b_brand}</span>
            <span class="meta-chip-white">카테고리: {b_cat}</span>
            <span class="meta-chip-white">성별: {b_gen}</span>
        </span>
    </div>
    <div style="display:flex; align-items:center; gap:6px;">
        <span>생성일시:</span>
        <span class="meta-chip-gray">{create_dt}</span>
    </div>
    <div style="display:flex; align-items:center; gap:6px;">
        <span>갱신일시:</span>
        <span class="meta-chip-gray">{update_dt}</span>
    </div>
</div>
""", unsafe_allow_html=True)

# 11. 가이드 카드 및 브랜드/키워드/기사 정보
guide_text_raw = data.get("guide_text") or data.get("guide_text_html") or "가이드 문구가 없습니다."
ext_kws = data.get("extracted_keywords", [])
ext_brands = data.get("extracted_brands", [])
cat_tag = data.get("extracted_category") or "기본"
gen_tag = data.get("extracted_gender") or "공용"
season_val = data.get("extracted_season", ["사계절"])
season_str = ", ".join(season_val) if isinstance(season_val, list) else str(season_val)

highlighted_guide = guide_text_raw
if ext_kws:
    sorted_kws = sorted(ext_kws + [current_kw], key=lambda x: len(x), reverse=True)
    for kw_item in sorted_kws:
        if kw_item and kw_item.strip():
            clean_item = re.sub(r'\s+', '', kw_item.strip())
            if clean_item:
                escaped_pat = r'\s*'.join(re.escape(ch) for ch in clean_item)
                pattern = rf'({escaped_pat})'
                highlighted_guide = re.sub(pattern, r'<strong class="highlight-kw">\1</strong>', highlighted_guide, flags=re.IGNORECASE)

if reason:
    highlighted_guide = f"""
    <div style="background:#fff1f2; border:1px solid #fecdd3; color:#9f1239; padding:14px 18px; border-radius:8px; line-height:1.6; margin-bottom:12px;">
        <div style="font-weight:700; margin-bottom:4px; color:#be123c;">[미표시 사유]</div>
        <div style="font-size:0.92rem; color:#be123c;">{reason}</div>
    </div>
    """ + highlighted_guide

products = data.get("recommended_products") or data.get("products") or data.get("items") or []
brand_map = {}
for b in brand_filter_list:
    b_nm = str(b.get("name") or b.get("brandNm") or b.get("key") or "").strip()
    b_cd = str(b.get("code") or b.get("brandCd") or b.get("brdCd") or "").strip()
    if b_nm and b_cd:
        brand_map[b_nm.lower()] = b_cd
        brand_map[b_nm] = b_cd
for p in products:
    b_nm = str(p.get("brandNm") or p.get("brdNm") or p.get("brand") or "").strip()
    b_cd = str(p.get("brandCd") or p.get("brdCd") or p.get("brandCode") or "").strip()
    if b_nm and b_cd:
        brand_map[b_nm.lower()] = b_cd
        brand_map[b_nm] = b_cd

brand_chips_html = ""
if ext_brands:
    chips = []
    for b in ext_brands:
        b_clean = str(b.get("name") if isinstance(b, dict) else b).strip()
        b_code = (b.get("code") if isinstance(b, dict) else None) or brand_map.get(b_clean.lower()) or brand_map.get(b_clean)
        search_url = f"https://halfclub.com/search/{urllib.parse.quote(current_kw)}?brandCd={urllib.parse.quote(b_code)}" if b_code else f"https://halfclub.com/search/{urllib.parse.quote(current_kw + ' ' + b_clean)}"
        title_txt = f"하프클럽 브랜드 필터 '{b_clean}' ({b_code}) 적용 검색" if b_code else f"하프클럽에서 '{current_kw} {b_clean}' 검색"
        chips.append(f'<a href="{search_url}" target="_blank" rel="noopener noreferrer" class="badge-chip-item badge-brand" style="text-decoration:none;" title="{title_txt}">{b_clean} ↗</a>')
    brand_chips_html = f'<div style="display:flex; align-items:center; gap:8px; flex-wrap:wrap; margin-top:8px;"><span style="flex-shrink:0; font-weight:700; font-size:0.8rem; color:#64748b;">추출 브랜드:</span><div style="display:flex; align-items:center; gap:6px; flex-wrap:wrap;">{"".join(chips)}</div></div>'

kw_chips_html = ""
if ext_kws:
    k_chips = []
    for k in ext_kws:
        s_url = f"https://halfclub.com/search/{urllib.parse.quote(current_kw + ' ' + k)}"
        k_chips.append(f'<a href="{s_url}" target="_blank" rel="noopener noreferrer" class="badge-chip-item badge-blue" style="text-decoration:none;" title="하프클럽에서 \'{current_kw} {k}\' 검색">{k} ↗</a>')
    kw_chips_html = f'<div style="display:flex; align-items:center; gap:8px; flex-wrap:wrap; margin-top:6px;"><span style="flex-shrink:0; font-weight:700; font-size:0.8rem; color:#64748b;">추출 키워드:</span><div style="display:flex; align-items:center; gap:6px; flex-wrap:wrap;">{"".join(k_chips)}</div></div>'

articles = data.get("keyword_articles") or llm_info.get("keyword_articles") or []
articles_html = ""
if articles:
    art_items = []
    for art in articles:
        link_url = art.get("link") or art.get("url") or "#"
        source_nm = art.get("source") or art.get("media") or "뉴스"
        title_txt = art.get("title") or art.get("text") or "제목 없음"
        pub_dt = art.get("publish_dt") or art.get("published_date") or art.get("date") or ""
        has_link = link_url and link_url != "#"
        art_items.append(f"""
        <div style="background:#f8fafc; padding:8px 12px; border-radius:6px; border:1px solid #e2e8f0; display:flex; align-items:center; justify-content:space-between; font-size:0.8rem; margin-bottom:6px;">
            <div style="display:flex; align-items:center; gap:8px; overflow:hidden;">
                <a href="{link_url}" {'target="_blank" rel="noopener noreferrer"' if has_link else ''} style="color:#0f172a; text-decoration:none; font-weight:600; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;" title="{title_txt}">{title_txt} <span class="badge-chip-item badge-media">{source_nm}</span></a>
            </div>
            <div style="display:flex; align-items:center; gap:8px; flex-shrink:0; font-size:0.75rem; color:#64748b;">
                {'<span>' + pub_dt + '</span>' if pub_dt else ''}
                {'<a href="' + link_url + '" target="_blank" rel="noopener noreferrer" style="color:#2563eb; text-decoration:underline; font-weight:600;">원문보기</a>' if has_link else ''}
            </div>
        </div>
        """)
    articles_html = f"""
    <div style="margin-top:14px; padding-top:12px; border-top:1px solid #e2e8f0;">
        <div style="font-size:0.8rem; font-weight:700; color:#475569; margin-bottom:8px; display:flex; align-items:center; justify-content:space-between;">
            <span>참고 뉴스 기사 목록</span>
            <span style="font-size:0.72rem; color:#94a3b8; font-weight:normal;">원문 클릭 이동</span>
        </div>
        <div>{"".join(art_items)}</div>
    </div>
    """

st.markdown(f"""
<div class="guide-card-box">
    <div class="guide-card-header">
        <div class="guide-title">AI 트렌드 큐레이션 가이드</div>
        <div style="display:flex; gap:6px;">
            <span class="badge-chip-item badge-gray">카테고리: {cat_tag}</span>
            <span class="badge-chip-item badge-gray">성별: {gen_tag}</span>
            <span class="badge-chip-item badge-gray">계절: {season_str}</span>
        </div>
    </div>
    <div class="guide-text">{highlighted_guide}</div>
    {brand_chips_html}
    {kw_chips_html}
    {articles_html}
</div>
""", unsafe_allow_html=True)

# 12. 4대 뷰 탭 구성
tab_grid, tab_table, tab_raw, tab_prompt = st.tabs([
    "추천 상품",
    "추천 상품 데이터 확인",
    "API JSON 데이터 확인",
    "LLM 프롬프트"
])

with tab_grid:
    if not products:
        st.info("추천 상품 데이터가 없습니다.")
    else:
        for row_start in range(0, len(products), 5):
            cols = st.columns(5)
            for col_idx in range(5):
                prod_idx = row_start + col_idx
                if prod_idx < len(products):
                    p = products[prod_idx]
                    rank = prod_idx + 1
                    prd_no = p.get("prdNo") or p.get("product_no") or p.get("id") or ""
                    prd_url = p.get("prd_url") or (f"https://halfclub.com/product/{prd_no}" if prd_no else "#")
                    name = p.get("prdNm") or p.get("name") or "상품명 없음"
                    brand = p.get("brandNm") or p.get("brdNm") or p.get("brand") or "브랜드"
                    sale_prc = p.get("dcPrcApp") or p.get("selPrc") or p.get("salePrc") or p.get("price") or 0
                    norm_prc = p.get("normPrc") or p.get("nrmPrc") or 0
                    disc_rt = p.get("totRateApp") or p.get("discRt") or 0
                    rating = p.get("reviewStar") or p.get("avgPoint") or 0.0
                    reviews = p.get("reviewQty") or p.get("revCnt") or 0
                    matched_kws = p.get("matched_keywords", [])

                    img_url = p.get("appPrdImgUrl") or p.get("prdImg") or ""
                    if img_url and not img_url.startswith("http"):
                        img_url = f"https://cdn2.halfclub.com/rimg/330x440/contain/{img_url}"

                    kw_chips_card = "".join([
                        f'<a href="https://halfclub.com/search/{urllib.parse.quote(current_kw + " " + k)}" target="_blank" rel="noopener noreferrer" class="badge-chip-item badge-blue" style="text-decoration:none;">{k} ↗</a>'
                        for k in matched_kws
                    ])

                    badge_items = []
                    icn_nms = p.get("icnNms", [])
                    if not icn_nms and p.get("icnNm"):
                        icn_nms = p.get("icnNm").split("@")
                    for icn in icn_nms:
                        clean_icn = str(icn).strip()
                        if clean_icn:
                            cls = "badge-blue" if "무료배송" in clean_icn else ("badge-red" if "온리" in clean_icn or "단독" in clean_icn else "badge-gray")
                            badge_items.append(f'<span class="badge-chip-item {cls}">{clean_icn}</span>')

                    with cols[col_idx]:
                        st.markdown(f"""
                        <div class="product-card">
                            <div>
                                <a href="{prd_url}" target="_blank" rel="noopener noreferrer" style="display:block; text-decoration:none; color:inherit;">
                                    <div class="product-img-wrap">
                                        <img src="{img_url}" class="product-img" alt="{name}"/>
                                        <span class="rank-badge">#{rank}</span>
                                    </div>
                                    <div class="product-info">
                                        <div class="brand-name">{brand}</div>
                                        <div class="product-name" title="{name}">{name}</div>
                                        <div class="price-wrap">
                                            <span class="sale-price">{sale_prc:,}원</span>
                                            {'<span class="normal-price">' + f'{norm_prc:,}원' + '</span>' if norm_prc > sale_prc else ''}
                                            {'<span class="discount-rate">' + f'{disc_rt}%' + '</span>' if disc_rt > 0 else ''}
                                        </div>
                                        <div style="font-size:0.72rem; color:#64748b;">평점 {rating} ({reviews}개 리뷰)</div>
                                    </div>
                                </a>
                            </div>
                            <div style="padding:0 12px 12px 12px;">
                                <div class="badge-chip-container"><span class="badge-chip-item" style="color:#64748b;">매칭:</span>{kw_chips_card}</div>
                                <div class="badge-chip-container">{' '.join(badge_items)}</div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

with tab_table:
    if not products:
        st.info("추천 상품 데이터가 없습니다.")
    else:
        table_rows = []
        for idx, prd in enumerate(products):
            rank = idx + 1
            p_no = prd.get("prdNo") or prd.get("product_no") or prd.get("id") or "-"
            p_url = prd.get("prd_url") or (f"https://halfclub.com/product/{p_no}" if p_no != "-" else "#")
            brand = prd.get("brandNm") or prd.get("brdNm") or prd.get("brand") or "-"
            name = prd.get("prdNm") or prd.get("name") or "-"
            s_prc = prd.get("dcPrcApp") or prd.get("selPrc") or prd.get("salePrc") or prd.get("price") or 0
            n_prc = prd.get("normPrc") or prd.get("nrmPrc") or 0
            d_rt = prd.get("totRateApp") or prd.get("discRt") or 0
            rating = prd.get("reviewStar") or prd.get("avgPoint") or 0.0
            revs = prd.get("reviewQty") or prd.get("revCnt") or 0
            cat_name = prd.get("dpCtgrNm2") or prd.get("dpCtgrNm1") or prd.get("catNm") or "-"

            mk_links = ", ".join([
                f'<a href="https://halfclub.com/search/{urllib.parse.quote(current_kw + " " + k)}" target="_blank" rel="noopener noreferrer" style="color:#2563eb; text-decoration:none; font-weight:600;">{k}</a>'
                for k in prd.get("matched_keywords", [])
            ]) or "-"

            table_rows.append(f"""
            <tr>
                <td style="font-weight:700;">#{rank}</td>
                <td><a href="{p_url}" target="_blank" rel="noopener noreferrer" style="color:#2563eb; text-decoration:none; font-weight:700;">{p_no} ↗</a></td>
                <td style="font-weight:600;">{brand}</td>
                <td><a href="{p_url}" target="_blank" rel="noopener noreferrer" style="color:#0f172a; text-decoration:none;">{name}</a></td>
                <td style="font-weight:700; color:#0f172a;">{s_prc:,}원</td>
                <td style="color:#94a3b8; text-decoration:line-through;">{f'{n_prc:,}원' if n_prc else '-'}</td>
                <td style="color:#ef4444; font-weight:700;">{f'{d_rt}%' if d_rt else '-'}</td>
                <td>{mk_links}</td>
                <td>{rating} ({revs})</td>
                <td>{cat_name}</td>
            </tr>
            """)

        st.markdown(f"""
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
            <tbody>{"".join(table_rows)}</tbody>
        </table>
        """, unsafe_allow_html=True)

with tab_raw:
    st.markdown(f"""
    <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:8px; padding:12px 16px; margin-bottom:16px; display:flex; align-items:center; justify-content:space-between;">
        <div style="display:flex; align-items:center; gap:10px; overflow:hidden;">
            <span style="background:#2563eb; color:#ffffff; font-size:11px; font-weight:800; padding:3px 8px; border-radius:4px;">GET</span>
            <span style="font-family:monospace; font-size:0.85rem; color:#2563eb; font-weight:700; word-break:break-all;">{current_api_url}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.json(data)

with tab_prompt:
    st.markdown("### STAGE 1 : 스타일 트렌드 가이드 작성 프롬프트 & LLM 산출")
    p1_sys = stage1.get("prompt_info", {}).get("system_prompt") or ""
    p1_user = stage1.get("prompt_info", {}).get("user_prompt") or ""
    p1_res = stage1.get("guide_result") or stage1.get("prompt_info", {}).get("raw_response") or ""

    if p1_sys:
        st.markdown("**1단계 System Prompt**")
        st.code(p1_sys if isinstance(p1_sys, str) else json.dumps(p1_sys, ensure_ascii=False, indent=2), language="markdown")
    if p1_user:
        st.markdown("**1단계 User Prompt (실 데이터)**")
        st.code(p1_user if isinstance(p1_user, str) else json.dumps(p1_user, ensure_ascii=False, indent=2), language="markdown")
    if p1_res:
        st.markdown("**1단계 LLM 가이드 생성 결과 JSON**")
        st.code(p1_res if isinstance(p1_res, str) else json.dumps(p1_res, ensure_ascii=False, indent=2), language="json")

    st.markdown("---")
    st.markdown("### STAGE 2 : 상품 큐레이션 및 정렬 프롬프트 & LLM 산출")
    p2_sys = stage2.get("prompt_info", {}).get("system_prompt") or ""
    p2_user = stage2.get("prompt_info", {}).get("user_prompt") or ""
    p2_res = stage2.get("prompt_info", {}).get("raw_response") or stage2.get("llm_response") or ""

    if p2_sys:
        st.markdown("**2단계 System Prompt**")
        st.code(p2_sys if isinstance(p2_sys, str) else json.dumps(p2_sys, ensure_ascii=False, indent=2), language="markdown")
    if p2_user:
        st.markdown("**2단계 User Prompt (실 데이터)**")
        st.code(p2_user if isinstance(p2_user, str) else json.dumps(p2_user, ensure_ascii=False, indent=2), language="markdown")
    if p2_res:
        st.markdown("**2단계 LLM 큐레이션 결과 JSON**")
        st.code(p2_res if isinstance(p2_res, str) else json.dumps(p2_res, ensure_ascii=False, indent=2), language="json")
