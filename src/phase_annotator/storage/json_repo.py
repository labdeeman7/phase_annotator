import json
import os
from dataclasses import asdict
from pathlib import Path
from typing import Dict, Any

from phase_annotator.domain.models import AnnotationInterval, AnnotationSession, VideoInfo


class JsonSessionRepository:
    """Handles persistent serialization and deserialization of AnnotationSession objects with atomic file writes."""

    def save(self, session: AnnotationSession, filepath: Path) -> None:
        """
        Saves session data atomically. Writes to a temporary file first, 
        then replaces the target file to prevent partial file corruption.
        """
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert session to dictionary
        data = asdict(session)

        # Temporary file path in same directory for atomic rename
        tmp_filepath = filepath.with_name(f".{filepath.name}.tmp")

        with open(tmp_filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        # Atomic replacement
        os.replace(tmp_filepath, filepath)

    def load(self, filepath: Path) -> AnnotationSession:
        """Loads and reconstructs an AnnotationSession from a JSON file."""
        filepath = Path(filepath)
        if not filepath.exists():
            raise FileNotFoundError(f"Session file not found: {filepath}")

        with open(filepath, "r", encoding="utf-8") as f:
            data: Dict[str, Any] = json.load(f)

        video_info = VideoInfo(**data["video_info"])
        intervals = [AnnotationInterval(**interval_data) for interval_data in data["intervals"]]

        session = AnnotationSession(
            video_info=video_info,
            annotator_id=data["annotator_id"],
            ontology_id=data.get("ontology_id", ""),
            ontology_version=data.get("ontology_version", ""),
            intervals=intervals,
            schema_version=data.get("schema_version", "1.0"),
            created_at=data.get("created_at", 0.0),
            updated_at=data.get("updated_at", 0.0),
        )

        return session
