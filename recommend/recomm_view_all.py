import streamlit as st
import requests
from pymilvus import connections, Collection

# 페이지 설정
st.set_page_config(
    page_title="상품 추천 서비스",
    page_icon="🛍️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 커스텀 CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
        color: white !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }
    .main-header h1 {
        margin: 0;
        font-size: 2.5rem;
        font-weight: 700;
        color: white !important;
    }
    .main-header p {
        margin: 0.5rem 0 0 0;
        font-size: 1.1rem;
        opacity: 0.9;
        color: white !important;
    }
    .section-card {
        background: rgba(255, 255, 255, 0.05);
        color: inherit;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        margin-bottom: 1.5rem;
        border-left: 4px solid #3498db;
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
    }
    .section-card h3 {
        color: #3498db !important;
        margin-top: 0;
    }
    .section-card p {
        color: inherit !important;
        opacity: 0.8;
    }
    .stButton > button {
        border-radius: 8px;
        border: none;
        background: linear-gradient(135deg, #3498db 0%, #2980b9 100%) !important;
        color: white !important;
        font-weight: 600;
        transition: all 0.3s ease;
        margin-top: 27px !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(52, 152, 219, 0.3);
    }
</style>
""", unsafe_allow_html=True)

# 메인 헤더
st.markdown("""
<div class="main-header">
    <h1>🛍️ 상품 추천 서비스</h1>
    <p>머신러닝 기반 상품 추천 시스템</p>
</div>
""", unsafe_allow_html=True)

# URL 파라미터 처리
query_params = st.query_params
url_site = query_params.get("siteCd", "1")
url_type = query_params.get("mlType", "")
url_prd = query_params.get("prdNo", "")
url_k = query_params.get("k", "")

# 기본 사이트 설정
if "siteCd" not in query_params:
    st.query_params["siteCd"] = "1"



col1, col2 = st.columns([3, 1])
with col1:
    site_cd = st.selectbox("사이트 선택", options=[1, 2], format_func=lambda x: "🛍️ 하프클럽" if x == 1 else "🌾 보리보리", index=int(url_site)-1 if url_site in ["1", "2"] else 0)
with col2:
    if st.button("🔄 초기화", type="secondary", use_container_width=True):
        # 세션 상태 초기화
        st.session_state.prd_no_list = set()
        st.session_state.prd_no = ""
        st.session_state.prd_nm = ""
        st.session_state.gender = ""
        st.session_state.age = ""
        st.session_state.type = ""
        st.session_state.type_nm = ""
        st.session_state.show_type = ""
        st.session_state.show_prd = []
        if 'last_api_url' in st.session_state:
            del st.session_state.last_api_url
        if 'last_api_response' in st.session_state:
            del st.session_state.last_api_response
        # 모든 URL 파라미터 초기화
        st.query_params.clear()
        st.rerun()

# 사이트 선택 시 URL 업데이트 및 상품 선택 초기화
if site_cd != int(url_site) if url_site in ["1", "2"] else 1:
    st.query_params["siteCd"] = str(site_cd)
    # 선택된 상품 초기화
    st.session_state.prd_no_list = set()
    st.session_state.prd_no = ""
    st.session_state.prd_nm = ""
    st.session_state.show_prd = []
    if 'last_api_url' in st.session_state:
        del st.session_state.last_api_url
    if 'last_api_response' in st.session_state:
        del st.session_state.last_api_response
    # URL에서 prdNo 파라미터 제거
    if "prdNo" in st.query_params:
        del st.query_params["prdNo"]
    st.rerun()


# --- BERT & Milvus 설정 ---
MODEL_NAME = "klue/bert-base"
MILVUS_URI = st.secrets["MILVUS"]["MILVUS_URI"]
MILVUS_TOKEN = st.secrets["MILVUS"]["MILVUS_TOKEN"]

@st.cache_resource
def load_resources(collection_alias):
    """모델 로드 및 Milvus 연결 (캐싱)"""
    connections.connect(uri=MILVUS_URI, token=MILVUS_TOKEN)
    collection = Collection(collection_alias)
    collection.load()
    return None, None, collection, None

def get_product_detail_info(prd_no, site_cd):
    """외부 API에서 상품 이미지 및 상세 정보를 가져옵니다."""
    base_url = "http://hapix.halfclub.com/searches/prdList/" if site_cd == 1 else "http://apix.boribori.co.kr/searches/prdList/"
    try:
        params = {"keyword": prd_no, "siteCd": site_cd, "device": "mc"}
        response = requests.get(base_url, params=params, timeout=0.5)
        if response.status_code == 200:
            data = response.json()
            hits = data.get("data", {}).get("result", {}).get("hits", {}).get("hits", [])
            if hits:
                return hits[0].get("_source", {})
    except Exception:
        pass
    return {}

# API_URL = "https://cf-api.boribori.co.kr/recommend"
API_URL = "https://cf-hapi.halfclub.com/recommend"
self_yn = False
if url_k and url_k.isdigit():
    k = int(url_k)
else:
    k = 50
select_prd_no = ""
select_prd_nm = ""
recomm_typ = ""
age = ""
gender = ""

if site_cd == 1:
    API_URL = "https://cf-hapi.halfclub.com/recommend"
else:
    API_URL = "https://cf-api.boribori.co.kr/recommend"

ml_types = [
    {"함께 본 상품 (viewTogether)": "viewtogether"},
    {"함께 구매한 상품 (buyTogether)": "buytogether"},
    {"유사 상품 (similarItem)": "similaritem"},
    {"유사 이미지 상품 (similarImage)": "similar-image"},
    {"개인화 추천 (recommendForYou)": "recommendforyou"},
    {"유사 상품 (BERT)": "bert_similar"},
    {"유사 상품 (조합)": "multiSimilarItem"},
    {"평균 meanSimilarItem":"meanSimilarItem"},
    {"평균 meanSimilarItemView":"meanSimilarItemView"},
    {"평균 meanSimilarItemBuy":"meanSimilarItemBuy"},
]

def get_best_products(site_cd):
    try:
        if site_cd == 1:
            url = "https://hapix.halfclub.com/searches/best/?offset=0&limit=200&dealYn=N&interval=24&countryCd=001&langCd=001&siteCd=1&deviceCd=001&device=pc&mandM=halfclub"
        else:
            url = "https://apix.boribori.co.kr/searches/best/?dealYn=N&interval=24&siteCd=2&limit=0,200&countryCd=001&langCd=001&deviceCd=001&mandM=b_boribori"
        
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            
            products = []
            seen_categories = set()
            

            if "data" in data:
                result_data = data["data"]
                if "result" in result_data:
                    hits_data = result_data["result"]
                    if "hits" in hits_data and "hits" in hits_data["hits"]:
                        hits = hits_data["hits"]["hits"]
                    else:
                        hits = hits_data.get("hits", [])
                else:
                    hits = result_data if isinstance(result_data, list) else []
            else:
                hits = data if isinstance(data, list) else []
            

            
            for i, hit in enumerate(hits):
                if isinstance(hit, dict) and len(products) < 12:
                    source = hit.get("_source", hit)
                    prd_no = source.get("prdNo")
                    prd_nm = source.get("prdNm", f"상품{i+1}")
                    prd_img = source.get("appPrdImgUrl", "")
                    

                    dp_ctgr_nm1 = source.get("dpCtgrNm1", "")
                    

                    if dp_ctgr_nm1 and "@" in dp_ctgr_nm1:
                        dp_ctgr_nm1 = dp_ctgr_nm1.split("@")[0].strip()
                    
                    if not dp_ctgr_nm1:
                        continue
                    

                    display_name = dp_ctgr_nm1
                    

                    if prd_no and dp_ctgr_nm1 not in seen_categories:
                        seen_categories.add(dp_ctgr_nm1)

                        if len(display_name) > 6:
                            formatted_name = display_name[:5] + "…"
                        else:
                            formatted_name = display_name.ljust(6, '　')
                        
                        products.append({
                            "prd_nm": formatted_name,
                            "prd_no": prd_no,
                            "prd_img": prd_img or f"https://via.placeholder.com/200x250/CCCCCC/000000?text={prd_no}",
                            "full_name": display_name
                        })
            

            if products:
                return products
                
    except Exception as e:
        st.error(f"베스트 상품 로드 오류: {e}")
    

    return [
        {"prd_nm": "여성의류", "prd_no": 380118214, "prd_img": "https://via.placeholder.com/200x250/FFB6C1/000000?text=여성의류"},
        {"prd_nm": "남성의류", "prd_no": 402544118, "prd_img": "https://via.placeholder.com/200x250/DDA0DD/000000?text=남성의류"},
        {"prd_nm": "신발", "prd_no": 379859455, "prd_img": "https://via.placeholder.com/200x250/F0E68C/000000?text=신발"},
        {"prd_nm": "가방", "prd_no": 393954850, "prd_img": "https://via.placeholder.com/200x250/87CEEB/000000?text=가방"},
        {"prd_nm": "스포츠", "prd_no": 391016367, "prd_img": "https://via.placeholder.com/200x250/98FB98/000000?text=스포츠"},
        {"prd_nm": "액세서리", "prd_no": 380115991, "prd_img": "https://via.placeholder.com/200x250/F4A460/000000?text=액세서리"}
    ]


if f"best_products_{site_cd}" not in st.session_state:
    st.session_state[f"best_products_{site_cd}"] = get_best_products(site_cd)

view_options = st.session_state[f"best_products_{site_cd}"] or [
    {"prd_nm": "여성의류", "prd_no": 380118214, "prd_img": "https://via.placeholder.com/200x250/FFB6C1/000000?text=여성의류"},
    {"prd_nm": "남성의류", "prd_no": 402544118, "prd_img": "https://via.placeholder.com/200x250/DDA0DD/000000?text=남성의류"},
    {"prd_nm": "신발", "prd_no": 379859455, "prd_img": "https://via.placeholder.com/200x250/F0E68C/000000?text=신발"},
    {"prd_nm": "가방", "prd_no": 393954850, "prd_img": "https://via.placeholder.com/200x250/87CEEB/000000?text=가방"},
    {"prd_nm": "스포츠", "prd_no": 391016367, "prd_img": "https://via.placeholder.com/200x250/98FB98/000000?text=스포츠"},
    {"prd_nm": "액세서리", "prd_no": 380115991, "prd_img": "https://via.placeholder.com/200x250/F4A460/000000?text=액세서리"}
]
search_gender_options = {
    "남성": "male",
    "여성": "female"
}
gender_options = {
    "남성": "01",
    "여성": "02"
}
age_options = {
    "40대 미만": "01",
    "40대 이상": "02"
}
recommend_sample = view_options
gender_params = gender_options
age_params = age_options
select_type = "함께 본 상품"
input_yn = False
user_yn = False

recommend_type = ""
recommend_type_nm = ""

service_type = "추천"

if "gender" not in st.session_state:
    st.session_state.gender = ""
else:
    gender = st.session_state.gender
    
if "age" not in st.session_state:
    st.session_state.age = ""
else:
    age = st.session_state.age
    
if "prd_no_list" not in st.session_state:
    st.session_state.prd_no_list = set()
    
if "prd_no" not in st.session_state:
    st.session_state.prd_no = ""
            
    
if "prd_nm" not in st.session_state:
    st.session_state.prd_nm = ""
else:
    select_prd_nm = st.session_state.prd_nm

if "type" not in st.session_state:
    st.session_state.type = ""
if "type_nm" not in st.session_state:
    st.session_state.type_nm = ""
if "show_type" not in st.session_state:
    st.session_state.show_type = ""
if "show_prd" not in st.session_state:
    st.session_state.show_prd = []

#  추천 대상 상품 표시
def show_target(items, columns_per_row=5, title=None):    
    if title:
        if input_yn:
            title = title + ": 직접 입력"
        else:
            if st.session_state.prd_nm:
                title = title + f": {st.session_state.prd_nm}"
        st.subheader(title)
    try:
        rows = [items[i: i + columns_per_row] for i in range(0, len(items), columns_per_row)]
        cols = st.columns([1.5, 8.5])
        for row in rows:
            rec = row[0]
            img_url = rec.get("prd_img", "")
            prd_nm = rec.get("prd_nm", "")
            with cols[0]:
                st.image(img_url, width=100)
            with cols[1]:
                st.markdown(prd_nm, unsafe_allow_html=True)
        # 가로선
        st.markdown("---")
    except Exception as e:
        st.error(f"이미지 표시 오류: {e}")

# 추천 결과 상품 리스트 표시
def show_grid(items, columns_per_row=5, title=None, img_width=220):
    if title:
        st.subheader(title)
    try:
        rows = [items[i: i + columns_per_row] for i in range(0, len(items), columns_per_row)]
        for row in rows:
            cols = st.columns(len(row), gap="small")
            for col, rec in zip(cols, row):
                img_url = rec.get("prd_img")
                prd_nm = rec.get("prd_nm")
                with col:
                    if img_url:
                        st.markdown(
                            f'<div style="text-align: center; width: {img_width}px; height: {int(img_width * 1.2)}px; overflow: hidden; border-radius: 8px; margin: 0 auto;"><img src="{img_url}" style="width: 100%; height: 100%; object-fit: cover;"></div>',
                            unsafe_allow_html=True
                        )
                        st.markdown(prd_nm, unsafe_allow_html=True)
                    else:
                        continue
    except Exception as e:
        return
  

# 추천 대상 이미지 버튼 CSS 설정
st.markdown("""
    <style>
    .stButton > button {
        width: 100% !important;
        height: 40px !important;
        font-family: 'Courier New', monospace !important;
        font-size: 13px !important;
        font-weight: bold !important;
        text-align: center !important;
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        padding: 0 5px !important;
        border: 2px solid transparent !important;
        border-radius: 8px !important;
    }
    .stButton > button:hover {
        border-color: #aaa !important;
    }

    .full-btn > button {
        width: 100% !important;
        height: auto !important;
        padding: 0 !important;
        border: 3px solid transparent;
        border-radius: 10px;
        overflow: hidden;
    }
    .full-btn > button:hover {
        border-color: #aaa;
    }
    .full-btn {
        margin-bottom: 10px;
    }
    .selected-btn > button {
        border-color: #ff4b4b !important;
    }
    .btn-content {
        display: flex;
        flex-direction: column;
        align-items: center;
    }
    .btn-content img {
        width: 80px;
        height: 100px;
        object-fit: cover;
    }
    .btn-text {
        font-weight: bold;
        font-size: 14px;
        padding: 8px;
        text-align: center;
        width: 100%;
        font-family: monospace;
        letter-spacing: -0.5px;
    }
    </style>
""", unsafe_allow_html=True)



col_count = 6
if service_type == "검색":
    col_count = 4
    
# 이미지 버튼 표시
cols = st.columns(col_count)
button_clicked = False
for i, value in enumerate(recommend_sample):
    prd_nm = value.get("prd_nm", "")
    prd_img = value.get("prd_img", "")
    prd_no = value.get("prd_no", "")
    
    selected_class = ""
    if str(prd_no) in st.session_state.prd_no_list:
        selected_class = "selected-button"
    
    with cols[i % col_count]:
        with st.container():
            if st.button(
                label=prd_nm,
                key=f"btn_{prd_no}",
                use_container_width=True
            ):
                button_clicked = True
                # 선택 표시
                selected_class = "selected-btn"
                
                if st.session_state.type in ["recommendforyou", "meanSimilarItem", "meanSimilarItemView", "meanSimilarItemBuy"]:
                    if str(prd_no) not in st.session_state.prd_no_list:
                        st.session_state.prd_no_list.add(str(prd_no))
                    else:
                        st.session_state.prd_no_list.remove(str(prd_no))
                    # 개인화 추천용 다중 상품 URL 업데이트
                    st.query_params["prdNo"] = ",".join(st.session_state.prd_no_list)
                else:
                    select_prd_no = str(prd_no)
                    st.session_state.prd_no = str(prd_no)
                    full_name = value.get("full_name", prd_nm)
                    select_prd_nm = str(full_name)
                    st.session_state.prd_nm = str(full_name)
                    st.session_state.prd_no_list = set()
                    st.session_state.prd_no_list.add(str(prd_no))
                    # 단일 상품 URL 업데이트
                    st.query_params["prdNo"] = str(prd_no)
            if prd_img:
                if (
                    st.session_state.prd_no_list
                    and str(prd_no) in st.session_state.prd_no_list
                ):
                    selected_class = "selected-btn"
                product_url = f"https://www.halfclub.com/product/{prd_no}" if site_cd == 1 else f"https://m.boribori.co.kr/product/{prd_no}"
                st.markdown(
                    f"""
                    <div class="full-btn {selected_class}">
                        <div class="btn-content">
                            <img src="{prd_img}" />
                            <a href="{product_url}">{prd_no}</a>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
# 가로선
st.markdown("---")



def show_target_list():
    if service_type != "검색":
        st.session_state.show_type = st.session_state.type
        
        target_prds = []
        if st.session_state.type in ["recommendforyou", "meanSimilarItem", "meanSimilarItemView", "meanSimilarItemBuy"]:
            target_prds = list(st.session_state.prd_no_list)
        elif st.session_state.prd_no:
            target_prds = [st.session_state.prd_no]
            
        if target_prds:
            with st.container():
                ori_prd_list = []
                st.session_state.show_prd = target_prds
                for resp_prd_no in target_prds:
                    search_url = f"http://hapix.halfclub.com/searches/prdList/?keyword={resp_prd_no}&siteCd={site_cd}&device=mc" if site_cd == 1 else f"http://apix.boribori.co.kr/searches/prdList/?keyword={resp_prd_no}&siteCd={site_cd}&device=mc"
                    try:
                        ori_img_resp = requests.get(search_url, timeout=2)
                    except Exception:
                        continue

                    if ori_img_resp.status_code == 200:
                        try:
                            j = ori_img_resp.json()
                            resp_data = j["data"]["result"]["hits"]["hits"][0]["_source"]
                            prdNo = resp_data.get("prdNo", "")
                            prdNm = resp_data.get("prdNm", "")
                            dcPrc = resp_data.get("dcPrcMc", 0)
                            imgUrl = resp_data.get("appPrdImgUrl", "")
                            brandNm = resp_data.get("brandNm", "")
                            prdUrl = f"https://www.halfclub.com/product/{prdNo}" if site_cd == 1 else f"https://m.boribori.co.kr/product/{prdNo}"
                            
                            text = ""
                            if len(target_prds) > 1:
                                text = text + "<p style='font-size:10pt;margin:0;padding:0;'>"

                            dp_ctgr_nm1 = resp_data.get("dpCtgrNm1", "")
                            dp_ctgr_nm2 = resp_data.get("dpCtgrNm2", "")
                            dp_ctgr_nm3 = resp_data.get("dpCtgrNm3", "")
                            

                            category_path = []
                            if dp_ctgr_nm1: category_path.append(dp_ctgr_nm1)
                            if dp_ctgr_nm2: category_path.append(dp_ctgr_nm2)
                            if dp_ctgr_nm3: category_path.append(dp_ctgr_nm3)
                            category_str = " > ".join(category_path) if category_path else ""
                            
                            text = text + f"브랜드 : {brandNm}<br/>"
                            product_link_url = f"https://www.halfclub.com/product/{prdNo}" if site_cd == 1 else f"https://m.boribori.co.kr/product/{prdNo}"
                            text = text + f"상 품 : <a href='{product_link_url}'>{prdNo}</a><br/>"
                            text = text + f"가 격 : {dcPrc:,}<br/>"
                            if len(target_prds) > 1:
                                text = text + f"상품명 :<br/>{prdNm}<br/>"
                            else:
                                text = text + f"상품명 : {prdNm}<br/>"
                            if category_str:
                                text = text + f"{category_str}"
                                
                            if age or gender:
                                text = text + f"<br/>"
                                if age:
                                    text = text + f" ■ 선택 나이 : {age}<br/>"
                                if gender:
                                    text = text + f" ■ 선택 성별 : {gender}<br/>"
                            if len(target_prds) > 1:
                                text = text + f"</p><br/>"
                            
                            ori_prd_list.append({
                                "prd_no": prdNo
                                , "score": 0
                                , "prd_nm": text
                                , "prd_url": prdUrl
                                , "prd_img": imgUrl
                            })
                        except Exception as ex:
                            continue
                if ori_prd_list:
                    if len(ori_prd_list) == 1:
                        show_target(ori_prd_list, columns_per_row=1, title="추천 대상 상품")
                    else:
                        show_grid(ori_prd_list, columns_per_row=5, title="추천 대상 상품", img_width=100)
show_target_list()







if service_type == "추천":

    
    # type_options = [
    #     list(ml_types[0].keys())[0],
    #     list(ml_types[2].keys())[0],
    #     list(ml_types[4].keys())[0],
    #     list(ml_types[5].keys())[0],
    #     list(ml_types[6].keys())[0],
    #     list(ml_types[7].keys())[0]
    # ]
    
    type_options = [list(item.keys())[0] for item in ml_types]
    
    
    # type_options = ["함께 본 상품 (view-together)","함께 구매한 상품 (buy-together)","유사 상품 (similar-item)","유사 이미지 상품 (similar-image)","개인화 추천 (recommend-for-you)"]
    
    # if site_cd == 2:
    #     type_options = ["함께 본 상품 (view-together)","함께 구매한 상품 (buy-together)","유사 상품 (similar-item)","유사 이미지 상품 (similar-image)","개인화 추천 (recommend-for-you)","유사 상품 (BERT)","유사 상품 (조합)"]
    
#     ml_types = [
#     {"함께 본 상품 (view-together)": "viewtogether"},
#     {"함께 본 상품 (연령/성별)": "viewuser"},
#     {"함께 구매한 상품 (buy-together)": "buytogether"},
#     {"함께 구매한 상품 (연령/성별)": "buyuser"},
#     {"유사 상품 (similar-item)": "similaritem"},
#     {"유사 이미지 상품 (similar-image)": "similar-image"},
#     {"개인화 추천 (recommend-for-you)": "recommendforyou"},
# ]
    
    # URL 파라미터로 추천 서비스 유형 설정
    default_index = 0
    if url_type:
        for i, option in enumerate(type_options):
            for item in ml_types:
                if list(item.values())[0] == url_type and list(item.keys())[0] == option:
                    default_index = i
                    break
    
    select_type = st.selectbox("추천 서비스 유형", options=type_options, index=default_index)
    for item in ml_types:
        if list(item.keys())[0] == select_type:
            recommend_type = list(item.values())[0]
            st.session_state.type = recommend_type
            recommend_type_nm = list(item.keys())[0]
            st.session_state.type_nm = recommend_type_nm
            # 추천 서비스 유형 선택 시 URL 업데이트
            if recommend_type != url_type:
                st.query_params["mlType"] = recommend_type
            break
    
    # URL 파라미터로 상품 설정
    if url_prd and not button_clicked:
        # prdNo 파라미터 처리
        if recommend_type in ["recommendforyou", "meanSimilarItem", "meanSimilarItemView", "meanSimilarItemBuy"]:
            # 기존 리스트 초기화 후 URL 파라미터로 설정
            st.session_state.prd_no_list = set()
            if "," in url_prd:
                for prd in url_prd.split(","):
                    st.session_state.prd_no_list.add(prd.strip())
            else:
                st.session_state.prd_no_list.add(url_prd.strip())
        else:
            if not st.session_state.prd_no:
                # 단일 상품 추천의 경우 첫 번째 상품만 사용
                first_prd = url_prd.split(",")[0].strip() if "," in url_prd else url_prd
                st.session_state.prd_no = first_prd
                st.session_state.prd_no_list.add(first_prd)

input_yn = st.checkbox("📝 상품번호 직접 입력", value=False, key="direct_input")

submit_button = None
# 직접 입력 표시
if input_yn:
    with st.form(key="view_form"):
        input_text = "상품번호"
        input_value = ""
        
        # 선택된 상품번호를 텍스트 박스에 표시
        if recommend_type in ["keyword-search"]:
            input_text = "검색어"
            input_value = st.session_state.prd_nm if st.session_state.prd_nm != "직접입력" else ""
        elif recommend_type in ["recommendforyou", "meanSimilarItem", "meanSimilarItemView", "meanSimilarItemBuy"]:
            input_text = "상품번호 리스트 (ex. 상품번호1,상품번호2,상품번호3)"
            input_value = ",".join(st.session_state.prd_no_list) if st.session_state.prd_no_list else ""
        else:
            input_value = st.session_state.prd_no if st.session_state.prd_no else ""
            
        prd_no = st.text_input(input_text, value=input_value, placeholder="여기에 입력해주세요...")
        submit_button = st.form_submit_button(label="🔍 조회 시작", use_container_width=True)
        
# 성별 선택 섹션
if recommend_type in ["keyword-search"]:
    gender = st.selectbox("성별", options=["", "👨 남성", "👩 여성"], index=0)
    if gender:
        st.session_state.gender = gender.replace("👨 ", "").replace("👩 ", "")

if st.session_state.type not in ["recommendforyou", "meanSimilarItem", "meanSimilarItemView", "meanSimilarItemBuy"]:
    st.session_state.prd_no_list = set()
    
# 가로선
st.markdown("---")

# 추천 조회
def submit():
    global recommend_type, gender, age
    # 추천 서비스 유형 선택
    if not select_type:
        return
    # 상품 번호 입력 (개인화 추천은 리스트로 확인)
    if recommend_type in ["recommendforyou", "meanSimilarItem", "meanSimilarItemView", "meanSimilarItemBuy"]:
        if not st.session_state.prd_no_list:
            return
    else:
        if not st.session_state.prd_no and not st.session_state.prd_nm:
            return
    
    try:
        selected_gender = ""
        selected_age = ""
        if recommend_type in ["viewtogether", "buytogether"]:
            if not gender and st.session_state.gender:
                gender = st.session_state.gender
            if gender:
                for item in gender_options:
                    if item == gender:
                        selected_gender = gender_options[item]
                        break
            if not age and st.session_state.age:
                age = st.session_state.age
            if age:
                for item in age_options:
                    if item == age:
                        selected_age = age_options[item]
                        break
            if gender and age:
                if recommend_type in ["viewtogether"]:
                    recommend_type = "viewuser"
                elif recommend_type in ["buytogether"]:
                    recommend_type = "buyuser"
                params = dict(
                    prdNo=int(st.session_state.prd_no),
                    age=selected_age,
                    gender=selected_gender,
                    siteCd=site_cd,
                    size=int(k),
                    # score=True
                )
            else:
                params = dict(
                    prdNo=int(st.session_state.prd_no),
                    siteCd=site_cd,
                    size=int(k),
                    # score=True
                )
        elif recommend_type in ["keyword-search"]:
            if st.session_state.gender:
                gender = st.session_state.gender
            else:
                gender = ""
            if gender:
                for item in search_gender_options:
                    if item == gender:
                        selected_gender = search_gender_options[item]
                        break
            params = dict(
                keyword=st.session_state.prd_nm,
                gender=selected_gender,
                siteCd=site_cd,
                limit=int(k),
                # score=True
            )
        elif recommend_type in ["recommendforyou", "meanSimilarItem", "meanSimilarItemView", "meanSimilarItemBuy"]:
            params = dict(
                prdNo=[int(prd) for prd in st.session_state.prd_no_list],
                siteCd=site_cd,
                size=int(k),
                # score=True
            )
        elif recommend_type == "bert_similar":
            pass
        else:
            # similar-image만 size=50, 나머지는 기본값 사용
            size_param = 100 if recommend_type == "similar-image" else int(k)
            
            # similar-image는 단일 상품만, 나머지는 여러 상품 처리
            if recommend_type == "similar-image":
                params = dict(
                    prdNo=int(st.session_state.prd_no),
                    siteCd=site_cd,
                    size=size_param
                )
            else:
                # 여러 상품번호가 있으면 모두 처리
                if st.session_state.prd_no_list and len(st.session_state.prd_no_list) > 1:
                    prd_list = [int(prd) for prd in st.session_state.prd_no_list]
                else:
                    prd_list = [int(st.session_state.prd_no)]
                
                params = dict(
                    prdNo=prd_list,
                    siteCd=site_cd,
                    size=size_param,
                    # score=True
                    randomYn=False,
                )
        
        if recommend_type == "bert_similar":
            with st.spinner("BERT 모델로 유사 상품을 검색 중입니다..."):
                # 1. 리소스 로드
                alias = "hf_prd" if site_cd == 1 else "br_prd"
                tokenizer, model, collection, device = load_resources(alias)
                
                # 2. 상품 번호로 벡터 조회
                target_prd_no = int(st.session_state.prd_no)
                res = collection.query(
                    expr=f"prd_no == {target_prd_no}",
                    output_fields=["vector"],
                    limit=1
                )
                
                if not res:
                    st.warning(f"Milvus에서 상품 번호 {target_prd_no}에 대한 데이터를 찾을 수 없습니다.")
                    return
                
                query_vector = res[0]["vector"]

                # 3. Milvus 검색
                search_params = {"metric_type": "COSINE", "params": {"nprobe": 10}}
                results = collection.search(
                    data=[query_vector], 
                    anns_field="vector", 
                    param=search_params, 
                    limit=int(k),
                    output_fields=["vector"]
                )

                # 4. 결과 매핑
                data = []
                for hits in results:
                    for hit in hits:
                        detail = get_product_detail_info(hit.id, site_cd)
                        item = detail.copy()
                        item["prd_no"] = hit.id
                        item["score"] = hit.distance
                        data.append(item)
                
                st.session_state.last_api_url = "Local Milvus Query"
                st.session_state.last_api_response = data
        else:
            api_url = f"{API_URL}/{recommend_type}"
            response = requests.get(api_url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            # 실제 호출된 URL 및 JSON 데이터 저장
            st.session_state.last_api_url = response.url
            st.session_state.last_api_response = data
        
        if not data:
            st.error("API 응답이 비어있습니다.")
            return
        
        # 추천 대상 상품 표시
        if recommend_type in ["keyword-search"]:
            if gender:
                st.subheader(f"검색 키워드: {st.session_state.prd_nm} ({gender})")
            else:
                st.subheader(f"검색 키워드: {st.session_state.prd_nm}")
            st.markdown("---")

                
        # 추천 상품 이미지 및 점수
        recs = []
        recs_title = "추천"
        ml_type = ""
                
        ml_data = []
        if recommend_type in ["keyword-search"]:
            if isinstance(data, list):
                ml_data = data
            elif isinstance(data, dict):
                ml_data = data.get("results", data.get("data", []))
            else:
                ml_data = []
        else:
            if isinstance(data, dict):
                ml_data = data.get("result", data.get("data", []))
            elif isinstance(data, list):
                ml_data = data
            else:
                ml_data = []
            ml_type = data.get("ml_type", "") if isinstance(data, dict) else ""
            if ml_type:
                if ml_type == "ml":
                    recs_title = recs_title + f": {recommend_type_nm} ML"
                else:
                    recs_title = recs_title + f": {recommend_type_nm}"
            else:
                recs_title = recs_title + f": {recommend_type_nm}"
                            
        if not ml_data:
            st.warning("추천 결과가 없습니다.")
            return
            
        for rec in ml_data:
            if not rec or not isinstance(rec, dict):
                continue
                
            # 필드명 호환성 처리
            prd_no = rec.get("prd_no") or rec.get("prdNo")
            if not prd_no:
                continue
                
            score = rec.get("score", 0.0)
            esscore = rec.get("esscore", 0.0)
            sgn = rec.get("sgnCd", [])
            prd_nm = rec.get("prd_nm") or rec.get("prdNm", "")
            prd_img = rec.get("prd_img") or rec.get("appPrdImgUrl", "")
            prc = rec.get("price") or rec.get("dcPrcMc", 0)
            brandNm = rec.get("brandNm", "")
                
                        
            text = ""
            
            # 추천 정보 표시
            if rec.get("rcm_prd_no", ""):
                text = text + f"<p style='font-size:9pt;margin:0;padding:0;'>"
                text = text + f"추천 대상: {rec.get("rcm_prd_no", "")}<br/>"
                text = text + f"</p>"
            if rec.get("age", ""):
                for item in age_options:
                    if age_options[item] == rec.get("age", ""):
                        text = text + f"<p style='font-size:9pt;margin:0;padding:0;'>"
                        text = text + f"■ 나이: {item}<br/>"
                        text = text + f"</p>"
                        break
            if rec.get("gender", ""):
                for item in gender_options:
                    if gender_options[item] == rec.get("gender", ""):
                        text = text + f"<p style='font-size:9pt;margin:0;padding:0;'>"
                        text = text + f"■ 성별: {item}<br/>"
                        text = text + f"</p>"
                        break
            
            # 카테고리 정보 추가 (추천 결과용)
            dp_ctgr_nm1 = rec.get("dpCtgrNm1", "")
            dp_ctgr_nm2 = rec.get("dpCtgrNm2", "")
            dp_ctgr_nm3 = rec.get("dpCtgrNm3", "")
            
            # 카테고리 경로 생성
            category_path = []
            if dp_ctgr_nm1: category_path.append(dp_ctgr_nm1)
            if dp_ctgr_nm2: category_path.append(dp_ctgr_nm2)
            if dp_ctgr_nm3: category_path.append(dp_ctgr_nm3)
            category_str = " > ".join(category_path) if category_path else ""
            
            # 상품 정보 표시
            text = text + f"<p style='font-size:10pt;margin:0;padding:0;'>"
            if score:
                text = text + f"추천 스코어 : {score:.4f}<br/>"
            if esscore:
                text = text + f"ES 스코어 : {esscore:.4f}<br/>"
            text = text + f"브랜드 : {brandNm}<br/>"
            product_link_url = f"https://www.halfclub.com/product/{prd_no}" if site_cd == 1 else f"https://m.boribori.co.kr/product/{prd_no}"
            text = text + f"상 품 : <a href='{product_link_url}'>{prd_no}</a><br/>"
            text = text + f"가 격 : {prc:,} 원<br/>"
            text = text + f"상품명 :<br/>{prd_nm}<br/>"
            if category_str:
                text = text + f"{category_str}"
            if sgn and isinstance(sgn, list) and len(sgn) > 0:
                for i, code in enumerate(sgn):
                    if code == "01":
                        sgn[i] = "봄"
                    elif code == "02":
                        sgn[i] = "여름"
                    elif code == "03":
                        sgn[i] = "가을"
                    elif code == "04":
                        sgn[i] = "겨울"
                    elif code == "05":
                        sgn[i] = "사계절"
                sgn_str = ", ".join(sgn)
                text = text + f"<br/>시즌 : {sgn_str}<br/>"
            text = text + f"</p><br/>"
            
            product_url = f"https://www.halfclub.com/product/{prd_no}" if site_cd == 1 else f"https://m.boribori.co.kr/product/{prd_no}"
            recs.append({"prd_no": prd_no, "score": score, "prd_nm": text, "prd_url": product_url, "prd_img": prd_img})

        if not recs:
            st.error("리스트 결과 없음")
        else:
            # 4의 배수로 결과 제한
            total_count = len(recs)
            display_count = (total_count // 4) * 4
            if display_count > 0:
                recs = recs[:display_count]
            show_grid(recs, columns_per_row=4, title=recs_title, img_width=150)

    except requests.exceptions.Timeout:
        st.error("API 요청 시간이 초과되었습니다.")
    except requests.exceptions.ConnectionError:
        st.error("API 서버에 연결할 수 없습니다.")
    except requests.exceptions.HTTPError as http_err:
        st.error(f"HTTP 에러 ({http_err.response.status_code}): {http_err}")
    except ValueError as json_err:
        st.error(f"API 응답 파싱 오류: {json_err}")
    except Exception as err:
        st.error(f"예상치 못한 오류: {err}")

# 폼 제출 시 API 호출 및 이미지 표시
if submit_button:
    select_prd_no = prd_no
    st.session_state.prd_no = select_prd_no
    st.session_state.prd_nm = "직접입력"
    
    if recommend_type in ["buytogether","viewtogether","keyword-search"]:
        if gender:
            st.session_state.gender = gender
    if recommend_type in ["buytogether","viewtogether"]:
        if age:
            st.session_state.age = age
    if recommend_type in ["recommendforyou", "meanSimilarItem", "meanSimilarItemView", "meanSimilarItemBuy"]:
        if prd_no:
            st.session_state.prd_no_list = set()
            for prd in prd_no.split(","):
                st.session_state.prd_no_list.add(prd.strip())
            # URL 파라미터 업데이트
            st.query_params["prdNo"] = ",".join(st.session_state.prd_no_list)
            if st.session_state.show_prd != st.session_state.prd_no_list:
                st.rerun()
    elif recommend_type != "similar-image":
        # similar-image를 제외한 다른 추천 유형에서 여러 상품 처리
        if prd_no and "," in prd_no:
            st.session_state.prd_no_list = set()
            for prd in prd_no.split(","):
                st.session_state.prd_no_list.add(prd.strip())
            st.session_state.prd_no = prd_no.split(",")[0].strip()  # 첫 번째 상품을 대표로
        else:
            st.session_state.prd_no = prd_no
            st.session_state.prd_no_list = {str(prd_no)}
        
        # URL 파라미터 업데이트
        st.query_params["prdNo"] = str(st.session_state.prd_no)
    
    st.rerun()

# URL 파라미터 또는 상품 선택 시 자동 실행
auto_submit = False

# URL 파라미터로 모든 값이 설정된 경우
if url_prd and url_type and recommend_type:
    auto_submit = True
# 또는 상품이 선택되고 추천 유형이 설정된 경우
elif (select_prd_no or st.session_state.prd_no_list) and recommend_type:
    auto_submit = True

if auto_submit:
    if recommend_type in ["keyword-search"]:
        if gender:
            st.session_state.gender = gender
    
    # recommendforyou가 아닌 경우에만 prd_no_list 초기화
    if recommend_type not in ["recommendforyou", "meanSimilarItem", "meanSimilarItemView", "meanSimilarItemBuy"]:
        if st.session_state.prd_no_list:
            st.session_state.prd_no_list = set()
        
    if st.session_state.show_type != recommend_type:
        if st.session_state.show_type in ["recommendforyou", "meanSimilarItem", "meanSimilarItemView", "meanSimilarItemBuy"] and recommend_type not in ["recommendforyou", "meanSimilarItem", "meanSimilarItemView", "meanSimilarItemBuy"]:
            st.session_state.prd_no_list = set()
        st.rerun()

    submit()

# API 정보 섹션
if 'last_api_url' in st.session_state:
        
    with st.expander("🔗 호출된 API URL", expanded=False):
        st.markdown(f"[{st.session_state.last_api_url}]({st.session_state.last_api_url})")
    
    if 'last_api_response' in st.session_state:
        with st.expander("📊 API 응답 JSON", expanded=False):
            st.json(st.session_state.last_api_response)
