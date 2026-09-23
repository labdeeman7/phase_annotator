from PySide6.QtWidgets import QApplication

from phase_annotator import __main__ as entrypoint
from phase_annotator.config import PACKAGED_PROCEDURES


def test_artifact_smoke_check_constructs_every_packaged_procedure(qtbot):
    entrypoint.artifact_smoke_check()


def test_artifact_smoke_argument_uses_noninteractive_path(monkeypatch, qtbot):
    calls = []
    application = QApplication.instance()
    original_stylesheet = application.styleSheet()
    monkeypatch.setattr(entrypoint, "artifact_smoke_check", lambda: calls.append(True))
    monkeypatch.setattr(
        entrypoint,
        "prompt_for_annotator_id",
        lambda: (_ for _ in ()).throw(AssertionError("interactive prompt was opened")),
    )

    try:
        result = entrypoint.main(
            ["phase-annotator", entrypoint.ARTIFACT_SMOKE_ARGUMENT]
        )
    finally:
        application.setStyleSheet(original_stylesheet)

    assert result == 0
    assert calls == [True]


def test_artifact_smoke_check_covers_the_full_registry(monkeypatch, qtbot):
    loaded_keys = []
    real_loader = entrypoint.load_procedure_ontology

    def recording_loader(procedure_key):
        loaded_keys.append(procedure_key)
        return real_loader(procedure_key)

    monkeypatch.setattr(entrypoint, "load_procedure_ontology", recording_loader)

    entrypoint.artifact_smoke_check()

    assert loaded_keys == [procedure.key for procedure in PACKAGED_PROCEDURES]
