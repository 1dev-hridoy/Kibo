# Pet Animations, Widget Expand/Collapse & Sounds

How the desktop pet's animations, the widget's open/close, and the
reminder sounds fit together.

## 1. Create a new animation

Animations live in `agent/desktop_widget/pet_anim.py` — three functions:

```python
def start_fx(av, kind):
    if kind == "wave2":
        av._fx["wave2"] = 120          # 120 frames ≈ 6 seconds
        return
```

```python
# in update_fx(av): count the timer down every frame
for key in (..., "wave2"):
    if fx.get(key, 0) > 0:
        fx[key] -= 1
```

```python
# in draw_fx(av): draw it on the space canvas (no backgrounds possible)
if fx.get("wave2", 0) > 0:
    av.create_text(cx, cy - body_r - 10, text="👋",
                   fill="#ffffff", font=("Segoe UI", 12))
```

Then register the trigger word in `MochiAvatar._FX_ALIASES`
(`agent/desktop_widget/avatar.py`):

```python
("wave2", ("wave2", "hello there", "hey pet")),
```

And handle it in `trigger()`:

```python
if kind == "wave2":
    self._petted = 100
    self.state = "happy"
    start_fx(self, "wave2")
    return
```

Rules:

- All drawing happens on the **single space canvas** via the `_PetView`
  proxy — coordinates are pet-local, items auto-tagged `pet`, never any
  background rectangles. Never create a new Tk widget for visuals.
- Keep new `trigger` kinds in the same style: set `_petted` (frames the
  mood lasts), set `state`, call `start_fx`.
- Particle lists (`sparkles`, `fire`, `drops`, `notes`, `wdrops`) must be
  added to `_fx_busy()` and the avatar `_fx` dict, or idle auto-play and
  the showcase queue won't wait for them.
- Short user-facing names win: users type `dance`, not `celebration_v2`.
- Test headless before pushing:

```bash
python3 -c "
import tkinter as tk
from agent.desktop_widget.space_bg import SpaceBackground
from agent.desktop_widget.avatar import MochiAvatar
root = tk.Tk(); root.withdraw()
cv = SpaceBackground(root, base_color='#0a0a18', bg='#0a0a18')
cv.pack(fill='both', expand=True)
av = MochiAvatar(root, size=96, base_bg='#0a0a18')
cv.pet = av
av.trigger('wave2')
for i in range(150):
    av._frame = i
    av._animate()
    root.update_idletasks()
print('pet items:', len(cv.find_withtag('pet')))
root.destroy()"
```

## 2. Expand / collapse the widget

`KiboWidget._set_expanded(expanded, compact)` in
`agent/desktop_widget/widget.py`:

- `(True, False)` — full 760px view (task activity)
- `(True, True)` — compact 480px card (peek, custom messages, idle info)
- `(False, …)` — minimized pill (avatar only)

Width changes always go through `animate_width()` in
`window_fx.py` (smooth ~250ms ease, stays centered) — never set
`geometry()` directly for resizes. Text is drawn on the canvas
(`canvas_text.py` slots), so shrinking clips it cleanly with no
backgrounds.

Auto behavior (already wired):

- Task done → `Done!` + collapse to pill in 5s
- Reminder/notification message → clears in 10s (30s default)
- Hover idle pill → info card, minimizes ~7s after mouse leaves
- Custom text with `expires_in` → `_expire_custom` wipes state + file

## 3. Sound rules

Sounds live in `agent/runner/reminder_sounds.py`:

```python
SOUNDS = {"mysound": ["https://.../mysound-preview.mp3"]}
```

Rules:

- **One sound per reminder/action**, short (1–3s), notification-style.
- Files download once to `~/.config/kibo/sounds/<name>.mp3` (min 10 KB
  validated) — never bundle audio in git.
- Always play via `play_sound(name)`: background thread, `mpg123` →
  `mpv` → `ffplay` → `play` fallback chain, never block the agent.
- Hook sounds in the **tool**, not the animation:

```python
from agent.runner.reminder_sounds import play_sound
play_sound("mysound")
```

- Quiet hours (11pm–7am) skip scheduled reminders entirely, so no
  night-time sounds. Manual triggers always play.
- Match the sound to the visual: water splash with droplets, chime with
  celebrations — never TTS over a sound effect.
