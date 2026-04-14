from fastapi import APIRouter, HTTPException

from ..schemas.user import LoginRequest, RegistrationRequest, RegistrationResponse
from ..services.user_service import login_user, register_user

router = APIRouter()


@router.post("/auth/signup", response_model=RegistrationResponse, status_code=201)
def signup(payload: RegistrationRequest):
    """
    User signup endpoint. Registers a new user in the system.
    Validates credentials, creates user record, initializes threshold and metric weights.
    Returns the created user information.
    """
    try:
        user = register_user(payload)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if user is None:
        raise HTTPException(status_code=400, detail="Signup failed")

    return {"message": "User registered successfully", "user": user}


@router.post("/auth/login")
def login(payload: LoginRequest):
    """
    User login endpoint. Authenticates user credentials.
    Returns user information if credentials are valid.
    """
    user = login_user(payload.email, payload.password)
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return {"message": "Login successful", "user": user}


@router.get("/reports/{user_id}")
def reports(user_id: int):
    return {"reports": get_reports(user_id)}


@router.post("/reports/compare")
def compare( video1: int,video2: int):
    return {"comparison": compare_reports(video1, video2)}

@router.put("/threshold")
def update_threshold(req: Threshold):
    set_threshold_score(req.user_id, req.score)
    return {"message": "Threshold is set"}


@router.post("/uploadVideo")
def upload(file: UploadFile = File(...), user_id: int = Form(...),video_name: str = Form(...)):
    return upload_video(file, user_id, video_name)



@router.put("/weights")
def update_weights(    user_id: int, weights: Dict[str, float]):
    set_weights(user_id, weights)
    return {"message": "Weights updated"}