# Drugs.com extraction pipeline

The scripts in this directory document the iterative Selenium-based extraction process used for Drugs.com Answers. The canonical complete extraction was produced by `step4_multi_page_drugs_selenium.py` and is stored in `../../data/sources/drugs/drugs_answers_all_pages.json`.

The pipeline uses a headless Chrome browser to enumerate answer pages, identify medical-answer URLs, remove page-interface noise, and extract the question, answer text, and source URL. The earlier scripts are retained to document the development stages of the scraper.

## Requirements

- Google Chrome or Chromium;
- a compatible ChromeDriver available to Selenium; and
- the dependencies in the repository root `requirements.txt`.

## Output

The canonical JSON file contains 3,609 records. `training/prepare_sft_dataset.py` converts it to the chat-format JSONL corpus used for SFT.

Use the source responsibly and review Drugs.com terms of use before running a new crawl or redistributing extracted material.
