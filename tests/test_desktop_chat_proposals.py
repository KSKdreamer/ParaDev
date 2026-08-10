from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path

import heavenbase as hb
import pytest

from paradev.desktop import local as desktop_local
from paradev.sdk import Project

PIHC3_ROOT = Path("projects/PIHC3").resolve()
pytestmark = pytest.mark.pihc3


def test_desktop_chat_template_catalog_rejects_divergent_form_projection() -> None:
    class DivergentProject:
        def templates(self, **_filters: object) -> dict[str, object]:
            return {
                "templates": [
                    {
                        "id": "demo:idea/basic",
                        "family": "idea",
                        "args": {"title": {"required": True}},
                        "form": {"fields": []},
                    }
                ],
                "source_roots": [],
            }

    with pytest.raises(RuntimeError, match="form fields do not match"):
        desktop_local._chat_module_template_catalog(DivergentProject())


def test_desktop_chat_template_catalog_preserves_extension_references() -> None:
    _, catalog = desktop_local._chat_module_template_catalog(Project.load(PIHC3_ROOT))
    templates = {str(row["template_id"]): row for row in catalog["templates"] if isinstance(row, Mapping)}

    assert templates["pihc3:focus/basic"]["values"]["tree"]["reference"] == {
        "kind": "collection",
        "family": "focus",
    }
    assert templates["pihc3:decision/basic"]["values"]["category_id"]["reference"] == {
        "kind": "collection",
        "family": "decision",
    }


def test_desktop_chat_source_catalog_rejects_malformed_registry_choice() -> None:
    sections = [
        {
            "id": "main",
            "controls": [
                {
                    "id": "mode",
                    "label": "Mode",
                    "control": "choice",
                    "value": "safe",
                    "patch": {"op": "replace-json-scalar", "path": ["mode"]},
                    "choices": [{"label": "Safe", "value": "safe"}, "invalid"],
                }
            ],
        }
    ]

    with pytest.raises(RuntimeError, match="returned an invalid choice"):
        desktop_local._chat_source_form_controls(sections, "src/modules/demo/def.json")


def _chat_with_structured_response(
    monkeypatch: pytest.MonkeyPatch,
    value: object,
    *,
    role: str = "create-module",
    sources: Sequence[Mapping[str, object]] | None = None,
) -> tuple[dict[str, object], dict[str, object]]:
    captured: dict[str, object] = {}

    class FakeSpec:
        def runtime(self) -> dict[str, str]:
            return {"base_url": "https://api.deepseek.com/v1"}

    class FakeLLM:
        spec = FakeSpec()

        def __init__(self, **kwargs: object) -> None:
            captured["llm_kwargs"] = kwargs

        def chat(self, prompt: str, **kwargs: object) -> object:
            captured["prompt"] = prompt
            captured["chat_kwargs"] = kwargs
            return value

    class FakeLLMEngine:
        def apply(self, spec: object) -> dict[str, object]:
            assert spec is FakeLLM.spec
            return dict(FakeLLM.spec.runtime())

    monkeypatch.setenv("PARADEV_CHAT_PROPOSAL_TEST_KEY", "present")
    monkeypatch.setattr(hb, "LLM", FakeLLM)
    monkeypatch.setattr(hb, "LLMEngine", FakeLLMEngine)
    payload = desktop_local.desktop_chat(
        provider="deepseek",
        model="deepseek-v4-flash",
        gateway="openai",
        prompt="Create five ideas named A, B, C, D, and E with CIC modifiers of 2%, 5%, 8%, 12%, and 16%.",
        role=role,
        project_root=str(PIHC3_ROOT),
        sources=sources,
        key_env="PARADEV_CHAT_PROPOSAL_TEST_KEY",
        base_url="https://api.deepseek.com/v1",
        preset="chat",
    )
    return payload, captured


def test_desktop_create_module_chat_returns_real_pihc3_batch_dry_plan(
    monkeypatch: pytest.MonkeyPatch,
    cm_paradev_lock: object,
) -> None:
    modules = [
        {
            "template_id": "pihc3:idea/basic",
            "object_id": object_id,
            "values": {"title": object_id, "cic": cic},
        }
        for object_id, cic in zip(("A", "B", "C", "D", "E"), (0.02, 0.05, 0.08, 0.12, 0.16))
    ]
    response = {
        "reply": "I prepared a five-idea dry plan for review.",
        "proposal": {
            "operation_id": "module.create_batch",
            "modules": modules,
        },
    }
    original_create_modules = Project.create_modules
    calls: list[dict[str, object]] = []

    def tracked_create_modules(
        project: Project,
        requests: Sequence[Mapping[str, object]],
        **kwargs: object,
    ) -> dict[str, object]:
        calls.append(
            {
                "project_root": str(project.root),
                "requests": [dict(request) for request in requests],
                "kwargs": dict(kwargs),
            }
        )
        return original_create_modules(project, requests, **kwargs)

    monkeypatch.setattr(Project, "create_modules", tracked_create_modules)
    module_roots = [PIHC3_ROOT / "src" / "modules" / "idea" / object_id for object_id in ("A", "B", "C", "D", "E")]
    assert all(not path.exists() for path in module_roots)

    payload, captured = _chat_with_structured_response(monkeypatch, response)

    assert len(calls) == 1
    assert calls[0]["project_root"] == str(PIHC3_ROOT)
    assert calls[0]["requests"] == modules
    assert calls[0]["kwargs"] == {"source_root": None, "write": False}
    assert captured["llm_kwargs"]["max_tokens"] == 32_768
    assert captured["chat_kwargs"] == {
        "response_format": {"type": "json_object"},
        "include": "structured",
    }
    prompt = str(captured["prompt"])
    assert "pihc3:idea/basic" in prompt
    assert '"label": "Title"' in prompt
    assert ('"description": "Preferred-language display name used by the readable ' 'module folder name and `main.loc`."') in prompt
    assert '"description_source": "generated"' in prompt
    assert '"label": "Civilian industry factor"' in prompt
    assert '"description": "Decimal factory-output modifier; use 0.02 for 2%."' in prompt
    assert '"description_source": "declared"' in prompt
    assert '"default": "0"' in prompt
    assert '"advanced": true' in prompt
    assert "including units and examples" in prompt
    assert "Do not include write, force, plan_hash" in prompt
    assert payload["status"] == "ready", payload
    assert payload["reply"] == "I prepared a five-idea dry plan for review."
    proposal = payload["proposal"]
    assert isinstance(proposal, Mapping)
    assert proposal["schema"] == "paradev.desktop.ai-chat-proposal.v1"
    assert proposal["operationId"] == "module.create_batch"
    assert proposal["familyId"] == "idea"
    assert proposal["requests"] == modules
    plan = proposal["plan"]
    assert isinstance(plan, Mapping)
    assert proposal["sourceRoot"] == plan["source_root"]
    assert plan["blocked"] is False
    assert plan["applied"] is False
    assert plan["written"] is False
    assert plan["requested_count"] == 5
    assert len(str(plan["plan_hash"])) == 64
    assert plan["counts"] == {
        "create": 5,
        "created": 0,
        "unchanged": 0,
        "blocked": 0,
    }
    plan_modules = plan["modules"]
    assert isinstance(plan_modules, Sequence)
    assert sum(len(row["files"]) for row in plan_modules if isinstance(row, Mapping)) == 10
    assert [(row["template_id"], row["family"], row["object_id"]) for row in plan_modules if isinstance(row, Mapping)] == [
        ("pihc3:idea/basic", "idea", object_id) for object_id in ("A", "B", "C", "D", "E")
    ]
    assert [row["values"]["cic"] for row in plan_modules if isinstance(row, Mapping)] == [
        "0.02",
        "0.05",
        "0.08",
        "0.12",
        "0.16",
    ]
    assert {row["values"]["language"] for row in plan_modules if isinstance(row, Mapping)} == {"zh"}
    assert all(not path.exists() for path in module_roots)


def test_desktop_create_module_chat_returns_real_pihc3_collection_dry_plan(
    monkeypatch: pytest.MonkeyPatch,
    cm_paradev_lock: object,
) -> None:
    collection_id = "C99_AI_REVIEW"
    response = {
        "reply": "I prepared a focus-tree collection plan for review.",
        "proposal": {
            "operation_id": "collection.scaffold",
            "template_id": "pihc3:focus-tree/basic",
            "collection_id": collection_id,
            "values": {
                "country_tag": "C99",
                "title": "AI Review Tree",
            },
        },
    }
    original_scaffold_collection = Project.scaffold_collection
    calls: list[dict[str, object]] = []

    def tracked_scaffold_collection(
        project: Project,
        template_id: str,
        requested_collection_id: str,
        **kwargs: object,
    ) -> dict[str, object]:
        calls.append(
            {
                "project_root": str(project.root),
                "template_id": template_id,
                "collection_id": requested_collection_id,
                "kwargs": dict(kwargs),
            }
        )
        return original_scaffold_collection(
            project,
            template_id,
            requested_collection_id,
            **kwargs,
        )

    monkeypatch.setattr(Project, "scaffold_collection", tracked_scaffold_collection)
    collection_roots = list((PIHC3_ROOT / "src" / "collections" / "focus").glob(f"{collection_id}*"))
    assert collection_roots == []

    payload, captured = _chat_with_structured_response(monkeypatch, response)

    assert calls == [
        {
            "project_root": str(PIHC3_ROOT),
            "template_id": "pihc3:focus-tree/basic",
            "collection_id": collection_id,
            "kwargs": {
                "source_root": None,
                "values": {
                    "country_tag": "C99",
                    "title": "AI Review Tree",
                },
                "write": False,
                "force": False,
            },
        }
    ]
    prompt = str(captured["prompt"])
    assert '"operation_id":"collection.scaffold"' in prompt
    assert '"kind": "collection"' in prompt
    assert "pihc3:focus-tree/basic" in prompt
    assert payload["status"] == "ready", payload
    proposal = payload["proposal"]
    assert isinstance(proposal, Mapping)
    assert proposal["operationId"] == "collection.scaffold"
    assert proposal["familyId"] == "focus"
    assert proposal["request"] == {
        "template_id": "pihc3:focus-tree/basic",
        "collection_id": collection_id,
        "values": {
            "country_tag": "C99",
            "title": "AI Review Tree",
        },
    }
    plan = proposal["plan"]
    assert isinstance(plan, Mapping)
    assert plan["schema"] == "paradev.sdk.collection_scaffold.v1"
    assert plan["kind"] == "collection"
    assert plan["blocked"] is False
    assert plan["written"] is False
    assert plan["collection_id"] == collection_id
    assert proposal["sourceRoot"] == plan["source_root"]
    assert len(str(plan["plan_hash"])) == 64
    replanned = original_scaffold_collection(
        Project.load(PIHC3_ROOT),
        str(proposal["request"]["template_id"]),
        str(proposal["request"]["collection_id"]),
        source_root=str(proposal["sourceRoot"]),
        values=proposal["request"]["values"],
        write=False,
        force=False,
    )
    assert replanned["plan_hash"] == plan["plan_hash"]
    assert list((PIHC3_ROOT / "src" / "collections" / "focus").glob(f"{collection_id}*")) == []


def test_desktop_edit_selection_chat_returns_real_pihc3_guided_dry_plan(
    monkeypatch: pytest.MonkeyPatch,
    cm_paradev_lock: object,
) -> None:
    relative_path = "src/modules/idea/IDEA_ALL_ARTIFACT_CROWN_OF_GROVER - " "发现法器：格罗弗皇冠/def.txt"
    source_path = PIHC3_ROOT / relative_path
    original_text = source_path.read_text(encoding="utf-8")
    response = {
        "reply": "I prepared a guarded crystal-resource edit for review.",
        "proposal": {
            "operation_id": "module.source_form_update_batch",
            "updates": [
                {
                    "source_path": relative_path,
                    "values": {"pdx-control-002": 2},
                }
            ],
        },
    }
    original_plan_source_form_updates = Project.plan_source_form_updates
    calls: list[list[dict[str, object]]] = []

    def tracked_plan_source_form_updates(
        project: Project,
        updates: Sequence[Mapping[str, object]],
    ) -> dict[str, object]:
        calls.append([dict(update) for update in updates])
        return original_plan_source_form_updates(project, updates)

    monkeypatch.setattr(
        Project,
        "plan_source_form_updates",
        tracked_plan_source_form_updates,
    )

    payload, captured = _chat_with_structured_response(
        monkeypatch,
        response,
        role="edit-selection",
        sources=[
            {
                "kind": "source",
                "label": "Crown of Grover idea",
                "path": relative_path,
                "familyId": "idea",
                "moduleId": "idea/IDEA_ALL_ARTIFACT_CROWN_OF_GROVER",
            }
        ],
    )

    assert len(calls) == 1
    assert calls[0] == [
        {
            "source_path": str(source_path),
            "values": {"pdx-control-002": 2},
        }
    ]
    prompt = str(captured["prompt"])
    assert '"operation_id":"module.source_form_update_batch"' in prompt
    assert relative_path in prompt
    assert '"id": "pdx-control-002"' in prompt
    assert '"label": "Country resource crystals"' in prompt
    assert '"current": 1' in prompt
    assert "never writes files" in prompt
    assert captured["chat_kwargs"] == {
        "response_format": {"type": "json_object"},
        "include": "structured",
    }
    assert payload["status"] == "ready", payload
    assert payload["reply"] == response["reply"]
    proposal = payload["proposal"]
    assert isinstance(proposal, Mapping)
    assert proposal["schema"] == "paradev.desktop.ai-chat-proposal.v1"
    assert proposal["operationId"] == "module.source_form_update_batch"
    assert proposal["familyId"] == "idea"
    assert proposal["requests"] == [
        {
            "source_path": relative_path,
            "module_id": "idea/IDEA_ALL_ARTIFACT_CROWN_OF_GROVER",
            "values": {"pdx-control-002": 2},
            "control_labels": {
                "pdx-control-002": "Country resource crystals",
            },
        }
    ]
    plan = proposal["plan"]
    assert isinstance(plan, Mapping)
    assert plan["schema"] == "paradev.source-form-update-batch.v1"
    assert plan["project_id"] == "PIHC3"
    assert plan["changed"] is True
    assert plan["counts"] == {"requested": 1, "changed": 1, "unchanged": 0}
    assert len(plan["source_edits"]) == 1
    update = plan["updates"][0]
    assert update["module_id"] == "idea/IDEA_ALL_ARTIFACT_CROWN_OF_GROVER"
    assert update["changes"] == [
        {
            "control_id": "pdx-control-002",
            "previous": 1,
            "value": 2,
        }
    ]
    assert "country_resource_crystals = 2" in update["source_edit"]["text"]
    assert source_path.read_text(encoding="utf-8") == original_text


@pytest.mark.parametrize(
    ("proposal", "detail"),
    [
        (
            {
                "operation_id": "module.source_form_update_batch",
                "updates": [
                    {
                        "source_path": "src/modules/idea/NOT_SELECTED/def.txt",
                        "values": {"pdx-control-002": 2},
                    }
                ],
            },
            "unknown or unselected source_path",
        ),
        (
            {
                "operation_id": "module.source_form_update_batch",
                "updates": [
                    {
                        "source_path": ("src/modules/idea/IDEA_ALL_ARTIFACT_CROWN_OF_GROVER - " "发现法器：格罗弗皇冠/def.txt"),
                        "values": {"not-a-control": 2},
                    }
                ],
            },
            "unknown Guided control",
        ),
        (
            {
                "operation_id": "module.source_form_update_batch",
                "updates": [],
                "write": True,
            },
            "unsupported fields: write",
        ),
    ],
)
def test_desktop_edit_selection_chat_rejects_untrusted_updates_before_planning(
    monkeypatch: pytest.MonkeyPatch,
    cm_paradev_lock: object,
    proposal: dict[str, object],
    detail: str,
) -> None:
    relative_path = "src/modules/idea/IDEA_ALL_ARTIFACT_CROWN_OF_GROVER - " "发现法器：格罗弗皇冠/def.txt"

    def unexpected_plan(
        _project: Project,
        _updates: Sequence[Mapping[str, object]],
    ) -> dict[str, object]:
        raise AssertionError("invalid model output must not invoke the source planner")

    monkeypatch.setattr(Project, "plan_source_form_updates", unexpected_plan)
    payload, _captured = _chat_with_structured_response(
        monkeypatch,
        {"reply": "Unsafe edit.", "proposal": proposal},
        role="edit-selection",
        sources=[
            {
                "kind": "source",
                "label": "Crown of Grover idea",
                "path": relative_path,
            }
        ],
    )

    assert payload["status"] == "error"
    assert detail in str(payload["detail"])
    assert "proposal" not in payload


def test_desktop_edit_selection_chat_rejects_unsaved_source_before_llm(
    monkeypatch: pytest.MonkeyPatch,
    cm_paradev_lock: object,
) -> None:
    relative_path = "src/modules/idea/IDEA_ALL_ARTIFACT_CROWN_OF_GROVER - " "发现法器：格罗弗皇冠/def.txt"

    with pytest.raises(ValueError, match="Apply or discard unsaved source drafts"):
        _chat_with_structured_response(
            monkeypatch,
            {"reply": "Should not run.", "proposal": None},
            role="edit-selection",
            sources=[
                {
                    "kind": "source",
                    "label": "Dirty idea",
                    "path": relative_path,
                    "content": "ideas = {}\n",
                }
            ],
        )


@pytest.mark.parametrize(
    ("proposal", "detail"),
    [
        (
            {
                "operation_id": "collection.scaffold",
                "template_id": "pihc3:idea/basic",
                "collection_id": "INVALID_KIND",
                "values": {},
            },
            "requires a collection template",
        ),
        (
            {
                "operation_id": "collection.scaffold",
                "template_id": "pihc3:focus-tree/basic",
                "collection_id": "UNSAFE",
                "values": {"title": "Unsafe"},
                "write": True,
            },
            "unsupported fields: write",
        ),
        (
            {
                "operation_id": "collection.scaffold",
                "template_id": "pihc3:focus-tree/basic",
                "collection_id": "UNKNOWN_VALUE",
                "values": {"not_a_field": "unsafe"},
            },
            "uses unknown template value 'not_a_field'",
        ),
    ],
)
def test_desktop_create_module_chat_rejects_untrusted_collection_before_planning(
    monkeypatch: pytest.MonkeyPatch,
    cm_paradev_lock: object,
    proposal: dict[str, object],
    detail: str,
) -> None:
    def unexpected_scaffold_collection(
        _project: Project,
        _template_id: str,
        _collection_id: str,
        **_kwargs: object,
    ) -> dict[str, object]:
        raise AssertionError("invalid model output must not invoke the collection planner")

    monkeypatch.setattr(Project, "scaffold_collection", unexpected_scaffold_collection)
    payload, _captured = _chat_with_structured_response(
        monkeypatch,
        {
            "reply": "Unsafe collection.",
            "proposal": proposal,
        },
    )

    assert payload["status"] == "error"
    assert detail in str(payload["detail"])
    assert "proposal" not in payload


def test_desktop_create_module_chat_allows_reply_without_proposal(
    monkeypatch: pytest.MonkeyPatch,
    cm_paradev_lock: object,
) -> None:
    def unexpected_create_modules(
        _project: Project,
        _requests: Sequence[Mapping[str, object]],
        **_kwargs: object,
    ) -> dict[str, object]:
        raise AssertionError("reply-only chat must not invoke the module planner")

    monkeypatch.setattr(Project, "create_modules", unexpected_create_modules)

    payload, _captured = _chat_with_structured_response(
        monkeypatch,
        {
            "reply": "Tell me which kind of module you want to create.",
            "proposal": None,
        },
    )

    assert payload["status"] == "ready"
    assert payload["reply"] == "Tell me which kind of module you want to create."
    assert "proposal" not in payload


@pytest.mark.parametrize(
    ("response", "detail"),
    [
        (
            [],
            "AI module-plan response must be a JSON object.",
        ),
        (
            {
                "reply": "Missing proposal field.",
            },
            "AI module-plan response is missing required fields: proposal.",
        ),
        (
            {
                "reply": "Unsafe proposal.",
                "proposal": {
                    "operation_id": "module.create_batch",
                    "write": True,
                    "modules": [],
                },
            },
            "AI module-plan proposal has unsupported fields: write.",
        ),
        (
            {
                "reply": "Unsafe request.",
                "proposal": {
                    "operation_id": "module.create_batch",
                    "modules": [
                        {
                            "template_id": "pihc3:idea/basic",
                            "object_id": "A",
                            "values": {"title": "A"},
                            "force": True,
                            "plan_hash": "untrusted",
                            "write": True,
                        }
                    ],
                },
            },
            "AI module-plan request 0 has unsupported fields: force, plan_hash, write.",
        ),
        (
            {
                "reply": "Unknown template.",
                "proposal": {
                    "operation_id": "module.create_batch",
                    "modules": [
                        {
                            "template_id": "pihc3:idea/unknown",
                            "object_id": "A",
                            "values": {"title": "A"},
                        }
                    ],
                },
            },
            "uses unknown or unavailable template_id 'pihc3:idea/unknown'.",
        ),
        (
            {
                "reply": "Unknown value.",
                "proposal": {
                    "operation_id": "module.create_batch",
                    "modules": [
                        {
                            "template_id": "pihc3:idea/basic",
                            "object_id": "A",
                            "values": {"title": "A", "unsupported": 1},
                        }
                    ],
                },
            },
            "uses unknown template value 'unsupported'.",
        ),
        (
            {
                "reply": "Mixed families.",
                "proposal": {
                    "operation_id": "module.create_batch",
                    "modules": [
                        {
                            "template_id": "pihc3:idea/basic",
                            "object_id": "A",
                            "values": {"title": "A"},
                        },
                        {
                            "template_id": "pihc3:achievement/basic",
                            "object_id": "B",
                            "values": {},
                        },
                    ],
                },
            },
            "must use templates from exactly one module family.",
        ),
        (
            {
                "reply": "Duplicate ids.",
                "proposal": {
                    "operation_id": "module.create_batch",
                    "modules": [
                        {
                            "template_id": "pihc3:idea/basic",
                            "object_id": "A",
                            "values": {"title": "A"},
                        },
                        {
                            "template_id": "pihc3:idea/basic",
                            "object_id": "a",
                            "values": {"title": "A again"},
                        },
                    ],
                },
            },
            "duplicates module id idea/a.",
        ),
        (
            {
                "reply": "Nested value.",
                "proposal": {
                    "operation_id": "module.create_batch",
                    "modules": [
                        {
                            "template_id": "pihc3:idea/basic",
                            "object_id": "A",
                            "values": {"title": "A", "cic": None},
                        }
                    ],
                },
            },
            "value 'cic' must be a JSON scalar other than null",
        ),
        (
            {
                "reply": "Non-finite value.",
                "proposal": {
                    "operation_id": "module.create_batch",
                    "modules": [
                        {
                            "template_id": "pihc3:idea/basic",
                            "object_id": "A",
                            "values": {"title": "A", "cic": float("nan")},
                        }
                    ],
                },
            },
            "value 'cic' must be a JSON scalar other than null",
        ),
        (
            {
                "reply": "Unsafe integer value.",
                "proposal": {
                    "operation_id": "module.create_batch",
                    "modules": [
                        {
                            "template_id": "pihc3:idea/basic",
                            "object_id": "A",
                            "values": {"title": "A", "cic": 9_007_199_254_740_992},
                        }
                    ],
                },
            },
            "value 'cic' must be a JSON scalar other than null",
        ),
        (
            {
                "reply": "Unsafe integral float value.",
                "proposal": {
                    "operation_id": "module.create_batch",
                    "modules": [
                        {
                            "template_id": "pihc3:idea/basic",
                            "object_id": "A",
                            "values": {"title": "A", "cic": 9_007_199_254_740_992.0},
                        }
                    ],
                },
            },
            "value 'cic' must be a JSON scalar other than null",
        ),
        (
            {
                "reply": "Oversized batch.",
                "proposal": {
                    "operation_id": "module.create_batch",
                    "modules": [
                        {
                            "template_id": "pihc3:idea/basic",
                            "object_id": f"IDEA_{index}",
                            "values": {"title": f"Idea {index}"},
                        }
                        for index in range(257)
                    ],
                },
            },
            "cannot contain more than 256 modules.",
        ),
    ],
)
def test_desktop_create_module_chat_rejects_untrusted_proposals_before_planning(
    monkeypatch: pytest.MonkeyPatch,
    cm_paradev_lock: object,
    response: object,
    detail: str,
) -> None:
    def unexpected_create_modules(
        _project: Project,
        _requests: Sequence[Mapping[str, object]],
        **_kwargs: object,
    ) -> dict[str, object]:
        raise AssertionError("invalid model output must not invoke the module planner")

    monkeypatch.setattr(Project, "create_modules", unexpected_create_modules)

    payload, _captured = _chat_with_structured_response(monkeypatch, response)

    assert payload["status"] == "error"
    assert payload["reply"] == ""
    assert detail in str(payload["detail"])
    assert "proposal" not in payload
