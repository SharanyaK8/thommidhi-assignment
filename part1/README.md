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

Duplicate JSON keys are not explicitly detected. Python's default JSON parser keeps the last value when a key appears more than once. Detecting duplicate keys could be added in a future version.