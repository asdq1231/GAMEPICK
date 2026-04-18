import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI

app = FastAPI()

# 보안 및 연결 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

class SearchQuery(BaseModel):
    query: str

# 1. 메인 화면: 접속하자마자 스팀 스타일의 카드들이 보이게 함
@app.get("/", response_class=HTMLResponse)
async def read_index():
    return """
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <title>GAMEPICK | Explore</title>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.css" />
        <style>
            :root { --s-dark: #171a21; --s-blue: #1b2838; --s-light: #66c0f4; --s-green: #a3d200; }
            body { font-family: 'Pretendard', sans-serif; background: #1b2838; color: #fff; margin: 0; padding-bottom: 50px; }
            nav { background: var(--s-dark); padding: 15px 10%; display: flex; align-items: center; gap: 20px; border-bottom: 1px solid #333; }
            .logo { font-size: 1.5rem; font-weight: 900; color: #fff; text-decoration: none; letter-spacing: 2px; }
            .search-input { background: #316282; border: none; padding: 10px 15px; border-radius: 3px; color: #fff; width: 300px; outline: none; }
            
            .container { max-width: 1100px; margin: 40px auto; padding: 0 20px; }
            .section-title { font-size: 1.1rem; color: var(--s-light); margin-bottom: 20px; text-transform: uppercase; letter-spacing: 1px; }
            
            /* 게임 그리드 레이아웃 */
            .game-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 20px; }
            .game-card { background: rgba(0,0,0,0.3); border-radius: 4px; overflow: hidden; cursor: pointer; transition: 0.3s; border: 1px solid transparent; }
            .game-card:hover { transform: translateY(-5px); border-color: var(--s-light); background: rgba(0,0,0,0.5); }
            .game-card img { width: 100%; height: 140px; object-fit: cover; }
            .card-info { padding: 15px; }
            .card-title { font-weight: bold; font-size: 1.1rem; margin-bottom: 5px; }
            .card-tag { color: var(--s-green); font-size: 0.85rem; font-weight: bold; }

            /* 상세 정보 팝업(모달) */
            #detail-view { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.9); display: none; z-index: 1000; overflow-y: auto; }
            .detail-box { max-width: 900px; margin: 50px auto; background: var(--s-blue); border-radius: 8px; position: relative; border: 1px solid #333; }
            .close-btn { position: absolute; top: 15px; right: 20px; font-size: 2rem; cursor: pointer; }
            .video-wrap { position: relative; padding-bottom: 56.25%; height: 0; }
            .video-wrap iframe { position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: none; }
            .detail-text { padding: 30px; line-height: 1.7; }
            .btn-link { display: inline-block; background: var(--s-green); color: #000; padding: 12px 25px; border-radius: 4px; font-weight: bold; text-decoration: none; margin-top: 15px; }
        </style>
    </head>
    <body>
        <nav>
            <a href="/" class="logo">GAMEPICK</a>
            <input type="text" id="gameInput" class="search-input" placeholder="게임 검색 후 엔터..." onkeypress="if(event.keyCode==13) searchGame()">
        </nav>

        <div class="container">
            <h2 class="section-title">지금 가장 핫한 게임</h2>
            <div class="game-grid">
                <div class="game-card" onclick="quickSearch('엘든 링')">
                    <img src="https://shared.fastly.steamstatic.com/store_item_assets/steam/apps/1245620/header.jpg">
                    <div class="card-info"><div class="card-title">ELDEN RING</div><div class="card-tag">압도적으로 긍정적</div></div>
                </div>
                <div class="game-card" onclick="quickSearch('팰월드')">
                    <img src="https://shared.fastly.steamstatic.com/store_item_assets/steam/apps/1623730/header.jpg">
                    <div class="card-info"><div class="card-title">Palworld</div><div class="card-tag">매우 긍정적</div></div>
                </div>
                <div class="game-card" onclick="quickSearch('몬스터 헌터 와일즈')">
                    <img src="https://shared.fastly.steamstatic.com/store_item_assets/steam/apps/2246340/header.jpg">
                    <div class="card-info"><div class="card-title">Monster Hunter Wilds</div><div class="card-tag">출시 예정</div></div>
                </div>
            </div>
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
                content.innerHTML = "<p style='padding:50px; text-align:center;'>AI가 실시간 영상과 정보를 가져오는 중입니다...</p>";

                try {
                    const res = await fetch("/search", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ query: query })
                    });
                    const data = await res.json();
                    content.innerHTML = data.result;
                } catch(e) { content.innerHTML = "<p>에러 발생!</p>"; }
            }
        </script>
    </body>
    </html>
    """

@app.post("/search")
async def search_game(data: SearchQuery):
    try:
        # GPT에게 영상, 상세정보, 스팀 링크를 포함한 HTML을 생성하도록 명령
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "너는 스팀 페이지 전문가야. 게임의 유튜브 트레일러(iframe), 상세 설명, 스팀 상점 페이지로 가는 하이퍼링크를 포함한 HTML을 작성해줘."},
                {"role": "user", "content": f"'{data.query}' 게임의 상세 정보를 영상과 함께 보여줘."}
            ]
        )
        return {"result": response.choices[0].message.content}
    except Exception as e:
        return {"result": str(e)}
