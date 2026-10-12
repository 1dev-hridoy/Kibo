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


class TestToolRouter(unittest.TestCase):
    """The shortlist must keep the right tool reachable, cheaply."""

    @classmethod
    def setUpClass(cls):
        from agent.tools import ALL_TOOLS
        from agent.core.tool_router import ToolRouter
        cls.tools = ALL_TOOLS
        cls.router = ToolRouter(ALL_TOOLS)

    def test_index_covers_every_tool(self):
        self.assertEqual(self.router.n, len(self.tools))
      
        self.assertGreater(len(self.router.idf), 500)



    def test_shortlist_finds_the_right_tool(self):
        cases = {
            "what's my battery level": "get_battery_status",
            "take a screenshot": "take_screenshot_now",
            "check the wifi connection": "get_wifi_info",
            "play some music": "play_media",
            "remind me to drink water": "remind_water",
            "schedule a task for 9am": "schedule_agent_task",
            "convert 5km to miles": "convert_units",
            "find large files": "find_large_files",
            "hash this text": "hash_text",
            "delete the temp file": "delete_file",
        }


        for query, expected in cases.items():
            self.assertIn(expected, self.router.route(query),
                          f"{query!r} should surface {expected}")

    def test_shortlist_is_small(self):
        names = self.router.route("what's my battery level")
        self.assertLessEqual(len(names), 8)
        self.assertLess(len(names), len(self.tools))

    def test_greeting_gets_no_noise(self):


        
        self.assertLessEqual(len(self.router.route("hi")), 4)

    def test_shortlist_shrinks_the_prompt(self):
        def schemas(names=None):
            keep = set(names) if names is not None else None
            out = []
            for fn in self.tools:
                n = fn.__name__
                if keep is not None and n not in keep:
                    continue
                doc = (fn.__doc__ or "").strip().split("\n")[0]
                out.append(f"- {n}: {doc}")
            return "\n".join(out)



        full = len(schemas())
        short = len(schemas(self.router.route("what's my battery level")))
        self.assertLess(short, full / 5)
      
        self.assertLess(short / 4, 2048 - 1024)


class TestVersion(unittest.TestCase):
    def test_version_format(self):
        import agent
        parts = agent.__version__.split(".")
        self.assertEqual(len(parts), 3)
        for part in parts:
            self.assertTrue(part.isdigit())


if __name__ == "__main__":
    unittest.main()
