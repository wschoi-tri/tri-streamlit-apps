import streamlit as st
import requests

BASE_URL = "https://cf-api.boribori.co.kr/recommend/home"
SIMILAR_URL = "https://cf-api.boribori.co.kr/recommend/similaritem"
SITE_CD = 2
DEVICE_CD = "001"

DEFAULT_PRD_NO = ""
DEFAULT_BASKET_PRD_NO = ""
DEFAULT_WISH_PRD_NO = ""
DEFAULT_MEM_NO = ""
DEFAULT_SIZE = 30

st.set_page_config(
    page_title="보리 recommend/home API 확인",
    layout="centered"
)

st.markdown("""
<style>
    .stButton > button {
        border: none;
    }
</style>
""", unsafe_allow_html=True)

st.title("보리 recommend/home API 확인")
# st.caption(f"siteCd={SITE_CD}, deviceCd={DEVICE_CD} 고정")


def parse_int_list(value, label):
    items = []
    if not value:
        return items
    for part in value.split(","):
        token = part.strip()
        if not token:
            continue
        try:
            items.append(int(token))
        except ValueError:
            st.warning(f"{label}에 숫자가 아닌 값이 있습니다: {token}")
    return items


def format_price(value):
    try:
        return f"{int(value):,}"
    except (TypeError, ValueError):
        return str(value)


def extract_seed_and_results(data):
    def extract_list(section):
        if isinstance(section, list):
            return section
        if isinstance(section, dict):
            for key in ("result", "list", "items", "data", "results"):
                value = section.get(key)
                if isinstance(value, list):
                    return value
        return []

    seeds = []
    results = []

    if isinstance(data, dict):
        seeds = extract_list(data.get("seed"))
        results = extract_list(data.get("result"))

        if not results:
            for key in ("data", "results"):
                results = extract_list(data.get(key))
                if results:
                    break

        if not seeds:
            for key in ("data", "result", "results"):
                section = data.get(key)
                if isinstance(section, dict):
                    seeds = extract_list(section.get("seed"))
                    if seeds:
                        break
    elif isinstance(data, list):
        results = data

    return seeds, results


def build_similar_prd_list(selected_prd_no, prd_no_list, basket_prd_no_list, wish_prd_no_list):
    prd_list = []
    seen = set()

    def add_item(value):
        if value is None:
            return
        if isinstance(value, str):
            value = value.strip()
            if not value:
                return
            try:
                value = int(value)
            except ValueError:
                return
        if value in seen:
            return
        seen.add(value)
        prd_list.append(value)

    add_item(selected_prd_no)
    for item in prd_no_list or []:
        add_item(item)
    for item in basket_prd_no_list or []:
        add_item(item)
    for item in wish_prd_no_list or []:
        add_item(item)

    return prd_list


def build_recs(items, is_similar=False):
    recs = []
    def fmt_score(val):
        try:
            return f"{float(val):.4f}"
        except (ValueError, TypeError):
            return str(val)

    for idx, rec in enumerate(items):
        if not rec or not isinstance(rec, dict):
            continue

        prd_no = rec.get("prd_no") or rec.get("prdNo")
        if not prd_no:
            continue

        # 추천 유사도 점수
        score = rec.get("score", "")
        # 추천 유사도 + 시즌 점수
        esscore = rec.get("esscore", "")
        # 상품 시즌
        sgn = rec.get("sgnCd", [])
        season_map = {
            "01": "봄",
            "02": "여름",
            "03": "가을",
            "04": "겨울",
            "05": "사계절"
        }        
        # 상품명
        prd_nm = rec.get("prd_nm") or rec.get("prdNm", "")
        # 상품 이미지
        prd_img = rec.get("prd_img") or rec.get("appPrdImgUrl", "")
        # 상품 가격
        prc = rec.get("price") or rec.get("dcPrcMc", 0)
        # 상품 브랜드
        brand_nm = rec.get("brandNm", "")
        # 카테고리 대
        dp_ctgr_nm1 = rec.get("dpCtgrNm1", "")
        # 카테고리 중
        dp_ctgr_nm2 = rec.get("dpCtgrNm2", "")
        # 카테고리 소
        dp_ctgr_nm3 = rec.get("dpCtgrNm3", "")

        text = ""
        if is_similar and str(rec.get("rcm_prd_no", "")) == str(prd_no):
            text += "<div style='text-align:center;color:#ff4b4b;font-weight:bold;'>[ 내가 본 ]</div>"
        elif rec.get("type"):
            rec_type = rec.get("type")
            type_label = "추천"
            if rec_type == "self": type_label = "베스트"
            elif rec_type == "DB": type_label = "휴리스틱"
            text += f"<div style='text-align:center;font-weight:bold;'> {type_label} </div>"
        if rec.get("rcm_prd_no", ""):
            text += "<p style='font-size:9pt;margin:0;padding:0;'>"
            text += f"추천 대상: {rec.get('rcm_prd_no', '')}<br/>"
            text += "</p>"
        product_link_url = f"https://www.boribori.co.kr/product/{prd_no}"
        if product_link_url:
            text += "<p style='font-size:9pt;margin:0;padding:0;'>"
            text += f"상품 상세 : <a href='{product_link_url}'>{prd_no}</a><br/>"
            text += "</p>"
        seed_value = rec.get("seed", "")
        if seed_value:
            seed_label_map = {
                "recent": "최근본상품",
                "basket": "장바구니",
                "wish": "좋아요"
            }
            seed_label = seed_label_map.get(seed_value, seed_value)
            text += "<p style='font-size:9pt;margin:0;padding:0;'>"
            text += f"Seed: {seed_label}<br/>"
            text += "</p>"

        text += "<p style='font-size:10pt;margin:0;padding:0;'>"
        text += f"<span style='display:block;text-align:right;font-size:8pt;'>Score : {fmt_score(score)} / ESS : {fmt_score(esscore)}</span>"
        text += f"<span style='display: -webkit-box; -webkit-line-clamp: 1; -webkit-box-orient: vertical; overflow: hidden; text-overflow: ellipsis;'>브랜드 : {brand_nm}</span>"
        text += f"가 격 : {format_price(prc)} 원<br/>"
        text += f"상품명 :<br/><span style='display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden; text-overflow: ellipsis; height: 4.2em; line-height: 1.4;'>{prd_nm}</span>"
        text += "</p><br/>"

        recs.append({
            "prd_no": prd_no,
            "score": score,
            "prd_nm": text,
            "prd_url": product_link_url,
            "prd_img": prd_img
        })

    return recs


def build_seed_recs(items):
    recs = []
    seed_label_map = {
        "recent": "최근본상품",
        "basket": "장바구니",
        "wish": "좋아요"
    }

    recs.append({
        "prd_no": "",
        "prd_nm": "<p style='font-size:10pt;margin:3px 0 0 0;padding:0;'>[Index 0]<br/>FORYOU</p>",
        "prd_url": "",
        "prd_img": "",
        "is_foryou": True
    })

    for i, rec in enumerate(items):
        if not rec or not isinstance(rec, dict):
            continue

        prd_no = rec.get("prd_no") or rec.get("prdNo")
        if not prd_no:
            continue

        seed_value = rec.get("seed", "")
        seed_label = seed_label_map.get(seed_value, seed_value)
        brand_nm = rec.get("brandNm", "")
        prd_img = rec.get("prd_img") or rec.get("appPrdImgUrl", "")
        product_link_url = f"https://www.boribori.co.kr/product/{prd_no}"

        text = "<p style='font-size:10pt;margin:3px 0 0 0;padding:0;'>"
        text += f"[Index {i+1}]<br/>"
        if seed_label:
            text += f"{seed_label}<br/>"
        if brand_nm:
            text += f"브랜드: {brand_nm}<br/>"
        text += "</p><br/>"

        recs.append({
            "prd_no": prd_no,
            "prd_nm": text,
            "prd_url": product_link_url,
            "prd_img": prd_img,
            "seed_prd_no": prd_no
        })

    return recs


def show_grid(items, columns_per_row=4, title=None, img_width=110):
    if title:
        st.subheader(title)
    try:
        rows = [items[i: i + columns_per_row] for i in range(0, len(items), columns_per_row)]
        for i, row in enumerate(rows):
            cols = st.columns(len(row), gap="small")
            for j, (col, rec) in enumerate(zip(cols, row)):
                img_url = rec.get("prd_img")
                prd_nm = rec.get("prd_nm")
                is_foryou = rec.get("is_foryou", False)
                seed_prd_no = rec.get("seed_prd_no")
                with col:
                    if is_foryou:
                        st.markdown(
                            f"<div style='display:flex;align-items:center;justify-content:center;text-align:center;width:{img_width}px;height:{int(img_width * 1.2)}px;border-radius:8px;margin:0 auto 2px auto;background:#f4f4f4;color:#333;font-weight:700;'>FORYOU</div>",
                            unsafe_allow_html=True
                        )
                        if st.button("FORYOU", key=f"btn_foryou_{i}_{j}", use_container_width=True):
                            st.session_state.selected_seed_prd_no = ""
                            st.rerun()
                    else:
                        if img_url:
                            margin_bottom = "2px" if seed_prd_no else "0"
                            st.markdown(
                                f"<div style='text-align:center;width:{img_width}px;height:{int(img_width * 1.2)}px;overflow:hidden;border-radius:8px;margin:0 auto {margin_bottom} auto;'><img src='{img_url}' style='width:100%;height:100%;object-fit:cover;'></div>",
                                unsafe_allow_html=True
                            )
                        if seed_prd_no:
                            if st.button(f"{seed_prd_no}", key=f"btn_seed_{seed_prd_no}_{i}_{j}", use_container_width=True):
                                st.session_state.selected_seed_prd_no = str(seed_prd_no)
                                st.rerun()
                    if prd_nm:
                        st.markdown(prd_nm, unsafe_allow_html=True)
    except Exception:
        return


with st.form("home_recommend_form"):
    prd_no_text = st.text_input("prdNo (comma-separated) : 최근 본 상품", value=DEFAULT_PRD_NO)
    basket_prd_no_text = st.text_input("basketPrdNo (comma-separated) : 장바구니 상품", value=DEFAULT_BASKET_PRD_NO)
    wish_prd_no_text = st.text_input("wishPrdNo (comma-separated) : 좋아요 상품", value=DEFAULT_WISH_PRD_NO)
    mem_no_text = st.text_input("memNo (comma-separated) : 회원번호", value=DEFAULT_MEM_NO)
    size = st.number_input("size", min_value=1, max_value=200, value=DEFAULT_SIZE, step=1)
    self_yn = st.checkbox("휴리스틱 조회", value=False)
    submitted = st.form_submit_button("API 호출")

seed_prd_no_param = st.query_params.get("seedPrdNo", "")
if seed_prd_no_param:
    st.session_state.selected_seed_prd_no = seed_prd_no_param

if submitted:
    prd_no_list = parse_int_list(prd_no_text, "prdNo")
    basket_prd_no_list = parse_int_list(basket_prd_no_text, "basketPrdNo")
    wish_prd_no_list = parse_int_list(wish_prd_no_text, "wishPrdNo")
    mem_no_list = parse_int_list(mem_no_text, "memNo")

    # if not prd_no_list and not basket_prd_no_list and not wish_prd_no_list:
    #     st.error("prdNo, basketPrdNo, wishPrdNo 중 최소 하나는 입력해 주세요.")
    #     st.stop()

    params = {
        "siteCd": SITE_CD,
        "deviceCd": DEVICE_CD,
        "size": int(size),
        "selfYn": self_yn
    }
    if prd_no_list:
        params["prdNo"] = prd_no_list
    if basket_prd_no_list:
        params["basketPrdNo"] = basket_prd_no_list
    if wish_prd_no_list:
        params["wishPrdNo"] = wish_prd_no_list
    if mem_no_list:
        params["memNo"] = mem_no_list

    try:
        with st.spinner("API 호출 중..."):
            response = requests.get(BASE_URL, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

        st.session_state.home_data = data
        st.session_state.home_url = response.url
        st.session_state.home_prd_no_list = prd_no_list
        st.session_state.home_basket_prd_no_list = basket_prd_no_list
        st.session_state.home_wish_prd_no_list = wish_prd_no_list
        st.session_state.home_size = int(size)
        st.session_state.selected_seed_prd_no = ""
        if "seedPrdNo" in st.query_params:
            del st.query_params["seedPrdNo"]

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

home_data = st.session_state.get("home_data")
if home_data:
    if st.session_state.get("home_url"):
        st.caption(f"요청 URL: {st.session_state.get('home_url')}")

    seeds, results = extract_seed_and_results(home_data)
    seed_recs = build_seed_recs(seeds)

    # if seed_recs:
    show_grid(seed_recs, columns_per_row=5, title="추천 탭", img_width=110)
    # else:
    #     st.info("Seed 데이터가 없습니다.")

    selected_seed_prd_no = st.session_state.get("selected_seed_prd_no", "")
    if selected_seed_prd_no:
        prd_list = [int(selected_seed_prd_no)]
        if not prd_list:
            st.warning("추천 조회에 사용할 상품번호가 없습니다.")
        else:
            try:
                with st.spinner("similaritem 호출 중..."):
                    response = requests.get(
                        SIMILAR_URL,
                        params={
                            "prdNo": prd_list,
                            "size": st.session_state.get("home_size", DEFAULT_SIZE),
                            "siteCd": SITE_CD,
                            "originPrdYn":True,
                            "randomYn":False,
                        },
                        timeout=30
                    )
                    response.raise_for_status()
                    similar_data = response.json()

                st.caption(f"요청 URL: {response.url}")

                similar_results = extract_seed_and_results(similar_data)[1]
                similar_recs = build_recs(similar_results, is_similar=True)

                if similar_recs:
                    show_grid(
                        similar_recs,
                        columns_per_row=5,
                        title=f"추천 결과 ({selected_seed_prd_no})",
                        img_width=110
                    )
                else:
                    st.warning("추천 결과가 없습니다.")

                with st.expander("similaritem 응답 원본"):
                    st.json(similar_data)

            except requests.exceptions.Timeout:
                st.error("similaritem 요청 시간이 초과되었습니다.")
            except requests.exceptions.ConnectionError:
                st.error("similaritem 서버에 연결할 수 없습니다.")
            except requests.exceptions.HTTPError as http_err:
                st.error(f"similaritem HTTP 에러 ({http_err.response.status_code}): {http_err}")
            except ValueError as json_err:
                st.error(f"similaritem 응답 파싱 오류: {json_err}")
            except Exception as err:
                st.error(f"similaritem 예상치 못한 오류: {err}")
    else:
        result_recs = build_recs(results)
        if result_recs:
            show_grid(result_recs, columns_per_row=5, title="추천 결과 (FORYOU)", img_width=110)
        else:
            st.warning("추천 결과가 없습니다.")

    with st.expander("응답 원본"):
        st.json(home_data)
