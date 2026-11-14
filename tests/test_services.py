"""Backend tests use an isolated in-memory SQLite connection."""
import unittest
from datetime import date
from backend.database import connect, initialize
from backend.expense_service import ExpenseService
from backend.category_service import CategoryService
from backend.settings_service import SettingsService


class ServiceTests(unittest.TestCase):
    def setUp(self):
        self.conn = connect(":memory:")
        initialize(self.conn)
        self.expenses = ExpenseService(self.conn)
        self.categories = CategoryService(self.conn)
        self.settings = SettingsService(self.conn)
        self.today = date.today().isoformat()

    def tearDown(self):
        self.conn.close()

    def test_initial_categories(self):
        self.assertEqual(len(self.categories.list_all()), 8)

    def test_seeded_expenses(self):
        self.assertEqual(len(self.expenses.list_all()), 40)

    def test_default_budget(self):
        self.assertEqual(self.settings.get_budget(), 30000)

    def test_update_budget(self):
        self.settings.set_budget("12,500")
        self.assertEqual(self.settings.get_budget(), 12500)

    def test_invalid_budget(self):
        for value in ("abc", "0", "-2", "nan", "inf"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.settings.set_budget(value)

    def test_add_expense(self):
        key = self.expenses.save("250", 1, self.today, "Special lunch")
        self.assertEqual(self.expenses.get(key)["note"], "Special lunch")

    def test_edit_expense(self):
        key = self.expenses.save("100", 1, self.today)
        self.expenses.save("200", 2, self.today, "Changed", key)
        self.assertEqual(self.expenses.get(key)["amount"], 200)

    def test_delete_expense(self):
        key = self.expenses.save("100", 1, self.today)
        self.expenses.delete(key)
        self.assertIsNone(self.expenses.get(key))

    def test_validate_amount(self):
        self.assertIn("amount", self.expenses.validate("-1", 1, self.today))
        self.assertIn("amount", self.expenses.validate("nan", 1, self.today))

    def test_validate_date(self):
        self.assertIn("date", self.expenses.validate("10", 1, "2026-02-31"))

    def test_validate_category(self):
        self.assertIn("category", self.expenses.validate("10", 999, self.today))

    def test_search_note(self):
        self.expenses.save("20", 1, self.today, "Uniquely Zebra")
        self.assertEqual(len(self.expenses.list_all(search="uniquely zebra")), 1)

    def test_filter_category_and_month(self):
        rows = self.expenses.list_all(category_id=1, month=self.today[:7])
        self.assertTrue(all(x["category_id"] == 1 and x["date"].startswith(self.today[:7]) for x in rows))

    def test_category_add(self):
        self.categories.add("Education")
        self.assertTrue(any(x["name"] == "Education" for x in self.categories.list_all()))

    def test_category_duplicate(self):
        with self.assertRaises(ValueError):
            self.categories.add("Food")

    def test_category_delete_empty(self):
        self.categories.add("Empty")
        key = next(x["id"] for x in self.categories.list_all() if x["name"] == "Empty")
        self.categories.delete(key)
        self.assertFalse(any(x["id"] == key for x in self.categories.list_all()))

    def test_category_delete_used(self):
        with self.assertRaises(ValueError):
            self.categories.delete(1)

    def test_summary(self):
        result = self.expenses.summary()
        self.assertGreater(result["total"], 0)
        self.assertGreater(result["month"], 0)
        self.assertTrue(result["top_category"])

    def test_foreign_keys(self):
        self.assertEqual(self.conn.execute("PRAGMA foreign_keys").fetchone()[0], 1)

    def test_sql_injection_remains_data(self):
        self.expenses.list_all(search="' OR 1=1 --")
        self.assertEqual(self.conn.execute("SELECT COUNT(*) FROM categories").fetchone()[0], 8)


if __name__ == "__main__":
    unittest.main()
