from PySide6.QtWidgets import QInputDialog

from phase_annotator.ui.procedure_selection import prompt_for_procedure


def test_procedure_prompt_returns_registry_key(monkeypatch):
    monkeypatch.setattr(
        QInputDialog,
        "getItem",
        lambda *args, **kwargs: (
            "Laparoscopic cholecystectomy",
            True,
        ),
    )

    assert prompt_for_procedure() == "cholecystectomy"


def test_procedure_prompt_cancel_returns_none(monkeypatch):
    monkeypatch.setattr(
        QInputDialog,
        "getItem",
        lambda *args, **kwargs: ("", False),
    )

    assert prompt_for_procedure() is None
