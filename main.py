from fastapi import FastAPI
from pydantic import BaseModel
import openai
from openai import OpenAI
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI()

# 모든 접속 허용 (프론트엔드 연결 필수 설정)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Render 환경변수에서 API 키를 가져옵니다.
# 'OPENAI_API_KEY'라는 이름으로 등록하셨다면 os.getenv가 자동으로 읽어옵니다.
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

class SearchQuery(BaseModel):
    query: str

# 기본 페이지 (접속 확인용)
@app.get("/")
def read_root():
    return {"message": "서버가 정상적으로 작동 중입니다!", "api_connected": api_key is not None}

@app.post("/search")
async def search_game(data: SearchQuery):
    prompt = f"게임 '{data.query}'에 대한 정보를 HTML 카드 형식으로 요약해줘."

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "너는 깔끔한 정보를 제공하는 게임 큐레이터야."},
                {"role": "user", "content": prompt}
            ]
        )
        return {"result": response.choices[0].message.content}
    except Exception as e:
        return {"result": f"에러 발생: {str(e)}"}
