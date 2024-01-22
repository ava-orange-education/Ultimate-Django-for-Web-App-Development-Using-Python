from accounts.services import issue_jwt_token_from_refresh
from ninja import Router, Schema

router = Router(tags=["accounts"])


class TokenSchema(Schema):
    refresh_token: str


@router.post("/refresh-token", auth=[lambda x: True])
def refresh_token(request, data: TokenSchema):
    try:
        access_token = issue_jwt_token_from_refresh(request.user, data.refresh_token)
        return {"access_token": access_token}
    except Exception:
        return {"error": "Invalid refresh token"}
