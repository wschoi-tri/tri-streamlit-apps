import ipaddress
import json
import streamlit as st
import streamlit.components.v1 as components
from streamlit.runtime import get_instance
from streamlit.runtime.scriptrunner import get_script_run_ctx


def is_private_ip(ip_str: str) -> bool:
    """IP가 사설망(10.x, 172.16~31.x, 192.168.x 등) 또는 로컬 루프백 대역인지 판별합니다."""
    if not ip_str:
        return True
    clean_ip = str(ip_str).strip()
    if clean_ip in ["localhost", "127.0.0.1", "::1"]:
        return True
    try:
        addr = ipaddress.ip_address(clean_ip)
        return addr.is_private or addr.is_loopback or addr.is_link_local or addr.is_reserved
    except ValueError:
        return False


def get_public_ip_from_headers() -> str:
    """Streamlit 요청 헤더에서 사설 IP를 철저히 배제하고 순수 외부 공인 IP만 추출합니다."""
    if not (hasattr(st, "context") and hasattr(st.context, "headers")):
        return ""

    headers = st.context.headers

    # 1. Cloudflare / CDN 직접 연결 헤더 (공인 IP)
    for key in ["CF-Connecting-IP", "True-Client-IP", "X-Client-IP"]:
        val = headers.get(key)
        if val:
            ip = val.strip()
            if not is_private_ip(ip):
                return ip

    # 2. X-Forwarded-For 체인에서 사설망(10.x, 172.x, 192.168.x)이 아닌 공인 IP만 검색
    xff = headers.get("X-Forwarded-For")
    if xff:
        candidates = [p.strip() for p in xff.split(",") if p.strip()]
        for cand in candidates:
            if not is_private_ip(cand):
                return cand

    # 3. X-Real-IP (사설망 제외)
    x_real = headers.get("X-Real-IP")
    if x_real:
        ip = x_real.strip()
        if not is_private_ip(ip):
            return ip

    # 4. st.context.ip_address (사설망 제외)
    if getattr(st.context, "ip_address", None):
        ip = str(st.context.ip_address).strip()
        if not is_private_ip(ip):
            return ip

    # 어떤 헤더에도 공인 IP가 없으면 빈 문자열 반환 (10.x.x.x 절대 반환 안 함)
    return ""


def is_ip_allowed(client_ip: str, allowed_list: list[str]) -> bool:
    """단일 IP 또는 CIDR 서브넷 대역과 클라이언트 IP의 일치 여부를 판별합니다."""
    if not client_ip:
        return False

    clean_client = str(client_ip).strip()
    if clean_client in ["localhost", "127.0.0.1", "::1"] and any(
        a in ["localhost", "127.0.0.1", "::1"] for a in allowed_list
    ):
        return True

    try:
        client_addr = ipaddress.ip_address(clean_client)
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
            if clean_client == clean_item:
                return True

    return False


def get_allowed_ips_from_secrets() -> list[str]:
    """secrets.toml에서 allowed_ips 화이트리스트 목록을 로드합니다."""
    if "security" not in st.secrets:
        raise ValueError(".streamlit/secrets.toml 내 [security] 섹션이 누락되었습니다.")

    security_conf = st.secrets["security"]
    if "allowed_ips" not in security_conf:
        raise ValueError(".streamlit/secrets.toml 내 [security] 섹션에 'allowed_ips' 키가 누락되었습니다.")

    raw_allowed = security_conf["allowed_ips"]
    if isinstance(raw_allowed, str):
        return [ip.strip() for ip in raw_allowed.split(",") if ip.strip()]
    elif isinstance(raw_allowed, (list, tuple)):
        return [str(ip).strip() for ip in raw_allowed if str(ip).strip()]
    else:
        raise ValueError(".streamlit/secrets.toml 내 'allowed_ips' 값은 리스트 또는 쉼표 구분 문자열이어야 합니다.")


def verify_ip_access() -> str:
    """접속자의 공인 IP를 화이트리스트와 비교하여 검증합니다.
    - 10.x.x.x, 172.x.x.x, 192.168.x.x 사설망 IP는 검증 대상에서 완전히 제외합니다.
    - 서버 헤더에 공인 IP가 없을 경우 브라우저에서 직접 외부 API(api.ipify.org)로 공인 IP를 확인하여 검증합니다.
    """
    allowed_ips = get_allowed_ips_from_secrets()

    # 1. 서버 헤더에서 순수 공인 IP 추출
    public_ip = get_public_ip_from_headers()

    # 2. 서버 헤더에서 공인 IP를 확인한 경우
    if public_ip:
        if not is_ip_allowed(public_ip, allowed_ips):
            st.error(f"접근이 허용되지 않은 IP입니다. (접속 IP: {public_ip})")
            st.stop()
        return public_ip

    # 3. 로컬 환경 확인 (로컬에서는 헤더가 없거나 loopback임)
    if is_local_environment(allowed_ips):
        return "127.0.0.1"

    # 4. 서버 헤더에 10.x.x.x 사설 IP만 있는 경우 (Streamlit Cloud 환경):
    # 브라우저(클라이언트)가 직접 api.ipify.org를 호출하여 내 실제 공인 IP를 확인하고,
    # 허용 목록에 없으면 화면 전체를 차단하도록 클라이언트 사이드 가드를 렌더링합니다.
    render_client_side_ip_guard(allowed_ips)
    return "VERIFYING_CLIENT_SIDE"


def is_local_environment(allowed_ips: list[str]) -> bool:
    """로컬 개발 환경(localhost, 127.0.0.1) 여부를 판별합니다."""
    if any(a in ["localhost", "127.0.0.1", "::1"] for a in allowed_ips):
        try:
            ctx = get_script_run_ctx()
            if ctx is not None:
                runtime_inst = get_instance()
                if runtime_inst and hasattr(runtime_inst, "_session_mgr"):
                    session_info = runtime_inst._session_mgr.get_session_info(ctx.session_id)
                    if session_info and session_info.client and session_info.client.request:
                        r_ip = str(session_info.client.request.remote_ip or "").strip()
                        if r_ip in ["127.0.0.1", "::1", "localhost"]:
                            return True
        except Exception:
            pass
    return False


def render_client_side_ip_guard(allowed_ips: list[str]):
    """서버에 사설 IP만 잡힐 때, 브라우저에서 직접 공인 IP를 조회하여 검증하는 가드 스크립트."""
    allowed_json = json.dumps(allowed_ips)
    guard_html = f"""
    <script>
        (async function() {{
            const allowedList = {allowed_json};

            function ipToLong(ip) {{
                return ip.split('.').reduce((acc, octet) => (acc << 8) + parseInt(octet, 10), 0) >>> 0;
            }}

            function isIpInCidr(ip, cidr) {{
                if (!cidr.includes('/')) return ip === cidr;
                const [range, bits] = cidr.split('/');
                const mask = ~((1 << (32 - parseInt(bits, 10))) - 1);
                return (ipToLong(ip) & mask) === (ipToLong(range) & mask);
            }}

            function checkAllowed(clientIp) {{
                if (!clientIp) return false;
                for (let pattern of allowedList) {{
                    pattern = String(pattern).trim();
                    if (!pattern) continue;
                    if (pattern === clientIp) return true;
                    if (pattern.includes('/')) {{
                        try {{
                            if (isIpInCidr(clientIp, pattern)) return true;
                        }} catch (e) {{}}
                    }}
                }}
                return false;
            }}

            try {{
                const res = await fetch('https://api.ipify.org?format=json', {{ timeout: 4000 }});
                if (!res.ok) throw new Error('IP 조회 실패');
                const data = await res.json();
                const myIp = (data && data.ip) ? data.ip.trim() : '';

                if (!myIp || !checkAllowed(myIp)) {{
                    // 미허용 IP: 부모 화면 전체를 차단 안내로 덮음
                    const msg = myIp ? `접근이 허용되지 않은 IP입니다. (내 공인 IP: ${{myIp}})` : '접속자 공인 IP를 확인할 수 없어 접속이 차단되었습니다.';
                    if (window.parent && window.parent.document) {{
                        const body = window.parent.document.body;
                        if (body) {{
                            body.innerHTML = `
                                <div style="display:flex; flex-direction:column; align-items:center; justify-content:center; height:100vh; background:#f8fafc; font-family:sans-serif; color:#0f172a; text-align:center; padding:20px;">
                                    <div style="background:#fee2e2; border:1px solid #ef4444; border-radius:12px; padding:32px 40px; max-width:550px; box-shadow:0 4px 12px rgba(0,0,0,0.05);">
                                        <div style="font-size:20px; font-weight:800; color:#b91c1c; margin-bottom:12px;">접근 제한 안내</div>
                                        <div style="font-size:15px; font-weight:600; color:#7f1d1d; line-height:1.5; margin-bottom:16px;">${{msg}}</div>
                                        <div style="font-size:12px; color:#991b1b;">관리자에게 IP 등록을 요청하세요. (.streamlit/secrets.toml)</div>
                                    </div>
                                </div>
                            `;
                        }}
                    }}
                }}
            }} catch (err) {{
                // 외부 IP API 호출 차단 시 안내
                console.error('IP check failed', err);
            }}
        }})();
    </script>
    """
    components.html(guard_html, height=0, width=0)
