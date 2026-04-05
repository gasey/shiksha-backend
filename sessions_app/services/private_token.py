import json
from datetime import timedelta

from django.conf import settings
from livekit.api import AccessToken, VideoGrants


def generate_private_token(user, session, display_name=None):
    token = AccessToken(
        settings.LIVEKIT_API_KEY,
        settings.LIVEKIT_API_SECRET,
    )

    token.with_identity(str(user.id))

    # display name
    if display_name is None:
        profile = getattr(user, "profile", None)
        if profile and getattr(profile, "full_name", None):
            display_name = profile.full_name
        else:
            display_name = user.get_full_name() or user.username

    token.with_name(display_name)

    # 🔥 BOTH CAN SPEAK
    token.with_metadata(json.dumps({
        "role": "participant",  # 🔥 no presenter/viewer split
        "type": "private_session",
        "user_id": str(user.id),
    }))

    token.with_ttl(timedelta(hours=2))

    room_name = session.room_name
    if not room_name:
        raise ValueError("Session has no room_name")

    # 🔥 EVERYONE CAN PUBLISH
    grants = VideoGrants(
        room_join=True,
        room=room_name,
        can_publish=True,   # ✅ both teacher & student
        can_subscribe=True,
    )

    token.with_grants(grants)

    return token.to_jwt()
