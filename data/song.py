from dataclasses import dataclass, asdict
import json

@dataclass
class Song:
    sid: int
    path: str
    title: str
    artist: str
    album: str
    track_length: float
    sample_rate: int

    def serialize(self) -> str:
        return json.dumps(asdict(self))
    
    @staticmethod
    def deserialize(json_str: str) -> 'Song':
        try:
            data = json.loads(json_str)
            return Song(**data)
        except (json.JSONDecodeError, TypeError) as e:
            raise Exception(f"Failed to deserialize from JSON {json_str}") from e