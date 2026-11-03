import math
from fastapi import FastAPI, HTTPException, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from datetime import date, timedelta
from threading import Lock
from typing import Annotated, List, Literal, Optional
from pydantic import BaseModel, Field, StringConstraints
from mock_data import inventory_items, orders, demand_forecasts, backlog_items, spending_summary, monthly_spending, category_spending, recent_transactions, purchase_orders

app = FastAPI(title="Factory Inventory Management System")

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # Python's json parser accepts Infinity/NaN, and echoing them back in the 422 body would crash serialization
    finite_floats = {float: lambda f: f if math.isfinite(f) else str(f)}
    return JSONResponse(status_code=422, content={"detail": jsonable_encoder(exc.errors(), custom_encoder=finite_floats)})

# Quarter mapping for date filtering
QUARTER_MAP = {
    'Q1-2025': ['2025-01', '2025-02', '2025-03'],
    'Q2-2025': ['2025-04', '2025-05', '2025-06'],
    'Q3-2025': ['2025-07', '2025-08', '2025-09'],
    'Q4-2025': ['2025-10', '2025-11', '2025-12']
}

def filter_by_month(items: list, month: Optional[str]) -> list:
    """Filter items by month/quarter based on order_date field"""
    if not month or month == 'all':
        return items

    if month.startswith('Q'):
        # Handle quarters
        if month in QUARTER_MAP:
            months = QUARTER_MAP[month]
            return [item for item in items if any(m in item.get('order_date', '') for m in months)]
    else:
        # Direct month match
        return [item for item in items if month in item.get('order_date', '')]

    return items

def apply_filters(items: list, warehouse: Optional[str] = None, category: Optional[str] = None,
                 status: Optional[str] = None) -> list:
    """Apply common filters to a list of items"""
    filtered = items

    if warehouse and warehouse != 'all':
        filtered = [item for item in filtered if item.get('warehouse') == warehouse]

    if category and category != 'all':
        filtered = [item for item in filtered if item.get('category', '').lower() == category.lower()]

    if status and status != 'all':
        filtered = [item for item in filtered if item.get('status', '').lower() == status.lower()]

    return filtered

# CORS middleware
# The API has no auth, so only the local Vite dev server may call it from a browser
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["Content-Type"],
)

# Data models
class InventoryItem(BaseModel):
    id: str
    sku: str
    name: str
    category: str
    warehouse: str
    quantity_on_hand: int
    reorder_point: int
    unit_cost: float
    location: str
    last_updated: str

class Order(BaseModel):
    id: str
    order_number: str
    customer: str
    items: List[dict]
    status: str
    order_date: str
    expected_delivery: str
    total_value: float
    actual_delivery: Optional[str] = None
    warehouse: Optional[str] = None
    category: Optional[str] = None

class DemandForecast(BaseModel):
    id: str
    item_sku: str
    item_name: str
    current_demand: int
    forecasted_demand: int
    trend: str
    period: str
    unit_cost: float
    lead_time_days: int

class BacklogItem(BaseModel):
    id: str
    order_id: str
    item_sku: str
    item_name: str
    quantity_needed: int
    quantity_available: int
    days_delayed: int
    priority: str
    has_purchase_order: Optional[bool] = False

class PurchaseOrder(BaseModel):
    id: str
    backlog_item_id: str
    supplier_name: str
    quantity: int
    unit_cost: float
    expected_delivery_date: str
    status: str
    created_date: str
    notes: Optional[str] = None

class CreatePurchaseOrderRequest(BaseModel):
    backlog_item_id: str
    supplier_name: str
    quantity: int
    unit_cost: float
    expected_delivery_date: str
    notes: Optional[str] = None

# Bounds keep the unauthenticated write endpoints from growing memory without limit
MAX_RESTOCK_QUANTITY = 100_000
MAX_RESTOCK_BUDGET = 100_000_000
MAX_RESTOCK_ITEMS = 50
MAX_RESTOCK_ORDERS = 1000
MAX_TASKS = 500

class RestockItemRequest(BaseModel):
    # Clients may send name/cost/lead time too; they're ignored in favour of the forecast data
    item_sku: str
    quantity: int = Field(gt=0, le=MAX_RESTOCK_QUANTITY)

class CreateRestockOrderRequest(BaseModel):
    # allow_inf_nan=False stops a JSON `Infinity` budget from bypassing the budget check
    budget: float = Field(ge=0, le=MAX_RESTOCK_BUDGET, allow_inf_nan=False)
    items: List[RestockItemRequest] = Field(max_length=MAX_RESTOCK_ITEMS)

class RestockItem(BaseModel):
    item_sku: str
    item_name: str
    quantity: int
    unit_cost: float
    lead_time_days: int

class RestockOrder(BaseModel):
    id: str
    order_number: str
    items: List[RestockItem]
    total_cost: float
    budget: float
    status: str
    submitted_date: str
    lead_time_days: int
    expected_delivery: str

# Submitted restocking orders live only in memory and reset on server restart
restocking_orders: List[dict] = []
restocking_orders_lock = Lock()

class TaskCreateRequest(BaseModel):
    title: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)]
    priority: Literal["high", "medium", "low"] = "medium"
    dueDate: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$")

class Task(BaseModel):
    id: str
    title: str
    priority: str
    dueDate: str
    status: Literal["pending", "completed"]

# Tasks created via the API live only in memory; the client merges them with the profile's mock tasks
tasks: List[dict] = []
tasks_lock = Lock()
# Monotonic counter so a deleted task's id is never reused
task_id_counter = 0

# API endpoints
@app.get("/")
def root():
    return {"message": "Factory Inventory Management System API", "version": "1.0.0"}

@app.get("/api/inventory", response_model=List[InventoryItem])
def get_inventory(
    warehouse: Optional[str] = None,
    category: Optional[str] = None
):
    """Get all inventory items with optional filtering"""
    return apply_filters(inventory_items, warehouse, category)

@app.get("/api/inventory/{item_id}", response_model=InventoryItem)
def get_inventory_item(item_id: str):
    """Get a specific inventory item"""
    item = next((item for item in inventory_items if item["id"] == item_id), None)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@app.get("/api/orders", response_model=List[Order])
def get_orders(
    warehouse: Optional[str] = None,
    category: Optional[str] = None,
    status: Optional[str] = None,
    month: Optional[str] = None
):
    """Get all orders with optional filtering"""
    filtered_orders = apply_filters(orders, warehouse, category, status)
    filtered_orders = filter_by_month(filtered_orders, month)
    return filtered_orders

@app.get("/api/orders/{order_id}", response_model=Order)
def get_order(order_id: str):
    """Get a specific order"""
    order = next((order for order in orders if order["id"] == order_id), None)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@app.get("/api/demand", response_model=List[DemandForecast])
def get_demand_forecasts():
    """Get demand forecasts"""
    return demand_forecasts

@app.get("/api/backlog", response_model=List[BacklogItem])
def get_backlog():
    """Get backlog items with purchase order status"""
    # Add has_purchase_order flag to each backlog item
    result = []
    for item in backlog_items:
        item_dict = dict(item)
        # Check if this backlog item has a purchase order
        has_po = any(po["backlog_item_id"] == item["id"] for po in purchase_orders)
        item_dict["has_purchase_order"] = has_po
        result.append(item_dict)
    return result

@app.get("/api/dashboard/summary")
def get_dashboard_summary(
    warehouse: Optional[str] = None,
    category: Optional[str] = None,
    status: Optional[str] = None,
    month: Optional[str] = None
):
    """Get summary statistics for dashboard with optional filtering"""
    # Filter inventory
    filtered_inventory = apply_filters(inventory_items, warehouse, category)

    # Filter orders
    filtered_orders = apply_filters(orders, warehouse, category, status)
    filtered_orders = filter_by_month(filtered_orders, month)

    total_inventory_value = sum(item["quantity_on_hand"] * item["unit_cost"] for item in filtered_inventory)
    low_stock_items = len([item for item in filtered_inventory if item["quantity_on_hand"] <= item["reorder_point"]])
    pending_orders = len([order for order in filtered_orders if order["status"] in ["Processing", "Backordered"]])
    total_backlog_items = len(backlog_items)

    return {
        "total_inventory_value": round(total_inventory_value, 2),
        "low_stock_items": low_stock_items,
        "pending_orders": pending_orders,
        "total_backlog_items": total_backlog_items,
        "total_orders_value": sum(order["total_value"] for order in filtered_orders)
    }

@app.get("/api/spending/summary")
def get_spending_summary():
    """Get spending summary statistics"""
    return spending_summary

@app.get("/api/spending/monthly")
def get_monthly_spending():
    """Get monthly spending breakdown"""
    return monthly_spending

@app.get("/api/spending/categories")
def get_category_spending():
    """Get spending by category"""
    return category_spending

@app.get("/api/spending/transactions")
def get_recent_transactions():
    """Get recent transactions"""
    return recent_transactions

@app.get("/api/reports/quarterly")
def get_quarterly_reports(
    warehouse: Optional[str] = None,
    category: Optional[str] = None,
    status: Optional[str] = None,
    month: Optional[str] = None
):
    """Get quarterly performance reports with optional filtering"""
    filtered_orders = filter_by_month(apply_filters(orders, warehouse, category, status), month)
    month_to_quarter = {m: q for q, months in QUARTER_MAP.items() for m in months}
    quarters = {}

    for order in filtered_orders:
        quarter = month_to_quarter.get((order.get('order_date') or '')[:7])
        if not quarter:
            continue

        if quarter not in quarters:
            quarters[quarter] = {
                'quarter': quarter,
                'total_orders': 0,
                'total_revenue': 0,
                'delivered_orders': 0,
                'avg_order_value': 0,
                'fulfillment_rate': 0
            }

        quarters[quarter]['total_orders'] += 1
        quarters[quarter]['total_revenue'] += order.get('total_value', 0)
        if order.get('status') == 'Delivered':
            quarters[quarter]['delivered_orders'] += 1

    result = []
    for data in quarters.values():
        data['avg_order_value'] = round(data['total_revenue'] / data['total_orders'], 2)
        data['fulfillment_rate'] = round((data['delivered_orders'] / data['total_orders']) * 100, 1)
        result.append(data)

    result.sort(key=lambda x: x['quarter'])
    return result

@app.get("/api/reports/monthly-trends")
def get_monthly_trends(
    warehouse: Optional[str] = None,
    category: Optional[str] = None,
    status: Optional[str] = None,
    month: Optional[str] = None
):
    """Get month-over-month trends with optional filtering"""
    filtered_orders = filter_by_month(apply_filters(orders, warehouse, category, status), month)
    months = {}

    for order in filtered_orders:
        order_date = order.get('order_date', '')
        if not order_date:
            continue

        # Extract month (format: YYYY-MM-DD)
        order_month = order_date[:7]  # Gets YYYY-MM

        if order_month not in months:
            months[order_month] = {
                'month': order_month,
                'order_count': 0,
                'revenue': 0,
                'delivered_count': 0
            }

        months[order_month]['order_count'] += 1
        months[order_month]['revenue'] += order.get('total_value', 0)
        if order.get('status') == 'Delivered':
            months[order_month]['delivered_count'] += 1

    # Convert to list and sort
    result = list(months.values())
    result.sort(key=lambda x: x['month'])
    return result

@app.get("/api/restocking-orders", response_model=List[RestockOrder])
def get_restocking_orders():
    """Get submitted restocking orders, newest first"""
    return list(reversed(restocking_orders))

@app.post("/api/restocking-orders", response_model=RestockOrder, status_code=201)
def create_restocking_order(request: CreateRestockOrderRequest):
    """Submit a restocking order priced from the demand forecast data"""
    if not request.items:
        raise HTTPException(status_code=400, detail="Order must contain at least one item")

    skus = [i.item_sku for i in request.items]
    if len(skus) != len(set(skus)):
        raise HTTPException(status_code=400, detail="Each SKU may appear only once per order")

    forecasts_by_sku = {f["item_sku"]: f for f in demand_forecasts}
    items = []
    for requested in request.items:
        forecast = forecasts_by_sku.get(requested.item_sku)
        if not forecast:
            raise HTTPException(status_code=400, detail=f"Unknown SKU {requested.item_sku}")
        # Price from server data so a client can't under-report cost to fit the budget
        items.append({
            "item_sku": forecast["item_sku"],
            "item_name": forecast["item_name"],
            "quantity": requested.quantity,
            "unit_cost": forecast["unit_cost"],
            "lead_time_days": forecast["lead_time_days"],
        })

    total_cost = round(sum(i["quantity"] * i["unit_cost"] for i in items), 2)
    if total_cost > request.budget:
        raise HTTPException(
            status_code=400,
            detail=f"Order total {total_cost:.2f} exceeds budget {request.budget:.2f}"
        )

    # The order can only arrive once its slowest item does
    lead_time_days = max(i["lead_time_days"] for i in items)
    today = date.today()
    # Sync endpoints run in a threadpool; lock so concurrent POSTs can't share an order number
    with restocking_orders_lock:
        if len(restocking_orders) >= MAX_RESTOCK_ORDERS:
            raise HTTPException(status_code=409, detail="Restocking order limit reached")
        sequence = len(restocking_orders) + 1
        order = {
            "id": str(sequence),
            "order_number": f"RST-{sequence:04d}",
            "items": items,
            "total_cost": total_cost,
            "budget": request.budget,
            "status": "Submitted",
            "submitted_date": today.isoformat(),
            "lead_time_days": lead_time_days,
            "expected_delivery": (today + timedelta(days=lead_time_days)).isoformat(),
        }
        restocking_orders.append(order)
    return order

def _find_task(task_id: str) -> dict:
    task = next((t for t in tasks if t["id"] == task_id), None)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@app.get("/api/tasks", response_model=List[Task])
def get_tasks():
    """Get tasks created via the API, newest first"""
    return list(reversed(tasks))

@app.post("/api/tasks", response_model=Task, status_code=201)
def create_task(request: TaskCreateRequest):
    """Create a pending task"""
    global task_id_counter
    with tasks_lock:
        if len(tasks) >= MAX_TASKS:
            raise HTTPException(status_code=409, detail="Task limit reached")
        task_id_counter += 1
        # String ids can't collide with the numeric ids of the profile's mock tasks
        task = {
            "id": f"task-{task_id_counter}",
            "title": request.title,
            "priority": request.priority,
            "dueDate": request.dueDate,
            "status": "pending",
        }
        tasks.append(task)
    return task

@app.patch("/api/tasks/{task_id}", response_model=Task)
def toggle_task(task_id: str):
    """Toggle a task between pending and completed"""
    with tasks_lock:
        task = _find_task(task_id)
        task["status"] = "completed" if task["status"] == "pending" else "pending"
    return task

@app.delete("/api/tasks/{task_id}", status_code=204)
def delete_task(task_id: str):
    """Delete a task"""
    with tasks_lock:
        tasks.remove(_find_task(task_id))

if __name__ == "__main__":
    import uvicorn
    # Loopback only: the API has no auth, so it must not be reachable from the network
    uvicorn.run(app, host="127.0.0.1", port=8001)
