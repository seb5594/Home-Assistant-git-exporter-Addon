import json
import time
import unittest
import urllib.error
import urllib.request

import support
from exporter import server, supervisor


class Api(unittest.TestCase):
    def setUp(self):
        self.world = support.World()
        self.addCleanup(self.world.close)
        self.current = self.world.settings("private")
        self.app = server.Application(lambda: self.current, "test")
        self.httpd = server.serve(self.app, 0)
        self.addCleanup(self.httpd.server_close)
        self.addCleanup(self.httpd.shutdown)
        self.base = f"http://127.0.0.1:{self.httpd.server_address[1]}"

    def call(self, path, body=None):
        data = json.dumps(body).encode() if body is not None else None
        request = urllib.request.Request(self.base + path, data=data, method="POST" if body is not None else "GET",
                                         headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(request, timeout=30) as reply:
                return json.load(reply)
        except urllib.error.HTTPError as error:
            return {"http": error.code, **json.load(error)}

    def wait(self, job):
        for _ in range(200):
            view = self.call(f"/api/job?id={job}")
            if view["done"]:
                return view
            time.sleep(0.1)
        self.fail("job did not finish")

    def test_state_lists_repositories_without_secrets_and_the_presets(self):
        self.current.repositories[0].password = "s3cr3t"
        view = self.call("/api/state")
        self.assertNotIn("s3cr3t", json.dumps(view))
        self.assertEqual(view["repositories"][0]["audience"], "private")
        self.assertIn("databases", [p["id"] for p in view["presets"]])
        self.assertTrue(next(s for s in view["sources"] if s["id"] == "config")["available"])

    def test_the_tree_shows_what_the_rules_do_to_each_entry(self):
        top = {e["name"]: e for e in self.call("/api/tree", {"source": "config", "path": ""})["entries"]}
        self.assertEqual(top["configuration.yaml"]["status"], "included")
        self.assertEqual(top["home-assistant_v2.db"]["status"], "excluded")
        self.assertEqual(top["custom_components"]["origin"], "preset:hacs_downloads")
        self.assertEqual(top[".storage"]["origin"], "mandatory")
        self.assertEqual(top["esphome"]["origin"], "separate:esphome")
        self.assertEqual(top["www"]["status"], "included")
        below = {e["name"]: e for e in self.call("/api/tree", {"source": "config", "path": "www"})["entries"]}
        self.assertEqual(below["big.png"]["status"], "too_large")

    def test_a_draft_changes_the_view_without_saving(self):
        draft = {"presets": {"hacs_downloads": False}, "exclude": ["automations.yaml"]}
        top = {e["name"]: e for e in self.call("/api/tree", {"source": "config", "draft": draft})["entries"]}
        self.assertEqual(top["custom_components"]["status"], "included")
        self.assertEqual(top["automations.yaml"]["origin"], "custom")
        again = {e["name"]: e for e in self.call("/api/tree", {"source": "config"})["entries"]}
        self.assertEqual(again["automations.yaml"]["status"], "included")

    def test_a_pattern_is_tested_before_it_is_added(self):
        effect = self.call("/api/pattern", {"pattern": "*.yaml"})
        self.assertGreaterEqual(effect["files"], 2)
        self.assertTrue(all(e["now_excluded"] for e in effect["examples"]))
        self.assertEqual(self.call("/api/pattern", {"pattern": "!"})["http"], 400)

    def test_summary_counts_what_stays_and_what_goes(self):
        rows = {r["path"]: r for r in self.call("/api/summary", {"source": "config"})["entries"]}
        self.assertGreater(rows["custom_components"]["left_files"], 0)
        self.assertEqual(rows["custom_components"]["kept_files"], 0)

    def test_preview_then_diff(self):
        job = self.call("/api/preview", {"repository": "main"})["job"]
        view = self.wait(job)
        result = view["results"][0]
        self.assertEqual(result["code"], "preview")
        paths = {c["path"]: c for c in result["changes"]}
        self.assertEqual(paths["config/automations.yaml"]["status"], "added")
        diff = self.call(f"/api/diff?job={job}&repository=main&path=config/automations.yaml")
        self.assertIn("+- alias: test", diff["diff"])

    def test_export_runs_as_a_job_and_a_second_one_waits(self):
        job = self.call("/api/export", {"repository": "main"})["job"]
        view = self.wait(job)
        self.assertEqual(view["results"][0]["code"], "pushed")

    def test_only_ingress_and_the_container_may_call(self):
        self.assertIn(self.httpd.server_address[0], ("0.0.0.0", "::"))
        self.assertFalse(server.Handler._allowed(type("H", (), {"client_address": ("10.0.0.9", 1)})()))
        self.assertTrue(server.Handler._allowed(type("H", (), {"client_address": ("172.30.32.2", 1)})()))

    def test_save_needs_the_supervisor(self):
        self.assertEqual(self.call("/api/save", {"draft": {"exclude": ["*.tmp"]}})["http"], 503)

    def test_save_writes_only_the_editable_options(self):
        stored = {"repositories": [{"name": "x", "url": "https://a/b", "audience": "private"}], "exclude": ["a"]}
        saved = {}
        for name, replacement in (("available", lambda: True), ("current_options", lambda: dict(stored)),
                                  ("save_options", lambda options: saved.update(options))):
            self.addCleanup(setattr, supervisor, name, getattr(supervisor, name))
            setattr(supervisor, name, replacement)
        reply = self.call("/api/save", {"draft": {"exclude": ["*.tmp"], "repositories": []}})
        self.assertTrue(reply["saved"])
        self.assertEqual(saved["exclude"], ["*.tmp"])
        self.assertEqual(saved["repositories"], stored["repositories"])
        self.assertEqual(self.call("/api/save", {"draft": {"exclude": ["!"]}})["http"], 400)

    def test_the_page_is_served(self):
        server.WEB_DIR = support.WEB_DIR
        with urllib.request.urlopen(self.base + "/") as reply:
            self.assertIn(b"<html", reply.read())


if __name__ == "__main__":
    unittest.main()
