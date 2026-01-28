"""
Test script to verify project creation behavior.

Tests:
1. Create test user
2. Create project with spaces in title
3. Verify space trimming, timestamps, and deletion status
"""

import asyncio
import os
import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))
os.chdir(backend_dir)

# Set UTF-8 encoding for Windows console
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

from datetime import datetime  # noqa: E402


async def main():
    from src.db.session import get_session_context
    from src.services.auth.user_service import UserService
    from src.services.project_service import ProjectService

    print("=" * 60)
    print("프로젝트 생성 테스트")
    print("=" * 60)

    async with get_session_context() as session:
        # 1. 테스트 사용자 생성
        print("\n[1] 테스트 사용자 생성...")
        user_service = UserService(session)

        test_email = (
            f"test_project_{datetime.now().strftime('%Y%m%d%H%M%S')}@example.com"
        )
        test_password = "SecurePass123!"

        try:
            user = await user_service.register(test_email, test_password)
            print(f"    [OK] 사용자 생성 완료: {user.email}")
            print(f"    - ID: {user.id}")
        except Exception as e:
            print(f"    [FAIL] 사용자 생성 실패: {e}")
            return

        # 2. 프로젝트 생성 (앞뒤 공백 포함)
        print("\n[2] 프로젝트 생성...")
        project_service = ProjectService(session)

        title_with_spaces = "  React 학습  "  # 앞뒤 공백 포함
        description = "컴포넌트 배우기"

        print(f"    입력 제목: '{title_with_spaces}' (길이: {len(title_with_spaces)})")
        print(f"    입력 설명: '{description}'")

        try:
            project = await project_service.create(
                user_id=user.id, title=title_with_spaces, description=description
            )
            print("    [OK] 프로젝트 생성 완료")
            print(f"    - ID: {project.id}")
        except Exception as e:
            print(f"    [FAIL] 프로젝트 생성 실패: {e}")
            return

        # 3. 검증
        print("\n[3] 검증 결과...")
        print("-" * 60)

        # 3-1. 공백 제거 확인
        print("\n    [CHECK] 제목 공백 처리:")
        print(f"       입력값: '{title_with_spaces}' (길이: {len(title_with_spaces)})")
        print(f"       저장값: '{project.title}' (길이: {len(project.title)})")

        if project.title == title_with_spaces:
            print("       [WARN] 공백이 제거되지 않음 (원본 그대로 저장)")
        elif project.title == title_with_spaces.strip():
            print("       [OK] 공백이 제거됨 (strip 적용)")
        else:
            print("       [?] 예상치 못한 결과")

        # 3-2. 타임스탬프 확인
        print("\n    [CHECK] 타임스탬프:")
        print(f"       created_at:       {project.created_at}")
        print(f"       updated_at:       {project.updated_at}")
        print(f"       last_activity_at: {project.last_activity_at}")

        # 타임스탬프 비교 (1초 이내 차이면 같은 것으로 간주)
        timestamps_match = True

        if project.created_at and project.updated_at:
            diff1 = abs((project.created_at - project.updated_at).total_seconds())
            if diff1 > 1:
                timestamps_match = False
                print(f"       [WARN] created_at과 updated_at 차이: {diff1}초")

        if project.created_at and project.last_activity_at:
            diff2 = abs((project.created_at - project.last_activity_at).total_seconds())
            if diff2 > 1:
                timestamps_match = False
                print(f"       [WARN] created_at과 last_activity_at 차이: {diff2}초")

        if timestamps_match:
            print("       [OK] 모든 타임스탬프가 동일 (1초 이내)")

        # 3-3. deletion_status 확인
        print("\n    [CHECK] 삭제 상태:")
        print(f"       deletion_status: '{project.deletion_status}'")
        print(f"       trashed_at: {project.trashed_at}")
        print(f"       scheduled_deletion_at: {project.scheduled_deletion_at}")

        if project.deletion_status == "active":
            print("       [OK] deletion_status가 'active'임")
        else:
            print("       [FAIL] deletion_status가 'active'가 아님!")

        if project.trashed_at is None and project.scheduled_deletion_at is None:
            print("       [OK] 휴지통 관련 필드가 None임")
        else:
            print("       [WARN] 휴지통 관련 필드에 값이 있음!")

        # 4. 요약
        print("\n" + "=" * 60)
        print("테스트 요약")
        print("=" * 60)

        issues = []

        if project.title == title_with_spaces:
            issues.append("공백이 제거되지 않음")

        if not timestamps_match:
            issues.append("타임스탬프가 일치하지 않음")

        if project.deletion_status != "active":
            issues.append("deletion_status가 active가 아님")

        if issues:
            print("\n[WARN] 발견된 이슈:")
            for issue in issues:
                print(f"   - {issue}")
        else:
            print("\n[OK] 모든 검증 통과!")

        print()


if __name__ == "__main__":
    asyncio.run(main())
