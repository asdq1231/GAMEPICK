import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI

app = FastAPI()

# 1. CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. OpenAI 설정
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

# 3. 메이플 분석 데이터 모델
class MapleData(BaseModel):
    currentStat: str     # 현재 주스탯
    targetStat: str      # 목표 주스탯
    budget: str          # 예산 (단위: 억)
    currentItems: str    # 현재 아이템 셋팅 (예: 3카 5앱)
    job: str             # 직업

# 4. 프론트엔드 UI (HTML/CSS/JS)
@app.get("/", response_class=HTMLResponse)
async def read_index():
    return """
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Maple AI Consultant | GAMEPICK B2B</title>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.css" />
        <style>
            :root { 
                --bg: #0f1218; --card: #1c2128; --orange: #ff9d00; --purple: #8b5cf6; --text: #f0f6fc; 
            }
            body { 
                font-family: 'Pretendard', sans-serif; background: var(--bg); color: var(--text); 
                margin: 0; display: flex; flex-direction: column; align-items: center; padding: 40px 20px;
            }
            .header { text-align: center; margin-bottom: 30px; }
            .header h1 { color: var(--orange); margin: 0; font-size: 2rem; }
            .container { 
                width: 100%; max-width: 800px; background: var(--card); border: 1px solid #30363d; 
                border-radius: 12px; padding: 30px; box-shadow: 0 10px 30px rgba(0,0,0,0.5);
            }
            .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 25px; }
            .field { display: flex; flex-direction: column; }
            label { font-size: 0.85rem; margin-bottom: 8px; color: #8b949e; font-weight: 600; }
            input { 
                background: #0d1117; border: 1px solid #30363d; color: #fff; padding: 12px; 
                border-radius: 6px; outline: none; transition: 0.2s;
            }
            input:focus { border-color: var(--orange); }
            button { 
                width: 100%; background: var(--orange); color: #000; border: none; padding: 15px; 
                border-radius: 8px; font-size: 1rem; font-weight: 800; cursor: pointer; transition: 0.3s;
            }
            button:hover { filter: brightness(1.1); transform: translateY(-2px); }
            #loading { display: none; text-align: center; margin-top: 20px; color: var(--orange); font-weight: bold; }
            #result { display: none; margin-top: 30px; background: #0d1117; padding: 25px; border-radius: 10px; border-left: 5px solid var(--orange); line-height: 1.8; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Maple AI 스펙업 컨설턴트</h1>
            <p style="color:#8b949e;">데이터 기반 최저가 고효율 아이템 세팅 제안</p>
        </div>

        <div class="container">
            <div class="grid">
                <div class="field" style="grid-column: span 2;">
                    <label>직업</label>
                    <input type="text" id="job" placeholder="예: 아델, 나이트로드">
                </div>
                <div class="field">
                    <label>현재 주스탯</label>
                    <input type="text" id="currentStat" placeholder="예: 25000">
                </div>
                <div class="field">
                    <label>목표 주스탯</label>
                    <input type="text" id="targetStat" placeholder="예: 35000">
                </div>
                <div class="field">
                    <label>가용 예산 (단위: 억 메소)</label>
                    <input type="text" id="budget" placeholder="예: 100">
                </div>
                <div class="field">
                    <label>현재 템셋팅</label>
                    <input type="text" id="currentItems" placeholder="예: 3카 5앱 9보장">
                </div>
            </div>
            <button onclick="runMapleAnalysis()">AI 정밀 진단 시작</button>
            <div id="loading">메이플 옥션 매물 시세 및 강화 기대값을 계산 중입니다...</div>
            <div id="result"></div>
        </div>

        <script>
            async function runMapleAnalysis() {
                const resultDiv = document.getElementById("result");
                const loading = document.getElementById("loading");
                
                const data = {
                    job: document.getElementById("job").value,
                    currentStat: document.getElementById("currentStat").value,
                    targetStat: document.getElementById("targetStat").value,
                    budget: document.getElementById("budget").value,
                    currentItems: document.getElementById("currentItems").value
                };

                if(!data.job || !data.budget) { alert("직업과 예산은 필수 입력 항목입니다."); return; }

                loading.style.display = "block";
                resultDiv.style.display = "none";

                try {
                    const res = await fetch("/analyze-maple", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify(data)
                    });
                    const responseData = await res.json();
                    resultDiv.innerHTML = responseData.report;
                    resultDiv.style.display = "block";
                } catch(e) {
                    alert("분석 중 오류가 발생했습니다.");
                } finally {
                    loading.style.display = "none";
                }
            }
        </script>
    </body>
    </html>
    """

# 5. 메이플 시뮬레이션 로직
@app.post("/analyze-maple")
async def analyze_maple(data: MapleData):
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": """너는 메이플스토리 경제 및 템셋팅 전문 AI 컨설턴트야.
                사용자가 제공한 직업, 스탯, 예산 정보를 바탕으로 '가장 가성비 좋은 스펙업 경로'를 제안해줘.
                보고서에는 다음 내용이 포함되어야 해:
                1. [현재 상황 진단]: 현재 템셋팅의 문제점 분석
                2. [우선순위 추천]: 예산 내에서 가장 효율이 좋은 부위 교체 순서 (1~3위)
                3. [강화 vs 구매]: 직작(강화)이 유리한 부위와 경매장 구매가 유리한 부위 구분
                4. [기대 결과]: 제안한 세팅 완료 시 예상되는 최종 주스탯 및 보스 레이드 가능 범위
                
                용어는 '추옵', '공마', '잠재', '별(스타포스)', '결정석' 등 유저들이 쓰는 용어를 사용하고, HTML 형식으로 세련되게 작성해줘."""},
                {"role": "user", "content": f"유저 데이터: {data.json()}"}
            ]
        )
        return {"report": response.choices[0].message.content}
    except Exception as e:
        return {"report": f"<p style='color:red;'>에러: {str(e)}</p>"}
