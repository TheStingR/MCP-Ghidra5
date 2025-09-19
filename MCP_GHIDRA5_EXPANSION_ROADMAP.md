# MCP-Ghidra5 Expansion and Reliability Roadmap

Last updated: 2025-09-19
Owner: TechSquad Inc. (project development for Debian-based Linux, incl. Kali)

## 1) Goals and Scope
- Deliver a best-in-class Ghidra MCP server for reverse engineering and exploitation.
- Expand the current 7-tool suite with additional, high-impact capabilities while increasing reliability and portability.
- Default to JSON outputs for downstream automation, with optional text summaries.
- Support graceful degradation when optional dependencies are missing.
- Provide ready-to-use MCP client configs and quickstart guides across popular clients.

Priority order for focus areas (confirmed):
1) Exploit development
2) Malware triage
3) Firmware
4) Code audit at scale

## 2) Current Tooling (Baseline)
Existing tools (from API and server):
- ghidra_binary_analysis: Full executable analysis
- ghidra_function_analysis: Specific function decompilation and analysis
- ghidra_exploit_development: Exploitability assessment and strategy/PoC outline
- ghidra_malware_analysis: Malware-focused static/behavioral analysis
- ghidra_firmware_analysis: Firmware/embedded analysis
- ghidra_code_pattern_search: Pattern hunting (vulns, crypto, anti-debug, APIs)
- gpt5_reverse_engineering_query: Expert Q&A with specialization

## 3) New Tools Proposal (Additions)
The following tools are divided into three tiers by complexity and dependency risk. All tools honor: output_format (json|text) and analysis_profile (ctf|pentest|malware|firmware|deep), with defaults noted below. All file-accepting tools undergo uniform validation and sandbox copying.

### Tier 1 (Low friction, high value; minimal deps)
1. ghidra_strings_xref_analysis
   - Purpose: Extract printable strings with addresses, xrefs, owning function, and nearby constants.
   - Inputs: binary_path (required), min_length=4, filters (regex), include_xrefs=true/false
   - Outputs: Table/JSON of strings with locations, xrefs, function context.
   - Deps: None (Ghidra). Fallback: Python-only strings pass (reduced fidelity) if Ghidra not available.

2. ghidra_import_export_report
   - Purpose: Summarize imports/exports, libraries, missing imports, syscall mapping.
   - Inputs: binary_path, platform_hint (auto|linux|windows)
   - Outputs: JSON report with imports/exports, libraries, anomalies; security hints per platform.
   - Deps: None. Optional: LIEF for richer headers if present. Fallback: Ghidra-only.

3. ghidra_security_features_check
   - Purpose: Detect hardening flags and memory protections.
   - Inputs: binary_path
   - Outputs: ELF (RELRO/NX/PIE/canary), PE (ASLR/DEP/SafeSEH/CFG), section RWX, reloc summary, exploitability notes.
   - Deps: None. Fallback: header heuristics if headless analysis unavailable.

4. ghidra_signature_matching_report
   - Purpose: Identify known functions/algorithms by signature; flag crypto/protocol constants.
   - Inputs: binary_path, custom_sig_dir (optional)
   - Outputs: Matches with confidence, locations, notes; signature coverage summary.
   - Deps: None. Fallback: simple byte-pattern heuristics.

5. ghidra_ioc_extractor
   - Purpose: Extract IOCs for triage and IR (URLs, IPs, domains, emails, file paths, registry, mutex, crypto constants).
   - Inputs: binary_path, ioc_types=[...]
   - Outputs: IOC list with offsets, surrounding context, confidence; optional STIX-lite JSON.
   - Deps: None. Fallback: strings + regex sweep when Ghidra not available.

### Tier 2 (Medium complexity; optional external deps)
6. ghidra_cfg_export_and_analyze
   - Purpose: Export & analyze CFG; compute metrics and hotspots.
   - Inputs: binary_path, format (graphviz|json), scope (all|hot)
   - Outputs: CFG metrics (nodes, edges, SCCs, cyclomatic complexity), hotspots, unreachable code; artifacts (.dot/.json).
   - Deps: Ghidra decompiler; graphviz optional for rendering. Fallback: function-level metrics only.

7. ghidra_binary_diff
   - Purpose: Diff two binaries (e.g., patched vs original) for structural changes.
   - Inputs: primary_binary_path, secondary_binary_path, mode (structural|signature|diaphora)
   - Outputs: matched/mismatched functions, changed BBs, probable patch regions.
   - Deps: Diaphora if installed. Fallback: signature and strings similarity.

8. ghidra_rop_gadget_search
   - Purpose: Gadget discovery and basic chain hints.
   - Inputs: binary_path, arch (auto), constraints (bad_bytes, depth)
   - Outputs: gadget list (addresses, semantics), candidate chains by syscall.
   - Deps: ropper/ROPgadget optional. Fallback: in-house lightweight gadget pass.

9. ghidra_entropy_packer_detection
   - Purpose: Spot packing/obfuscation via entropy and signatures.
   - Inputs: binary_path
   - Outputs: per-section entropy, packer signatures, overlay data, suspicious gaps; recommended unpack route.
   - Deps: YARA optional for packer rules. Fallback: entropy + section heuristics.

10. ghidra_api_sequence_search
    - Purpose: Identify API usage sequences that imply behaviors (e.g., injection, keylogging, credential dumping).
    - Inputs: binary_path, sequence_profile (predefined), custom_sequence (optional)
    - Outputs: matches with confidence, locations, quick execution path sketch.
    - Deps: None.

### Tier 3 (Advanced; heavier/hard deps; still graceful)
11. ghidra_yara_scan
    - Purpose: Run YARA rules against binary or sections.
    - Inputs: binary_path, rules_path (file/dir), tags (optional)
    - Outputs: matches with rule names, severity, offsets; summary.
    - Deps: YARA CLI. Fallback: minimal built-in regex signatures.

12. ghidra_firmware_extract_and_analyze
    - Purpose: Binwalk-based extraction, re-analysis of embedded binaries; runs Tier 1 checks across findings.
    - Inputs: firmware_path, extract=true/false, reanalyze_components=true/false
    - Outputs: extraction log, embedded binaries list, per-binary summaries.
    - Deps: binwalk, unsquashfs. Fallback: header scan + simple carving.

13. ghidra_emulation_function_trace
    - Purpose: P-code emulation of a target function for trace and side-effect summary.
    - Inputs: binary_path, function_address|name, seed_args (optional), max_steps
    - Outputs: trace of basic blocks, memory writes, callouts, branches; notes on side-effects.
    - Deps: Ghidra p-code emulator. Fallback: static trace.

14. ghidra_taint_analysis
    - Purpose: Source→sink analysis for dataflow (argv/env/stdin/sockets → exec/file_write/crypto).
    - Inputs: binary_path, sources=[...], sinks=[...]
    - Outputs: paths with sanitization points, risk ranking.
    - Deps: Ghidra dataflow framework.

15. ghidra_patch_suggestion (read-only)
    - Purpose: Generate patch plan (assembly diff), relocation implications, and test steps. Does NOT apply patches.
    - Inputs: binary_path, issue_descriptor (address/region & behavior)
    - Outputs: recommended patch steps, Ghidra/radare2 script stubs.
    - Deps: None; guarded to avoid destructive changes.

16. ghidra_symbol_rename_batch
    - Purpose: Mass-prepare renames for review and manual application in Ghidra.
    - Inputs: binary_path, rename_map (json), heuristics (regex rules)
    - Outputs: rename script, preview, conflicts report.
    - Deps: None.

## 4) Cross-cutting Reliability Upgrades
- Uniform validation & sandboxing
  - Apply security_utils validation to all path-taking tools (size, path, hash, basic signature scan), with sandbox copy.
- Output format & profiles
  - Add output_format=json (default) | text. Add analysis_profile (ctf|pentest|malware|firmware|deep); tailor prompts and cutoffs.
- Caching (AnalysisCache)
  - Enable for deterministic read-only tools (strings/imports/entropy/signatures). Provide cache-hit metrics in output.
- Concurrency & timeout control
  - Wrap headless calls behind an asyncio semaphore; per-tool timeouts (quick/standard/deep); safe termination; clear errors.
- Ghidra discovery & scriptPath portability
  - Detect GHIDRA_INSTALL_DIR; probe common Debian paths; allow GHIDRA_SCRIPT_PATH override; remove hard-coded scriptPath.
- Provider fallback
  - If OpenAI throttled/unavailable, optionally route to configured alternate (Anthropic/Azure/Gemini), annotate provider in result.
- Batch/aggregator support
  - Optional ghidra_batch_analyze to run N tools across M binaries with safe parallelism; ghidra_report_exporter to merge outputs.

## 5) Quick Wins (Phase 1)
1) Add Tier 1 tools (5):
   - ghidra_strings_xref_analysis
   - ghidra_import_export_report
   - ghidra_security_features_check
   - ghidra_signature_matching_report
   - ghidra_ioc_extractor

2) Add output_format and analysis_profile to all existing handlers
   - Default output_format=json; provide concise text summaries on request.

3) Extend security validation to all path-taking tools
   - Use common validator in security_utils; consistent error messages.

4) Turn on caching for strings/imports/entropy/signatures
   - Include cache stats in responses.

5) Improve Ghidra detection and scriptPath discovery
   - GHIDRA_INSTALL_DIR + common Debian paths; GHIDRA_SCRIPT_PATH env override.

Acceptance (Phase 1):
- All 12 tools (7 existing + 5 new) support output_format=json by default and analysis_profile.
- Uniform validation and sandbox applied; consistent error messages.
- Caching enabled and observable for eligible tools.
- Ghidra auto-detection works on Debian-based systems (incl. Kali); scriptPath not hard-coded.

## 6) Client Support Roadmap (Prioritized)
Primary targets (in order):
1. Warp Terminal (Agent Mode)
   - Provide ready JSON config (env-only; no hardcoded keys) and generate_client_configs.sh to emit per-env variants.
2. Claude Desktop
   - Same JSON config shape; steps.md for interactive tool debugging; env-only keys.
3. MCP CLI (reference)
   - cli-quickstart.md: list-tools, call-tool JSON payloads, redirection to files.
4. VS Code (bridge)
   - tasks.json example to launch the server; guide for using MCP via Claude/bridge where supported, else CLI workflows.

Secondary (backlog, optional docs/templates):
- JetBrains IDEs (External Tools run config)
- Neovim (jobstart wrappers), Emacs (elisp call-process wrappers)
- Cursor (terminal task workflows), Zed (task runner)

## 7) Dependency Policy & Debian Support
- Strategy: All tools degrade gracefully on missing optional dependencies and annotate the output with a dependency matrix (found/missing, version).
- Target OS family: Debian-based (Kali, Ubuntu, Debian).
- Common optional dependencies:
  - binwalk, unsquashfs (firmware)
  - yara (signatures/packer rules)
  - ropper or ROPgadget (gadget search)
  - diaphora (binary diff)
  - lief (header/format enrichment)
  - graphviz (CFG rendering)
- Detection: Runtime detection with clear messages; offer apt install hints (not auto-install).
- Behavior: No tool fails hard solely due to missing optional deps; fallback mode is documented and annotated in outputs.

## 8) API Adjustments
- New common parameters (all tools):
  - output_format: json (default) | text
  - analysis_profile: ctf|pentest|malware|firmware|deep (default: pentest unless stated by tool)
- Common response structure (json):
  - metadata: tool_name, provider_used, analysis_profile, cache_hit, dependency_matrix
  - summary: short text
  - findings: tool-specific structured data
  - artifacts: paths or embedded data (if small)
  - recommendations: next steps or related tools
- Text mode: Provide concise, operator-friendly narrative.

## 9) Interoperability (Advisory only)
- Meta-tool (advisory): ghidra_ai_provider_recommendation (non-executing) returns guidance on when to call other MCP providers (e.g., SuperGrok’s grok_exploit_analysis) with suggested payloads; keeps this server decoupled from others.

## 10) Milestones
- Phase 1 (Quick Wins; 1–2 sprints)
  - Tier 1 tools (5), uniform validation, output_format & profiles, caching, Ghidra detection.
- Phase 2 (Core advanced; 1–2 sprints)
  - Tier 2 tools (5), concurrency limits, provider fallback, initial multi-client templates.
- Phase 3 (Expert features; 2+ sprints)
  - Tier 3 tools (6), batch analysis & report exporter, extended docs, test coverage & CI for Debian variants.

## 11) Testing & Benchmarks
- Expand tests for each new tool with:
  - Valid input cases, edge cases (big files up to 100MB cap), missing deps scenarios, timeouts, and cache validation.
- Performance tracking:
  - Baseline vs cached; concurrency scaling.
  - Ensure JSON outputs remain stable (contract tests).

## 12) Open Decisions (Resolved)
- Focus order: exploit dev → malware → firmware → scale code audit (confirmed).
- Default output: JSON (confirmed) with optional text summaries.
- Client priority: Warp → Claude Desktop → MCP CLI → VS Code (confirmed), then backlog clients.
- Deps: Prefer graceful degradation; surface apt recommendations; develop for Debian family, not Kali-only.

## 13) Next Actions
- Implement Phase 1 (Quick Wins) with acceptance criteria above.
- Generate initial client configs/guides for the 4 prioritized clients.
- Validate on a Debian/Kali environment matrix and update docs accordingly.

---

Appendix A: Optional Dependency Hints (Debian-based)
- yara: sudo apt-get install yara
- binwalk: sudo apt-get install binwalk
- ropper: sudo apt-get install ropper (or pipx/pip if preferred)
- diaphora: packaged via Python + IDA/Ghidra export; document manual setup
- lief: pip install lief
- graphviz: sudo apt-get install graphviz
- unsquashfs: sudo apt-get install squashfs-tools

Appendix B: Example JSON Envelope (common)
{
  "metadata": {
    "tool_name": "ghidra_import_export_report",
    "provider_used": "openai:gpt-4o",
    "analysis_profile": "pentest",
    "cache_hit": false,
    "dependency_matrix": {
      "ghidra": "11.x",
      "lief": "missing"
    }
  },
  "summary": "Imports indicate network and crypto usage; missing import suggests ...",
  "findings": { "imports": [ ... ], "exports": [ ... ] },
  "artifacts": {},
  "recommendations": ["Run ghidra_security_features_check next"]
}
