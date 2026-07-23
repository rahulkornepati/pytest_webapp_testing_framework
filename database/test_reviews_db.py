from __future__ import annotations

"""Database validation tests for the **Reviews / Ratings** module.

Verifies product reviews, ratings, moderation status, and
review-related business rules at the database level.
"""

import pytest

from database.db_helpers import DBHelpers
from database.db_queries import count, fetch_all, fetch_one, fetch_scalar
from database.sql_constants import SQLQueries

pytestmark = [
    pytest.mark.database,
    pytest.mark.regression,
    pytest.mark.products,
]


class TestReviewsDB:
    """Database-level validation of product review data."""

    # ── Review existence ──────────────────────────────────────────────────────

    def test_verify_review_exists(self) -> None:
        """Verify that a review exists by its ID."""
        review = fetch_one(SQLQueries.REVIEW_BY_ID, (1,))
        assert review is not None, "Expected review with ID 1 to exist"

    def test_verify_review_for_product(self) -> None:
        """Verify that reviews exist for a specific product."""
        reviews = fetch_all(SQLQueries.REVIEWS_BY_PRODUCT_ID, (1,))  # Sauce Labs Backpack
        assert len(reviews) >= 2, (
            f"Expected at least 2 reviews for product 1, found {len(reviews)}"
        )

    def test_verify_review_from_user(self, known_users: dict) -> None:
        """Verify that a specific user has written reviews."""
        user_id = known_users["standard_user"]["user_id"]
        reviews = fetch_all(SQLQueries.REVIEWS_BY_USER_ID, (user_id,))
        assert len(reviews) >= 1, (
            f"Expected at least 1 review from standard_user, found {len(reviews)}"
        )

    # ── Rating validation ─────────────────────────────────────────────────────

    def test_verify_review_rating(self) -> None:
        """Verify that a review has the correct rating."""
        rating = fetch_scalar(SQLQueries.REVIEW_RATING, (1,))
        assert rating == 5, (
            f"Expected review 1 rating to be 5, got {rating}"
        )

    def test_verify_rating_within_range(self) -> None:
        """Verify that all ratings are between 1 and 5."""
        invalid = fetch_scalar(
            "SELECT COUNT(*) FROM reviews WHERE rating < 1 OR rating > 5"
        )
        assert invalid == 0, (
            f"Expected 0 reviews with out-of-range ratings, found {invalid}"
        )

    def test_verify_average_rating(self, db_helpers: DBHelpers) -> None:
        """Verify that the average rating for a product is calculated correctly."""
        avg = db_helpers.average_rating(1)  # Sauce Labs Backpack
        # reviews: ID1 (std_user, 5★), ID3 (problem_user, 2★)
        expected_avg = (5 + 2) / 2
        assert abs(avg - expected_avg) < 0.01, (
            f"Expected average rating {expected_avg} for product 1, got {avg}"
        )

    # ── Review count ──────────────────────────────────────────────────────────

    def test_verify_review_count_by_product(self, db_helpers: DBHelpers) -> None:
        """Verify that the review count for a product is correct."""
        count_for_product = db_helpers.review_count_by_product(1)
        assert count_for_product >= 2, (
            f"Expected at least 2 reviews for product 1, found {count_for_product}"
        )

    def test_verify_multiple_products_have_reviews(self) -> None:
        """Verify that multiple products have at least one review."""
        products_with_reviews = fetch_scalar(
            "SELECT COUNT(DISTINCT product_id) FROM reviews"
        )
        assert products_with_reviews >= 5, (
            f"Expected at least 5 products with reviews, found {products_with_reviews}"
        )

    # ── Moderation / approval ─────────────────────────────────────────────────

    def test_verify_review_approval_status(self, db_helpers: DBHelpers) -> None:
        """Verify that approved reviews have is_approved = 1."""
        assert db_helpers.review_is_approved(1), (
            "Expected review 1 to be approved"
        )

    def test_verify_unapproved_reviews_exist(self, db_helpers: DBHelpers) -> None:
        """Verify that some reviews are not yet approved."""
        assert not db_helpers.review_is_approved(3), (
            "Expected review 3 to be unapproved"
        )

    def test_verify_moderation_status_counts(self) -> None:
        """Verify the distribution of approved vs unapproved reviews."""
        approved = fetch_scalar("SELECT COUNT(*) FROM reviews WHERE is_approved = 1")
        unapproved = fetch_scalar("SELECT COUNT(*) FROM reviews WHERE is_approved = 0")
        assert approved >= 7, (
            f"Expected at least 7 approved reviews, found {approved}"
        )
        assert unapproved >= 2, (
            f"Expected at least 2 unapproved reviews, found {unapproved}"
        )

    # ── Duplicate prevention ─────────────────────────────────────────────────

    def test_verify_no_duplicate_reviews(self, known_users: dict) -> None:
        """Verify that a user can only review a product once (UNIQUE constraint)."""
        duplicates = fetch_scalar(
            """SELECT COUNT(*) FROM (SELECT user_id, product_id, COUNT(*)
               FROM reviews GROUP BY user_id, product_id HAVING COUNT(*) > 1)"""
        )
        assert duplicates == 0, (
            f"Expected 0 duplicate user/product review pairs, found {duplicates}"
        )

    def test_verify_duplicate_check_helper(self, known_users: dict, known_products: dict) -> None:
        """Verify that the duplicate review check works correctly."""
        user_id = known_users["standard_user"]["user_id"]
        product_id = known_products["Sauce Labs Backpack"]
        duplicate = fetch_scalar(
            SQLQueries.REVIEW_DUPLICATE_CHECK,
            (user_id, product_id),
        )
        assert duplicate > 0, (
            "Expected duplicate check to find existing review"
        )

    # ── Review content ────────────────────────────────────────────────────────

    def test_verify_review_has_title(self) -> None:
        """Verify that reviews have non-empty titles."""
        no_title = fetch_scalar(
            "SELECT COUNT(*) FROM reviews WHERE title IS NULL OR title = ''"
        )
        assert no_title == 0, (
            f"Expected 0 reviews without titles, found {no_title}"
        )

    def test_verify_review_has_text(self) -> None:
        """Verify that reviews have non-empty review text."""
        no_text = fetch_scalar(
            "SELECT COUNT(*) FROM reviews WHERE review_text IS NULL OR review_text = ''"
        )
        assert no_text == 0, (
            f"Expected 0 reviews without text, found {no_text}"
        )

    # ── Timestamps ────────────────────────────────────────────────────────────

    def test_verify_review_created_at(self) -> None:
        """Verify that all reviews have a created_at timestamp."""
        null_dates = fetch_scalar(
            "SELECT COUNT(*) FROM reviews WHERE created_at IS NULL"
        )
        assert null_dates == 0, (
            f"Expected 0 reviews with NULL created_at, found {null_dates}"
        )

    # ── Foreign key integrity ─────────────────────────────────────────────────

    def test_verify_review_product_exists(self) -> None:
        """Verify that all reviews reference existing products."""
        orphaned = fetch_scalar(
            "SELECT COUNT(*) FROM reviews WHERE product_id NOT IN (SELECT product_id FROM products)"
        )
        assert orphaned == 0, (
            f"Expected 0 reviews with invalid product references, found {orphaned}"
        )

    def test_verify_review_user_exists(self) -> None:
        """Verify that all reviews reference existing users."""
        orphaned = fetch_scalar(
            "SELECT COUNT(*) FROM reviews WHERE user_id NOT IN (SELECT user_id FROM users)"
        )
        assert orphaned == 0, (
            f"Expected 0 reviews with invalid user references, found {orphaned}"
        )
