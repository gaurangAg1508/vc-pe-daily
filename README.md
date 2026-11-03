# VC & PE Daily

A free, mobile-first daily reading hub for venture capital, private equity and startup investing, focused on global markets and India.

## What it does
- Collects recent stories from configurable RSS feeds and Google News RSS searches.
- Curates a balanced India + global news list.
- Selects one deeper article to read each day.
- Creates a first-pass deal lens: reported context, plausible hypotheses, diligence questions and VCIC practice prompts.
- Saves dated editions and publishes a mobile-friendly site with GitHub Pages.

## Important limitation
The initial version uses deterministic, rule-based analysis of headlines and RSS excerpts. It does not call a paid AI API, and it does not claim to know an investor's private reasoning. Treat the deal rationale as hypotheses to test against the linked article and further diligence.

## Daily schedule
The workflow is scheduled for 7:15 AM Asia/Singapore. You can also run it manually from Actions → VC & PE Daily → Run workflow.

## One-time setup
1. Open Settings → Pages in this repository.
2. Under Build and deployment → Source, select GitHub Actions.
3. Open Actions and enable workflows if GitHub prompts you.
4. Run Actions → VC & PE Daily → Run workflow to publish the first live edition.
5. The expected site URL is https://gaurangAg1508.github.io/vc-pe-daily/

## Customise it
- Add or remove publishers and RSS feeds in config/feeds.json.
- Change daily story volume and freshness window in config/settings.json.
- Change the deal-analysis logic in scripts/build_digest.py.
- Change the reading experience in site/index.html.
- Change the scheduled time in .github/workflows/daily.yml.

## Repository layout
- config/: news sources and digest settings
- scripts/build_digest.py: RSS collection, ranking and edition generation
- site/index.html: mobile reading interface
- site/data/latest.json: latest edition
- site/data/archive/: historical daily editions
- .github/workflows/: daily automation and Pages deployment

## Content and copyright
The site links to original publishers and stores only headlines, source names, publication dates and short RSS excerpts for discovery. Read full articles on publisher sites and respect their terms and paywalls.
