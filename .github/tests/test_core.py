import subprocess
import unittest

import support  # noqa: F401  (puts the exporter package on the path)
from exporter import export, gitops, matcher, presets, runner, sanitize, sources


class Patterns(unittest.TestCase):
    def excluded(self, patterns, path, is_dir=False):
        verdict = matcher.Ruleset(patterns).match(path, is_dir)
        return bool(verdict and verdict[0])

    def test_names_match_at_any_depth(self):
        self.assertTrue(self.excluded(["*.db"], "a/b/c.db"))
        self.assertFalse(self.excluded(["*.db"], "a/b/c.db.txt"))

    def test_a_trailing_slash_means_folders_only(self):
        self.assertTrue(self.excluded(["deps/"], "x/deps", True))
        self.assertFalse(self.excluded(["deps/"], "x/deps", False))

    def test_a_slash_anchors_the_pattern(self):
        self.assertTrue(self.excluded(["/tts/"], "tts", True))
        self.assertFalse(self.excluded(["/tts/"], "a/tts", True))
        self.assertTrue(self.excluded(["custom_components/foo"], "custom_components/foo", True))
        self.assertFalse(self.excluded(["custom_components/foo"], "x/custom_components/foo", True))

    def test_double_star_crosses_folders_and_single_star_does_not(self):
        self.assertTrue(self.excluded(["**/cache/*.tmp"], "a/b/cache/x.tmp"))
        self.assertFalse(self.excluded(["a/*.tmp"], "a/b/x.tmp"))

    def test_the_last_matching_pattern_wins(self):
        self.assertFalse(self.excluded(["*.db", "!keep.db"], "keep.db"))
        self.assertTrue(self.excluded(["!keep.db", "*.db"], "keep.db"))

    def test_the_rsync_patterns_of_version_one_keep_their_meaning(self):
        old = ["*.db", "*.log*", "__pycache__", "._*", ".DS_Store", "deps/", "known_devices.yaml", "tts/", "*.gz"]
        for path, is_dir in (("home-assistant.log.1", False), ("x/__pycache__", True), ("deps", True), ("tts", True),
                             ("known_devices.yaml", False), ("backup.tar.gz", False), ("._x", False)):
            self.assertTrue(self.excluded(old, path, is_dir), path)

    def test_every_preset_pattern_is_valid(self):
        for preset in presets.PRESETS:
            for pattern in preset.patterns:
                self.assertIsNone(matcher.check(pattern), (preset.id, pattern))


class SecretsFile(unittest.TestCase):
    def test_block_scalars_comments_and_nested_mappings_are_understood(self):
        secrets, error = sanitize.parse_secrets(support.SECRETS)
        self.assertIsNone(error)
        keys = {secret.key for secret in secrets}
        self.assertIn("template_home_presence", keys)
        self.assertIn("whatsapp_phonebook.sebi", keys)
        self.assertIn("api_key_weather", keys)

    def test_blanking_keeps_keys_and_comments_and_drops_every_value(self):
        blanked = sanitize.blank_secrets_yaml(support.SECRETS)
        self.assertIn("# whatsapp nummern", blanked)
        self.assertIn("whatsapp_phonebook:\n  sebi: \"\"", blanked)
        self.assertIn('template_home_presence: ""', blanked)
        for value in ("491701234567", "192.168.178.1", "selectattr", "abcdef1234567890abcdef", "# desktop"):
            self.assertNotIn(value, blanked)
        import yaml
        self.assertEqual(set(yaml.safe_load(blanked)), set(yaml.safe_load(support.SECRETS)))

    def test_a_file_that_is_not_valid_yaml_does_not_stop_anything(self):
        secrets, error = sanitize.parse_secrets("good: value12345\nbroken: [unclosed\n")
        self.assertIsNotNone(error)
        self.assertTrue(any(secret.value == "value12345" for secret in secrets))

    def test_tags_in_secrets_do_not_break_the_parser(self):
        secrets, error = sanitize.parse_secrets("a: !env_var HOME\nb: valuevalue\n")
        self.assertIsNone(error)


class Censoring(unittest.TestCase):
    def censor(self, **kwargs):
        secrets, _ = sanitize.parse_secrets(support.SECRETS)
        return sanitize.Censor(secrets, **kwargs)

    def test_values_of_secrets_yaml_are_replaced_in_other_files(self):
        result = self.censor().apply("host: 192.168.178.1\nname: Sebis Zuhause\nkey: abcdef1234567890abcdef\n", yaml_file=True)
        self.assertNotIn("192.168.178.1", result.text)
        self.assertIn("!secret ip_router", result.text)
        self.assertIn("!secret server_friendly_name", result.text)
        self.assertIn("!secret api_key_weather", result.text)

    def test_a_whole_multiline_secret_is_found(self):
        secrets, _ = sanitize.parse_secrets(support.SECRETS)
        block = next(secret.value for secret in secrets if secret.key == "template_home_presence")
        result = sanitize.Censor(secrets).apply("template: |\n" + "\n".join("  " + line for line in block.splitlines()))
        self.assertNotIn("sensor.zuhause_sebastian_entfernung", result.text)

    def test_ip_check_hides_addresses_and_leaves_versions_masks_and_known_services(self):
        text = "a: 10.1.2.3\nversion: 1.2.3.4\nmask: 255.255.255.0\ndns: 8.8.8.8\nlocal: 127.0.0.1\nv: v10.0.0.1\n"
        result = sanitize.Censor([], check_secrets=False).apply(text)
        self.assertNotIn("10.1.2.3", result.text)
        for kept in ("version: 1.2.3.4", "255.255.255.0", "8.8.8.8", "127.0.0.1", "v10.0.0.1"):
            self.assertIn(kept, result.text)

    def test_the_same_address_always_gets_the_same_placeholder(self):
        one = sanitize.Censor([], check_secrets=False).apply("a: 10.1.2.3\nb: 10.1.2.3\nc: 10.1.2.4\n").text.splitlines()
        self.assertEqual(one[0].split(": ")[1], one[1].split(": ")[1])
        self.assertNotEqual(one[0].split(": ")[1], one[2].split(": ")[1])

    def test_numbers_that_only_look_like_addresses_stay(self):
        result = sanitize.Censor([], check_secrets=False).apply("a: 999.1.1.1\nb: 1.2.3.4.5\nc: 10.0.0\n")
        self.assertEqual(result.findings.total(), 0)

    def test_mac_addresses_and_ipv6_are_hidden_with_their_notation_kept(self):
        result = sanitize.Censor([], check_secrets=False).apply("m: AA-BB-CC-11-22-33\nn: fe80::1234:abcd\nt: 12:30:45\n")
        self.assertNotIn("AA-BB", result.text)
        self.assertRegex(result.text, r"m: 00-00-5E-00-53-[0-9A-F]{2}")
        self.assertNotIn("fe80", result.text)
        self.assertIn("12:30:45", result.text)

    def test_keys_that_are_named_like_secrets_lose_their_value(self):
        result = sanitize.Censor([], check_addresses=False).apply(
            "password: hunter2hunter2\ntoken: !secret x\nlatitude: 52.5\napi_key: \"{{ states('a') }}\"\n", yaml_file=True)
        self.assertIn('password: "<censored>"', result.text)
        self.assertIn("token: !secret x", result.text)
        self.assertIn("latitude: 0.0", result.text)
        self.assertIn("{{ states('a') }}", result.text)

    def test_allowed_values_are_left_alone(self):
        result = self.censor(allowed=["192.168.178.1"]).apply("host: 192.168.178.1\n")
        self.assertIn("192.168.178.1", result.text)

    def test_private_keys_block_the_file(self):
        self.assertEqual(sanitize.Censor([]).apply("-----BEGIN PRIVATE KEY-----\nx").blocked, "contains a private key")

    def test_passwords_in_urls_and_mail_addresses_go(self):
        result = sanitize.Censor([], check_addresses=False).apply("u: https://me:secret123@host.example/x\nm: me@gmail.com\n")
        self.assertNotIn("secret123", result.text)
        self.assertNotIn("me@gmail.com", result.text)


class Exporting(unittest.TestCase):
    def setUp(self):
        self.world = support.World()
        self.addCleanup(self.world.close)

    def collect(self, audience, **overrides):
        settings = self.world.settings(audience, **overrides)
        return settings, export.collect(settings, settings.repositories[0])

    def test_presets_keep_databases_logs_runtime_state_and_third_party_code_out(self):
        _settings, collected = self.collect("private")
        paths = set(collected.outputs)
        self.assertIn("config/configuration.yaml", paths)
        self.assertIn("addons_config/abc_gitea/app.ini", paths)
        for left_out in ("config/home-assistant.log", "config/home-assistant_v2.db", "config/.storage/auth",
                         "config/custom_components/foo/__init__.py", "addons_config/abc_gitea/data/gitea.db",
                         "config/esphome/node.yaml"):
            self.assertNotIn(left_out, paths)
        self.assertIn("esphome/node.yaml", paths)
        self.assertNotIn("esphome/build.bin", paths)

    def test_files_over_the_size_limit_are_skipped_and_counted(self):
        _settings, collected = self.collect("private")
        self.assertNotIn("config/www/big.png", collected.outputs)
        self.assertEqual(collected.too_large, 1)

    def test_a_private_repository_gets_secrets_yaml_unchanged(self):
        _settings, collected = self.collect("private")
        self.assertEqual(collected.outputs["config/secrets.yaml"].data.decode(), support.SECRETS)
        self.assertIn("192.168.178.1", collected.outputs["config/configuration.yaml"].file and
                      open(collected.outputs["config/configuration.yaml"].file).read())

    def test_a_public_repository_gets_blanked_secrets_and_censored_files(self):
        _settings, collected = self.collect("public")
        self.assertNotIn("491701234567", collected.outputs["config/secrets.yaml"].data.decode())
        text = collected.outputs["config/configuration.yaml"].data.decode()
        for private in ("192.168.178.1", "AA:BB:CC:11:22:33", "hunter2hunter2", "52.52"):
            self.assertNotIn(private, text)
        self.assertIn("!secret server_friendly_name", text)
        self.assertGreater(collected.findings.total(), 3)
        self.assertNotIn("10.0.0.5", collected.outputs["addons_config/abc_gitea/app.ini"].data.decode())

    def test_the_user_can_keep_back_a_file_from_a_preset(self):
        _settings, collected = self.collect("private", exclude=["/custom_components/*", "!/custom_components/foo/"])
        self.assertIn("config/custom_components/foo/__init__.py", collected.outputs)

    def test_switching_a_preset_off_exports_what_it_excluded(self):
        _settings, collected = self.collect("private", presets={"logs": False})
        self.assertIn("config/home-assistant.log", collected.outputs)

    def test_a_missing_source_is_left_out_not_emptied(self):
        _settings, collected = self.collect("private")
        self.assertNotIn("local_apps", collected.synced)

    def test_plan_names_added_modified_and_removed_files(self):
        settings, collected = self.collect("private")
        directory = self.world.data / "repo"
        directory.mkdir()
        first = export.plan(collected, str(directory))
        self.assertEqual(first.counts()["added"], len(collected.outputs))
        export.apply(first, str(directory))
        (self.world.config / "automations.yaml").write_text("- alias: changed\n")
        (self.world.config / "scenes.yaml").write_text("[]\n")
        (directory / "config/stale.yaml").write_text("old")
        again = export.plan(export.collect(settings, settings.repositories[0]), str(directory))
        by_status = {(change.status, change.path) for change in again.changes}
        self.assertEqual(by_status, {("modified", "config/automations.yaml"), ("added", "config/scenes.yaml"),
                                     ("removed", "config/stale.yaml")})

    def test_a_diff_hides_known_secret_values(self):
        _settings, collected = self.collect("private")
        directory = self.world.data / "repo2"
        (directory / "config").mkdir(parents=True)
        (directory / "config/secrets.yaml").write_text("api_key_weather: oldvalue\n")
        plan = export.plan(collected, str(directory))
        text = export.diff(plan, str(directory), "config/secrets.yaml", mask=["abcdef1234567890abcdef"])
        self.assertNotIn("abcdef1234567890abcdef", text)
        self.assertIn("••••", text)


class Running(unittest.TestCase):
    def setUp(self):
        self.world = support.World()
        self.addCleanup(self.world.close)

    def remote_files(self):
        return subprocess.run(["git", "ls-tree", "-r", "--name-only", "main"], cwd=self.world.remote, text=True,
                              capture_output=True, check=False).stdout.split()

    def test_an_export_pushes_and_a_second_one_has_nothing_to_do(self):
        settings = self.world.settings("private")
        repository = settings.repositories[0]
        result, _plan = runner.run(settings, repository)
        self.assertEqual((result["status"], result["code"]), ("ok", "pushed"), result)
        self.assertIn("config/configuration.yaml", self.remote_files())
        self.assertNotIn("config/home-assistant_v2.db", self.remote_files())
        again, _plan = runner.run(settings, repository)
        self.assertEqual(again["code"], "nothing")

    def test_a_preview_changes_nothing(self):
        settings = self.world.settings("private")
        result, plan = runner.run(settings, settings.repositories[0], dry_run=True)
        self.assertEqual(result["code"], "preview")
        self.assertGreater(result["counts"]["added"], 3)
        self.assertEqual(subprocess.run(["git", "branch", "-a"], cwd=self.world.remote, text=True,
                                        capture_output=True).stdout.strip(), "")

    def test_a_public_repository_never_receives_the_secrets(self):
        settings = self.world.settings("public")
        runner.run(settings, settings.repositories[0])
        shown = subprocess.run(["git", "show", "main:config/secrets.yaml"], cwd=self.world.remote, text=True,
                               capture_output=True, check=True).stdout
        self.assertNotIn("491701234567", shown)
        everything = subprocess.run(["git", "grep", "-I", "-e", "192.168.178", "-e", "hunter2", "main"],
                                    cwd=self.world.remote, text=True, capture_output=True).stdout
        self.assertEqual(everything, "")

    def test_block_mode_stops_an_export_that_found_something(self):
        settings = self.world.settings("public", check={"on_finding": "block"})
        result, _plan = runner.run(settings, settings.repositories[0])
        self.assertEqual(result["status"], "blocked")
        self.assertEqual(self.remote_files(), [])

    def test_a_removed_file_disappears_from_the_remote_with_the_next_export(self):
        settings = self.world.settings("private")
        runner.run(settings, settings.repositories[0])
        (self.world.config / "automations.yaml").unlink()
        runner.run(settings, settings.repositories[0])
        self.assertNotIn("config/automations.yaml", self.remote_files())

    def test_credentials_never_reach_the_git_config(self):
        settings = self.world.settings("private")
        settings.repositories[0].password = "s3cr3t-token"
        settings.repositories[0].username = "me"
        runner.run(settings, settings.repositories[0])
        config = (self.world.data / "repositories/main/.git/config").read_text()
        self.assertNotIn("s3cr3t-token", config)

    def test_errors_do_not_show_the_token(self):
        settings = self.world.settings("private")
        repository = settings.repositories[0]
        repository.url = "https://127.0.0.1:9/none.git"
        repository.password = "s3cr3t-token"
        result, _plan = runner.run(settings, repository)
        self.assertEqual(result["status"], "error")
        self.assertNotIn("s3cr3t-token", str(result))


class Settings(unittest.TestCase):
    def test_the_single_repository_of_version_one_becomes_a_public_entry(self):
        from exporter import options
        old = {"repository": {"url": "https://example.org/a/b.git", "username": "u", "password": "p", "branch_name": "dev",
                              "commit_message": "x"}, "dry_run": True}
        settings = options.parse(old)
        self.assertTrue(settings.legacy_repository)
        repository = settings.repositories[0]
        self.assertEqual((repository.audience, repository.branch, repository.name), ("public", "dev", "default"))
        migrated = options.migrated_options(old, settings)
        self.assertEqual(migrated["repository"], {})
        self.assertNotIn("dry_run", migrated)
        self.assertEqual(migrated["repositories"][0]["password"], "p")

    def test_an_entry_without_an_audience_is_treated_as_public(self):
        from exporter import options
        settings = options.parse({"repositories": [{"name": "a", "url": "https://x/y"}, {"name": "a", "url": "https://x/z"}]})
        self.assertTrue(all(r.public for r in settings.repositories))
        self.assertEqual([r.slug for r in settings.repositories], ["a", "a-2"])

    def test_urls_with_credentials_are_split(self):
        url, user, password = gitops.split_url("https://me:tok%40en@host.example:8443/a/b.git")
        self.assertEqual((url, user), ("https://host.example:8443/a/b.git", "me"))


if __name__ == "__main__":
    unittest.main()
