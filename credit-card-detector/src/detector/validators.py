"""
Credit Card Validation Utilities

Luhn algorithm and card validation functions.
"""

from typing import Optional


class CardValidators:
    """Credit card validation utilities."""

    @staticmethod
    def luhn_check(card_number: str) -> bool:
        """
        Validate card number using Luhn algorithm.

        Args:
            card_number: Card number to validate

        Returns:
            True if valid, False otherwise
        """
        # Remove non-digits
        digits = [int(d) for d in card_number if d.isdigit()]

        if len(digits) < 13 or len(digits) > 19:
            return False

        total = 0
        reverse = digits[::-1]

        for i, d in enumerate(reverse):
            if i % 2 == 1:
                doubled = d * 2
                if doubled > 9:
                    doubled -= 9
                total += doubled
            else:
                total += d

        return total % 10 == 0

    @staticmethod
    def is_valid_card(card_number: str, check_luhn: bool = True) -> bool:
        """
        Validate card number.

        Args:
            card_number: Card number to validate
            check_luhn: Whether to perform Luhn check

        Returns:
            True if valid, False otherwise
        """
        # Remove separators
        normalized = ''.join(d for d in card_number if d.isdigit())

        # Check length
        if len(normalized) < 13 or len(normalized) > 19:
            return False

        # Check if all digits
        if not normalized.isdigit():
            return False

        # Luhn check if requested
        if check_luhn:
            return CardValidators.luhn_check(normalized)

        return True

    @staticmethod
    def get_validation_errors(card_number: str) -> Optional[str]:
        """
        Get validation error for card number.

        Args:
            card_number: Card number to validate

        Returns:
            Error message or None if valid
        """
        # Remove separators
        normalized = ''.join(d for d in card_number if d.isdigit())

        # Check length
        if len(normalized) < 13:
            return "Card number too short (minimum 13 digits)"
        if len(normalized) > 19:
            return "Card number too long (maximum 19 digits)"

        # Check if all digits
        if not normalized.isdigit():
            return "Card number must contain only digits"

        # Luhn check
        if not CardValidators.luhn_check(normalized):
            return "Invalid card number (failed Luhn check)"

        return None

    @staticmethod
    def validate_batch(card_numbers: list, check_luhn: bool = True) -> dict:
        """
        Validate multiple card numbers.

        Args:
            card_numbers: List of card numbers to validate
            check_luhn: Whether to perform Luhn check

        Returns:
            Dictionary with validation results
        """
        results = {
            'valid': [],
            'invalid': [],
            'total': len(card_numbers)
        }

        for card_number in card_numbers:
            error = CardValidators.get_validation_errors(card_number)
            if error is None:
                results['valid'].append(card_number)
            else:
                results['invalid'].append({
                    'number': card_number,
                    'error': error
                })

        return results