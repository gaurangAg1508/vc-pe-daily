# VC & PE Daily

A free, mobile-first daily learning hub for venture capital, private equity and startup investing, focused on global markets and India.

## Daily format: one deal, 15 minutes
The site intentionally selects **one** important startup / VC / PE story per day, rather than showing a long news list. It alternates India and global focus to keep both markets in your reading routine.

Each case study is organised as:
1. What happened? — company and transaction facts; undisclosed information is labelled.
2. How does the business make money? — customer, revenue engine and unit economics.
3. Would I invest? — a provisional investor view, thesis and conditions that must be true.
4. Biggest risks — why they matter and how to test them.
5. What would I ask before investing? — concrete diligence requests and why each matters.
6. One VC/PE concept — a concept explained through the deal, with a clearly labelled hypothetical example if the transaction does not disclose enough information.
7. How to present it in VCIC — a sample recommendation and questions to take into the room.

## Better case analysis (optional, no paid subscription required)
The project can use Google's Gemini API free tier for a more detailed, company-specific teaching analysis. To enable it:
1. Create an API key in Google AI Studio: https://aistudio.google.com/app/apikey
2. In this repository, open Settings → Secrets and variables → Actions → New repository secret.
3. Set the secret name to `GEMINI_API_KEY` and paste your key as its value.
4. Run the workflow manually once to test it.

The workflow uses `gemini-3.1-flash-lite` by default. Do not enable paid billing or upgrade the API project if you want to keep this zero-cost. Google says the Gemini API free tier has limited model access/rate limits and that free-tier content may be used to improve its products. This project sends only public article headlines and RSS excerpts, not private personal data. Review Google's current terms before enabling it.

Without the secret, the site still publishes a basic rule-based teaching template. It is less company-specific and will say when the available information is insufficient.

## Accuracy rules
- The model receives only the public headline and RSS excerpt collected from the feed; it does not read paywalled articles or access private investor information.
- Reported facts and investment hypotheses are shown separately.
- The system must not invent transaction values, valuations, revenue, margins, customer numbers or investor intent.
- When the excerpt does not include a fact, the edition should say it is not disclosed and explain what to request during diligence.
- The sample investment view is an educational starting point, not investment advice.

## Daily schedule
The workflow is scheduled for 7:15 AM Asia/Singapore. Run it manually from Actions → VC & PE Daily → Run workflow.

## Setup and reading site
1. Open Settings → Pages and set Build and deployment → Source to GitHub Actions.
2. Run the workflow once from the Actions tab.
3. Read on phone at https://gaurangAg1508.github.io/vc-pe-daily/
4. Bookmark the site or add it to your phone's home screen.

## Customise
- Add/remove RSS feeds in `config/feeds.json`.
- Adjust freshness and archive settings in `config/settings.json`.
- Change the case analysis and concept rotation in `scripts/build_digest.py`.
- Change the mobile reading design in `site/index.html`.
- Change the daily publication time in `.github/workflows/daily.yml`.

## Repository layout
- `config/`: sources and settings
- `scripts/build_digest.py`: collector, selection, concept teaching and analysis
- `site/index.html`: mobile reading interface
- `site/data/latest.json`: current case study
- `site/data/archive/`: dated editions
- `.github/workflows/`: daily automation and publishing

## Content and copyright
The site stores headlines, source names, publication dates and short RSS excerpts as discovery aids. Read full articles on publisher sites and respect their terms and paywalls. Original reporting remains the property of each publisher.

## Reliability
GitHub Free public repositories may have scheduled workflows disabled after 60 days without repository activity. Visit the repository occasionally and check the Actions tab if an edition is missing.
