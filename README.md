# Q-Nonfiction-Author

**Write your non-fiction book with an AI companion that remembers your journey**

---

## What This Is

Q-Nonfiction-Author is a template for Claude Code that guides you through writing a non-fiction book. It's designed for:

- People who want to write a book but don't know where to start
- Non-professional writers with jobs and busy lives
- Anyone who needs structure and support for a 1-3 year creative project

**This is not a quick fix.** Writing a book takes time. Q-Nonfiction-Author makes that journey sustainable by giving you a companion who:

- Tracks your progress across months and years
- Remembers why you started when you forget
- Helps you through the hard parts without empty encouragement
- Celebrates showing up, not just word counts

---

## Methodology

This software provides tools to structure a non-fiction book based on proven writing methodologies for non-fiction authors.

### Trademark Notice

This project references principles from various non-fiction book writing methodologies. We are not affiliated with, endorsed by, or sponsored by any methodology creators or publishing companies. Any methodology names mentioned are trademarks of their respective owners.

---

## Getting Started

### Prerequisites

1. [Claude Code](https://claude.ai/code) installed

### Installation

```bash
# Extract the downloaded zip
unzip q-nonfiction-author.zip -d my-book-project

# Navigate to your project
cd my-book-project

# Start Claude Code
claude
```

### First Session

When you start Claude Code for the first time, just say:

> "I want to write a book."

Claude will:
1. Welcome you to Q-Nonfiction-Author
2. Ask you some questions to get to know you
3. Explain what the journey looks like
4. Set you up for your first real session

---

## How It Works

### The Journey (1-3 years)

| Phase | What Happens | Sessions |
|-------|--------------|----------|
| **Part 1: Prepare** | Set expectations, face fears | 1-2 |
| **Part 2: Position** | Find your book idea, audience, purpose | 3-5 |
| **Part 3: Outline** | Build the blueprint | 3-5 |
| **Part 4: Write** | The first draft (no editing!) | 50-100 |
| **Part 5: Edit** | Revise, beta readers, professional editing | 10-20 |
| **Part 6: Finish** | Title, dedication, acknowledgments | 5-10 |
| **Part 7: Design** | Cover, layout, bio | 5-10 |
| **Part 8: Publish** | Get it into the world | 3-5 |

### Daily Practice

- **~30 minutes per session**
- **200-250 words minimum** (some days you'll write 500, some days 50)
- **No rereading, no editing** during the writing phase
- **Consistency over intensity** - show up, even when you don't want to

### The Companion

Unlike most AI tools, Q-Nonfiction-Author builds a relationship over time:

- **Session 1:** Claude is getting to know you
- **Session 50:** Claude has seen you struggle and persist
- **Session 100:** Claude remembers what you said on day 1

When you've been away for a week, Claude notices and asks how you're doing - without judgment. When you're stuck, Claude reminds you why you started. When you want to quit, Claude takes it seriously and helps you decide if you need a break or if you're really done.

---

## Working Across Multiple Sessions

This template is built on the **Q-Command System** - a session management layer that gives Claude memory across conversations. This matters because:

- Claude Code sessions can end (context limit, you close the app, your laptop dies)
- Without session management, Claude forgets everything
- With Q-System, Claude picks up where you left off - even months later

For a 1-3 year writing journey, this is essential.

### Essential Commands

| Command | When to Use | What It Does |
|---------|-------------|--------------|
| `/q-begin` | Starting a session | Reviews where you left off, loads your context |
| `/q-end` | Finishing for now | Saves progress, documents what was done |
| `/q-checkpoint` | Mid-session | Saves progress without ending the session |
| `/q-status` | Anytime | Shows current state |

**First session?** Just start chatting - Claude will help you set up. Use `/q-end` when you're done.

**Returning?** Start with `/q-begin` so Claude remembers your book, your progress, and your journey.

Type `/q-` and press Tab to see all available commands.

---

## Project Structure

```
my-book-project/
├── my-book/                  # Your working area
│   ├── author-profile.md     # Who you are, why you're writing
│   ├── session-log.md        # Progress tracking
│   ├── outline/              # Your book outline
│   └── chapters/             # Your draft chapters
├── methodology/              # The system (don't edit)
├── seed-materials/           # Reference materials
├── .claude/                  # Claude Code configuration
└── CLAUDE.md                 # Claude's instructions
```

---

## Philosophy

**Showing up is the win.**

Some days you'll write 500 words and feel like a genius. Some days you'll write 100 words and wonder why you started. Some days you'll show up and not write at all.

All of this is normal. The book gets written by showing up, again and again, over months and years.

Q-Nonfiction-Author is designed to support that journey - not to pressure you, not to judge you, but to be there with you the whole way.

---

## Need More?

Want hands-on help with this template, or curious what else is possible with AI-powered workflows?

[The AI Masters](https://the-ai-masters.com) offers VIP implementation sessions.

---

## Credits

- [Q-Command System](https://github.com/contactTAM/q-command-system) - Session management for Claude Code
- [Claude Code](https://claude.ai/claude-code) - AI-powered development environment
- **Case Study:** Based on a real 2.5-year book writing journey

---

## License

MIT License - see LICENSE file for details.

---

*"A patient friend who believes in your book more than you do on your worst days, but respects you enough to be honest."*
