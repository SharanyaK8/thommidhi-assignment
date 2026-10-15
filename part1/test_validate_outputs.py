import json
import unittest

from validate_outputs import FAILURE_CATEGORIES, validate_outputs


def make(title="T", probability=0.5, reason="because"):
    """Build a JSON string for a well-formed entry, overriding any field."""
    return json.dumps(
        {"title": title, "probability": probability, "reason": reason}
    )


def only_failure(result):
    """Return the single non-zero failure category, asserting there is one."""
    nonzero = {k: v for k, v in result["failures"].items() if v}
    assert len(nonzero) == 1, nonzero
    return nonzero


class ValidateOutputsTests(unittest.TestCase):
    def test_valid_entry_is_returned_parsed(self):
        result = validate_outputs([make()])
        self.assertEqual(
            result["valid"],
            [{"title": "T", "probability": 0.5, "reason": "because"}],
        )
        self.assertEqual(sum(result["failures"].values()), 0)

    def test_boolean_probability_is_wrong_type(self):
        # Naive trap: isinstance(True, (int, float)) is True.
        raw = '{"title": "T", "probability": true, "reason": "r"}'
        result = validate_outputs([raw])
        self.assertEqual(result["valid"], [])
        self.assertEqual(only_failure(result), {"wrong_type": 1})

    def test_extra_key_is_wrong_keys(self):
        # Naive trap: checking only that the three keys are present.
        raw = '{"title": "T", "probability": 0.5, "reason": "r", "extra": 1}'
        result = validate_outputs([raw])
        self.assertEqual(result["valid"], [])
        self.assertEqual(only_failure(result), {"wrong_keys": 1})

    def test_invalid_json(self):
        result = validate_outputs(["not json at all"])
        self.assertEqual(only_failure(result), {"invalid_json": 1})

    def test_nan_and_infinity_are_invalid_json(self):
        raws = [
            '{"title": "T", "probability": NaN, "reason": "r"}',
            '{"title": "T", "probability": Infinity, "reason": "r"}',
        ]
        result = validate_outputs(raws)
        self.assertEqual(only_failure(result), {"invalid_json": 2})

    def test_json_but_not_an_object(self):
        result = validate_outputs(["[]", "null", "42", '"hi"'])
        self.assertEqual(only_failure(result), {"not_an_object": 4})

    def test_non_string_item(self):
        result = validate_outputs([None, 42])
        self.assertEqual(only_failure(result), {"not_a_string": 2})

    def test_probability_boundaries(self):
        ok = [make(probability=0), make(probability=1), make(probability=0.0)]
        self.assertEqual(len(validate_outputs(ok)["valid"]), 3)
        for bad in (-0.01, 1.01):
            result = validate_outputs([make(probability=bad)])
            self.assertEqual(only_failure(result), {"probability_out_of_range": 1})

    def test_reason_length_boundary(self):
        self.assertEqual(len(validate_outputs([make(reason="x" * 200)])["valid"]), 1)
        result = validate_outputs([make(reason="x" * 201)])
        self.assertEqual(only_failure(result), {"reason_too_long": 1})

    def test_missing_key_and_numeric_string(self):
        missing = '{"title": "T", "probability": 0.5}'
        as_string = make(probability="0.5")
        self.assertEqual(only_failure(validate_outputs([missing])), {"wrong_keys": 1})
        self.assertEqual(only_failure(validate_outputs([as_string])), {"wrong_type": 1})

    def test_multiple_problems_counted_once_in_fixed_order(self):
        # Extra key AND bad probability: wrong_keys is checked first.
        raw = '{"title": "T", "probability": 5, "reason": "r", "x": 1}'
        result = validate_outputs([raw])
        self.assertEqual(only_failure(result), {"wrong_keys": 1})

    def test_mixed_batch_invariant(self):
        batch = [
            make(),
            "garbage",
            "[]",
            None,
            make(probability=True),
            make(probability=2),
            make(reason="x" * 201),
            '{"title": "T", "probability": 0.5, "reason": "r", "z": 0}',
        ]
        result = validate_outputs(batch)
        self.assertEqual(
            len(result["valid"]) + sum(result["failures"].values()), len(batch)
        )
        self.assertEqual(set(result["failures"]), set(FAILURE_CATEGORIES))


if __name__ == "__main__":
    unittest.main()
