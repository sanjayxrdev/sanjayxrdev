![metrics](info-card.svg)
![Metrics](contrib-heatmap.svg)

---

## 🚀 About This Profile

This is a **terminal-style GitHub profile** with animated SVGs that refresh **daily automatically** via GitHub Actions workflow.

The profile showcases:
- **Contribution Heatmap** – Your GitHub contribution graph rendered as an animated SVG with stats
- **Info Card** – A neofetch-style card displaying your current work, stack, and focus
- **ASCII Portrait** – An optional animated ASCII art version of your photo (if provided)

All visuals are **generated programmatically** from your GitHub data, and the pipeline runs **daily** or **on-demand**.

---

## 📂 Project Structure

```
.
├── .github/workflows/
│   └── update-profile.yml          # Daily + manual workflow
├── scripts/
│   ├��─ fetch_contributions.py      # Fetch GitHub contribution data
│   ├── render_heatmap_svg.py       # Generate contribution heatmap SVG
│   ├── make_info_card.py           # Generate neofetch-style info card
│   ├── make_ascii_svg.py           # Convert photo to animated ASCII SVG
│   ├── prep_photo.py               # Prep photo (bg removal + contrast boost)
│   ├── requirements.txt            # Production dependencies
│   └── requirements-portrait.txt   # Portrait generation deps (local only)
├── data/
│   └── contributions.json          # Cached contribution data
├── info-card.svg                   # Generated info card
├── contrib-heatmap.svg             # Generated contribution heatmap
├── ascii-portrait.svg              # Generated ASCII portrait (optional)
└── README.md                       # This file
```

---

## 🔧 Scripts Overview

### 1. **fetch_contributions.py**
Scrapes your GitHub contribution calendar (no token needed) and generates JSON with stats.

**Usage:**
```bash
python scripts/fetch_contributions.py [USERNAME]
```

**Output:** `data/contributions.json`

**What it extracts:**
- Raw day-by-day contribution counts
- Total contributions
- Current streak
- Longest streak
- Best day
- Monthly totals

---

### 2. **render_heatmap_svg.py**
Converts `data/contributions.json` into an animated contribution heatmap SVG.

**Features:**
- Animated grid reveal (diagonal, column-by-column)
- GitHub-style color palette
- Embedded statistics (total, streaks, best day)
- Legend (Less/More)

**Usage:**
```bash
python scripts/render_heatmap_svg.py
```

**Output:** `contrib-heatmap.svg`

---

### 3. **make_info_card.py**
Generates a neofetch-style info card SVG with your current work, stack, and focus.

**Features:**
- Terminal window frame with macOS-style traffic lights
- Animated text entries (fade + slide-in)
- Customizable rows (Now, Prev, Stack, Focus)
- Blinking cursor

**Usage:**
```bash
python scripts/make_info_card.py
```

**Environment variables:**
- `STATIC=1` – Output a frozen (non-animated) version

**Output:** `info-card.svg`

**To customize:** Edit the `ROWS` dictionary in the script:
```python
ROWS = [
    ("Now",   "Your current work"),
    ("Prev",  "Previous projects"),
    ("Stack", "Your tech stack"),
    ("Focus", "Your focus area"),
]
```

---

### 4. **prep_photo.py** (Optional)
Prepares a photo for ASCII conversion by removing background and boosting contrast.

**Requirements:**
```
pillow
numpy
opencv-python
rembg
```

**Usage:**
```bash
python scripts/prep_photo.py my-photo.jpg [-o output.png]
```

**Process:**
1. Remove background with rembg (U2Net model)
2. Crop to subject with small margin
3. Composite onto white background
4. Boost local contrast with CLAHE

**Output:** `source-prepped.png` (or custom path with `-o`)

---

### 5. **make_ascii_svg.py** (Optional)
Converts a prepared photo into an animated ASCII SVG.

**Requirements:**
```
pillow
numpy
```

**Usage:**
```bash
python scripts/make_ascii_svg.py [input.png] [-o output.svg]
```

**Features:**
- Downsamples image to character grid (100 cols by default)
- Brightness-based character density ramp
- Self-typing animation (rows wipe left-to-right with cursor)
- Plays once and freezes (no looping)

**Output:** `ascii-portrait.svg`

---

## ⚙️ GitHub Actions Workflow

### Daily Schedule + Manual Trigger

The workflow is defined in `.github/workflows/update-profile.yml` and:

✅ **Runs daily at midnight UTC** (`0 0 * * *`)  
✅ **Can be manually triggered** from Actions tab  
✅ **Executes all scripts in order**  
✅ **Auto-commits changes** (only if files changed)  
✅ **Caches dependencies** for speed

### How to Trigger Manually

1. Go to your repository on GitHub
2. Click **Actions** tab
3. Select **Update Profile Daily** workflow
4. Click **Run workflow** → choose branch → **Run workflow**

### Customize Schedule

Edit `.github/workflows/update-profile.yml` and change the `cron` expression:

```yaml
schedule:
  - cron: '0 0 * * *'  # Daily at midnight UTC
```

**Common schedules:**
- `0 9 * * *` – Daily at 9 AM UTC
- `0 */6 * * *` – Every 6 hours
- `0 0 * * 0` – Weekly on Sundays
- `*/30 * * * *` – Every 30 minutes

---

## 📦 Dependencies

### Production (Workflow)
```
requests==2.32.3
beautifulsoup4==4.12.3
```

### Optional (Portrait Generation - Local Only)
```
pillow
numpy
opencv-python
rembg
```

---

## 🚀 Quick Start

### 1. **First Time Setup**

Clone the repo and install dependencies:
```bash
git clone https://github.com/sanjayxrdev/sanjayxrdev.git
cd sanjayxrdev
pip install -r scripts/requirements.txt
```

### 2. **Generate Contribution Heatmap**

```bash
python scripts/fetch_contributions.py sanjayxrdev
python scripts/render_heatmap_svg.py
```

### 3. **Generate Info Card**

```bash
python scripts/make_info_card.py
```

Edit the card content by modifying `ROWS` in `make_info_card.py`.

### 4. **Optional: Generate ASCII Portrait**

Prep your photo:
```bash
pip install pillow numpy opencv-python rembg
python scripts/prep_photo.py my-photo.jpg
```

Generate ASCII SVG:
```bash
python scripts/make_ascii_svg.py
```

### 5. **Enable Automatic Updates**

The workflow is already in `.github/workflows/update-profile.yml`. It will:
- Run daily at midnight UTC
- Be manually triggerable from the Actions tab
- Auto-commit any changes

---

## 🎨 Customization

### Info Card
Edit `scripts/make_info_card.py`:
- Change `ROWS` for content
- Adjust colors (`FG_NAME`, `FG_KEY`, `FG_VAL`, etc.)
- Modify animations (delays, durations)

### Heatmap
Edit `scripts/render_heatmap_svg.py`:
- Adjust `PALETTE` for colors
- Change cell size (`CELL`)
- Modify animation timings

### Workflow
Edit `.github/workflows/update-profile.yml`:
- Change `cron` schedule
- Add environment variables
- Modify which scripts run

---

## 🐛 Troubleshooting

### Workflow fails to find scripts

Ensure all scripts are in `scripts/` directory and have correct permissions:
```bash
chmod +x scripts/*.py
```

### Photo prep fails (rembg)

The `rembg` model is downloaded on first run (~250 MB). Ensure stable internet.

### ASCII SVG is blank

The photo may be too flat or have poor contrast. Try:
- Using a different photo
- Adjusting CLAHE parameters in `prep_photo.py`
- Increasing image brightness before prep

### Workflow doesn't auto-commit

Ensure the repository has write permissions for GitHub Actions:
- Go to Settings → Actions → General
- Enable "Read and write permissions"

---

## 📊 What Gets Generated

| File | Description | Generated By | Frequency |
|------|-------------|--------------|-----------|
| `contrib-heatmap.svg` | Animated contribution grid | `render_heatmap_svg.py` | Daily |
| `info-card.svg` | Neofetch-style info card | `make_info_card.py` | Daily |
| `ascii-portrait.svg` | Animated ASCII art | `make_ascii_svg.py` | On-demand |
| `data/contributions.json` | Raw contribution data | `fetch_contributions.py` | Daily |

---

## 📝 Notes

- **No GitHub token needed** for contribution scraping (uses public HTML)
- **SMIL animations** are GitHub-compatible (play in `<img>` tags)
- **Portrait generation** requires `rembg` (~2-3 min first run, then cached)
- **All timestamps** are in UTC

---

## 🔗 Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Cron Syntax Reference](https://crontab.guru/)
- [rembg Documentation](https://github.com/danielgatis/rembg)
- [BeautifulSoup Documentation](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)

---

**Generated with ❤️ by automated scripts · Last updated: [automated]**
