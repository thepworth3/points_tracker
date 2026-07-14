# The Scoreboard

A tiny static site for tracking points across a bunch of made-up competition
categories, hosted for free on GitHub Pages, updated from the command line.

## How it works

- `data.json` holds everyone's scores. This is the only "database."
- `index.html` / `style.css` / `script.js` just read `data.json` and render it.
- `scoreboard.py` is a CLI that edits `data.json` for you, so you never have
  to hand-edit JSON.

## One-time setup

1. Create a new repo on GitHub (e.g. `scoreboard`), and put all these files
   in it.
2. Push it:
   ```bash
   git init
   git add -A
   git commit -m "initial scoreboard"
   git branch -M main
   git remote add origin https://github.com/<your-username>/<repo-name>.git
   git push -u origin main
   ```
3. On GitHub: **Settings → Pages → Source → Deploy from branch → main → / (root)**.
   Your site will be live at `https://<your-username>.github.io/<repo-name>/`
   within a minute or two.

## Updating scores from the command line

All commands run from inside the project folder.

```bash
# see current standings
python3 scoreboard.py list

# add a competitor or category
python3 scoreboard.py add-player "Alice"
python3 scoreboard.py add-category "Trivia Night"

# set an exact score
python3 scoreboard.py set "Alice" "Trivia Night" 12

# increment/decrement instead of setting
python3 scoreboard.py add "Alice" "Trivia Night" 3
python3 scoreboard.py add "Alice" "Trivia Night" -1

# remove someone/something
python3 scoreboard.py remove-player "Alice"
python3 scoreboard.py remove-category "Trivia Night"
```

Every command that changes data saves `data.json` immediately. To actually
update the live website, commit and push:

```bash
git add data.json
git commit -m "update scores"
git push
```

Or use the built-in shortcut, which does all three for you:

```bash
python3 scoreboard.py publish "week 3 scores"
```

GitHub Pages will pick up the change automatically — refresh the site in
about 30–60 seconds and the new numbers will show up.

## Customizing

- Colors and fonts are all in `style.css` under the `:root` block at the top.
- The layout is plain HTML/CSS/JS, no build step, so you can edit it directly.

## Testing locally

Since the page uses `fetch()` to load `data.json`, opening `index.html`
directly as a `file://` URL won't work in most browsers. Run a tiny local
server instead:

```bash
python3 -m http.server 8000
```

then open `http://localhost:8000`.
