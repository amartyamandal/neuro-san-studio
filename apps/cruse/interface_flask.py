import atexit
import os
import queue
import hashlib
import time
from pathlib import Path
import logging

# pylint: disable=import-error
import schedule
from flask import Flask
from flask import jsonify
from flask import render_template
from flask import request, send_file
from flask_socketio import SocketIO

from apps.cruse.cruse_assistant import cruse
from dotenv import load_dotenv

# Ensure .env variables are loaded for CRUSE standalone mode
load_dotenv()

# Configure logging to stdout so it appears in cruse_logs
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
log = logging.getLogger("cruse_tts")

# Print startup messages immediately (bypassing logging)
print("[CRUSE-TTS] Starting CRUSE with TTS support...")
print(f"[CRUSE-TTS] ENABLE_OPENAI_TTS={os.getenv('ENABLE_OPENAI_TTS')}")
print(f"[CRUSE-TTS] OPENAI_API_KEY present: {bool(os.getenv('OPENAI_API_KEY'))}")
from apps.cruse.cruse_assistant import get_available_systems
from apps.cruse.cruse_assistant import parse_response_blocks
from apps.cruse.cruse_assistant import set_up_cruse_assistant
from apps.cruse.cruse_assistant import tear_down_cruse_assistant

os.environ["AGENT_MANIFEST_FILE"] = "registries/manifest.hocon"
os.environ["AGENT_TOOL_PATH"] = "coded_tools"

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret!"
socketio = SocketIO(app, ping_timeout=360, ping_interval=25)

# ------------------ OpenAI TTS Config ------------------
ENABLE_OPENAI_TTS = os.getenv("ENABLE_OPENAI_TTS", "false").lower() == "true"
OPENAI_TTS_MODEL = os.getenv("OPENAI_TTS_MODEL", "tts-1")
OPENAI_TTS_VOICE = "coral"  # Force coral voice for singing
OPENAI_TTS_FORMAT = os.getenv("OPENAI_TTS_FORMAT", "mp3")
OPENAI_TTS_TEMPERATURE = float(os.getenv("OPENAI_TTS_TEMPERATURE", "0.6"))
TTS_CACHE_DIR = Path(os.getenv("TTS_AUDIO_CACHE_DIR", "./logs/tts_cache"))
TTS_CACHE_TTL = int(os.getenv("TTS_AUDIO_CACHE_TTL_SECONDS", "600"))
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if ENABLE_OPENAI_TTS:
    TTS_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    print(f"[CRUSE-TTS] TTS enabled, cache dir: {TTS_CACHE_DIR}")
    if not OPENAI_API_KEY:
        print("[CRUSE-TTS] WARNING: ENABLE_OPENAI_TTS=true but OPENAI_API_KEY is missing; disabling remote TTS")
        log.warning("[TTS] ENABLE_OPENAI_TTS=true but OPENAI_API_KEY is missing; disabling remote TTS")
        openai_client = None
    else:
        try:
            from openai import OpenAI  # type: ignore
            openai_client = OpenAI(api_key=OPENAI_API_KEY)
            print(f"[CRUSE-TTS] OpenAI client initialized (model={OPENAI_TTS_MODEL} voice={OPENAI_TTS_VOICE})")
            log.info("[TTS] OpenAI client initialized (model=%s voice=%s)", OPENAI_TTS_MODEL, OPENAI_TTS_VOICE)
        except Exception as exc:  # pragma: no cover
            print(f"[CRUSE-TTS] ERROR: Failed to initialize OpenAI client: {exc}")
            log.error("[TTS] Failed to initialize OpenAI client: %s", exc)
            openai_client = None
else:
    print("[CRUSE-TTS] TTS disabled via ENABLE_OPENAI_TTS=false")
    openai_client = None
thread_started = False  # pylint: disable=invalid-name

user_input_queue = queue.Queue()
gui_context_queue = queue.Queue()

cruse_session, cruse_agent_state = set_up_cruse_assistant(get_available_systems()[0])


def cruse_thinking_process():
    """Main permanent agent-calling loop."""
    with app.app_context():
        global cruse_agent_state  # pylint: disable=global-statement
        user_input = ""

        while True:
            socketio.sleep(1)
            try:
                gui_context = gui_context_queue.get_nowait()
            except queue.Empty:
                gui_context = ""

            if user_input or gui_context:

                print(f"USER INPUT:{user_input}\n\nGUI CONTEXT:{gui_context}\n")
                response, cruse_agent_state = cruse(cruse_session, cruse_agent_state, user_input + str(gui_context))
                print(response)

                blocks = parse_response_blocks(response)

                gui_to_emit = []
                speeches_to_emit = []

                for kind, content in blocks:
                    if not content:
                        continue
                    if kind == "gui":
                        gui_to_emit.append(content)
                    elif kind == "say":
                        speeches_to_emit.append(content)

                # fallback if nothing was matched
                if not blocks and response.strip():
                    speeches_to_emit.append(response.strip())

                if gui_to_emit:
                    socketio.emit("update_gui", {"data": "\n".join(gui_to_emit)}, namespace="/chat")

                if speeches_to_emit:
                    socketio.emit("update_speech", {"data": "\n".join(speeches_to_emit)}, namespace="/chat")

            try:
                user_input = user_input_queue.get_nowait()
                if user_input == "exit":
                    break
            except queue.Empty:
                user_input = ""
                socketio.sleep(1)
                continue


@socketio.on("connect", namespace="/chat")
def on_connect():
    """Start background task on connect."""
    global thread_started  # pylint: disable=global-statement
    if not thread_started:
        thread_started = True
        # let socketio manage the green-thread
        socketio.start_background_task(cruse_thinking_process)


@app.route("/")
def index():
    """Return the html."""
    return render_template("index.html")


@socketio.on("user_input", namespace="/chat")
def handle_user_input(json, *_):
    """
    Handles user input.

    :param json: A json object
    """
    user_input = json["data"]
    user_input_queue.put(user_input)
    socketio.emit("update_user_input", {"data": user_input}, namespace="/chat")


@socketio.on("gui_context", namespace="/chat")
def handle_gui_context(json, *_):
    """
    Handles gui context.

    :param json: A json object
    """
    gui_context = json["gui_context"]
    gui_context_queue.put(gui_context)
    socketio.emit("gui_context_input", {"gui_context": gui_context}, namespace="/chat")


def cleanup():
    """Tear things down on exit."""
    print("Bye!")
    tear_down_cruse_assistant(cruse_session)
    socketio.stop()


@app.route("/shutdown", methods=["GET", "POST"])
def shutdown():
    """Shut down process."""
    cleanup()
    return "Capture ended"


@app.after_request
def add_header(response):
    """Add the header."""
    response.headers["Cache-Control"] = "no-store"
    return response


@app.route("/systems")
def systems():
    """
    Flask route to retrieve a list of available agent systems.

    Returns:
        Response: A JSON response containing a list of system names derived
                  from the manifest file.
    """
    return jsonify(get_available_systems())


@app.route("/tts_config")
def tts_config():
    """Expose whether remote TTS is enabled and basic parameters."""
    enabled = ENABLE_OPENAI_TTS and (openai_client is not None)
    return jsonify({
        "enabled": enabled,
        "model": OPENAI_TTS_MODEL,
        "voice": OPENAI_TTS_VOICE,
        "format": OPENAI_TTS_FORMAT,
        "cache_ttl": TTS_CACHE_TTL,
        "cache_dir": str(TTS_CACHE_DIR),
        "has_api_key": bool(OPENAI_API_KEY),
    })


@app.route("/tts", methods=["POST"])
def tts_generate():  # pragma: no cover - network path
    """Generate (or fetch cached) OpenAI TTS audio for posted text via streaming API.

    Request JSON:
        {"text": "...", "voice": "optional", "model": "optional"}
    Response: audio file (Content-Type based on format) or JSON error.
    """
    if not ENABLE_OPENAI_TTS or openai_client is None:
        return jsonify({"error": "OpenAI TTS disabled"}), 400

    data = request.get_json(silent=True) or {}
    text = (data.get("text") or "").strip()
    if not text:
        return jsonify({"error": "No text"}), 400

    model = (data.get("model") or OPENAI_TTS_MODEL).strip()
    voice = (data.get("voice") or OPENAI_TTS_VOICE).strip()
    audio_format = OPENAI_TTS_FORMAT

    # Hash for cache key
    h = hashlib.sha256(
        f"{model}|{voice}|{audio_format}|{text}".encode("utf-8")
    ).hexdigest()[:40]
    fname = TTS_CACHE_DIR / f"{h}.{audio_format}"

    fresh = fname.exists() and (time.time() - fname.stat().st_mtime) < TTS_CACHE_TTL
    if fresh:
        log.info("[TTS] Cache hit %s", fname.name)
        response = send_file(
            fname,
            mimetype=("audio/mpeg" if audio_format == "mp3" else f"audio/{audio_format}"),
        )
        response.headers["X-Remote-TTS"] = "1"
        response.headers["X-Cache"] = "HIT"
        return response

    # Try a short list of fallback models if first fails (helps when model not provisioned)
    fallback_models = [model]
    if model not in ("tts-1", "tts-1-hd"):
        fallback_models.append("tts-1")
    if "mini" in model and "gpt-4o-mini-tts" not in fallback_models:
        fallback_models.append("gpt-4o-mini-tts")

    last_error = None
    for attempt_model in fallback_models:
        try:
            from openai import OpenAI  # type: ignore  # noqa
            client = openai_client or OpenAI(api_key=OPENAI_API_KEY)
            log.info(
                "[TTS] Generating (model=%s voice=%s len=%d chars) non-stream (org streaming restrictions avoided)",
                attempt_model,
                voice,
                len(text),
            )

            # Build base params
            base_params = {
                "model": attempt_model,
                "voice": voice,
                "input": text,
            }

            tried_param_styles = []
            result = None
            audio_bytes: bytes | None = None
            # Some SDK versions expect 'format', newer/older may expect 'response_format'
            for fmt_key in ("format", "response_format", None):
                params = dict(base_params)
                if fmt_key:
                    params[fmt_key] = audio_format
                tried_param_styles.append(fmt_key or "<none>")
                try:
                    result = client.audio.speech.create(**params)
                    # Extract bytes from result
                    if hasattr(result, "read"):
                        audio_bytes = result.read()
                    elif isinstance(result, (bytes, bytearray)):
                        audio_bytes = bytes(result)
                    elif hasattr(result, "data") and isinstance(result.data, (bytes, bytearray)):
                        audio_bytes = bytes(result.data)  # type: ignore[arg-type]
                    elif hasattr(result, "output") and isinstance(result.output, (bytes, bytearray)):
                        audio_bytes = bytes(result.output)  # type: ignore[arg-type]
                    else:  # pragma: no cover - defensive
                        # Try attribute 'content'
                        maybe = getattr(result, "content", None)
                        if isinstance(maybe, (bytes, bytearray)):
                            audio_bytes = bytes(maybe)
                    if not audio_bytes:
                        raise RuntimeError("TTS response did not contain audio bytes (param styles tried: %s)" % tried_param_styles)
                    # Ensure destination dir exists in case it was cleaned up between startup and write
                    fname.parent.mkdir(parents=True, exist_ok=True)
                    with open(fname, "wb") as f:  # noqa: P103
                        f.write(audio_bytes)
                    log.info(
                        "[TTS] Success model=%s size=%.1fKB param_key=%s tried=%s",
                        attempt_model,
                        fname.stat().st_size / 1024,
                        fmt_key or "<none>",
                        tried_param_styles,
                    )
                    break
                except TypeError as type_exc:
                    # Wrong param name, try next variant
                    log.debug("[TTS] Param style %s failed: %s", fmt_key, type_exc)
                    continue
                except Exception as inner_exc:  # pragma: no cover
                    # Real failure for this model
                    raise inner_exc

            if not fname.exists():
                raise RuntimeError(f"Failed to produce audio file for model {attempt_model}")

            response = send_file(
                fname,
                mimetype=("audio/mpeg" if audio_format == "mp3" else f"audio/{audio_format}"),
            )
            response.headers["X-Remote-TTS"] = "1"
            response.headers["X-Cache"] = "MISS"
            response.headers["X-TTS-Model"] = attempt_model
            response.headers["X-TTS-Mode"] = "direct"
            return response
        except Exception as exc:  # pragma: no cover
            last_error = exc
            log.warning("[TTS] Model %s attempt failed: %s", attempt_model, exc)
            if fname.exists() and fname.stat().st_size == 0:
                try:
                    fname.unlink()
                except OSError:
                    pass
            continue

    log.error("[TTS] All model attempts failed: %s", last_error)
    return jsonify({"error": str(last_error), "attempted_models": fallback_models}), 500


def run_scheduled_tasks():
    """
    Continuously runs pending scheduled tasks.

    This function enters an infinite loop where it checks for and executes any tasks
    that are due to run, as defined in the `schedule` module. It pauses for one second
    between iterations to avoid excessive CPU usage.

    Intended to be run as a background thread or greenlet alongside other application logic.
    """
    while True:
        schedule.run_pending()
        socketio.sleep(1)


@socketio.on("new_chat", namespace="/chat")
def handle_new_chat(data, *args):
    """
    Initializes a new chat session with a selected conversational agent.

    This function resets the current Cruse assistant session and sets up a new one
    based on the provided `data`, which can be either a dictionary (with a "system" key)
    or a direct string specifying the agent name. If no valid agent is specified, it
    defaults to the first available system retrieved by `get_available_systems()`.

    Parameters:
    ----------
    data : dict or str
        The input specifying which agent/system to use. Can be a dictionary containing
        a "system" key or a string representing the agent's name.

    *args : tuple
        Additional arguments (currently unused).

    Side Effects:
    ------------
    - Tears down the existing Cruse assistant session.
    - Sets up a new session and updates the global `cruse_session` and `cruse_agent_state`.
    - Prints diagnostic messages to the console.

    Notes:
    -----
    - If no valid agent is found and no available systems are returned, the function exits early.
    - Relies on global variables: `cruse_session`, `cruse_agent_state`.

    """
    del args
    # pylint: disable=global-statement
    global cruse_session, cruse_agent_state

    if isinstance(data, dict):
        selected_agent = data.get("system")
    elif isinstance(data, str):
        selected_agent = data
    else:
        selected_agent = None

    # Fallback to default system if none was provided
    if not selected_agent:
        available_systems = get_available_systems()
        selected_agent = available_systems[0] if available_systems else None

    if not selected_agent:
        print("No available systems to initialize!")
        return

    print(f"Resetting session for new chat... Selected agent is: {selected_agent}")

    tear_down_cruse_assistant(cruse_session)
    cruse_session, cruse_agent_state = set_up_cruse_assistant(selected_agent)

    print("****New chat started****")


# Register the cleanup function
atexit.register(cleanup)

if __name__ == "__main__":
    socketio.run(
        app,
        host="0.0.0.0",
        port=5001,
        debug=False,
        allow_unsafe_werkzeug=True,
        log_output=True,
        use_reloader=False,
    )
