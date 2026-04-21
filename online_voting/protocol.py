import json
from typing import Any, Dict

MESSAGE_SIZE = 4096


class ProtocolError(ValueError):
    """Raised when a message does not follow the expected protocol."""


def encode_message(payload: Dict[str, Any]) -> bytes:
    return json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def decode_message(raw_data: bytes) -> Dict[str, Any]:
    try:
        data = json.loads(raw_data.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ProtocolError("Invalid JSON message.") from exc

    if not isinstance(data, dict):
        raise ProtocolError("Message must be a JSON object.")
    return data


def validate_vote_message(message: Dict[str, Any]) -> Dict[str, str]:
    msg_type = message.get("type")
    candidate = message.get("candidate")
    voter_id = message.get("voter_id")

    if msg_type != "vote":
        raise ProtocolError("Only vote messages are supported.")
    if not isinstance(candidate, str) or not candidate.strip():
        raise ProtocolError("candidate must be a non-empty string.")
    if not isinstance(voter_id, str) or not voter_id.strip():
        raise ProtocolError("voter_id must be a non-empty string.")

    return {"type": "vote", "candidate": candidate.strip(), "voter_id": voter_id.strip()}

