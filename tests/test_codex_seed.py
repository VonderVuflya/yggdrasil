"""Codex session seeding: rollout-*.jsonl extraction + project labelling."""

import json
import tempfile
import unittest
from pathlib import Path

from yggdrasil import ygg_seed as s


def _rollout(path: Path) -> None:
    """A minimal but realistic Codex rollout-*.jsonl."""
    lines = [
        {"timestamp": "t", "type": "session_meta",
         "payload": {"id": "x", "cwd": "/Users/me/Projects/acme", "originator": "Codex"}},
        {"timestamp": "t", "type": "event_msg", "payload": {"type": "task_started"}},
        # developer role = AGENTS.md/system injection -> must be dropped
        {"timestamp": "t", "type": "response_item",
         "payload": {"type": "message", "role": "developer",
                     "content": [{"type": "input_text", "text": "system rules here"}]}},
        # user turn whose first part is boilerplate context -> that part dropped, real text kept
        {"timestamp": "t", "type": "response_item",
         "payload": {"type": "message", "role": "user",
                     "content": [{"type": "input_text", "text": "# AGENTS.md instructions for /x"},
                                 {"type": "input_text", "text": "Fix the deploy script please"}]}},
        # assistant turn
        {"timestamp": "t", "type": "response_item",
         "payload": {"type": "message", "role": "assistant",
                     "content": [{"type": "output_text", "text": "Done: rotated the token and redeployed"}]}},
        # reasoning item (no role) -> ignored
        {"timestamp": "t", "type": "response_item",
         "payload": {"type": "reasoning", "summary": [], "content": None}},
    ]
    path.write_text("\n".join(json.dumps(x) for x in lines))


class CodexSeedTest(unittest.TestCase):
    def setUp(self):
        self.f = Path(tempfile.mktemp(suffix=".jsonl", prefix="rollout-"))
        _rollout(self.f)

    def tearDown(self):
        self.f.unlink(missing_ok=True)

    def test_extract_keeps_dialogue_drops_noise(self):
        txt = s._extract_codex_text(self.f)
        self.assertIn("Fix the deploy script please", txt)
        self.assertIn("rotated the token and redeployed", txt)
        # developer system text + AGENTS.md boilerplate must be filtered out
        self.assertNotIn("system rules here", txt)
        self.assertNotIn("# AGENTS.md", txt)

    def test_project_from_cwd(self):
        self.assertEqual(s._codex_project(self.f), "acme")

    def test_project_falls_back(self):
        empty = Path(tempfile.mktemp(suffix=".jsonl"))
        empty.write_text('{"type":"event_msg","payload":{}}')
        try:
            self.assertEqual(s._codex_project(empty), "codex")
        finally:
            empty.unlink(missing_ok=True)

    def test_source_files_uses_explicit_paths(self):
        src = {"kind": "codex", "path": "/x", "paths": [str(self.f)]}
        self.assertEqual(s._source_files(src), [self.f])

    def test_extract_text_routes_codex_by_path(self):
        # a path under .codex/sessions should go through the codex extractor
        d = Path(tempfile.mkdtemp()) / ".codex" / "sessions"
        d.mkdir(parents=True)
        f = d / "rollout-x.jsonl"
        _rollout(f)
        txt = s._extract_text(f)
        self.assertIn("rotated the token", txt)


if __name__ == "__main__":
    unittest.main()
