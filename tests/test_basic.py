"""Basic tests for Kibo."""

import unittest


class TestImports(unittest.TestCase):
    def test_agent_import(self):
        import agent
        self.assertTrue(hasattr(agent, "__version__"))

    def test_tools_import(self):
        from agent.tools import ALL_TOOLS
        self.assertEqual(len(ALL_TOOLS), 57)

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


class TestVersion(unittest.TestCase):
    def test_version_format(self):
        import agent
        parts = agent.__version__.split(".")
        self.assertEqual(len(parts), 3)
        for part in parts:
            self.assertTrue(part.isdigit())


if __name__ == "__main__":
    unittest.main()
