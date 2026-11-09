import ipaddress
import streamlit as st
from streamlit.runtime import get_instance
from streamlit.runtime.scriptrunner import get_script_run_ctx


def get_client_ip() -> str:
    """접속자의 클라이언트 IP 주소를 추출합니다.
    1. 프록시 / 로드밸런서 헤더 (X-Forwarded-For, X-Real-IP)
    2. Streamlit 1.45+ 공식 st.context.ip_address
    3. Tornado 런타임 세션 request.remote_ip (로컬 루프백 호환)
    """
    # 1. 프록시 헤더 확인
    if hasattr(st, "context") and hasattr(st.context, "headers"):
        headers = st.context.headers
        xff = headers.get("X-Forwarded-For")
        if xff:
            return xff.split(",")[0].strip()
        x_real_ip = headers.get("X-Real-IP")
        if x_real_ip:
            return x_real_ip.strip()

    # 2. st.context.ip_address 확인 (Streamlit 1.45.0+)
    if hasattr(st, "context") and getattr(st.context, "ip_address", None):
        return str(st.context.ip_address).strip()

    # 3. Tornado 세션의 remote_ip 확인
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

    # localhost 문자열 호환
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
            # CIDR 대역 또는 단일 IP 처리
            network = ipaddress.ip_network(clean_item, strict=False)
            if client_addr in network:
                return True
        except ValueError:
            # 문자열 직접 비교
            if client_ip == clean_item:
                return True

    return False


def verify_ip_access() -> str:
    """접속자의 IP를 화이트리스트와 비교하여 검증합니다.
    - .streamlit/secrets.toml 내 [security] allowed_ips 참조 (기본값 설정 금지 원칙 준수)
    - 허용되지 않은 경우 화면 렌더링을 즉시 중단(st.stop())합니다.
    - 허용된 경우 정상 접속된 client_ip를 반환합니다.
    """
    # 기본값 금지 원칙 준수: 키 누락 시 ValueError 발생
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

    client_ip = get_client_ip()

    if not is_ip_allowed(client_ip, allowed_ips):
        st.error(f"접근이 허용되지 않은 IP입니다. (접속 IP: {client_ip if client_ip else '확인 불가'})")
        st.stop()

    return client_ip
