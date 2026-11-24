import json
import os
from google import genai
from google.genai import types
import streamlit as st

# 1. 리스트 활용: 광고 종류 및 확인 질문 목록
ad_categories = ["화장품", "음식", "다이어트,운동 관련", "일상 물건"]

check_questions = [
    {"question": "정확하게 증명되어있는 증거가 있는가?", "danger_answer": "아니오"},
    {"question": "사용자들의 정보에서 AI의 정황이 있는가?", "danger_answer": "예"},
    {"question": "영상이 AI로 만들어 졌는가?", "danger_answer": "예"},
    {"question": "영상이 두개 이상의 영상으로 짜집기 되었는가?", "danger_answer": "예"},
]


# 2. 함수 활용: 제미나이 AI 자동 분석 + 허위사실 점수 계산 및 최종 판정 메시지 반환
def evaluate_ad_with_ai(category, link):
    # API 키 설정 (환경변수 GEMINI_API_KEY 사용)
    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

    prompt = f"""
    당신은 과장·허위 광고를 판별하는 AI 탐정입니다.
    사용자가 제출한 아래 광고 정보를 분석하여 4가지 질문에 대해 각각 "예" 또는 "아니오"로 판정하고, 짧은 판정 이유를 작성하세요.

    - 광고 종류: {category}
    - 광고 링크: {link}

    질문 목록:
    1. 정확하게 증명되어있는 증거가 있는가?
    2. 사용자들의 정보에서 AI의 정황이 있는가?
    3. 영상이 AI로 만들어 졌는가?
    4. 영상이 두개 이상의 영상으로 짜집기 되었는가?
    """

    # 제미나이 호출 (JSON 구조화 출력)
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema={
                "type": "OBJECT",
                "properties": {
                    "results": {
                        "type": "ARRAY",
                        "items": {
                            "type": "OBJECT",
                            "properties": {
                                "answer": {"type": "STRING", "enum": ["예", "아니오"]},
                                "reason": {"type": "STRING"},
                            },
                            "required": ["answer", "reason"],
                        },
                    }
                },
                "required": ["results"],
            },
        ),
    )

    ai_data = json.loads(response.text)["results"]
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

# 제목 출력
st.title("허위사실 광고, 체포하겠어!")
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

# '분석하기' 버튼 (초기 화면에는 제목, 종류선택, 링크제시, 분석하기 버튼만 표시)
if st.button("분석하기"):
    # 조건문으로 링크 입력 여부 확인
    if ad_link.strip() == "":
        st.warning("광고 링크를 먼저 입력해주세요!")
    else:
        with st.spinner("제미나이 AI가 광고 링크와 정황을 분석 중입니다..."):
            try:
                # 함수를 호출하여 AI 판정 결과, 점수, 판정 메시지 받아오기
                fake_score, final_message, ai_results = evaluate_ad_with_ai(
                    selected_category, ad_link
                )

                st.divider()
                st.subheader("🔍 AI 분석 결과 출력")
                st.write(f"**선택한 광고 종류:** {selected_category}")
                st.write(f"**입력한 광고 링크:** {ad_link}")
                st.write("")

                # 각 질문과 제미나이 AI의 판정 대답 및 이유 출력 (반복문 활용)
                for idx, item in enumerate(check_questions):
                    ans = ai_results[idx]["answer"]
                    reason = ai_results[idx]["reason"]
                    st.write(f"- {item['question']} : **{ans}**")
                    st.caption(f"└ AI 판정 근거: {reason}")
                    st.write("")

                # 점수 및 최종 판정 결과 출력
                st.write(f"### - 허위사실점수: [{fake_score}%]")
                st.write("")

                if fake_score < 50:
                    st.warning(f"### {final_message}")
                else:
                    st.error(f"### {final_message}")

            except Exception as e:
                st.error(f"분석 중 오류가 발생했습니다. API 키 설정을 확인해주세요. ({e})")
