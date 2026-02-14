Street-Fight MVP (Pygame)

Run instructions (Windows):

1. Install dependencies (use a virtualenv recommended):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Run the game:

```powershell
python execution\run_game.py
```

Controls:
- Move left: A or Left Arrow
- Move right: D or Right Arrow
- Attack: J (tap repeatedly to chain combos)
- Block: K (hold to reduce incoming damage, cannot move while blocking)
- Jump: W, Up Arrow, or Space (optional)
- Exit: Esc

Notes:
- This MVP includes combos, blocking, multiple enemy types (melee and ranged), and simple wave progression.
- The game generates tiny sound effects automatically into `.tmp/sounds/` on first run. You can replace them with your own `.wav` files.
- Tweak constants in `execution/run_game.py` to change health, damage, AI, waves, or spawn positions.
