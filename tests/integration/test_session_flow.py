from pathlib import Path
from phase_annotator.domain.models import AnnotationInterval, AnnotationSession, VideoInfo
from phase_annotator.domain.ontology import PhaseOntology
from phase_annotator.domain.validation import validate_no_overlaps
from phase_annotator.storage.json_repo import JsonSessionRepository


def test_full_session_lifecycle(tmp_path: Path):
    # 1. Load appendectomy ontology
    ontology = PhaseOntology.default_appendectomy()
    assert len(ontology.phases) == 6

    # 2. Create session for a video case
    video = VideoInfo(video_id="appendectomy_case_101.mp4", duration_ms=300000, fps=30.0)
    session = AnnotationSession(video_info=video, annotator_id="dr_surgeon")

    # 3. Add valid phase intervals
    session.add_interval(AnnotationInterval(start_ms=0, end_ms=15000, phase_id=1, notes="App. identified"))
    session.add_interval(AnnotationInterval(start_ms=15000, end_ms=45000, phase_id=2, notes="Adhesions dissected"))
    session.add_interval(AnnotationInterval(start_ms=45000, end_ms=120000, phase_id=3, notes="Mesoappendix coagulated"))

    # 4. Validate no overlaps
    errors = validate_no_overlaps(session.intervals)
    assert len(errors) == 0

    # 5. Persist to disk atomically
    repo = JsonSessionRepository()
    session_file = tmp_path / "case_101.json"
    repo.save(session, session_file)

    # 6. Re-load from disk and verify integrity
    reloaded_session = repo.load(session_file)
    assert reloaded_session.annotator_id == "dr_surgeon"
    assert len(reloaded_session.intervals) == 3
    assert reloaded_session.intervals[2].notes == "Mesoappendix coagulated"
