"""Validate JSON strings returned by a language model.

Each valid string must decode to a JSON object with exactly three keys:
  title        - string
  probability  - number from 0 to 1 inclusive (booleans are not numbers here)
  reason       - string of at most 200 characters

Each invalid input is counted once, under the FIRST check it fails.
"""

import json

EXPECTED_KEYS = {"title", "probability", "reason"}
MAX_REASON_LENGTH = 200

FAILURE_CATEGORIES = (
    "not_a_string",
    "invalid_json",
    "not_an_object",
    "wrong_keys",
    "wrong_type",
    "probability_out_of_range",
    "reason_too_long",
)


def _reject_constant(name):
    """Called by json.loads for NaN, Infinity and -Infinity. Always refuse."""
    raise ValueError(f"non-standard JSON constant: {name}")


def _check_one(item):
    """Check a single input.

    Returns (parsed_object, None) if valid, or (None, category) on the
    first failed check. Each early return is what enforces "first failure".
    """
    # 1. Must be a string, otherwise json.loads raises TypeError.
    if not isinstance(item, str):
        return None, "not_a_string"

    # 2. Must parse as JSON (NaN/Infinity rejected via parse_constant).
    try:
        data = json.loads(item, parse_constant=_reject_constant)
    except ValueError:  # JSONDecodeError is a subclass of ValueError
        return None, "invalid_json"

    # 3. Must be a JSON object (a dict), or key checks would crash.
    if not isinstance(data, dict):
        return None, "not_an_object"

    # 4. Keys must be exactly the expected three: none missing, none extra.
    if set(data) != EXPECTED_KEYS:
        return None, "wrong_keys"

    title = data["title"]
    probability = data["probability"]
    reason = data["reason"]

    # 5. Types. bool is a subclass of int, so it must be excluded explicitly.
    if not isinstance(title, str) or not isinstance(reason, str):
        return None, "wrong_type"
    if isinstance(probability, bool) or not isinstance(probability, (int, float)):
        return None, "wrong_type"

    # 6. Range check.
    if not (0 <= probability <= 1):
        return None, "probability_out_of_range"

    # 7. Length check.
    if len(reason) > MAX_REASON_LENGTH:
        return None, "reason_too_long"

    return data, None


def validate_outputs(outputs):
    """Validate a list of model output strings.

    Returns {"valid": [parsed dicts], "failures": {category: count}}.
    Invariant: len(valid) + sum(failures.values()) == len(outputs).
    """
    valid = []
    failures = dict.fromkeys(FAILURE_CATEGORIES, 0)

    for item in outputs:
        parsed, failure = _check_one(item)
        if failure is None:
            valid.append(parsed)
        else:
            failures[failure] += 1

    return {"valid": valid, "failures": failures}


if __name__ == "__main__":
    sample = [
        '{"title": "A", "probability": 0.9, "reason": "ok"}',
        '{"title": "B", "probability": true, "reason": "ok"}',
        "not json",
    ]
    print(json.dumps(validate_outputs(sample), indent=2))
