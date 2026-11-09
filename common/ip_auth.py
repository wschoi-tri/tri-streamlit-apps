import ipaddress
import streamlit as st
import streamlit.components.v1 as components
from streamlit.runtime import get_instance
from streamlit.runtime.scriptrunner import get_script_run_ctx


def is_private_ip(ip_str: str) -> bool:
    """IP가 사설망(Private) 또는 로컬 루프백 대역인지 판별합니다."""
    if not ip_str:
        return True
    if ip_str in ["localhost", "127.0.0.1", "::1"]:
        return True
    try:
        addr = ipaddress.ip_address(ip_str)
        return addr.is_private or addr.is_loopback or addr.is_link_local
    except ValueError:
        return False


def get_client_ip_from_headers() -> str:
    """Streamlit 요청 헤더에서 실제 외부 공인 IP를 우선 추출합니다."""
    if not (hasattr(st, "context") and hasattr(st.context, "headers")):
        return ""

    headers = st.context.headers

    # 1. Cloudflare / CDN 직접 연결 헤더 (공인 IP 보장)
    for key in ["CF-Connecting-IP", "True-Client-IP", "X-Client-IP"]:
        val = headers.get(key)
        if val:
            ip = val.strip()
            if ip and not is_private_ip(ip):
                return ip

    # 2. X-Forwarded-For 헤더에서 공인 IP 탐색
    # 프록시 체인: client, proxy1, proxy2 ...
    xff = headers.get("X-Forwarded-For")
    if xff:
        candidates = [p.strip() for p in xff.split(",") if p.strip()]
        # 사설망(10.x, 172.x, 192.168.x)이 아닌 첫 번째 공인 IP 추출
        for cand in candidates:
            if not is_private_ip(cand):
                return cand
        # 공인 IP가 없으면 첫 번째 값
        if candidates:
            return candidates[0]

    # 3. X-Real-IP 확인
    x_real = headers.get("X-Real-IP")
    if x_real:
        ip = x_real.strip()
        if not is_private_ip(ip):
            return ip

    # 4. Streamlit 1.45+ st.context.ip_address
    if getattr(st.context, "ip_address", None):
        ip = str(st.context.ip_address).strip()
        if not is_private_ip(ip):
            return ip

    return ""


def get_client_ip_fallback() -> str:
    """헤더에서 공인 IP를 찾지 못했을 때 Tornado 세션 또는 헤더의 기본 IP 조회."""
    # 헤더의 x-forwarded-for 또는 x-real-ip 마지막 시도
    if hasattr(st, "context") and hasattr(st.context, "headers"):
        headers = st.context.headers
        xff = headers.get("X-Forwarded-For")
        if xff:
            return xff.split(",")[0].strip()
        x_real = headers.get("X-Real-IP")
        if x_real:
            return x_real.strip()

    # Tornado 내부 세션
    try:
        ctx = get_script_run_ctx()
        if ctx is not None:
            runtime_inst = get_instance()
            if runtime_inst and hasattr(runtime_inst, "_session_mgr"):
                session_info = runtime_inst._session_mgr.get_session_info(ctx.session_id)
                if session_info and session_info.client and session_info.client.request:
                    remote_ip = session_info.client.request.remote_ip
                    if remote_ip:
                        return str(remote_ip).strip()
    except Exception:
        pass

    return ""


def is_ip_allowed(client_ip: str, allowed_list: list[str]) -> bool:
    """단일 IP 또는 CIDR 서브넷 대역과 클라이언트 IP의 일치 여부를 판별합니다."""
    if not client_ip:
        return False

    if client_ip in ["localhost", "127.0.0.1", "::1"] and any(
        a in ["localhost", "127.0.0.1", "::1"] for a in allowed_list
    ):
        return True

    try:
        client_addr = ipaddress.ip_address(client_ip)
    except ValueError:
        return False

    for item in allowed_list:
        clean_item = str(item).strip()
        if not clean_item:
            continue

        if clean_item == "localhost":
            if client_addr.is_loopback:
                return True
            continue

        try:
            network = ipaddress.ip_network(clean_item, strict=False)
            if client_addr in network:
                return True
        except ValueError:
            if client_ip == clean_item:
                return True

    return False


def verify_ip_access() -> str:
    """접속자의 공인 IP를 화이트리스트와 비교하여 검증합니다.
    1. Streamlit 헤더에서 공인 IP(CF-Connecting-IP, X-Forwarded-For) 추출
    2. URL 쿼리 파라미터 '_client_ip' (브라우저 외부 공인 IP API 조회 결과) 확인
    3. 둘 다 없거나 사설 IP인 경우, 브라우저에서 직접 외부 IP 조회(api.ipify.org) 실행
    4. 미허용 IP일 경우 화면 렌더링 즉시 차단(st.stop())
    """
    if "security" not in st.secrets:
        raise ValueError(".streamlit/secrets.toml 내 [security] 섹션이 누락되었습니다.")

    security_conf = st.secrets["security"]
    if "allowed_ips" not in security_conf:
        raise ValueError(".streamlit/secrets.toml 내 [security] 섹션에 'allowed_ips' 키가 누락되었습니다.")

    raw_allowed = security_conf["allowed_ips"]
    if isinstance(raw_allowed, str):
        allowed_ips = [ip.strip() for ip in raw_allowed.split(",") if ip.strip()]
    elif isinstance(raw_allowed, (list, tuple)):
        allowed_ips = [str(ip).strip() for ip in raw_allowed if str(ip).strip()]
    else:
        raise ValueError(".streamlit/secrets.toml 내 'allowed_ips' 값은 리스트 또는 쉼표 구분 문자열이어야 합니다.")

    # 1. 브라우저에서 외부 IP 조회하여 URL 쿼리로 전달한 값 확인
    query_ip = st.query_params.get("_client_ip", "").strip()

    # 2. 서버 헤더에서 공인 IP 추출
    header_public_ip = get_client_ip_from_headers()

    # 최종 공인 IP 결정
    if header_public_ip and not is_private_ip(header_public_ip):
        client_ip = header_public_ip
    elif query_ip and not is_private_ip(query_ip):
        client_ip = query_ip
    else:
        # 헤더에서도 공인 IP가 안 잡힌 경우(10.x 사설 IP만 있는 경우),
        # 브라우저에서 직접 외부 API(api.ipify.org)로 공인 IP를 조회하여 URL에 주입
        fallback_ip = get_client_ip_fallback()

        # 브라우저에서 직접 공인 IP를 조회하여 리로드하는 스크립트 실행
        html_code = """
        <script>
            (async function() {
                try {
                    const res = await fetch('https://api.ipify.org?format=json', { timeout: 3000 });
                    if (res.ok) {
                        const data = await res.json();
                        if (data && data.ip) {
                            const url = new URL(window.location.href);
                            if (url.searchParams.get('_client_ip') !== data.ip) {
                                url.searchParams.set('_client_ip', data.ip);
                                window.location.replace(url.toString());
                            }
                        }
                    }
                } catch (e) {
                    // 외부 IP 조회 실패 시 fallback
                }
            })();
        </script>
        <div style="font-family:sans-serif; padding:12px; font-size:13px; color:#64748b; text-align:center;">
            접속자 공인 IP 확인 중...
        </div>
        """
        components.html(html_code, height=45)

        # fallback_ip로 임시 설정하되, allowed_ips에 로컬/사설이 포함되어 있다면 통과
        client_ip = fallback_ip

    # 화이트리스트 검증
    if not is_ip_allowed(client_ip, allowed_ips):
        # 디버깅 헤더 정보 추출
        debug_headers = {}
        if hasattr(st, "context") and hasattr(st.context, "headers"):
            debug_headers = {
                k: st.context.headers.get(k)
                for k in ["CF-Connecting-IP", "X-Forwarded-For", "X-Real-IP", "Host"]
                if st.context.headers.get(k)
            }

        st.error(f"접근이 허용되지 않은 IP입니다. (감지된 IP: {client_ip if client_ip else '확인 불가'})")
        if debug_headers:
            st.caption(f"프록시 헤더 정보: {debug_headers}")
        st.stop()

    return client_ip
