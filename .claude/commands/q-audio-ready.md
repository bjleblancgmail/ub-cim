---
description: Generate audio-ready text for ElevenLabs from book chapters
version: 1.0.0
---

# Generate Audio-Ready Text for ElevenLabs

**Purpose:** Create an audio-optimized copy of the book for ElevenLabs TTS conversion. Does NOT modify original chapter files.

---

## Output Location

All audio-ready files go to: `my-book/audio/`

---

## ElevenLabs Formatting Rules

Apply ALL of the following transformations when generating audio-ready text:

### 1. Em Dashes (—)
- Replace `—` with `, ` (comma + space) for parenthetical asides
- Replace `—` with `. ` (period + space) when the em dash separates independent clauses
- Use judgment: the goal is a natural spoken pause

**Example:**
- Original: `the mortal will and the divine will become one — whether in this life or on the mansion worlds`
- Audio: `the mortal will and the divine will become one, whether in this life or on the mansion worlds`

### 2. Tables
- Convert all markdown tables to narrated prose
- Pattern: "**[Term].** The Course speaks of [CIM term]. The Urantia Book calls this [UB term]. [Notes]."
- Each row becomes a sentence or short paragraph

### 3. Markdown Formatting
- Remove all `**bold**` markers — they are visual only
- Remove all `*italic*` markers — they are visual only
- Remove all `---` horizontal rules
- Remove all `## Section` headings — replace with a brief pause marker or omit
- Keep `# Chapter` headings as spoken text (e.g., "Chapter 5: The Terminology Bridge")
- Remove `**STATUS:**` lines entirely

### 4. Blockquotes
- Remove the `>` marker
- Keep the quote text as-is — the lead-in attribution we added handles the audio context

### 5. Special Characters
- Replace `...` (three dots) with `...` (ellipsis character) — ElevenLabs handles the unicode ellipsis more consistently
- Remove any remaining em-dash variants (en-dash `–`, etc.) — replace with commas

### 6. Parenthetical References
- Spell out references: "(Ch 6)" becomes "as discussed in Chapter 6"
- Remove or narrate any cross-references naturally

### 7. Known ElevenLabs Issues to Avoid
- Do NOT use excessive `<break>` tags — causes audio instability
- Do NOT leave bare URLs in text
- Do NOT leave markdown link syntax `[text](url)` — convert to just the text
- Avoid very long paragraphs (>500 words) — break into smaller chunks if needed

---

## Process

### Step 1: Create output directory

```bash
mkdir -p my-book/audio
```

### Step 2: Process each chapter

For each chapter file in `my-book/chapters/`:
1. Read the original markdown
2. Apply ALL formatting rules above
3. Write the audio-ready version to `my-book/audio/` with the same filename but `.txt` extension

### Step 3: Process appendices (if requested)

Only process appendices if the user explicitly asks. By default, skip them.

### Step 4: Report

List all files generated with word counts.

---

## EPUB Option

If the user requests an EPUB instead of text files:
- Generate a single audio-ready EPUB at `my-book/audio/UB-CIM-Study-Guide-audio.epub`
- Use the same formatting rules
- EPUB is ElevenLabs' preferred import format — it auto-detects chapters from H1 headings

---

## Important

- NEVER modify files in `my-book/chapters/` or `my-book/appendices/`
- Audio-ready files are COPIES with formatting changes only
- No editorial changes — same words, same meaning, just TTS-friendly formatting
