import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI

app = FastAPI()

# 보안 및 CORS 설정 (Render 배포 시 필수)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

api_key = "sk-...B74A"
client = OpenAI(api_key=api_key)

class SearchQuery(BaseModel):
    query: str

@app.get("/", response_class=HTMLResponse)
async def read_index():
    return """
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>GAMEPICK | AI Experience Matcher</title>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.css" />
        <style>
            :root { 
                --gp-bg: #0b0e14; 
                --gp-card: #161b22; 
                --gp-purple: #8b5cf6; 
                --gp-purple-light: #a78bfa;
                --gp-green: #10b981; 
                --gp-text: #e2e8f0;
                --gp-sidebar: #12151e;
            }
            
            body { 
                font-family: 'Pretendard', sans-serif; 
                background: var(--gp-bg); 
                color: var(--gp-text); 
                margin: 0; 
                display: flex; 
                flex-direction: column; 
                height: 100vh;
                overflow: hidden;
            }
            
            /* 상단 네비게이션 */
            nav { 
                background: #000; 
                padding: 15px 5%; 
                display: flex; 
                align-items: center; 
                justify-content: space-between; 
                border-bottom: 1px solid #333; 
                z-index: 100;
            }
            .logo { 
                font-size: 1.6rem; 
                font-weight: 900; 
                color: var(--gp-purple); 
                text-decoration: none; 
                letter-spacing: 2px;
                text-transform: uppercase;
            }
            .search-box { 
                background: #1c2128; 
                border: 1px solid #30363d;
                padding: 8px 20px; 
                border-radius: 20px; 
                display: flex; 
                align-items: center;
                transition: 0.3s;
            }
            .search-box:focus-within { border-color: var(--gp-purple); box-shadow: 0 0 10px rgba(139, 92, 246, 0.2); }
            .search-box input { background: transparent; border: none; color: #fff; outline: none; width: 300px; }

            /* 전체 레이아웃 */
            .wrapper { display: flex; flex: 1; overflow: hidden; }
            
            /* 좌측 사이드바 */
            .sidebar { 
                width: 240px; 
                background: var(--gp-sidebar); 
                padding: 40px 20px; 
                border-right: 1px solid rgba(255,255,255,0.05);
            }
            .side-title { color: var(--gp-purple-light); font-size: 0.8rem; font-weight: bold; text-transform: uppercase; margin-bottom: 20px; letter-spacing: 1px; }
            .side-menu { list-style: none; padding: 0; margin-bottom: 40px; }
            .side-menu li { padding: 12px 0; color: #8b949e; cursor: pointer; transition: 0.2s; font-size: 0.95rem; }
            .side-menu li:hover { color: #fff; transform: translateX(8px); }

            /* 우측 메인 영역 */
            .main-content { flex: 1; padding: 40px; overflow-y: auto; background: radial-gradient(at top left, #1a1033 0%, #0b0e14 40%); }
            .hero-section { text-align: center; margin-bottom: 50px; }
            .hero-section h1 { font-size: 2.2rem; margin-bottom: 15px; }
            
            /* 플레이 성향 태그 */
            .tag-group { display: flex; justify-content: center; gap: 10px; flex-wrap: wrap; margin-top: 20px; }
            .play-tag { 
                background: rgba(139, 92, 246, 0.1); 
                border: 1px solid rgba(139, 92, 246, 0.3);
                padding: 8px 18px; 
                border-radius: 30px; 
                font-size: 0.85rem; 
                cursor: pointer; 
                transition: 0.3s;
            }
            .play-tag:hover { background: var(--gp-purple); color: #fff; transform: scale(1.05); }

            /* 게임 그리드 */
            .game-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 25px; margin-top: 40px; }
            .game-card { 
                background: var(--gp-card); 
                border-radius: 12px; 
                overflow: hidden; 
                cursor: pointer; 
                transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275); 
                border: 1px solid rgba(255,255,255,0.05);
                position: relative;
            }
            .game-card:hover { transform: translateY(-10px); border-color: var(--gp-purple); box-shadow: 0 10px 30px rgba(139, 92, 246, 0.2); }
            .game-card img { width: 100%; height: 160px; object-fit: cover; }
            .card-info { padding: 20px; }
            .card-title { font-weight: bold; font-size: 1.1rem; margin-bottom: 8px; }
            .card-tag { color: var(--gp-green); font-size: 0.85rem; font-weight: bold; }
            .discount { position: absolute; top: 10px; right: 10px; background: var(--gp-green); color: #000; padding: 3px 8px; border-radius: 4px; font-weight: 900; font-size: 0.8rem; }

            /* 상세 분석 모달 */
            #detail-view { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.95); display: none; z-index: 2000; overflow-y: auto; }
            .detail-box { max-width: 850px; margin: 50px auto; background: var(--gp-bg); border-radius: 15px; border: 1px solid #333; overflow: hidden; position: relative; }
            .close-btn { position: absolute; top: 20px; right: 25px; font-size: 2.5rem; cursor: pointer; color: #fff; z-index: 10; }
            .video-wrap { position: relative; padding-bottom: 56.25%; height: 0; background: #000; }
            .video-wrap iframe { position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: none; }
            .detail-text { padding: 40px; line-height: 1.8; }
            .btn-buy { display: block; background: var(--gp-purple); color: #fff; padding: 18px; text-align: center; border-radius: 8px; font-weight: bold; text-decoration: none; margin-top: 25px; transition: 0.3s; }
            .btn-buy:hover { filter: brightness(1.2); transform: scale(1.02); }
        </style>
    </head>
    <body>
        <nav>
            <a href="/" class="logo">GAMEPICK</a>
            <div class="search-box">
                <input type="text" id="gameInput" placeholder="하고 싶은 플레이를 입력해보세요..." onkeypress="if(event.keyCode==13) searchGame()">
            </div>
        </nav>

        <div class="wrapper">
            <aside class="sidebar">
                <div class="side-title">장르 카테고리</div>
                <ul class="side-menu">
                    <li onclick="quickSearch('액션')">액션</li>
                    <li onclick="quickSearch('RPG')">RPG</li>
                    <li onclick="quickSearch('전략')">전략</li>
                    <li onclick="quickSearch('시뮬레이션')">시뮬레이션</li>
                </ul>
                <div class="side-title">플레이 성향</div>
                <ul class="side-menu">
                    <li onclick="quickSearch('무료 게임')">무료 플레이</li>
                    <li onclick="quickSearch('할인 중인 게임')">특별 할인</li>
                    <li onclick="quickSearch('AI 추천 게임')">AI 추천</li>
                </ul>
            </aside>

            <main class="main-content">
                <div class="hero-section">
                    <h1>무엇을 플레이하고 싶나요?</h1>
                    <div class="tag-group">
                        <span class="play-tag" onclick="quickSearch('타격감 폭발하는 액션 게임')">#타격감_폭발</span>
                        <span class="play-tag" onclick="quickSearch('친구랑 밤샐 수 있는 협동 게임')">#친구랑_함께</span>
                        <span class="play-tag" onclick="quickSearch('조용히 힐링하는 농장 게임')">#힐링_필요</span>
                        <span class="play-tag" onclick="quickSearch('머리 터지는 고난이도 전략')">#뇌섹남_전략</span>
                        <span class="play-tag" onclick="quickSearch('압도적인 그래픽의 오픈월드')">#그래픽_깡패</span>
                    </div>
                </div>

                <div class="game-grid">
                    <div class="game-card" onclick="quickSearch('엘든 링')">
                        <div class="discount">-30%</div>
                        <img src="https://shared.fastly.steamstatic.com/store_item_assets/steam/apps/1245620/header.jpg">
                        <div class="card-info"><div class="card-title">ELDEN RING</div><div class="card-tag">#정복감 #고난이도</div></div>
                    </div>
                    <div class="game-card" onclick="quickSearch('팰월드')">
                        <img src="https://shared.fastly.steamstatic.com/store_item_assets/steam/apps/1623730/header.jpg">
                        <div class="card-info"><div class="card-title">Palworld</div><div class="card-tag">#생존 #수집</div></div>
                    </div>
                    <div class="game-card" onclick="quickSearch('사이버펑크 2077')">
                        <div class="discount">-50%</div>
                        <img src="https://shared.fastly.steamstatic.com/store_item_assets/steam/apps/1091500/header.jpg">
                        <div class="card-info"><div class="card-title">Cyberpunk 2077</div><div class="card-tag">#오픈월드 #미래</div></div>
                    </div>
                    <div class="game-card" onclick="quickSearch('몬스터 헌터 와일즈')">
                        <img src="https://shared.fastly.steamstatic.com/store_item_assets/steam/apps/2246340/header.jpg">
                        <div class="card-info"><div class="card-title">Monster Hunter Wilds</div><div class="card-tag">#사냥 #대작</div></div>
                    </div>
                </div>
            </main>
        </div>

        <div id="detail-view">
            <div class="detail-box">
                <span class="close-btn" onclick="closeDetail()">&times;</span>
                <div id="detail-content"></div>
            </div>
        </div>

        <script>
            function closeDetail() { document.getElementById('detail-view').style.display = 'none'; }
            function quickSearch(name) { document.getElementById('gameInput').value = name; searchGame(); }
            
            async function searchGame() {
                const query = document.getElementById("gameInput").value;
                const view = document.getElementById("detail-view");
                const content = document.getElementById("detail-content");
                if(!query) return;

                view.style.display = 'block';
                content.innerHTML = "<div style='padding:100px; text-align:center;'><h2>AI가 최적의 게임 경험을 분석 중입니다...</h2></div>";

                try {
                    const res = await fetch("/search", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ query: query })
                    });
                    const data = await res.json();
                    content.innerHTML = data.result;
                } catch(e) { content.innerHTML = "<div style='padding:100px;'>서버 연결에 실패했습니다.</div>"; }
            }
        </script>
    </body>
    </html>
    """

@app.post("/search")
async def search_game(data: SearchQuery):
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": """너는 게임 경험 큐레이터야. 사용자가 원하는 '플레이 스타일'을 입력하면 다음을 포함한 HTML 결과물을 만들어줘:
                1. 상단: 해당 게임의 '공식 트레일러' 유튜브 iframe (가장 몰입감 있는 영상으로)
                2. 중간: 게임 제목, 핵심 특징, 그리고 '왜 이 게임이 당신의 플레이 스타일에 적합한지'에 대한 AI 분석 리포트.
                3. 하단: [스팀 상점 페이지로 이동] 버튼 (class='btn-buy' 사용).
                디자인은 보라색 포인트가 들어간 다크 모드 스타일로 세련되게 작성해줘."""},
                {"role": "user", "content": f"내 플레이 성향 분석 요청: {data.query}"}
            ]
        )
        return {"result": response.choices[0].message.content}
    except Exception as e:
        return {"result": f"에러 발생: {str(e)}"}
