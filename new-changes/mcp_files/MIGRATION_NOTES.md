# Higgsfield: REST API key → MCP migration

## What changed
- `config.py` — added `HIGGSFIELD_MCP_URL` and `HIGGSFIELD_TOKEN_STORE_PATH`.
  Old `HF_API_KEY` / `HF_API_SECRET` are left in place but unused by
  generation now.
- `utils/higgsfield_mcp_client.py` (new) — the MCP client: one-time
  browser OAuth login, disk-cached tokens, tool calling.
- `utils/image_generation.py` — `generate_image()` keeps the exact same
  signature your `nodes/image_generator.py` already calls, so that file
  needs **no changes**. Internally it now calls the MCP tool instead of
  `higgsfield_client.subscribe()`.
- `pyproject.toml` — swapped `higgsfield-client` for `mcp`.

## Setup steps
1. Copy these files into your project at the matching paths.
2. `uv sync` (or `pip install mcp>=1.27.0 --break-system-packages` if not
   using uv) to pull in the MCP SDK.
3. Add to `.env`:
   ```
   HIGGSFIELD_MCP_URL=https://mcp.higgsfield.ai/mcp
   ```
   (optional — this is already the default)
4. Run the debug check first, **before** touching the main app:
   ```
   python -m utils.higgsfield_mcp_client
   ```
   This opens your browser once for Higgsfield login, caches the token to
   `~/.config/ootsav-ads/higgsfield_tokens.json`, and prints every tool
   the server currently exposes.
5. **Confirm two things against that printed tool list** before running
   the app for real — Higgsfield's exact tool/argument names may differ
   from what I assumed:
   - `GENERATE_IMAGE_TOOL` in `utils/image_generation.py` (guessed as
     `"generate_image"`)
   - The argument names in the `arguments` dict in that same file
     (`prompt`, `aspect_ratio`, `model`, `resolution`, `reference_images`)
6. Run the app as usual (`python app.py`). The first image generation
   will reuse the cached token from step 4 — no browser popup.

## One open question you'll need to resolve
The MCP tool takes reference images as **public URLs**, not local file
paths. Your old flow uploaded local files via `higgsfield_client.upload_file()`
to get a URL. That upload call isn't wired up in the new code — check the
tool list from step 4 for something like `upload_image`; if there isn't
one, you'll need to host reference files yourself (S3, your own static
file server, etc.) before passing them in.

This does **not** affect your main "generate → feed the result back in as
a reference to edit it" loop — Higgsfield already returns a hosted URL for
generated images, so that URL can be passed straight back into
`reference_images` with no upload step at all.
