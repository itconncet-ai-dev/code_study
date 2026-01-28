# Python 기초 문법 예제


def greet(name):
    """사용자에게 인사하는 함수"""
    return f"안녕하세요, {name}님!"


class Calculator:
    """간단한 계산기 클래스"""

    def __init__(self):
        self.result = 0

    def add(self, a, b):
        """두 수를 더합니다"""
        self.result = a + b
        return self.result

    def subtract(self, a, b):
        """두 수를 뺍니다"""
        self.result = a - b
        return self.result


# 메인 실행 코드
if __name__ == "__main__":
    # 인사 함수 테스트
    print(greet("학습자"))

    # 계산기 테스트
    calc = Calculator()
    print(f"10 + 5 = {calc.add(10, 5)}")
    print(f"10 - 5 = {calc.subtract(10, 5)}")
