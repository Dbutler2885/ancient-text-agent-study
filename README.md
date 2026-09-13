# Ancient text agent study

A capability test of an AI coding and research agent, and a worked example for further agentic study of ancient texts.
Using a supplied Hebrew manuscript screenshot, this project explores how an agent can inspect damaged writing, propose transcriptions and translations, test its assumptions, and make its reasoning inspectable.
The result is an interactive, independently hostable evidence viewer.

## Methods

- **Image evidence:** unchanged crops, magnification, contrast and threshold comparisons, and experimental deblurring, with recorded source coordinates.
  No reverse image search, OCR service, or generative image restoration was used.
- **Text analysis:** provisional letter readings, 64 annotated word windows, comparisons with clearer writing in the same image, and explicit alignment with Genesis 1.
- **Three paired Hebrew/English readings:** strict transcription and fragmentary translation, contextual reading with marked inferences, and fuller reconstruction with reference-supplied wording marked.
- **Auditable conclusions:** evidence, alternative readings, lexical sources, and limits accompany the interpretation.
  The shape matcher agreed with only 7 of 13 held-out manual labels and was not accepted as a basis for deciding readings.

This is a documented experiment, not an independently reviewed critical edition.
Familiar wording was already in context, so the reading was not blind.
The project does not establish the object's date, authenticity, or provenance.
See the [analysis report](analysis/REPORT.md) for the full methods, sources, and limitations.

## Run locally

Requires Node.js 22 or newer; there are no npm package dependencies.

```sh
npm run dev
```

Open `http://127.0.0.1:4173`.
To check the deployable output, run `npm run build`, then `npm run preview`.
