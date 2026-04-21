from collections import Counter
from dataclasses import dataclass, field
from threading import RLock
from typing import Dict, Iterable, List


@dataclass
class VotingStore:
    candidates: List[str]
    _vote_by_voter: Dict[str, str] = field(default_factory=dict)
    _vote_counter: Counter = field(default_factory=Counter)
    _lock: RLock = field(default_factory=RLock)

    def __post_init__(self) -> None:
        self.candidates = [candidate.strip() for candidate in self.candidates if candidate.strip()]
        if not self.candidates:
            raise ValueError("At least one candidate is required.")

    def cast_vote(self, voter_id: str, candidate: str) -> Dict[str, int]:
        if candidate not in self.candidates:
            raise ValueError(f"Unknown candidate: {candidate}")

        with self._lock:
            previous_candidate = self._vote_by_voter.get(voter_id)
            if previous_candidate == candidate:
                return self.results()

            if previous_candidate is not None:
                self._vote_counter[previous_candidate] -= 1
                if self._vote_counter[previous_candidate] <= 0:
                    del self._vote_counter[previous_candidate]

            self._vote_by_voter[voter_id] = candidate
            self._vote_counter[candidate] += 1
            return self.results()

    def results(self) -> Dict[str, int]:
        with self._lock:
            return {candidate: int(self._vote_counter.get(candidate, 0)) for candidate in self.candidates}

    @property
    def total_votes(self) -> int:
        with self._lock:
            return len(self._vote_by_voter)

    @classmethod
    def from_candidates(cls, candidates: Iterable[str]) -> "VotingStore":
        return cls(candidates=list(candidates))
