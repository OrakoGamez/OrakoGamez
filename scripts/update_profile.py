import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config" / "skills.json"
README = ROOT / "README.md"
PROGRESS_DIR = ROOT / "assets" / "progress"

SKILLS = {
    "cpp": ("C++", "Programming fundamentals", "cpp.svg"),
    "unreal_engine": ("Unreal Engine 5", "Game development", "unreal.svg"),
    "blender": ("Blender", "3D and visual work", "blender.svg"),
    "content_creation": ("Content Creation", "YouTube", "content-creation.svg"),
}

LEVELS = [
    (20, "🌱 Starting"),
    (40, "📚 Beginner"),
    (60, "🔧 Developing"),
    (80, "🚀 Intermediate"),
    (100, "🏆 Advanced"),
]

COLORS = {
    "cpp": "#56B4F8",
    "unreal_engine": "#A970FF",
    "blender": "#FF8A2A",
    "content_creation": "#FF4F4F",
}


def level(value):
    for maximum, name in LEVELS:
        if value <= maximum:
            return name
    return "🏆 Advanced"


def validate(data):
    for key in SKILLS:
        if key not in data or not isinstance(data[key], int) or not 0 <= data[key] <= 100:
            raise ValueError(f"{key} must be an integer from 0 to 100")


def progress_svg(key, value):
    color = COLORS[key]
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="520" height="12" viewBox="0 0 520 12" role="img" aria-label="{SKILLS[key][0]} learning progress: {value} percent">
  <rect width="520" height="12" rx="6" fill="#30363d"/>
  <rect width="{5.2 * value:.1f}" height="12" rx="6" fill="{color}"/>
</svg>\n'''


def replace_block(text, start, end, replacement):
    pattern = re.compile(re.escape(start) + r".*?" + re.escape(end), re.DOTALL)
    if not pattern.search(text):
        raise ValueError(f"README markers not found: {start} / {end}")
    return pattern.sub(start + "\n" + replacement.rstrip() + "\n" + end, text, count=1)


data = json.loads(CONFIG.read_text(encoding="utf-8"))
validate(data)

# Generate the four visual progress-bar components from the central config.
PROGRESS_DIR.mkdir(parents=True, exist_ok=True)
for key, value in data.items():
    (PROGRESS_DIR / SKILLS[key][2]).write_text(progress_svg(key, value), encoding="utf-8")

cards = []
for key, (name, subtitle, svg) in SKILLS.items():
    value = data[key]
    cards.append(f'''<td width="50%" valign="top" align="center">
<p><img src="https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/{'cplusplus/cplusplus-original' if key == 'cpp' else 'unrealengine/unrealengine-original' if key == 'unreal_engine' else 'blender/blender-original' if key == 'blender' else 'youtube/youtube-original'}.svg" width="48" height="48" alt="{name}"></p>
<p><strong>{name}</strong></p>
<p><sub>{level(value)} · {subtitle}</sub></p>
<p><strong>{value}%</strong></p>
<p><img src="./assets/progress/{svg}" width="260" height="10" alt="{name} learning progress: {value} percent"></p>
</td>''')

cards_block = f'''<table>
<tr>
{cards[0]}
{cards[1]}
</tr>
<tr>
{cards[2]}
{cards[3]}
</tr>
</table>

> Progress percentages are personal learning estimates, not professional proficiency.'''

rows = "\n".join(
    f'| {SKILLS[key][0]} | {level(data[key])} | `{"█" * round(data[key] / 10)}{"░" * (10 - round(data[key] / 10))} {data[key]}%` |'
    for key in SKILLS
)

table_block = f'''<details>
<summary>🎯 Learning Progress</summary>

| Skill | Level | Progress |
|---|---|---|
{rows}

</details>'''

text = README.read_text(encoding="utf-8")
text = replace_block(text, "<!-- SKILL-CARDS-START -->", "<!-- SKILL-CARDS-END -->", cards_block)
text = replace_block(text, "<!-- SKILL-TABLE-START -->", "<!-- SKILL-TABLE-END -->", table_block)
README.write_text(text, encoding="utf-8")
print("Profile updated from config/skills.json")
