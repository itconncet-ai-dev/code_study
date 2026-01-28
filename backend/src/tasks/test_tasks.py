"""
Test Tasks for Celery and Redis Integration Testing

This module provides test tasks to verify Celery worker and Redis
broker/backend connectivity. These tasks simulate long-running operations
like AI document generation.

Usage:
    # From Python shell or test script
    from src.tasks.test_tasks import simulate_document_generation

    # Async call (returns immediately)
    result = simulate_document_generation.delay(document_name="테스트 문서")

    # Check status
    print(result.status)  # PENDING -> STARTED -> SUCCESS

    # Get result (blocks until complete)
    print(result.get(timeout=60))
"""

import time
from datetime import datetime

from .celery_app import celery_app


@celery_app.task(bind=True, name="src.tasks.test_tasks.simulate_document_generation")
def simulate_document_generation(
    self,
    document_name: str = "테스트 문서",
    duration_seconds: int = 30,
) -> dict:
    """
    Simulate a long-running document generation task.

    This task mimics the behavior of AI document generation by:
    1. Starting with a "processing" status
    2. Updating progress every 5 seconds
    3. Completing after the specified duration

    Args:
        document_name: Name of the simulated document
        duration_seconds: How long the task should take (default: 30s)

    Returns:
        dict: Task result with document info and timing
    """
    start_time = datetime.now()
    task_id = self.request.id

    print(f"[{task_id}] 문서 생성 시작: {document_name}")

    # Simulate processing with progress updates
    steps = duration_seconds // 5  # Update every 5 seconds
    for step in range(steps):
        progress = (step + 1) / steps * 100

        # Update task state with progress info
        self.update_state(
            state="PROGRESS",
            meta={
                "current": step + 1,
                "total": steps,
                "progress": progress,
                "status": f"처리 중... {progress:.0f}%",
                "document_name": document_name,
            },
        )

        print(f"[{task_id}] 진행률: {progress:.0f}% ({step + 1}/{steps})")
        time.sleep(5)

    end_time = datetime.now()
    elapsed = (end_time - start_time).total_seconds()

    result = {
        "success": True,
        "document_name": document_name,
        "task_id": task_id,
        "started_at": start_time.isoformat(),
        "completed_at": end_time.isoformat(),
        "elapsed_seconds": elapsed,
        "message": f"'{document_name}' 문서가 {elapsed:.1f}초 만에 생성되었습니다!",
    }

    print(f"[{task_id}] 문서 생성 완료: {elapsed:.1f}초 소요")

    return result


@celery_app.task(bind=True, name="src.tasks.test_tasks.quick_test")
def quick_test(self, message: str = "Hello") -> dict:
    """
    Quick test task for verifying basic Celery connectivity.

    Args:
        message: Test message to echo back

    Returns:
        dict: Echo response with task info
    """
    return {
        "success": True,
        "message": message,
        "task_id": self.request.id,
        "timestamp": datetime.now().isoformat(),
        "echo": f"받은 메시지: {message}",
    }
