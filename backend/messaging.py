from database.database import find_friend


MAX_MESSAGE_LENGTH = 2000


def prepare_message(recipient_name: str, message: str):
    message = message.strip()

    if not message:
        raise ValueError("Message cannot be empty.")

    if len(message) > MAX_MESSAGE_LENGTH:
        raise ValueError(
            f"Message cannot exceed {MAX_MESSAGE_LENGTH} characters."
        )

    friend = find_friend(recipient_name)

    if friend is None:
        raise ValueError("Recipient is not registered.")

    return {
        "discord_user_id": int(friend["discord_user_id"]),
        "display_name": friend["display_name"],
        "message": message,
    }