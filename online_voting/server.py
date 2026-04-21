import argparse
import socket
from typing import Iterable, Tuple

from .protocol import MESSAGE_SIZE, ProtocolError, decode_message, encode_message, validate_vote_message
from .voting_store import VotingStore


class VotingServer:
    def __init__(self, host: str, port: int, candidates: Iterable[str]) -> None:
        self.address: Tuple[str, int] = (host, port)
        self.store = VotingStore.from_candidates(candidates)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def serve_forever(self) -> None:
        self.socket.bind(self.address)
        print(f"[server] listening on {self.address[0]}:{self.address[1]}")
        print(f"[server] candidates: {', '.join(self.store.candidates)}")

        while True:
            try:
                data, client_address = self.socket.recvfrom(MESSAGE_SIZE)
                response = self._handle_message(data)
                self.socket.sendto(encode_message(response), client_address)
            except OSError as exc:
                print(f"[server] socket error: {exc}")

    def _handle_message(self, data: bytes) -> dict:
        try:
            message = decode_message(data)
            vote = validate_vote_message(message)
            totals = self.store.cast_vote(voter_id=vote["voter_id"], candidate=vote["candidate"])
        except (ProtocolError, ValueError) as exc:
            return {"status": "error", "message": str(exc)}

        self._print_live_results(totals)
        return {
            "status": "ok",
            "message": "Vote recorded.",
            "totals": totals,
            "total_voters": self.store.total_votes,
        }

    def _print_live_results(self, totals: dict) -> None:
        results_line = " | ".join(f"{candidate}: {count}" for candidate, count in totals.items())
        print(f"[server] live results -> {results_line}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="UDP online voting server")
    parser.add_argument("--host", default="127.0.0.1", help="Host address to bind")
    parser.add_argument("--port", type=int, default=9999, help="UDP port to bind")
    parser.add_argument(
        "--candidates",
        nargs="+",
        required=True,
        help="Space-separated candidate names",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    server = VotingServer(host=args.host, port=args.port, candidates=args.candidates)
    server.serve_forever()


if __name__ == "__main__":
    main()
