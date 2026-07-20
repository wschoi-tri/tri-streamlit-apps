import streamlit as st

def main():
    st.set_page_config(page_title="건보료 연봉 계산기", page_icon="💰", layout="centered")
    
    st.title("💰 건강보험료 기준 연봉 역산 계산기")
    st.markdown("급여명세서에 고지된 **본인부담 건강보험료**를 바탕으로 세전 월급과 예상 연봉을 계산합니다.")
    st.caption("*(2026년 요율 7.19% 기준)*")
    st.divider()
    
    # 입력 필드 (기본값 100,000원)
    premium = st.number_input(
        "급여명세서 상의 '건강보험료' 본인부담금을 입력하세요 (원)", 
        min_value=0, 
        value=100000, 
        step=10000,
        format="%d"
    )
    
    # 계산 로직 (본인부담 요율: 3.595%)
    individual_rate = 0.03595
    
    if premium > 0:
        monthly_salary = int(premium / individual_rate)
        annual_salary = monthly_salary * 12
        
        # 결과 시각화
        st.subheader("📊 역산 결과")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric(
                label="월 세전 급여 (보수월액)", 
                value=f"{monthly_salary:,} 원"
            )
        with col2:
            st.metric(
                label="예상 연봉", 
                value=f"약 {annual_salary // 10000:,} 만원",
                delta=f"{annual_salary:,} 원",
                delta_color="off"
            )
            
        st.caption("⚠️ **주의사항:** 식대, 차량유지비 등 비과세 급여는 보수월액 산정에서 제외되므로, 실제 계약하신 총수령 연봉과는 일부 오차가 발생할 수 있습니다.")
    else:
        st.warning("0보다 큰 금액을 입력해주세요.")

if __name__ == "__main__":
    main()
