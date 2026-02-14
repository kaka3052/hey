# Game Directive

## Title
Street Fight Prototype — Pygame MVP

## Purpose
Provide a concise, testable specification for a small side-on street-fight/beat-'em-up prototype using Pygame.

## Chosen Tech
- Engine: Pygame (Python)
- Perspective: Side-on street fight (single-screen / short horizontal playfield)
- Controls: Keyboard only
- Art style: Pixel (placeholder sprites)
- Scope: MVP (player, 1 enemy type, basic attacks, health, win/lose)

## High-level Gameplay Summary
- 2D side-on street fight: player faces enemies, moves left/right, and performs melee attacks.
- Single-player, keyboard controls (left, right, attack, jump optional).
- Core loop: player fights one or more enemies; defeat enemies to win; player dies → lose state.

## Deliverables (MVP)
- Playable script: `execution/run_game.py` (Pygame-based).
- `requirements.txt` listing dependencies.
- `README.md` with run instructions and controls.
- Placeholder assets using colored rectangles.

## Inputs
- Design choices: number of enemies, enemy behavior aggressiveness, attack damage values. These are constants in `execution/run_game.py` for MVP.

## Tools / Execution
- `execution/run_game.py` launches the game locally. No external services required.

## Milestones for MVP
1. Player movement (left/right) and basic attack with cooldown.
2. One enemy type that moves toward the player and can damage the player.
3. Health bars for player and enemies, hit detection and damage.
4. Win condition: defeat all enemies; Lose condition: player health reaches 0.

## Acceptance Criteria
- Runs locally with `python execution/run_game.py` after `pip install -r requirements.txt`.
- Player can attack and defeat enemies; health updates and win/lose states trigger correctly.

## Constraints
- Keep performance modest and deterministic.
- All assets are placeholders (colored rectangles) for MVP.

## Next Steps
- I will refactor the MVP runner into a street-fight prototype now. After you test, we can iterate on enemy AI, combos, levels, or add polish.

---

If you'd like different mechanics (combo attacks, blocking, multiple enemy types), tell me which features to prioritize next.
