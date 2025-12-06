import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from core.detect_credit_cards import detect as find_credit_cards, is_valid_luhn


def test_luhn_valid_and_invalid():
    # Known valid Visa test number
    assert is_valid_luhn("4111111111111111")
    # Change last digit to make it invalid
    assert not is_valid_luhn("4111111111111112")


def test_find_unformatted_and_formatted():
    text = "Here is a card: 4111111111111111 and another: 4012-8888-8888-1881 and some nonsense 1234-5678-9012-3456"
    res = find_credit_cards(text)
    digits = [r['number'] for r in res]
    assert "4111111111111111" in digits
    assert "4012888888881881" in digits
    # The third one should be detected but should fail Luhn
    assert any(r['number'] == "1234567890123456" and not r['valid'] for r in res)


def test_formatted_with_spaces():
    text = "My card: 4111 1111 1111 1111"
    res = find_credit_cards(text)
    assert res and res[0]['number'] == "4111111111111111"
    assert res[0]['valid']
