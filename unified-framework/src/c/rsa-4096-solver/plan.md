Deep Dive: Grok-Codex Fork (zfifteen/Grok-Codex) - Current State & xAI Integration Analysis

Repo Structure (Root): Multi-lang monorepo (Rust core in codex-rs/, TS CLI in codex-cli/, docs/scripts). No root Cargo.toml; build via codex-rs/Cargo.toml (Rust edition 2024, workspace crates: core, tui, exec, etc.). Untracked: .codex/ (local config), config.toml (gpt-5 default - WIP mismatch), package-lock.json (Node deps). Git: Main branch, up-to-date w/ origin; commits show xAI migration (e.g., aef405d: full integration, cf a9d54b9: from OpenAI Codex).

Integration Progress (WIP Strengths):
- Defaults: config.rs sets XAI_DEFAULT_MODEL="grok-code-fast-1" (used in tests/docs/scripts, e.g., exec/tests/resume.rs, xai_config.toml examples).
- Providers: Built-in model_providers() includes xAI? (From code: defaults to "api_x" in load_from_base_config_with_overrides - partial; grep shows openai remnants dominate).
- Docs/Scripts: xai_testing_guide.md, validate_xai_integration.sh, test_xai_api.py/curl.sh use "grok-code-fast-1"; examples migrated.
- Tests: Suite (review.rs, compact_resume_fork.rs, etc.) mocks xAI calls; reasoning_effort="high" for Grok.
- Config: .codex/config.toml has [projects] trust_levels; root config.toml untracked w/ gpt-5 (fix needed).

Gaps/Remnants (OpenAI Legacy - ~80% codebase):
- Code: Heavy OpenAI deps (e.g., core/src/client.rs: openai_tools, auth::read_openai_api_key_from_env; model_provider_info.rs: requires_openai_auth everywhere; ollama/src: is_openai_compatible_base_url). MCP protocol assumes OpenAI wire_api ("chat"/"responses"). Error.rs: OpenAI rate limits/pricing links.
- Auth: Still OPENAI_API_KEY; no XAI_API_KEY handling (auth.rs: post to auth.openai.com).
- Providers: built_in_model_providers() hardcoded for openai (base_url="https://api.openai.com/v1", env_key="OPENAI_API_KEY"). No native xAI provider (add: base_url="https://api.x.ai/v1", env_key="XAI_API_KEY", wire_api="chat").
- Docs/README: Install/usage still @openai/codex (npm/brew); links to openai.com/docs, ZDR, security@openai.com. FAQ/CHANGELOG reference OpenAI verification/pricing.
- Tests: Many require_openai_auth=true; mocks hit openai.com (e.g., suite/client.rs: /openai/responses). No xAI-specific error handling (e.g., Grok token limits).
- CLI/TS: codex-cli/ still OpenAI-focused (README: npm i -g @openai/codex; scripts: api.openai.com).
- Config: Default model_provider_id="openai" fallback; .codex/config.toml uses "gpt-5" (not Grok). No auto-setup for XAI_API_KEY.

Out-of-Box Plan: Full xAI/Grok Readiness (5 Phases, ~2-4 hrs impl + test):
Phase 1: Core Provider Migration (config.rs, model_provider_info.rs)
- Add xAI to built_in_model_providers(): { name="xAI Grok", base_url="https://api.x.ai/v1", env_key="XAI_API_KEY", wire_api="chat", requires_openai_auth=false, max_retries=3, idle_timeout=5m }.
- Set default model_provider_id="xai" (replace "api_x"/"openai").
- Update default_model() -> "grok-code-fast-1"; review_model="grok-2-1212".
- Migrate auth.rs: Add read_xai_api_key_from_env(); fallback to XAI_API_KEY. Remove openai.com endpoints.
- Edit: Use tool to sed -i in codex-rs/core/src/{config,auth,client,model_provider_info}.rs: s/openai/xai/g; s/api.openai.com/api.x.ai/g; add XAI consts.

Phase 2: Codebase Purge & Compatibility (core/, protocol/):
- Grep & replace: s/OpenAI/xAI/g; s/openai/grok/g (non-provider). Remove ZDR/openai-specific (error.rs, client.rs: rate limits -> xAI equivs, e.g., "https://console.x.ai/account/limits").
- Tools: Update openai_tools.rs -> grok_tools.rs (adapt function-calling to Grok's tool_calls schema; test mcp_tool_to_grok_tool).
- MCP: protocol/mcp_protocol.rs: Drop requires_openai_auth; ensure streamable_http for xAI SSE.
- Ollama: src/url.rs: Add is_xai_compatible_base_url.
- Edit: Parallel tool calls on core/src/{openai_tools,client,exec_command}.rs; remove Azure/OpenAI proxies.

Phase 3: Config/Docs/Install (root, docs/, scripts/):
- .codex/config.toml: Set model="grok-code-fast-1"; model_provider="xai"; [projects."$PWD"] trust_level="trusted".
- Root config.toml: model="grok-code-fast-1"; add [model_providers.xai] as above.
- README.md: Update install: cargo install --git https://github.com/zfifteen/Grok-Codex codex-rs (or npm @zfifteen/grok-codex); auth: echo "XAI_API_KEY=your_key" >> ~/.codex/env.
- Docs: config.md/examples: xAI base_url/key; remove OpenAI sections (faq.md, zdr.md, advanced.md). xai_configuration.md: Expand Grok models/effort.
- Scripts: test_xai_*.sh/py: Default to xAI; add XAI_API_KEY check.
- Gitignore: Add /xai_key.env.
- Edit: sed -i on README/docs; git add/commit -m "xAI out-of-box defaults".

Phase 4: Tests & Validation (codex-rs/):
- Update suite/*.rs: Mock xAI responses (e.g., client.rs: base_url="https://api.x.ai/v1/chat/completions"); set requires_openai_auth=false.
- Run: cargo test -- --test-threads=1 (fix failures: auth mocks, tool schemas).
- E2E: ./scripts/validate_xai_integration.sh; test_xai_api.py --model grok-code-fast-1.
- Binary: cargo build --release; test ./target/release/codex --model grok-code-fast-1 "Hello Grok".
- Add: xAI-specific tests (e.g., reasoning_effort=high, tool_calls).

Phase 5: Packaging & Release (Out-of-Box Verify):
- Cargo.toml (codex-rs/): Update version; deps: Add any xAI crates if needed (e.g., reqwest for API).
- Build: cargo install; fresh ~./codex/config.toml should default to xAI/Grok (no OpenAI key prompt).
- GitHub: Update repo desc/README; release v0.1.0-wip-xai; Actions: rust-release.yml -> xAI tests.
- Verify: Clone fresh; codex --help; codex "Write Rust hello" -> Uses Grok, no config needed (prompt for XAI_API_KEY if unset).

Risks: Grok API diffs (e.g., no "responses" wire_api? Use chat); token limits (Grok: 128k ctx). Total: ~500 LOC changes. Post-plan: Implement Phase 1?
