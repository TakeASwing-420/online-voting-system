import argparse
import socket
from typing import List, Tuple

from .protocol import MESSAGE_SIZE, decode_message, encode_message


class VotingClient:
    def __init__(self, server_host: str, server_port: int, voter_id: str) -> None:
        self.server_address: Tuple[str, int] = (server_host, server_port)
        self.voter_id = voter_id
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.settimeout(3)

    def send_vote(self, candidate: str) -> dict:
        payload = {"type": "vote", "voter_id": self.voter_id, "candidate": candidate}
        self.socket.sendto(encode_message(payload), self.server_address)
        response_data, _ = self.socket.recvfrom(MESSAGE_SIZE)
        return decode_message(response_data)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="UDP online voting client")
    parser.add_argument("--host", default="127.0.0.1", help="Voting server host")
    parser.add_argument("--port", type=int, default=9999, help="Voting server UDP port")
    parser.add_argument("--voter-id", required=True, help="Unique voter id")
    parser.add_argument(
        "--candidates",
        nargs="+",
        default=["Alice", "Bob", "Charlie"],
        help="Candidate list shown in prompt (must match server)",
    )
    return parser.parse_args()


def prompt_choice(candidates: List[str]) -> str:
    for idx, candidate in enumerate(candidates, start=1):
        print(f"{idx}. {candidate}")
    selected = input("Select candidate number (or q to quit): ").strip().lower()
    if selected == "q":
        raise KeyboardInterrupt
    if not selected.isdigit():
        raise ValueError("Please enter a valid number.")
    index = int(selected) - 1
    if index < 0 or index >= len(candidates):
        raise ValueError("Selection is out of range.")
    return candidates[index]


def main() -> None:
    args = parse_args()
    client = VotingClient(server_host=args.host, server_port=args.port, voter_id=args.voter_id)

    print(f"[client] connected to {args.host}:{args.port} as voter '{args.voter_id}'")
    while True:
        try:
            candidate = prompt_choice(args.candidates)
            response = client.send_vote(candidate)
            print(f"[client] response: {response}")
        except KeyboardInterrupt:
            print("\n[client] exiting.")
            break
        except Exception as exc:
            print(f"[client] error: {exc}")


if __name__ == "__main__":
    main()

