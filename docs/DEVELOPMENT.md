# Development and reproducibility

A standalone static website for the manuscript image analysis, paired Hebrew and English readings, word segmentation, and textual-location comparison.
All interface scripts, styles, images, and analysis data are included locally.
There is no Lavish runtime, backend, API key, or Python requirement for hosting.

The reader starts with the strict transcription and translation and can switch between three explicitly labelled versions using tabs with an animated underline:

- Image-only transcription with a fragmentary translation.
- Contextual Hebrew reading with a working translation and marked inferences.
- Reference-led Hebrew reconstruction with a fuller translation and marked supplies.

The page follows three stages: read the text, inspect the image, and review the method.
Each stage uses the same tab bar and sliding underline above its active card.
Inspection has four tool tabs; methodology has two analysis tabs.
Each passage has one inline Reading notes section containing its phrase evidence and translation alternatives.
Links into the image viewer include a return link to the selected passage.
The reference reconstruction retains the apparent image spellings יומם and לשמים.
The methods and search scope remain visible, including the unsuccessful shape-matching control.

## Preview locally

Use Node.js 22 or newer.
There are no npm package dependencies.

```sh
npm run dev
```

Open `http://127.0.0.1:4173`.
Direct links select a version: `?reading=strict`, `?reading=contextual`, or `?reading=reconstructed`.
Browser Back and Forward preserve version selection.
To use another port, run `npm run dev -- --port 4174`.

## Deploy to Vercel

From this project directory, run:

```sh
npx vercel
```

The CLI guides you through selecting your account and creating or linking a project.
For a production deployment, run `npx vercel --prod`.

Alternatively, push this project to a Git repository and import it into Vercel.
Use the repository root as the project root.
The included `vercel.json` configures the following settings:

| Setting | Value |
| --- | --- |
| Framework preset | Other |
| Build command | `npm run build` |
| Output directory | `dist` |

These settings use Vercel’s documented [static configuration](https://vercel.com/docs/project-configuration/vercel-json).
Keep `site/`, `scripts/`, `package.json`, `package-lock.json`, and `vercel.json` in the repository.
The `.vercelignore` file excludes the local Python environment, old review sessions, and research tooling from uploads.

## Build and inspect the deployable output

```sh
npm run build
npm run preview
```

The build verifies referenced evidence files and local runtime dependencies before copying the public site into `dist/`.
You can also serve `dist/` with any static web host.

## Edit the site

- `site/assets/app.js`: image inspection and main page interactions.
- `site/assets/segmentation.js`: word selection, spacing plots, and passage-location tables.
- `site/assets/section-tabs.js`: inspection and method tabs, keyboard navigation, and automatic target revealing.
- `site/assets/interpretation.js`: paired reading modes and inline passage notes.
- `site/assets/styles.css`: interface styling.
- `analysis/templates/index.html`: source HTML template.
- `analysis/segmentation_section.html`: source markup for the additional analysis sections.
- `analysis/findings.json`: readings, uncertainty notes, and translations.
- `analysis/interpretation.json`: paired contextual and restored phrases, provenance, hypotheses, and sources.
- `analysis/interpretation_section.html`: source markup for the reading modes.
- `analysis/method_section.html`: source markup for methods and hypotheses.

After editing the HTML templates or findings, regenerate the page and data:

```sh
.venv/bin/python analysis/build_review.py
```

`site/index.html` and `site/assets/data.js` are generated outputs and should be regenerated from these inputs.
Commit the regenerated files so Vercel can build without Python.

## Reproduce the image analysis

The original screenshot remains in the project root.
Python is needed only when regenerating the research outputs:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r analysis/requirements.txt
.venv/bin/python analysis/inspect_manuscript.py
.venv/bin/python analysis/compare_glyphs.py
.venv/bin/python analysis/segment_and_locate.py
.venv/bin/python analysis/build_review.py
npm run build
```

The scripts write to `site/evidence/` directly.
They do not depend on the former review folder.
See [the analysis report](../analysis/REPORT.md) for methods, provenance, and limitations.
