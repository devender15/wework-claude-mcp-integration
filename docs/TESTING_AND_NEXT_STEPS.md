# Testing and Next Steps

Your container is running **Appium** (port 4723) and the **MCP server** (stdio). Here’s how to run the flow and test it.

---

## Booking on macOS with Claude (recommended)

On **macOS**, Docker runs in a VM, so the container **cannot see your Android device**. If you see errors like `adb died with SIGTRAP` or "No connected Android device", use the **host** for both Appium and the MCP server:

1. **Install on the host** (if not already): Node 20, Python 3.10+, Android SDK platform-tools (`adb`), and project deps. If you use conda:
   ```bash
   conda activate wework
   cd /path/to/wework-automate
   pip install -r requirements.txt
   ```
   Then install Appium (Node): `npm install -g appium && appium driver install uiautomator2 && appium plugin install inspector`
2. **Start Appium on the host** (in a terminal):
   ```bash
   appium --use-plugins=inspector
   ```
   Leave it running (port 4723).
3. **Point Claude Desktop at the host MCP server** (not Docker). In `~/Library/Application Support/Claude/claude_desktop_config.json` use **one** of these:

   **Option A – conda env `wework` via shell script (recommended if conda server disconnects):**
   ```json
   {
     "mcpServers": {
       "personal-automation": {
         "command": "bash",
         "args": ["/Users/devenderpal/work/wework-automate/run_mcp_server_with_conda.sh"]
       }
     }
   }
   ```
   Uses a script that sources conda and activates **wework** so Claude doesn’t need `conda` on PATH. If your conda is not in `~/miniconda3` or `~/anaconda3`, edit the script and set `CONDA_ROOT` at the top. Use your **actual project path** in `args`.

   **Option A2 – conda env via direct Python path (no script):**  
   Run `conda activate wework && which python` and use that path as `command`:
   ```json
   {
     "mcpServers": {
       "personal-automation": {
         "command": "/Users/devenderpal/miniconda3/envs/wework/bin/python",
         "args": ["/Users/devenderpal/work/wework-automate/run_mcp_server.py"]
       }
     }
   }
   ```
   Replace the command path with your actual wework Python path.

   **Option B – launcher script (no conda; no `cwd` needed):**
   ```json
   {
     "mcpServers": {
       "personal-automation": {
         "command": "python3",
         "args": ["/Users/devenderpal/work/wework-automate/run_mcp_server.py"]
       }
     }
   }
   ```
   Use your **actual project path** in `args`.

   **Option C – module with `cwd` set:**
   ```json
   {
     "mcpServers": {
       "personal-automation": {
         "command": "python3",
         "args": ["-m", "app_mcp.server"],
         "cwd": "/Users/devenderpal/work/wework-automate"
       }
     }
   }
   ```
   Use your actual project path for `cwd`. Use `python3` if your system doesn't have `python`.
4. **Connect your Android device** (USB or `adb connect <ip>:5555`) and run `adb devices`.
5. Restart Claude and ask it to book desks; the tool will run on the host and see the device.

---

## Prerequisites

1. **Android device or emulator**
   - WeWork app installed: `in.co.wework.spacecraft`
   - Device connected via USB **or** over network (e.g. `adb connect <ip>:5555`)

2. **If using Docker with a USB device**
   - Use `--network host` (you already do) and pass the device through, e.g.:
     ```bash
     docker run -it --rm --network host \
       -v /var/run/docker.sock:/var/run/docker.sock \
       --privileged -v /dev/bus/usb:/dev/bus/usb \
       personal-automation
     ```
   - Or run Appium + automation on the **host** (no Docker) so `adb` and the device are on the same machine.

---

## Option 1: Test via MCP (e.g. from Cursor)

The MCP server exposes one tool: **`wework_book_desks(dates, building)`**.

### A. Add the server to Cursor

1. Open **Cursor Settings** → **MCP** (or **Features** → **MCP**).
2. Add a new MCP server. Example config (run the server **inside** the container via Docker):

   **Using Docker (container runs the server):**
   ```json
   {
     "mcpServers": {
       "personal-automation": {
         "command": "docker",
         "args": [
           "run",
           "-i",
           "--rm",
           "--network", "host",
           "personal-automation"
         ]
       }
     }
   }
   ```
   `-i` keeps stdin open so Cursor can talk to the MCP server over stdio.

   **Or run the server locally (no Docker):**
   ```json
   {
     "mcpServers": {
       "personal-automation": {
         "command": "python",
         "args": ["-m", "app_mcp.server"],
         "cwd": "/path/to/wework-automate"
       }
     }
   }
   ```
   Use this when you run `python -m app_mcp.server` from the project root on your machine (Appium can still be in Docker or on the host).

3. Restart Cursor or reload MCP.
4. In chat, you can ask: *“Book WeWork desks for 2026-02-25 and 2026-02-26 at Two Horizon Center”* — Cursor will call the `wework_book_desks` tool.

### B. Test the MCP tool from the command line (optional)

You can use the MCP Inspector or any MCP client that speaks stdio. Example with the official inspector:

```bash
npx -y @modelcontextprotocol/inspector
```

Then add a server with:

- **Transport:** Stdio  
- **Command:** `docker`  
- **Args:** `run -i --rm --network host personal-automation`  

(Or point to a local `python -m app_mcp.server` if you run the server on the host.)

---

## Option 2: Test the WeWork flow directly (no MCP)

This runs the same booking logic that the MCP tool uses, without going through MCP.

### A. Appium must be reachable

- If Appium runs in Docker with `--network host`, use base URL **`http://127.0.0.1:4723`** from the host (same as inside the container with host network).
- Ensure one Android device is connected: `adb devices`.

### B. Run the flow from the repo (on the host)

From the project root:

```bash
# Optional: use the same Python/env as in the image
pip install -r requirements.txt

# Run the booking flow (same as MCP tool logic)
python -m automation.wework_flow
```

Or run the module’s `__main__` block (edit dates/building in `automation/wework_flow.py` first):

```bash
python automation/wework_flow.py
```

### C. Smoke test (session only)

Checks that Appium and the device work; does not book anything:

```bash
# Edit wework_smoke.py if your UDID differs, then:
python wework_smoke.py
```

Make sure the Appium URL in the script matches where Appium is running (e.g. `http://127.0.0.1:4723` when using host network).

---

## Troubleshooting

| Error | What to do |
|-------|------------|
| **"Unexpected token … is not valid JSON"** (Docker) | Appium’s log output was leaking to stdout. Rebuild the image so the updated entrypoint is used: `docker build -t personal-automation -f docker/Dockerfile .` Then restart Claude. |
| **"Failed to spawn process: No such file or directory"** (Python config) | Add **`cwd`** with the full path to this project (e.g. `"/Users/devenderpal/work/wework-automate"`). Use **`python3`** instead of `python` if your Mac doesn’t have a `python` command. |
| **"Server disconnected"** | Use the **launcher** with your **conda env**: `"command": "conda"`, `"args": ["run", "-n", "wework", "python", "/full/path/to/run_mcp_server.py"]`. Or use the launcher with `python3`; quit Claude completely after changing config. |
| **"adb died with SIGTRAP"** / **"rosetta error"** | You’re running the server inside Docker on macOS; the container can’t see your device. Use the **host** setup (Python + Appium on the host) as in “Booking on macOS with Claude” above. |
| **"The instrumentation process cannot be initialized"** | UiAutomator2 or the WeWork app failed to start on the device. See **Instrumentation error** below. |

---

## Instrumentation error (“instrumentation process cannot be initialized”)

This Appium error usually means the UiAutomator2 test helper or the WeWork app failed on the device. Try in order:

1. **Device state**
   - Unlock the device and keep the screen on.
   - Ensure only one device is connected: `adb devices`.

2. **Run the WeWork app manually**
   - Open the WeWork app on the phone and confirm it launches (log in if needed). If it crashes, fix the app or reinstall it before automating.

3. **Inspect logcat**
   - In a terminal, run:  
     `adb logcat -c && adb logcat *:E`  
     then trigger the booking again. Look for Java crashes, `Instrumentation`, or `io.appium` lines. Fix or report the cause (e.g. missing permission, app crash).

4. **Reinstall UiAutomator2 components**
   - Uninstall the Appium test apps from the device (Settings → Apps → show system → “Appium” or “io.appium”), or run:  
     `adb uninstall io.appium.uiautomator2.server` and `adb uninstall io.appium.uiautomator2.server.test`.  
     Then run the flow again so Appium reinstalls them.

5. **Capabilities**
   - If the app was updated, the main activity might have changed. In `automation/driver.py` and `automation/wework_flow.py`, `APP_ACTIVITY` is `in.co.wework.spacecraft.SpacecraftActivity`; adjust if your WeWork build uses a different launcher activity.

---

## Quick checklist

| Step | Action |
|------|--------|
| 1 | Start container: `docker run -it --rm -p 4723:4723 --network host personal-automation` (and device args if using USB) |
| 2 | Connect Android device: `adb devices` (from host or inside container if adb is there) |
| 3 | **MCP:** Add the server in Cursor/Inspector and invoke “book desks for …” in chat |
| 4 | **Direct:** Run `python -m automation.wework_flow` or `python wework_smoke.py` from the repo with Appium on 4723 |

---

## Summary

- **To run the flow:** Use the MCP tool from Cursor (or another MCP client) **or** run the Python automation directly. Both use the same logic under `automation.wework_flow` and `app_mcp.tools.wework`.
- **To test:**  
  - **MCP:** Add the server to Cursor and ask it to book desks; or use MCP Inspector.  
  - **Appium/device:** Run `wework_smoke.py` or `automation.wework_flow` with Appium on 4723 and one device connected.
