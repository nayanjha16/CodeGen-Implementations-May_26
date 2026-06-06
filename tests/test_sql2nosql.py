"""Tests for SQL to NoSQL translation."""

import pytest

from src.sql2nosql.evaluator import NoSQLEvaluator
from src.sql2nosql.translator import SQLToNoSQLTranslator


class TestSQLToNoSQLTranslator:
    def setup_method(self):
        self.translator = SQLToNoSQLTranslator()

    def test_simple_select_where(self):
        sql = "SELECT name FROM users WHERE age > 20"
        result = self.translator.translate(sql)
        assert result["success"] is True
        assert "db.users.find" in result["mongodb_query"]
        assert "$gt" in result["mongodb_query"] or "20" in result["mongodb_query"]

    def test_select_star(self):
        sql = "SELECT * FROM products"
        result = self.translator.translate(sql)
        assert "db.products.find" in result["mongodb_query"]

    def test_order_by_limit(self):
        sql = "SELECT name FROM users ORDER BY name DESC LIMIT 10"
        result = self.translator.translate(sql)
        assert ".sort" in result["mongodb_query"]
        assert ".limit(10)" in result["mongodb_query"]

    def test_group_by(self):
        sql = "SELECT department, COUNT(*) FROM employees GROUP BY department"
        result = self.translator.translate(sql)
        assert "aggregate" in result["mongodb_query"]

    def test_unsupported_join_warning(self):
        sql = "SELECT a.name FROM a JOIN b ON a.id = b.id"
        result = self.translator.translate(sql)
        assert any("JOIN" in w for w in result["warnings"])

    def test_filter_extraction(self):
        sql = "SELECT name FROM users WHERE age > 20 AND name = 'Alice'"
        result = self.translator.translate(sql)
        assert "age" in result.get("filter", {}) or "20" in result["mongodb_query"]


class TestNoSQLEvaluator:
    def test_exact_match(self):
        evaluator = NoSQLEvaluator()
        query = "db.users.find({ age: { $gt: 20 } })"
        result = evaluator.translation_accuracy(query, query)
        assert result["exact_match"] is True

    def test_token_f1(self):
        evaluator = NoSQLEvaluator()
        pred = "db.users.find({ age: { $gt: 20 } })"
        ref = "db.users.find({ age: { $gt: 20 } }, { name: 1 })"
        result = evaluator.translation_accuracy(pred, ref)
        assert result["token_f1"] > 0

    def test_evaluate_batch(self):
        evaluator = NoSQLEvaluator()
        preds = [{"mongodb_query": "db.t.find({})"}]
        refs = [{"mongodb_query": "db.t.find({})"}]
        result = evaluator.evaluate_batch(preds, refs)
        assert result["exact_match_rate"] == 1.0

    def test_query_equivalence(self):
        evaluator = NoSQLEvaluator()
        pred = {"collection": "users", "filter": {"age": {"$gt": 20}}, "projection": {"name": 1}}
        ref = {"collection": "users", "filter": {"age": {"$gt": 20}}, "projection": {"name": 1}}
        result = evaluator.query_equivalence(pred, ref)
        assert result["equivalent"] is True

    def test_empty_batch(self):
        evaluator = NoSQLEvaluator()
        result = evaluator.evaluate_batch([], [])
        assert result["translation_accuracy"] == 0.0
