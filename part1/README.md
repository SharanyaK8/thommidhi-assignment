# LLM Output Validator

## How to Run

This project validates JSON strings returned by a language model using only Python's standard library.

Run the tests from the project directory:

```bash
python -m unittest -v
```

To run the demonstration:

```bash
python validate_outputs.py
```

The validator returns valid parsed entries and counts invalid entries by failure category. Each invalid entry is counted only once, according to the first validation failure.

## Known Limitation

Duplicate JSON keys are not detected: an entry like `{"title": "a", "title": "b", ...}` is accepted as valid. I left this unhandled because Python's `json.loads` silently keeps the last value and gives no error, so detecting it needs a custom parser hook, and the brief did not say whether duplicates should count as invalid.