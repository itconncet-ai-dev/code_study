#!/usr/bin/env python
"""
Celery and Redis Integration Test Script

This script tests the Celery worker and Redis connection by:
1. Running a quick connectivity test
2. Running a 30-second simulated document generation task

Usage:
    # Make sure Redis is running and Celery worker is started first!
    # Terminal 1: docker-compose up redis
    # Terminal 2: cd backend && celery -A src.tasks.celery_app worker --loglevel=info

    # Then run this script:
    cd backend
    python scripts/test_celery.py
"""

import sys
import time

# Add src to path for imports
sys.path.insert(0, ".")

from src.tasks.test_tasks import quick_test, simulate_document_generation


def test_quick_connectivity():
    """Test basic Celery connectivity with a quick task."""
    print("\n" + "=" * 60)
    print("1️⃣  빠른 연결 테스트")
    print("=" * 60)

    result = quick_test.delay(message="안녕하세요, Celery!")
    print(f"   태스크 ID: {result.id}")
    print(f"   상태: {result.status}")

    print("   결과 대기 중...")
    try:
        response = result.get(timeout=10)
        print("   ✅ 성공!")
        print(f"   응답: {response['echo']}")
        return True
    except Exception as e:
        print(f"   ❌ 실패: {e}")
        return False


def test_long_running_task():
    """Test a 30-second document generation simulation."""
    print("\n" + "=" * 60)
    print("2️⃣  문서 생성 시뮬레이션 (30초)")
    print("=" * 60)

    result = simulate_document_generation.delay(
        document_name="Python 기초 학습 문서",
        duration_seconds=30,
    )

    print(f"   태스크 ID: {result.id}")
    print(f"   상태: {result.status}")
    print("\n   진행 상황 모니터링:")
    print("   " + "-" * 40)

    # Monitor progress
    while not result.ready():
        state = result.state
        info = result.info

        if state == "PROGRESS" and isinstance(info, dict):
            progress = info.get("progress", 0)
            status = info.get("status", "처리 중...")
            bar_length = 30
            filled = int(bar_length * progress / 100)
            bar = "█" * filled + "░" * (bar_length - filled)
            print(f"\r   [{bar}] {progress:.0f}% - {status}", end="", flush=True)
        elif state == "PENDING":
            print(
                "\r   대기 중... (워커가 태스크를 가져가길 기다리는 중)",
                end="",
                flush=True,
            )
        elif state == "STARTED":
            print("\r   시작됨...", end="", flush=True)

        time.sleep(1)

    print()  # New line after progress bar

    if result.successful():
        response = result.get()
        print("\n   ✅ 문서 생성 완료!")
        print(f"   문서명: {response['document_name']}")
        print(f"   소요 시간: {response['elapsed_seconds']:.1f}초")
        print(f"   메시지: {response['message']}")
        return True
    else:
        print(f"\n   ❌ 실패: {result.result}")
        return False


def main():
    print("\n" + "🔴" * 20)
    print("   Celery + Redis 통합 테스트")
    print("🔴" * 20)

    print("\n⚠️  주의: 이 테스트를 실행하기 전에:")
    print("   1. Redis가 실행 중이어야 합니다 (docker-compose up redis)")
    print("   2. Celery 워커가 실행 중이어야 합니다:")
    print("      cd backend && celery -A src.tasks.celery_app worker --loglevel=info")
    print()

    input("준비가 되었으면 Enter를 누르세요...")

    # Run tests
    quick_ok = test_quick_connectivity()

    if quick_ok:
        long_ok = test_long_running_task()
    else:
        print("\n⚠️  빠른 테스트 실패로 문서 생성 테스트를 건너뜁니다.")
        long_ok = False

    # Summary
    print("\n" + "=" * 60)
    print("📊 테스트 결과 요약")
    print("=" * 60)
    print(f"   빠른 연결 테스트: {'✅ 통과' if quick_ok else '❌ 실패'}")
    print(f"   문서 생성 테스트: {'✅ 통과' if long_ok else '❌ 실패'}")

    if quick_ok and long_ok:
        print("\n🎉 모든 테스트 통과! Celery와 Redis가 정상 작동합니다.")
    else:
        print("\n⚠️  일부 테스트 실패. 위의 오류 메시지를 확인하세요.")


if __name__ == "__main__":
    main()
