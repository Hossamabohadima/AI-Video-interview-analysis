from fastapi import FastAPI
from api.user import router as user_router 

# 1. Change the Title and the URL path
app = FastAPI(
    title="interviewMe",
    docs_url="/interviewMe",  # This changes http://127.0.0.1:8000/docs to /interviewMe
    redoc_url=None           # Optional: disables the alternative /redoc path
)

app.include_router(user_router)

# 2. Print the custom URL to the terminal
@app.on_event("startup")
async def startup_event():
    print("\n" + "★"*40)
    print("  interviewMe BACKEND IS ACTIVE")
    print("  Access Swagger UI: http://127.0.0.1:8000/interviewMe")
    print("★"*40 + "\n")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)