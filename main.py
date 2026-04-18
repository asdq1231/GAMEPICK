import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI

app = FastAPI()

# 1. CORS 설정 (브라우저 통신 허용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. OpenAI 클라이언트 설정
# 주의: Render의 Environment Variables에 OPENAI_API_KEY가 반드시 등록되어 있어야 합니다.
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

# 3. 데이터 모델 정의 (기획자가 입력할 수치들)
class EconomyData(BaseModel):
    itemName: str
    attackPower: int
    itemPrice: int
    dropRate: float
    userLevel: int

# 4. 메인 페이지 (UI)
@app.get("/", response_class=HTMLResponse)
async def read_index():
    return """
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>GAMEPICK B2B | AI Economy Simulator</title>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.css" />
        <style>
            :root { 
                --bg: #0b0e14; --card: #161b22; --purple: #8b5cf6; --accent: #10b981; --text: #e2e8f0; 
            }
            body { 
                font-family: 'Pretendard', sans-serif; background: var(--bg); color: var(--text); 
                margin: 0; display: flex; flex-direction: column; min-height: 100vh; align-items: center; padding: 40px 20px;
            }
            .header { text-align: center; margin-bottom: 40px; }
            .header h1 { font-size: 2.2rem; color: var(--purple); margin: 0; }
            .header p { color: #8b949e; margin-top: 10px; }

            .container { 
                width: 100%; max-width: 900px; background: var(--card); border: 1px solid #30363d; 
                border-radius: 16px; padding: 40px; box-shadow: 0 20px 50px rgba(0,0,0,0.5);
            }
            
            /* 입력 폼 스타일 */
            .input-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 25px; margin-bottom: 30px; }
            .input-group { display: flex; flex-direction: column; }
            .input-group label { font-size: 0.9rem; font-weight: 600; margin-bottom: 8px; color: #acb2b8; }
            .input-group input { 
                background: #0d1117; border: 1px solid #30363d; color: #fff; padding: 12px 15px; 
                border-radius: 8px; font-size: 1rem; outline: none; transition: 0.2s;
            }
            .input-group input:focus { border-color: var(--purple); box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.2); }

            button { 
                width: 100%; background: var(--purple); color: #fff; border: none; padding: 18px; 
                border-radius: 12px; font-size: 1.1rem; font-weight: 700; cursor: pointer; transition: 0.3s;
            }
            button:hover { filter: brightness(1.2); transform: translateY(-2px); }

            /* 분석 결과 창 */
            #loading { display: none; text-align: center; margin-top: 30px; }
            #result-area { display: none; margin-top: 40px; border-top: 1px solid #30363d; padding-top: 30px; line-height: 1.7; }
            
            /* AI 보고서 내 HTML 스타일링 */
            .report-card { background: #0d1117; border-radius: 10px; padding: 25px; border-left: 4px solid var(--purple); }
            .stat-badge { display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 0.8rem; font-weight: bold; background: var(--purple); margin-bottom: 10px; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>GAMEPICK <span style="color:#fff;">B2B</span></h1>
            <p>AI 기반 수리적 게임 밸런스 및 경제 시뮬레이터</p>
        </div>

        <div class="container">
            <div class="input-grid">
                <div class="input-group" style="grid-column: span 2;">
                    <label>아이템/시스템 명칭</label>
                    <input type="text" id="itemName" placeholder="예: 드래곤 슬레이어 검">
                </div>
                <div class="input-group">
                    <label>주요 능력치 (공격력/방어력 등)</label>
                    <input type="number" id="attackPower" placeholder="150">
                </div>
                <div class="input-group">
                    <label>설정 가격 (게임 재화)</label>
                    <input type="number" id="itemPrice" placeholder="50000">
                </div>
                <div class="input-group">
                    <label>드롭/획득 확률 (0.001 ~ 1.0)</label>
                    <input type="text" id="dropRate" placeholder="0.005">
                </div>
                <div class="input-group">
                    <label>권장 사용 레벨</label>
                    <input type="number" id="userLevel" placeholder="50">
                </div>
            </div>
            <button onclick="runSimulation()">AI 시뮬레이션 및 보고서 생성</button>

            <div id="loading">
                <div style="color: var(--purple); font-size: 1.2rem; font-weight: bold;">AI가 가상 플레이어 10,000명을 투입하여 경제를 분석 중입니다...</div>
            </div>

            <div id="result-area"></div>
        </div>

        <script>
            async function runSimulation() {
                const resultArea = document.getElementById("result-area");
                const loading = document.getElementById("loading");
                
                const data = {
                    itemName: document.getElementById("itemName").value,
                    attackPower: parseInt(document.getElementById("attackPower").value),
                    itemPrice: parseInt(document.getElementById("itemPrice").value),
                    dropRate: parseFloat(document.getElementById("dropRate").value),
                    userLevel: parseInt(document.getElementById("userLevel").value)
                };

                if(!data.itemName) { alert("항목 이름을 입력해주세요."); return; }

                loading.style.display = "block";
                resultArea.style.display = "none";

                try {
                    const res = await fetch("/analyze-economy", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify(data)
                    });
                    const result = await res.json();
                    resultArea.innerHTML = result.report;
                    resultArea.style.display = "block";
                } catch(e) {
                    alert("서버 통신 에러가 발생했습니다.");
                } finally {
                    loading.style.display = "none";
                }
            }
        </script>
    </body>
    </html>
    """

# 5. AI 분석 로직
@app.post("/analyze-economy")
async def analyze_economy(data: EconomyData):
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": """너는 세계 최고의 게임 경제 기획자이자 수리 밸런스 전문가야. 
                사용자가 입력한 게임 아이템/시스템 데이터를 바탕으로 다음 내용을 포함한 전문적인 컨설팅 보고서를 HTML로 작성해줘.
                
                1. [핵심 요약] 아이템의 가치와 현재 기획의 적절성 평가.
                2. [수리적 분석] 드롭률과 가격을 고려했을 때 유저가 이 아이템을 얻기 위해 평균적으로 소요되는 시간(Playtime)과 재화 가치 산출.
                3. [밸런스 경고] 이 수치가 유지될 경우 발생할 수 있는 '오버밸런스' 혹은 '버려지는 아이템' 가능성 경고.
                4. [경제 전망] 인플레이션에 미치는 영향 (재화 회수 효율성 등).
                5. [최종 권고안] 기획자가 수정해야 할 스탯이나 가격의 구체적인 수치 제안.
                
                디자인: 보라색 포인트를 사용하고, 전문 용어를 섞어서 격식 있게 작성해줘."""},
                {"role": "user", "content": f"기획 데이터: {data.json()}"}
            ]
        )
        return {"report": response.choices[0].message.content}
    except Exception as e:
        return {"report": f"<p style='color:red;'>분석 실패: {str(e)}</p>"}
