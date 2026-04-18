import os
import requests
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# API 키 설정 (보안을 위해 환경 변수 사용 권장)
# Render의 Environment 변수에 넣으면 os.getenv가 읽어옵니다.
OPENAI_KEY = os.getenv("OPENAI_API_KEY", "sk-여기에_실제_키를_넣으셔도_됩니다")
client = OpenAI(api_key=OPENAI_KEY)

class MapleAnalysisRequest(BaseModel):
    charName: str
    targetStat: str
    budgetMezo: str
    mesoPrice: str # 1억당 메포 가격

@app.get("/", response_class=HTMLResponse)
async def read_index():
    return """
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <title>Maple Asset Intelligence | GAMEPICK</title>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.css" />
        <style>
            :root { --bg: #0d1117; --orange: #f39c12; --text: #c9d1d9; }
            body { font-family: 'Pretendard', sans-serif; background: var(--bg); color: var(--text); padding: 40px 20px; display: flex; flex-direction: column; align-items: center; }
            .container { width: 100%; max-width: 700px; background: #161b22; border: 1px solid #30363d; border-radius: 12px; padding: 30px; }
            input { width: 100%; padding: 12px; margin: 10px 0; background: #0d1117; border: 1px solid #30363d; color: #fff; border-radius: 6px; box-sizing: border-box; }
            button { width: 100%; background: var(--orange); color: #000; border: none; padding: 16px; border-radius: 8px; font-weight: 800; cursor: pointer; margin-top: 10px; }
            #result { margin-top: 30px; padding: 20px; border-radius: 10px; background: #0d1117; display: none; line-height: 1.8; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1 style="color:var(--orange); text-align:center;">🍁 메이플 AI 경제/보스 시뮬레이터</h1>
            <input type="text" id="charName" placeholder="캐릭터 닉네임 (넥슨 API 연동 준비)">
            <input type="text" id="targetStat" placeholder="목표 주스탯 (예: 45000)">
            <input type="text" id="budgetMezo" placeholder="보유 예산 (단위: 억 메소)">
            <input type="text" id="mesoPrice" placeholder="현재 메포 시세 (1억당 가격, 예: 2500)">
            <button onclick="runAnalysis()">경제 분석 및 시세 예측 시작</button>
            <div id="result"></div>
        </div>
        <script>
            async function runAnalysis() {
                const resDiv = document.getElementById("result");
                resDiv.style.display = "block";
                resDiv.innerHTML = "AI가 옥션 시세와 메포 환율을 대조 분석 중입니다...";

                const data = {
                    charName: document.getElementById("charName").value,
                    targetStat: document.getElementById("targetStat").value,
                    budgetMezo: document.getElementById("budgetMezo").value,
                    mesoPrice: document.getElementById("mesoPrice").value
                };

                const res = await fetch("/analyze-complex", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(data)
                });
                const result = await res.json();
                resDiv.innerHTML = result.report;
            }
        </script>
    </body>
    </html>
    """

@app.post("/analyze-complex")
async def analyze_complex(data: MapleAnalysisRequest):
    try:
        # 실제로는 여기서 넥슨 API를 호출하여 데이터를 가져오는 로직이 들어갑니다.
        # 현재는 OpenAI를 통해 경제 시뮬레이션을 수행합니다.
        prompt = f"""
        메이플스토리 경제 전문가로서 분석해줘.
        - 캐릭터: {data.charName}
        - 목표 스탯: {data.targetStat}
        - 예산: {data.budgetMezo}억 메소
        - 현재 메포 시세: 1억당 {data.mesoPrice}메포
        
        다음 내용을 HTML 형식으로 작성해:
        1. [현금 효율]: 현재 환율 기준, 메소 구매 vs 메포 강화 중 무엇이 이득인지.
        2. [보스 가이드]: 이 예산으로 템셋팅 시 잡을 수 있는 보스와 주간 결정석 수익 예상.
        3. [시세 예측]: 현재가 매수 적기인지, 이벤트(선데이 등)를 기다려야 하는지.
        4. [효율적 루트]: 템값 방어가 잘 되는 아이템군 추천.
        """
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": "You are a professional MapleStory economy analyst."},
                      {"role": "user", "content": prompt}]
        )
        return {"report": response.choices[0].message.content}
    except Exception as e:
        return {"report": f"<div style='color:red;'>에러 발생: {str(e)}</div>"}
