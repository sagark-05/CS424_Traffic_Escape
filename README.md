# Traffic Escape

Cross eight lanes of traffic to reach the top of the screen. Avoid cars, and ride the moving rafts through the central water lane.

## Setup

```bash
pip install -r requirements.txt
python main.py
```

## Controls

| Key | Action |
|-----|--------|
| A/D or Left/Right | Change lane |
| W / UP | Move forward |
| S / DOWN | Move back |
| R | Restart |

## Gameplay Features

- The player starts with three lives. Car collisions and falling into the water cost one life; the player respawns while lives remain.
- The central water lane has horizontally moving rafts. The player must be supported by a raft to cross and is carried along while riding it.
- The score increases during play. The top five scores are shown on screen and saved across sessions in `high_scores.json` at the project root. This file is created when a game ends or the player wins.
- The environment switches between day and night every 30 seconds. At night, cars show headlights and beams ahead of their direction of travel.
- Reach the top of the screen to win. The game ends when all three lives are lost.

## Folder Structure

```
traffic-escape/
├── main.py
├── requirements.txt
├── game/
│   ├── __init__.py
│   ├── game_engine.py
│   ├── player.py
│   └── traffic.py
├── high_scores.json  # created automatically after a run ends
└── README.md
```

## Submission Checklist

Completed tasks:

- [x] Fixed false car collisions caused by the player's starting position.
- [x] Added a three-life system with respawning after car collisions.
- [x] Added a moving-raft water lane that carries the player across safely.
- [x] Added persistent high scores with a top-five leaderboard.
- [x] Added an automatic day/night cycle with visible car headlights at night.

