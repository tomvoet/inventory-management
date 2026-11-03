"""
Tests for reports API endpoints.
"""
import pytest


class TestReportsEndpoints:
    """Test suite for quarterly and monthly-trend report endpoints."""

    def test_get_quarterly_reports(self, client):
        """Test getting quarterly reports without filters."""
        response = client.get("/api/reports/quarterly")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

        for q in data:
            for field in ["quarter", "total_orders", "total_revenue", "avg_order_value", "fulfillment_rate"]:
                assert field in q
            assert q["quarter"].startswith("Q")
            assert 0 <= q["fulfillment_rate"] <= 100

    def test_quarterly_reports_sorted(self, client):
        """Test that quarters are returned in order."""
        data = client.get("/api/reports/quarterly").json()
        quarters = [q["quarter"] for q in data]
        assert quarters == sorted(quarters)

    def test_get_monthly_trends(self, client):
        """Test getting monthly trends without filters."""
        response = client.get("/api/reports/monthly-trends")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

        for m in data:
            assert "month" in m
            assert "order_count" in m
            assert "revenue" in m
            assert len(m["month"]) == 7

        months = [m["month"] for m in data]
        assert months == sorted(months)

    @pytest.mark.parametrize("endpoint", ["/api/reports/quarterly", "/api/reports/monthly-trends"])
    @pytest.mark.parametrize("query", [
        "warehouse=Tokyo",
        "category=Sensors",
        "status=Delivered",
        "month=2025-03",
        "month=Q2-2025",
        "warehouse=San Francisco&category=Power Supplies&status=Delivered",
    ])
    def test_reports_match_filtered_orders(self, client, endpoint, query):
        """Test that report totals match the orders endpoint under the same filters."""
        orders = client.get(f"/api/orders?{query}").json()
        report = client.get(f"{endpoint}?{query}")
        assert report.status_code == 200
        data = report.json()

        count_key = "total_orders" if "quarterly" in endpoint else "order_count"
        revenue_key = "total_revenue" if "quarterly" in endpoint else "revenue"

        assert sum(r[count_key] for r in data) == len(orders)
        expected_revenue = sum(o["total_value"] for o in orders)
        assert abs(sum(r[revenue_key] for r in data) - expected_revenue) < 0.01

    def test_quarterly_reports_quarter_filter(self, client):
        """Test that a quarter filter returns only that quarter."""
        data = client.get("/api/reports/quarterly?month=Q2-2025").json()
        assert [q["quarter"] for q in data] == ["Q2-2025"]

    def test_monthly_trends_month_filter(self, client):
        """Test that a month filter returns only that month."""
        data = client.get("/api/reports/monthly-trends?month=2025-03").json()
        assert [m["month"] for m in data] == ["2025-03"]

    def test_reports_filters_with_no_matches(self, client):
        """Test that filters matching nothing return empty lists."""
        for endpoint in ["/api/reports/quarterly", "/api/reports/monthly-trends"]:
            response = client.get(f"{endpoint}?warehouse=Nowhere")
            assert response.status_code == 200
            assert response.json() == []

    def test_reports_all_filter_values_are_ignored(self, client):
        """Test that 'all' filter values return the unfiltered report."""
        for endpoint in ["/api/reports/quarterly", "/api/reports/monthly-trends"]:
            unfiltered = client.get(endpoint).json()
            all_filters = client.get(f"{endpoint}?warehouse=all&category=all&status=all&month=all").json()
            assert all_filters == unfiltered
