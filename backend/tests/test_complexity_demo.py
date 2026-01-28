"""
Complexity Analyzer Demo - Task T066

This script demonstrates the complexity analyzer by creating 3 test files
at different complexity levels and comparing their analysis results.

Test Cases:
1. Beginner (~30 lines, 2 functions, 0 classes)
2. Intermediate (~150 lines, 10 functions, 3 classes)
3. Advanced (~300 lines, 25 functions, 8 classes)
"""

import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.src.services.code_analysis.complexity_analyzer import (  # noqa: E402
    ComplexityAnalyzer,
    ComplexityResult,
)

# =============================================================================
# Test Code: BEGINNER LEVEL
# ~30 lines, 2 functions, 0 classes
# =============================================================================

BEGINNER_CODE = '''"""Simple calculator script for beginners."""

def add_numbers(a, b):
    """Add two numbers together."""
    result = a + b
    return result


def multiply_numbers(a, b):
    """Multiply two numbers."""
    result = a * b
    return result


# Main program
if __name__ == "__main__":
    # Get user input
    num1 = 10
    num2 = 5

    # Calculate sum
    sum_result = add_numbers(num1, num2)
    print(f"Sum: {sum_result}")

    # Calculate product
    product_result = multiply_numbers(num1, num2)
    print(f"Product: {product_result}")
'''


# =============================================================================
# Test Code: INTERMEDIATE LEVEL
# ~150 lines, 10 functions, 3 classes
# =============================================================================

INTERMEDIATE_CODE = '''"""
Shopping Cart System - Intermediate complexity example.
Demonstrates OOP with multiple classes and methods.
"""

from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime
import json


@dataclass
class Product:
    """Represents a product in the store."""
    id: str
    name: str
    price: float
    category: str
    stock: int = 0

    def is_available(self) -> bool:
        """Check if product is in stock."""
        return self.stock > 0

    def reduce_stock(self, quantity: int) -> bool:
        """Reduce stock by given quantity."""
        if quantity <= self.stock:
            self.stock -= quantity
            return True
        return False


class ShoppingCart:
    """Manages shopping cart operations."""

    def __init__(self, user_id: str):
        self.user_id = user_id
        self.items: List[dict] = []
        self.created_at = datetime.now()

    def add_item(self, product: Product, quantity: int) -> bool:
        """Add item to cart."""
        if not product.is_available():
            return False

        for item in self.items:
            if item["product_id"] == product.id:
                item["quantity"] += quantity
                return True

        self.items.append({
            "product_id": product.id,
            "name": product.name,
            "price": product.price,
            "quantity": quantity
        })
        return True

    def remove_item(self, product_id: str) -> bool:
        """Remove item from cart."""
        for i, item in enumerate(self.items):
            if item["product_id"] == product_id:
                del self.items[i]
                return True
        return False

    def get_total(self) -> float:
        """Calculate cart total."""
        total = 0.0
        for item in self.items:
            total += item["price"] * item["quantity"]
        return round(total, 2)

    def get_item_count(self) -> int:
        """Get total number of items."""
        return sum(item["quantity"] for item in self.items)

    def clear(self) -> None:
        """Clear all items from cart."""
        self.items = []


class OrderProcessor:
    """Handles order processing and validation."""

    def __init__(self):
        self.orders: List[dict] = []

    def validate_cart(self, cart: ShoppingCart) -> tuple[bool, str]:
        """Validate cart before checkout."""
        if not cart.items:
            return False, "Cart is empty"

        if cart.get_total() <= 0:
            return False, "Invalid cart total"

        return True, "Cart is valid"

    def create_order(self, cart: ShoppingCart) -> Optional[dict]:
        """Create order from cart."""
        is_valid, message = self.validate_cart(cart)
        if not is_valid:
            print(f"Validation failed: {message}")
            return None

        order = {
            "order_id": f"ORD-{len(self.orders) + 1:04d}",
            "user_id": cart.user_id,
            "items": cart.items.copy(),
            "total": cart.get_total(),
            "created_at": datetime.now().isoformat()
        }

        self.orders.append(order)
        cart.clear()
        return order

    def get_order(self, order_id: str) -> Optional[dict]:
        """Retrieve order by ID."""
        for order in self.orders:
            if order["order_id"] == order_id:
                return order
        return None


def format_currency(amount: float) -> str:
    """Format amount as currency string."""
    return f"${amount:,.2f}"


def calculate_discount(total: float, discount_percent: float) -> float:
    """Calculate discounted total."""
    discount = total * (discount_percent / 100)
    return round(total - discount, 2)


def validate_product_data(data: dict) -> bool:
    """Validate product data dictionary."""
    required_fields = ["id", "name", "price", "category"]
    return all(field in data for field in required_fields)


def load_products_from_json(json_string: str) -> List[Product]:
    """Load products from JSON string."""
    try:
        data = json.loads(json_string)
        products = []
        for item in data:
            if validate_product_data(item):
                products.append(Product(**item))
        return products
    except json.JSONDecodeError:
        return []
'''


# =============================================================================
# Test Code: ADVANCED LEVEL
# ~300 lines, 25 functions, 8 classes
# =============================================================================

ADVANCED_CODE = '''"""
Advanced Event-Driven Task Scheduler System.
Demonstrates async programming, decorators, generators, and design patterns.
"""

from __future__ import annotations
import asyncio
import functools
import logging
from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum, auto
from typing import (
    Any, Callable, Coroutine, Dict, Generic, List, Optional,
    Protocol, Set, TypeVar, Union
)
from contextlib import asynccontextmanager
import heapq
import weakref


T = TypeVar("T")
R = TypeVar("R")


class TaskStatus(Enum):
    """Task execution status."""
    PENDING = auto()
    RUNNING = auto()
    COMPLETED = auto()
    FAILED = auto()
    CANCELLED = auto()


class Priority(Enum):
    """Task priority levels."""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


def retry(max_attempts: int = 3, delay: float = 1.0):
    """Decorator for automatic retry with exponential backoff."""
    def decorator(func: Callable[..., Coroutine]) -> Callable[..., Coroutine]:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    wait_time = delay * (2 ** attempt)
                    await asyncio.sleep(wait_time)
            raise last_exception
        return wrapper
    return decorator


def log_execution(logger: logging.Logger):
    """Decorator to log function execution."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            logger.debug(f"Executing {func.__name__}")
            try:
                result = await func(*args, **kwargs)
                logger.debug(f"Completed {func.__name__}")
                return result
            except Exception as e:
                logger.error(f"Failed {func.__name__}: {e}")
                raise

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            logger.debug(f"Executing {func.__name__}")
            try:
                result = func(*args, **kwargs)
                logger.debug(f"Completed {func.__name__}")
                return result
            except Exception as e:
                logger.error(f"Failed {func.__name__}: {e}")
                raise

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    return decorator


class TaskHandler(Protocol):
    """Protocol for task handlers."""

    async def execute(self, context: TaskContext) -> Any:
        """Execute the task."""
        ...


@dataclass
class TaskContext:
    """Execution context for tasks."""
    task_id: str
    data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    parent_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)


@dataclass(order=True)
class ScheduledTask:
    """Task with scheduling information."""
    execute_at: datetime
    priority: Priority = field(compare=False)
    task_id: str = field(compare=False)
    handler: TaskHandler = field(compare=False)
    context: TaskContext = field(compare=False)
    status: TaskStatus = field(default=TaskStatus.PENDING, compare=False)
    result: Optional[Any] = field(default=None, compare=False)
    error: Optional[Exception] = field(default=None, compare=False)


class EventEmitter(Generic[T]):
    """Generic event emitter with type-safe listeners."""

    def __init__(self):
        self._listeners: Dict[str, List[Callable[[T], Coroutine]]] = defaultdict(list)
        self._once_listeners: Dict[str, List[Callable[[T], Coroutine]]] = defaultdict(list)

    def on(self, event: str, callback: Callable[[T], Coroutine]) -> None:
        """Register event listener."""
        self._listeners[event].append(callback)

    def once(self, event: str, callback: Callable[[T], Coroutine]) -> None:
        """Register one-time event listener."""
        self._once_listeners[event].append(callback)

    def off(self, event: str, callback: Callable[[T], Coroutine]) -> None:
        """Remove event listener."""
        if callback in self._listeners[event]:
            self._listeners[event].remove(callback)

    async def emit(self, event: str, data: T) -> None:
        """Emit event to all listeners."""
        tasks = []
        for callback in self._listeners.get(event, []):
            tasks.append(callback(data))

        once_callbacks = self._once_listeners.pop(event, [])
        for callback in once_callbacks:
            tasks.append(callback(data))

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)


class TaskQueue:
    """Priority queue for scheduled tasks."""

    def __init__(self):
        self._heap: List[ScheduledTask] = []
        self._task_map: Dict[str, ScheduledTask] = {}

    def push(self, task: ScheduledTask) -> None:
        """Add task to queue."""
        heapq.heappush(self._heap, task)
        self._task_map[task.task_id] = task

    def pop(self) -> Optional[ScheduledTask]:
        """Remove and return highest priority task."""
        while self._heap:
            task = heapq.heappop(self._heap)
            if task.status == TaskStatus.PENDING:
                return task
        return None

    def peek(self) -> Optional[ScheduledTask]:
        """View next task without removing."""
        for task in self._heap:
            if task.status == TaskStatus.PENDING:
                return task
        return None

    def cancel(self, task_id: str) -> bool:
        """Cancel a scheduled task."""
        if task_id in self._task_map:
            self._task_map[task_id].status = TaskStatus.CANCELLED
            return True
        return False

    def __len__(self) -> int:
        return sum(1 for t in self._heap if t.status == TaskStatus.PENDING)

    def pending_tasks(self):
        """Generate pending tasks."""
        for task in self._heap:
            if task.status == TaskStatus.PENDING:
                yield task


class BaseHandler(ABC):
    """Abstract base handler with common functionality."""

    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(name)

    @abstractmethod
    async def execute(self, context: TaskContext) -> Any:
        """Execute the handler logic."""
        pass

    def validate(self, context: TaskContext) -> bool:
        """Validate task context."""
        return bool(context.task_id)


class ComputeHandler(BaseHandler):
    """Handler for computation tasks."""

    def __init__(self):
        super().__init__("ComputeHandler")

    @retry(max_attempts=2)
    async def execute(self, context: TaskContext) -> Dict[str, Any]:
        """Execute computation."""
        data = context.data
        result = await self._process(data)
        return {"status": "completed", "result": result}

    async def _process(self, data: Dict[str, Any]) -> Any:
        """Process the computation."""
        await asyncio.sleep(0.1)  # Simulate work
        return sum(data.get("values", []))


class NotificationHandler(BaseHandler):
    """Handler for sending notifications."""

    def __init__(self, transport: str = "email"):
        super().__init__("NotificationHandler")
        self.transport = transport

    async def execute(self, context: TaskContext) -> bool:
        """Send notification."""
        recipient = context.data.get("recipient")
        message = context.data.get("message")
        return await self._send(recipient, message)

    async def _send(self, recipient: str, message: str) -> bool:
        """Send via transport."""
        await asyncio.sleep(0.05)
        return True


class TaskScheduler:
    """Main task scheduler with async execution."""

    def __init__(self, max_concurrent: int = 10):
        self.queue = TaskQueue()
        self.events = EventEmitter[ScheduledTask]()
        self.max_concurrent = max_concurrent
        self._running = False
        self._active_tasks: Set[str] = set()
        self._task_counter = 0

    def schedule(
        self,
        handler: TaskHandler,
        data: Dict[str, Any],
        priority: Priority = Priority.NORMAL,
        delay: Optional[timedelta] = None
    ) -> str:
        """Schedule a new task."""
        self._task_counter += 1
        task_id = f"task-{self._task_counter:06d}"

        execute_at = datetime.now()
        if delay:
            execute_at += delay

        context = TaskContext(task_id=task_id, data=data)
        task = ScheduledTask(
            execute_at=execute_at,
            priority=priority,
            task_id=task_id,
            handler=handler,
            context=context
        )

        self.queue.push(task)
        return task_id

    async def start(self) -> None:
        """Start the scheduler."""
        self._running = True
        while self._running:
            await self._process_tasks()
            await asyncio.sleep(0.01)

    async def stop(self) -> None:
        """Stop the scheduler."""
        self._running = False

    async def _process_tasks(self) -> None:
        """Process ready tasks."""
        now = datetime.now()
        ready = [
            t for t in self.queue.pending_tasks()
            if t.execute_at <= now and t.task_id not in self._active_tasks
        ]

        available_slots = self.max_concurrent - len(self._active_tasks)
        tasks_to_run = ready[:available_slots]

        for task in tasks_to_run:
            asyncio.create_task(self._execute_task(task))

    async def _execute_task(self, task: ScheduledTask) -> None:
        """Execute a single task."""
        self._active_tasks.add(task.task_id)
        task.status = TaskStatus.RUNNING

        try:
            await self.events.emit("task_started", task)
            task.result = await task.handler.execute(task.context)
            task.status = TaskStatus.COMPLETED
            await self.events.emit("task_completed", task)
        except Exception as e:
            task.error = e
            task.status = TaskStatus.FAILED
            await self.events.emit("task_failed", task)
        finally:
            self._active_tasks.discard(task.task_id)


@asynccontextmanager
async def managed_scheduler(max_concurrent: int = 10):
    """Context manager for scheduler lifecycle."""
    scheduler = TaskScheduler(max_concurrent)
    task = asyncio.create_task(scheduler.start())
    try:
        yield scheduler
    finally:
        await scheduler.stop()
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
'''


def print_separator(title: str) -> None:
    """Print a formatted separator."""
    print("\n" + "=" * 70)
    print(f" {title}")
    print("=" * 70)


def print_metrics_table(result: ComplexityResult) -> None:
    """Print detailed metrics breakdown table."""
    print(
        "\n┌─────────────────────────┬───────────┬────────────┬────────┬───────────────┐"
    )
    print(
        "│ Metric                  │ Raw Value │ Score(100) │ Weight │ Weighted      │"
    )
    print(
        "├─────────────────────────┼───────────┼────────────┼────────┼───────────────┤"
    )

    for score in result.metric_scores:
        weighted = score.normalized_score * score.weight
        print(
            f"│ {score.name:<23} │ {str(score.raw_value):>9} │ "
            f"{score.normalized_score:>10.1f} │ {score.weight:>6.2f} │ {weighted:>13.2f} │"
        )

    print(
        "├─────────────────────────┴───────────┴────────────┴────────┼───────────────┤"
    )
    print(
        f"│ TOTAL SCORE                                              │ {result.total_score:>13.2f} │"
    )
    print(
        "└──────────────────────────────────────────────────────────┴───────────────┘"
    )
    print(f"\nComplexity Level: {result.level.value.upper()}")


def print_comparison_table(results: dict[str, ComplexityResult]) -> None:
    """Print comparison table of all results."""
    print_separator("COMPARISON TABLE")

    print(
        "\n┌────────────────┬─────────┬───────────┬─────────┬─────────┬─────────┬───────────┬──────────────┐"
    )
    print(
        "│ Level          │ Lines   │ Functions │ Classes │ Methods │ Nesting │ Score     │ Result       │"
    )
    print(
        "├────────────────┼─────────┼───────────┼─────────┼─────────┼─────────┼───────────┼──────────────┤"
    )

    for name, result in results.items():
        m = result.metrics
        level_result = result.level.value.upper()
        print(
            f"│ {name:<14} │ {m.code_lines:>7} │ {m.function_count:>9} │ "
            f"{m.class_count:>7} │ {m.method_count:>7} │ {m.max_nesting_depth:>7} │ "
            f"{result.total_score:>9.2f} │ {level_result:<12} │"
        )

    print(
        "└────────────────┴─────────┴───────────┴─────────┴─────────┴─────────┴───────────┴──────────────┘"
    )


def run_analysis():
    """Run complexity analysis on all test codes."""
    print("=" * 70)
    print(" COMPLEXITY ANALYZER DEMO - Task T066")
    print(" Testing 3 complexity levels: Beginner, Intermediate, Advanced")
    print("=" * 70)

    # Analyze each test code
    results = {}

    test_cases = [
        ("BEGINNER", BEGINNER_CODE, "~30 lines, 2 functions, 0 classes"),
        ("INTERMEDIATE", INTERMEDIATE_CODE, "~150 lines, 10 functions, 3 classes"),
        ("ADVANCED", ADVANCED_CODE, "~300 lines, 25 functions, 8 classes"),
    ]

    for name, code, description in test_cases:
        print_separator(f"{name} ({description})")

        result = ComplexityAnalyzer.analyze(code)
        results[name] = result

        print("\nCode Statistics:")
        print(f"  - Total Lines: {result.metrics.total_lines}")
        print(f"  - Code Lines: {result.metrics.code_lines}")
        print(f"  - Functions: {result.metrics.function_count}")
        print(f"  - Classes: {result.metrics.class_count}")
        print(f"  - Methods: {result.metrics.method_count}")
        print(f"  - Max Nesting: {result.metrics.max_nesting_depth}")
        print(f"  - Imports: {result.metrics.import_count}")

        if result.analysis_notes:
            print("\nAnalysis Notes:")
            for note in result.analysis_notes:
                print(f"  - {note}")

        print_metrics_table(result)

    # Print comparison
    print_comparison_table(results)

    # Verify expected results
    print_separator("VERIFICATION")
    expected = {
        "BEGINNER": "beginner",
        "INTERMEDIATE": "intermediate",
        "ADVANCED": "advanced",
    }

    all_match = True
    for name, expected_level in expected.items():
        actual = results[name].level.value
        match = "PASS" if actual == expected_level else "FAIL"
        if actual != expected_level:
            all_match = False
        print(f"  [{match}] {name}: Expected '{expected_level}' -> Got '{actual}'")

    print(f"\n{'All tests PASSED!' if all_match else 'Some tests FAILED!'}")

    return results


if __name__ == "__main__":
    run_analysis()
