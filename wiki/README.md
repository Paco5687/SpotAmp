# Wiki source

These Markdown files are the **source for the GitHub Wiki**. GitHub stores a
wiki in a separate git repo (`SpotAmp.wiki.git`), so to publish:

1. Create the wiki by adding one page in the repo's **Wiki** tab (this
   initializes `…​.wiki.git`).
2. `git clone git@github.com:Paco5687/SpotAmp.wiki.git`
3. Copy these files in, `git add -A && git commit && git push`.

Page names map to titles (`Bill-of-Materials.md` → "Bill of Materials").
`Home.md` is the landing page; `_Sidebar.md` is the nav. **Placeholders for now** —
most pages link to the authoritative docs under [`/docs`](../docs) and
[`/hardware`](../hardware) so there's a single source of truth.
