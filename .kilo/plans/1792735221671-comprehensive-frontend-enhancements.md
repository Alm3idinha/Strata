# Comprehensive Frontend Enhancements Plan

## Goal
Address multiple UX gaps in the Strata web UI: per-tool MCP toggles, theme consistency, expanded attachments, API connectivity info, and external client integration guidance.

---

## 1. Per-Tool MCP Toggle (NOT all-or-nothing)

### Current State
- `/mcp` endpoint returns all tools from all servers
- Chat sends `"strata_mcp": true` → model gets ALL tools from ALL ready servers
- Monitor tab shows server list with tool chips but no toggles
- Sampling tab has single "Use tools from MCP servers" toggle (on/off only)

### Required Changes

**Backend (`serve/mcp.py`):**
- ✓ Add `enabled` field to each tool in `status()` response
- ✓ Add `enabled` field to each server in `status()` response
- ✓ Persist tool/server enable state in run config (`mcp_servers` + `mcp_tools_enabled` map)
- ✓ Filter `routes()` and `template_tools()` to only include enabled tools
- ✓ Add `is_tool_enabled()`, `set_tool_enabled()`, `set_server_enabled()`, `get_tools_enabled_config()` methods
- Add POST `/mcp/toggle` endpoint: `{server?, tool?, enabled: bool}`

**Frontend (`serve/web/app.js` + `index.html`):**
- Monitor tab: add toggle per tool (chip → toggle switch)
- Monitor tab: add toggle per server (server header)
- Sampling tab: replace single toggle with expandable list showing servers → tools with individual toggles
- Persist state via new API endpoint

**Config Schema:**
```json
{
  "mcp_servers": {...},
  "mcp_tools_enabled": {"server__tool": true, "server2__tool2": false}
}
```

---

## 2. Theme Consistency Fix (Light Mode Shows Dark/Grey)

### Current State
- `tokens.css` defines both light (`:root`) and dark (`[data-theme="dark"]`) tokens correctly
- `app.js:setTheme()` toggles `document.documentElement.dataset.theme`
- `index.html` has `<html data-theme="light">` as default
- Inline script in `<head>` reads `localStorage.getItem("strata.theme")` or system preference

### Issue to Investigate
- Check if `components.css` or `app.css` overrides tokens with hardcoded colors
- Check if any inline styles bypass CSS variables
- Verify `setTheme()` is called on load (line 67: `setTheme(document.documentElement.dataset.theme || "light", false)`)

### Debug Steps
1. Open DevTools → Elements → `<html>` → check `data-theme` attribute
2. Inspect a grey element → Computed styles → trace to source
3. Check if `components.css` (Strata UI kit) has hardcoded colors

### Fix Approach
- ✓ Ensure all colors in `app.css`/`components.css` use `var(--st-*)` tokens
- ✓ Remove any hardcoded `#hex` or `rgb()` values (fixed `.scrim` in `app.css` to use `--st-scrim`)
- ✓ Verify the inline script runs before body renders (it does, in `<head>`)

---

## 3. Expanded Attachment Support

### Current State
- `attach-btn` accepts text files only (title says "Attach a text file")
- `input[type=file]` has `multiple` but no `accept` attribute
- Files uploaded via chat API as base64? Need to check

### Required Changes

**Backend (`serve/server.py`):**
- ✓ Extend `/api/chat` or add `/api/upload` to handle multipart/form-data
- ✓ Support: images (PNG, JPG, WebP), PDFs, text files (MD, TXT, JSON, CSV), code files
- ✓ For images: if model has vision (`health.images=true`), send as vision content
- ✓ For PDFs/text: extract text content, inject as system/user message
- ✓ Return file ID/reference for chat to use

**Frontend (`serve/web/app.js` + `index.html`):**
- ✓ Update `attach-btn` title dynamically based on `health.images`
- ✓ Add `accept` attribute: `accept=".txt,.md,.json,.csv,.pdf,.png,.jpg,.jpeg,.webp"`
- ✓ Show file preview chips in `.attachments` div (already exists, hidden)
- ✓ Drag-drop support (already has `.st-composer.dragging` styles)
- ✓ File size limit indicator (configurable, default 10MB)

**Config:**
- ✓ Add `max_upload_mb` to run config

---

## 4. API Connectivity Info in Frontend

### Current State
- About tab → "Connect your tools" section (`#facts-api`) - shows API endpoints
- About tab → Settings card has API key input (only if server started with `--api-key`)
- No display of: base URL, OpenAI vs Anthropic endpoint paths, WebSocket status

### Required Changes

**Frontend (`serve/web/app.js` + `index.html`):**
- ✓ Enhance `#facts-api` in About tab to show:
  - ✓ Base URL (e.g., `http://127.0.0.1:8080`)
  - ✓ OpenAI-compatible: `/v1/chat/completions`, `/v1/models`
  - ✓ Anthropic-compatible: `/v1/messages`
  - ✓ Health: `/health`, `/api/health`
  - ✓ WebSocket: `/ws` (if implemented)
  - ✓ API key status: "Required" / "Not required" / "Saved in browser"
- ✓ Add "Copy endpoint" buttons
- ✓ Add "Test connection" button that calls `/health`
- ✓ Show CORS origins if configured

**Backend (`serve/server.py`):**
- ✓ Add `/api/config/public` endpoint returning safe config (port, host, api_key_required, cors_origins, endpoints)
- ✓ Or extend `/health` with `api` object

---

## 5. External Client Integration Guide (LM Studio, VS Code, Kilo Code)

### Current State
- About tab shows endpoints but no client-specific instructions
- No generated config snippets

### Required Changes

**Frontend (About tab - new section or enhanced "Connect your tools"):**
- ✓ Add client-specific cards with:
  - ✓ **LM Studio**: "OpenAI compatible" → Base URL, Model name, API key
  - ✓ **VS Code (Continue/Cline/CodeGPT)**: JSON config snippets
  - ✓ **Kilo Code**: `kilo.json` provider config snippet
  - ✓ **Cursor**: `.cursorrules` or settings.json
  - ✓ **Open WebUI**: Admin panel → Connections
  - ✓ **Generic OpenAI SDK**: Code snippet (Python/JS)

**Content Source:**
- ✓ Generate from server config: `host`, `port`, `api_key`, `model`
- ✓ Static markdown templates per client, interpolated at render time

---

## Implementation Order (Dependencies)

| Phase | Task | Status |
|-------|------|--------|
| 1 | Theme consistency fix | ✓ Complete |
| 2 | API connectivity info in About tab | ✓ Complete |
| 3 | Expanded attachments | ✓ Complete |
| 4 | Per-tool MCP toggle | **In Progress** - Backend 90% complete, Frontend pending |
| 5 | External client guides | ✓ Complete |

---

## Files to Modify

| File | Changes |
|------|---------|
| `serve/server.py` | ✓ `/api/config/public`, `/api/upload`, `/mcp/toggle` (pending), config persistence |
| `serve/mcp.py` | ✓ Tool/server enable filtering, status() includes enabled state, config persistence |
| `serve/web/index.html` | ✓ Monitor tab tool toggles (pending), Sampling tab expandable list (pending), About tab API info + client guides, attachment accept/types |
| `serve/web/app.js` | ✓ Theme debug, attachment handling, MCP toggle UI (pending), API info fetch, client guide rendering |
| `serve/web/app.css` | ✓ Toggle switch styles, attachment chips, client guide cards |
| `serve/web/tokens.css` | ✓ Verify no hardcoded colors (audit) - added `--st-scrim` |
| `serve/web/components.css` | ✓ Audit for hardcoded colors |

---

## Validation Checklist

- ✓ Light theme: all text readable, backgrounds white/light grey, accents green
- ✓ Dark theme: all text readable, backgrounds dark, accents mint green
- ✓ Attach: image → shows preview, sends as vision content (if vision model)
- ✓ Attach: PDF → extracts text, injects into chat
- ✓ Attach: code file → shows as text attachment
- [ ] MCP: toggle individual tool → immediately affects next chat request
- [ ] MCP: toggle server → enables/disables all its tools
- [ ] Sampling tab: shows hierarchical server→tool toggles
- ✓ About tab: shows copyable endpoints for OpenAI/Anthropic
- ✓ About tab: shows client-specific config snippets (LM Studio, VS Code, Kilo, Cursor)
- ✓ API key: save in browser → used in Authorization header for all fetches

---

## Out of Scope

- Building actual MCP servers (user provides them)
- WebSocket streaming for chat (separate feature)
- Multi-user/auth (Strata is single-user local)
- Model download/management UI (handled by installer)

---

## Open Questions

1. **Attachment processing**: Server-side (Python) or client-side (JS FileReader)? ✓ Server-side (allows PDF parsing libraries).
2. **MCP toggle persistence**: Per-browser (localStorage) or per-server (config file)? ✓ Config file survives restarts.
3. **API key in client snippets**: Include placeholder or instruct user to generate? ✓ Placeholder with comment.
4. **Theme issue**: Need to reproduce first - is it specific elements or global? ✓ Fixed via CSS token audit.