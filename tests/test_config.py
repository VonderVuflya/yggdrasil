"""ygg_config: precedence (flag > env > config > default), persistence, typed accessors."""

import importlib
import os
import tempfile
import unittest


class ConfigPrecedenceTest(unittest.TestCase):
    def setUp(self):
        self.home = tempfile.mkdtemp()
        os.environ["YGG_HOME"] = self.home
        for e in ("YGG_DISTILL_URL", "YGG_EMBED_URL", "YGG_DISTILL_TIMEOUT", "YGG_BG_MODEL"):
            os.environ.pop(e, None)
        import yggdrasil.ygg_config as C
        self.C = importlib.reload(C)  # re-evaluate YGG_HOME/CONFIG under the temp dir

    def tearDown(self):
        for e in ("YGG_DISTILL_URL", "YGG_EMBED_URL", "YGG_DISTILL_TIMEOUT", "YGG_BG_MODEL"):
            os.environ.pop(e, None)

    def test_default(self):
        self.assertEqual(self.C.distill_url(), "http://127.0.0.1:11434")
        self.assertEqual(self.C.distill_timeout(), 120)
        self.assertEqual(self.C.bg_model(), "qwen2.5:1.5b")
        self.assertEqual(self.C.source("distill_url"), "default")

    def test_config_layer(self):
        self.C.save({"distill_url": "http://box:11434", "distill_timeout": "240"})
        self.assertEqual(self.C.distill_url(), "http://box:11434")
        self.assertEqual(self.C.distill_timeout(), 240)
        self.assertEqual(self.C.source("distill_url"), "config")

    def test_env_beats_config(self):
        self.C.save({"distill_url": "http://config:11434"})
        os.environ["YGG_EMBED_URL"] = "http://env:11434"
        self.assertEqual(self.C.distill_url(), "http://env:11434")
        self.assertEqual(self.C.source("distill_url"), "env:YGG_EMBED_URL")

    def test_flag_beats_all(self):
        self.C.save({"distill_url": "http://config:11434"})
        os.environ["YGG_EMBED_URL"] = "http://env:11434"
        self.assertEqual(self.C.distill_url("http://flag:11434"), "http://flag:11434")
        self.assertEqual(self.C.source("distill_url", "http://flag:11434"), "flag")

    def test_timeout_is_int_and_robust(self):
        self.C.save({"distill_timeout": "not-a-number"})
        self.assertEqual(self.C.distill_timeout(), 120)  # falls back, never crashes
        self.assertEqual(self.C.distill_timeout("300"), 300)

    def test_url_trailing_slash_stripped(self):
        self.assertEqual(self.C.distill_url("http://box:11434/"), "http://box:11434")


if __name__ == "__main__":
    unittest.main()
