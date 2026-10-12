"""Basic tests for Kibo."""

import unittest


class TestImports(unittest.TestCase):
    def test_agent_import(self):
        import agent
        self.assertTrue(hasattr(agent, "__version__"))

    def test_tools_import(self):
        from agent.tools import ALL_TOOLS
        self.assertGreaterEqual(len(ALL_TOOLS), 57)

    def test_core_import(self):
        from agent.core import ask
        self.assertTrue(callable(ask))

    def test_config_import(self):
        from agent.config import WEB_HOST, WEB_PORT
        self.assertIsInstance(WEB_HOST, str)
        self.assertIsInstance(WEB_PORT, int)

    def test_model_manager_import(self):
        from agent.model_manager import MODELS
        self.assertIn("needle", MODELS)
        self.assertIn("functiongemma", MODELS)
        for key in ("qwen3-0.6b", "qwen2.5-1.5b", "qwen2.5-3b",
                    "gemma3-1b", "gemma3-4b"):
            self.assertIn(key, MODELS)
            self.assertIn("license", MODELS[key])

    def test_model_aliases_resolve(self):
        from agent.model_manager import MODEL_ALIASES, resolve_model_name
        cases = {
            "qwen": "qwen3-0.6b",
            "qwen3": "qwen3-0.6b",
            "qwen2.5-1.5b": "qwen2.5-1.5b",
            "qwen1.5b": "qwen2.5-1.5b",
            "qwen3b": "qwen2.5-3b",
            "qwen2.5-3b": "qwen2.5-3b",
            "gemma3": "gemma3-1b",
            "gemma3-1b": "gemma3-1b",
            "gemma3-4b": "gemma3-4b",
            "gemma-4b": "gemma3-4b",
            "gemma": "functiongemma",
            "n": "needle",
        }
        for alias, target in cases.items():
            self.assertEqual(resolve_model_name(alias), target, alias)
            self.assertIn(alias, MODEL_ALIASES)

    def test_gguf_registry(self):
        from agent.model_manager import GGUF_MODELS, model_path, model_url
        for key in ("functiongemma", "qwen3-0.6b", "qwen2.5-1.5b",
                    "qwen2.5-3b", "gemma3-1b", "gemma3-4b"):
            self.assertIn(key, GGUF_MODELS)
            self.assertTrue(model_path(key).endswith(".gguf"))
            self.assertIn("huggingface.co", model_url(key))


class TestVersion(unittest.TestCase):
    def test_version_format(self):
        import agent
        parts = agent.__version__.split(".")
        self.assertEqual(len(parts), 3)
        for part in parts:
            self.assertTrue(part.isdigit())


if __name__ == "__main__":
    unittest.main()
