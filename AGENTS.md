# Instructions for AI coding assistants

Everything is in [CLAUDE.md](CLAUDE.md). Read it first; it applies to every AI assistant,
whichever company made it.

Then follow the guide for your lane:

- Builder: [BUILD_GUIDE_BUILDER.md](BUILD_GUIDE_BUILDER.md)
- Team leader: [BUILD_GUIDE_LEADER.md](BUILD_GUIDE_LEADER.md)
- Writer (write-up and video): start from [docs/WRITER_BRIEF.md](docs/WRITER_BRIEF.md), then [STATUS.md](STATUS.md) and
  [docs/COMPETITION_RULES.md](docs/COMPETITION_RULES.md); the write-up template is there.

## Interface components (ui-sdk)

The pages in `web/` use ui-sdk web components with no build step. The library is copied into
`web/vendor/ui-sdk/` so the demo works offline; never edit that folder. Before using ui-sdk,
follow the ui-sdk skill (`.agents/skills/ui-sdk/`).
