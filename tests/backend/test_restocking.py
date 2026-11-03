"""
Tests for restocking order API endpoints.
"""
from datetime import date, timedelta

import pytest

import main


@pytest.fixture(autouse=True)
def reset_restocking_orders():
    """Clear the in-memory order store so each test starts empty."""
    main.restocking_orders.clear()
    yield
    main.restocking_orders.clear()


class TestDemandRestockFields:
    """Test suite for restocking fields on demand forecasts."""

    def test_demand_forecast_restock_field_types(self, client):
        """Test that every forecast has a unit cost and lead time."""
        response = client.get("/api/demand")
        assert response.status_code == 200

        data = response.json()
        assert len(data) > 0
        for forecast in data:
            assert isinstance(forecast["unit_cost"], (int, float))
            assert isinstance(forecast["lead_time_days"], int)
            assert forecast["unit_cost"] > 0
            assert forecast["lead_time_days"] > 0


class TestRestockingOrdersEndpoints:
    """Test suite for restocking order endpoints."""

    def _forecasts(self, client):
        return {f["item_sku"]: f for f in client.get("/api/demand").json()}

    def test_get_all_restocking_orders_empty(self, client):
        """Test that no restocking orders exist initially."""
        response = client.get("/api/restocking-orders")
        assert response.status_code == 200
        assert response.json() == []

    def test_create_restocking_order(self, client):
        """Test submitting a restocking order."""
        forecasts = self._forecasts(client)
        skus = list(forecasts)[:2]
        payload = {
            "budget": 1_000_000,
            "items": [{"item_sku": skus[0], "quantity": 10}, {"item_sku": skus[1], "quantity": 5}],
        }

        response = client.post("/api/restocking-orders", json=payload)
        assert response.status_code == 201

        order = response.json()
        assert order["order_number"] == "RST-0001"
        assert order["status"] == "Submitted"
        assert order["budget"] == 1_000_000
        assert len(order["items"]) == 2
        for item in order["items"]:
            assert item["item_name"] == forecasts[item["item_sku"]]["item_name"]

    def test_restocking_order_total_cost_calculation(self, client):
        """Test that the total uses server-side unit costs, not client-sent ones."""
        forecasts = self._forecasts(client)
        sku = next(iter(forecasts))
        payload = {
            "budget": 1_000_000,
            "items": [{"item_sku": sku, "quantity": 7, "unit_cost": 0.01}],
        }

        order = client.post("/api/restocking-orders", json=payload).json()

        expected = 7 * forecasts[sku]["unit_cost"]
        assert abs(order["total_cost"] - expected) < 0.01
        assert order["items"][0]["unit_cost"] == forecasts[sku]["unit_cost"]

    def test_restocking_order_lead_time_calculation(self, client):
        """Test that lead time is the slowest item's and drives expected delivery."""
        forecasts = self._forecasts(client)
        payload = {
            "budget": 10_000_000,
            "items": [{"item_sku": sku, "quantity": 1} for sku in forecasts],
        }

        order = client.post("/api/restocking-orders", json=payload).json()

        max_lead = max(f["lead_time_days"] for f in forecasts.values())
        assert order["lead_time_days"] == max_lead
        assert order["submitted_date"] == date.today().isoformat()
        assert order["expected_delivery"] == (date.today() + timedelta(days=max_lead)).isoformat()

    def test_create_restocking_order_over_budget(self, client):
        """Test that an order costing more than the budget is rejected."""
        sku = next(iter(self._forecasts(client)))
        payload = {"budget": 1, "items": [{"item_sku": sku, "quantity": 1000}]}

        response = client.post("/api/restocking-orders", json=payload)
        assert response.status_code == 400
        assert "budget" in response.json()["detail"].lower()
        assert client.get("/api/restocking-orders").json() == []

    def test_create_restocking_order_unknown_sku(self, client):
        """Test that an unknown SKU is rejected."""
        payload = {"budget": 1000, "items": [{"item_sku": "NOPE-999", "quantity": 1}]}

        response = client.post("/api/restocking-orders", json=payload)
        assert response.status_code == 400
        assert "NOPE-999" in response.json()["detail"]

    def test_create_restocking_order_empty_items(self, client):
        """Test that an order without items is rejected."""
        response = client.post("/api/restocking-orders", json={"budget": 1000, "items": []})
        assert response.status_code == 400

    def test_create_restocking_order_duplicate_sku(self, client):
        """Test that the same SKU twice in one order is rejected."""
        sku = next(iter(self._forecasts(client)))
        payload = {
            "budget": 1_000_000,
            "items": [{"item_sku": sku, "quantity": 1}, {"item_sku": sku, "quantity": 2}],
        }

        response = client.post("/api/restocking-orders", json=payload)
        assert response.status_code == 400

    def test_create_restocking_order_exact_budget(self, client):
        """Test that an order costing exactly the budget is accepted."""
        forecasts = self._forecasts(client)
        sku = next(iter(forecasts))
        budget = round(3 * forecasts[sku]["unit_cost"], 2)
        payload = {"budget": budget, "items": [{"item_sku": sku, "quantity": 3}]}

        response = client.post("/api/restocking-orders", json=payload)
        assert response.status_code == 201

    def test_create_restocking_order_negative_budget(self, client):
        """Test that a negative budget fails validation."""
        sku = next(iter(self._forecasts(client)))
        payload = {"budget": -1, "items": [{"item_sku": sku, "quantity": 1}]}

        response = client.post("/api/restocking-orders", json=payload)
        assert response.status_code == 422

    def test_create_restocking_order_invalid_quantity(self, client):
        """Test that zero quantities fail validation."""
        sku = next(iter(self._forecasts(client)))
        payload = {"budget": 1000, "items": [{"item_sku": sku, "quantity": 0}]}

        response = client.post("/api/restocking-orders", json=payload)
        assert response.status_code == 422

    def test_get_restocking_orders_newest_first(self, client):
        """Test that submitted orders are listed newest first."""
        sku = next(iter(self._forecasts(client)))
        payload = {"budget": 1_000_000, "items": [{"item_sku": sku, "quantity": 1}]}
        client.post("/api/restocking-orders", json=payload)
        client.post("/api/restocking-orders", json=payload)

        response = client.get("/api/restocking-orders")
        assert response.status_code == 200

        data = response.json()
        assert [o["order_number"] for o in data] == ["RST-0002", "RST-0001"]
