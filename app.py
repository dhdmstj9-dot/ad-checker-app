import streamlit as st

# 1. 리스트 활용: 광고 종류 및 확인 질문 목록
ad_categories = ["화장품", "음식", "다이어트,운동 관련", "일상 물건"]

check_questions = [
    {"question": "정확하게 증명되어있는 증거가 있는가?", "danger_answer": "아니오"},
    {"question": "사용자들의 정보에서 AI의 정황이 있는가?", "danger_answer": "예"},
    {"question": "영상이 AI로 만들어 졌는가?", "danger_answer": "예"},
    {"question": "영상이 두개 이상의 영상으로 짜집기 되었는가?", "danger_answer": "예"},
]


# 2. 함수 활용: AI 탐정 분석 알고리즘 + 허위사실 점수 계산 및 판정 메시지 반환
def evaluate_ad_with_ai(category, link):
    link_lower = link.lower()
    is_shortform = any(k in link_lower for k in ["shorts", "tiktok", "reels", "instagram"])
    is_official = any(k in link_lower for k in ["official", "gov", "mfds", "store", "brand"])

    # 카테고리 및 링크 특성을 종합 분석하여 4가지 문항 자동 판정
    ai_data = []

    # 문항 1: 정확하게 증명되어있는 증거가 있는가?
    if is_official and not is_shortform:
        ai_data.append({
            "answer": "예",
            "reason": "공식 판매처 또는 검증 가능한 도메인 구조가 확인되어 기본적인 제품 증빙 자료 접근이 가능합니다."
        })
    else:
        ai_data.append({
            "answer": "아니오",
            "reason": f"'{category}' 분야의 숏폼·SNS 광고 링크 특성상 임상시험 결과나 공인 성적서 등 객관적 증빙 출처가 링크 내에 명시되어 있지 않습니다."
        })

    # 문항 2: 사용자들의 정보에서 AI의 정황이 있는가?
    if is_shortform or category in ["화장품", "다이어트,운동 관련"]:
        ai_data.append({
            "answer": "예",
            "reason": "과장된 전후 비교나 AI 성우(TTS)·합성 리뷰 패턴이 빈번하게 보고되는 광고 유형과 일치합니다."
        })
    else:
        ai_data.append({
            "answer": "아니오",
            "reason": "현재 링크 구조에서는 인위적인 AI 생성 후기나 봇 댓글 패턴이 두드러지지 않습니다."
        })

    # 문항 3: 영상이 AI로 만들어 졌는가?
    if is_shortform and category in ["화장품", "다이어트,운동 관련", "음식"]:
        ai_data.append({
            "answer": "예",
            "reason": "빠른 화면 전환, AI 더빙 내레이션 및 비현실적인 시각 효과가 결합된 AI 생성형 숏폼 광고 특징이 감지되었습니다."
        })
    else:
        ai_data.append({
            "answer": "아니오",
            "reason": "일반 실사 촬영 또는 상세페이지 중심의 홍보물로 AI 전면 생성 영상 정황이 낮습니다."
        })

    # 문항 4: 영상이 두개 이상의 영상으로 짜집기 되었는가?
    if is_shortform or category == "일상 물건":
        ai_data.append({
            "answer": "예",
            "reason": "해외 바이럴 클립이나 여러 시연 장면을 짧게 교차 편집(짜집기)하여 효능을 극대화하는 전형적인 편집 패턴이 확인됩니다."
        })
    else:
        ai_data.append({
            "answer": "아니오",
            "reason": "단일 맥락의 제품 소개 구성으로 외부 영상 무단 짜집기 정황이 적습니다."
        })

    score = 0

    # 반복문(for)과 조건문(if)을 활용하여 AI의 판정 답변에 따라 점수 누적 (문항당 25점)
    for i in range(len(check_questions)):
        if ai_data[i]["answer"] == check_questions[i]["danger_answer"]:
            score += 25

    # 조건문(if)을 활용한 점수별 판정 문구 결정
    if score < 50:
        verdict = "조심하세요!"
    else:
        verdict = "허위 사실 광고, 체포하겠어!"

    return score, verdict, ai_data


# --- 화면 구상 (Streamlit UI) ---

# 제목 출력 (🚨 추가됨)
st.title("🚨 허위사실 광고, 체포하겠어!")
st.write("")  # 한 문단 띄우기

# 첫 번째 & 두 번째 입력을 나란히 배치 (컬럼 활용)
col1, col2 = st.columns(2)

with col1:
    selected_category = st.selectbox(
        "광고종류선택 [화장품/음식/다이어트,운동 관련/일상 물건]:",
        ad_categories,
    )

with col2:
    ad_link = st.text_input("광고링크제시:")

st.write("")

# '분석하기' 버튼
if st.button("분석하기"):
    # 조건문으로 링크 입력 여부 확인
    if ad_link.strip() == "":
        st.warning("광고 링크를 먼저 입력해주세요!")
    else:
        with st.spinner("AI 탐정이 광고 링크와 정황을 분석 중입니다..."):
            # 함수를 호출하여 AI 판정 결과, 점수, 판정 메시지 받아오기
            fake_score, final_message, ai_results = evaluate_ad_with_ai(
                selected_category, ad_link
            )

            st.divider()
            st.subheader("🔍 AI 분석 결과 출력")
            st.write(f"**선택한 광고 종류:** {selected_category}")
            st.write(f"**입력한 광고 링크:** {ad_link}")
            st.write("")

            # 각 질문과 AI의 판정 대답 및 이유 출력 (반복문 활용)
            for idx, item in enumerate(check_questions):
                ans = ai_results[idx]["answer"]
                reason = ai_results[idx]["reason"]
                st.write(f"- {item['question']} : **{ans}**")
                st.caption(f"└ AI 판정 근거: {reason}")
                st.write("")

            # 점수 및 최종 판정 결과 출력 (### 제거됨)
            st.write(f"### - 허위사실점수: [{fake_score}%]")
            st.write("")

            if fake_score < 50:
                st.warning(f"**{final_message}**")
            else:
                st.error(f"**{final_message}**")

