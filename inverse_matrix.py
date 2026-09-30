from fractions import Fraction
import copy
import random
import time

def to_number(token):
    return Fraction(token)

def input_matrix():
    while True:
        try:
            n = int(input("정방행렬의 차수를 입력하세요: ").strip())
            if n <= 0:
                print("  [오류] 차수는 1 이상의 정수여야 합니다.")
                continue
            break
        except ValueError:
            print("  [오류] 정수를 입력해주세요.")
 
    matrix = []                                  
    i = 0
    while i < n:
        try:
            row_input = input(f"{i + 1}행: ").split()
            if len(row_input) != n:
                print(f"  [오류] 원소를 정확히 {n}개 입력해주세요. "
                      f"(현재 {len(row_input)}개)")
                continue
            row = [to_number(x) for x in row_input]
            matrix.append(row)                 
            i += 1
        except (ValueError, ZeroDivisionError):
            print("  [오류] 숫자 형식이 올바르지 않습니다. (예: 3, 0.5, 1/2)")
 
    return matrix
 
 
def print_matrix(matrix, indent="    ", as_decimal=False):
    """행렬을 보기 좋게 정렬하여 출력한다."""
    if not matrix:
        print(indent + "(빈 행렬)")
        return
 
    # 각 원소를 문자열로 변환
    text = []
    for row in matrix:
        line = []
        for value in row:
            if as_decimal:
                line.append(f"{float(value):.4f}")
            elif value.denominator == 1:          # 정수이면 정수로 표기
                line.append(str(value.numerator))
            else:                                 # 아니면 분수로 표기
                line.append(f"{value.numerator}/{value.denominator}")
        text.append(line)
 
    width = max(len(s) for line in text for s in line)   # 열 너비 통일
    for line in text:
        print(indent + "[ " + "  ".join(s.rjust(width) for s in line) + " ]")


def minor(matrix, row, col):
    return [[matrix[i][j] for j in range(len(matrix)) if j != col]
            for i in range(len(matrix)) if i != row]
 
def determinant(matrix):
    n = len(matrix)
 
    if n == 1:                                   
        return matrix[0][0]
    if n == 2:                                   
        return matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]
 
    det = Fraction(0)
    for col in range(n):                         
        sign = (-1) ** col
        det += sign * matrix[0][col] * determinant(minor(matrix, 0, col))
    return det
 
 
def cofactor_matrix(matrix):
    n = len(matrix)
    if n == 1:
        return [[Fraction(1)]]
    return [[((-1) ** (i + j)) * determinant(minor(matrix, i, j))
             for j in range(n)] for i in range(n)]
 
 
def transpose(matrix):
    n = len(matrix)
    return [[matrix[j][i] for j in range(n)] for i in range(n)]
 
 
def inverse_by_determinant(matrix):
    det = determinant(matrix)
 
    if det == 0:                                
        return None, f"행렬식이 0이므로 역행렬이 존재하지 않습니다. (det = 0)"
 
    adjugate = transpose(cofactor_matrix(matrix))  
    n = len(matrix)
    inverse = [[adjugate[i][j] / det for j in range(n)] for i in range(n)]
    return inverse, f"det(A) = {det}"


def inverse_by_gauss_jordan(matrix, verbose=False):
    n = len(matrix)
    aug = [list(matrix[i]) + [Fraction(1) if i == j else Fraction(0)
                              for j in range(n)] for i in range(n)]
 
    if verbose:
        print("\n  [초기 첨가행렬 A | I]")
        print_augmented(aug, n)
 
    for col in range(n):
        pivot_row = max(range(col, n), key=lambda r: abs(aug[r][col]))
 
        if aug[pivot_row][col] == 0:           
            return None, ("피벗이 0이므로 역행렬이 존재하지 않습니다. "
                          "(특이행렬 / singular matrix)")
 
        if pivot_row != col:
            aug[col], aug[pivot_row] = aug[pivot_row], aug[col]
            if verbose:
                print(f"\n  [{col + 1}단계] R{col + 1} <-> R{pivot_row + 1} "
                      f"(행 교환)")
        pivot = aug[col][col]
        aug[col] = [value / pivot for value in aug[col]]
        for row in range(n):
            if row != col and aug[row][col] != 0:
                factor = aug[row][col]
                aug[row] = [aug[row][k] - factor * aug[col][k]
                            for k in range(2 * n)]
 
        if verbose:
            print(f"\n  [{col + 1}단계] {col + 1}열 소거 완료")
            print_augmented(aug, n)
    inverse = [row[n:] for row in aug]
    return inverse, "가우스-조던 소거법 완료"
 
 
def print_augmented(aug, n, indent="    "):
    """첨가행렬 [ A | I ]를 구분선과 함께 출력한다."""
    text = []
    for row in aug:
        line = []
        for value in row:
            if value.denominator == 1:
                line.append(str(value.numerator))
            else:
                line.append(f"{value.numerator}/{value.denominator}")
        text.append(line)
 
    width = max(len(s) for line in text for s in line)
    for line in text:
        left = "  ".join(s.rjust(width) for s in line[:n])
        right = "  ".join(s.rjust(width) for s in line[n:])
        print(f"{indent}[ {left} | {right} ]")

  # ===========================================================
# [구성조건 4] 결과 출력 및 비교 기능
# ===========================================================
 
def matrices_equal(A, B):
    """두 행렬이 동일한지 비교한다. (Fraction이므로 오차 없이 정확 비교)"""
    if A is None or B is None:
        return A is B
    if len(A) != len(B):
        return False
    for i in range(len(A)):
        for j in range(len(A)):
            if A[i][j] != B[i][j]:
                return False
    return True
 
 
# ===========================================================
# [추가기능]
# ===========================================================
 
def multiply(A, B):
    """행렬 곱 A x B를 계산한다. (검증용)"""
    n = len(A)
    return [[sum(A[i][k] * B[k][j] for k in range(n)) for j in range(n)]
            for i in range(n)]
 
 
def is_identity(matrix):
    """주어진 행렬이 단위행렬인지 확인한다."""
    n = len(matrix)
    for i in range(n):
        for j in range(n):
            expected = Fraction(1) if i == j else Fraction(0)
            if matrix[i][j] != expected:
                return False
    return True
 
 
def verify_inverse(A, A_inv):
    """A x A^-1 = I 인지 실제로 곱해서 검증한다. (추가기능 1)"""
    product = multiply(A, A_inv)
    print("    A x A^-1 =")
    print_matrix(product, indent="    ")
    if is_identity(product):
        print("    => 단위행렬 I와 일치합니다. 역행렬이 정확합니다.")
    else:
        print("    => 단위행렬이 아닙니다. 계산에 오류가 있습니다.")
    return is_identity(product)
 
 
def random_matrix(n, low=-9, high=9):
    """테스트용 랜덤 정수 행렬을 생성한다. (추가기능 2)"""
    return [[Fraction(random.randint(low, high)) for _ in range(n)]
            for _ in range(n)]


# ===========================================================
#  메인 실행부
# ===========================================================
 
def run(matrix):
    print()
    print("입력한 행렬 A:")
    print_matrix(matrix)
    start = time.perf_counter()
    inv_det, msg_det = inverse_by_determinant(matrix)
    time_det = time.perf_counter() - start
 
    print("\n행렬식으로 구한 역행렬:")
    if inv_det is None:
        print(f"    [오류] {msg_det}")
    else:
        print_matrix(inv_det)
        print(f"    (det(A) = {determinant(matrix)})")

    start = time.perf_counter()
    inv_gj, msg_gj = inverse_by_gauss_jordan(matrix)
    time_gj = time.perf_counter() - start
 
    print("\n가우스-조던 소거법으로 구한 역행렬:")
    if inv_gj is None:
        print(f"    [오류] {msg_gj}")
    else:
        print_matrix(inv_gj)
 
    print()
    if inv_det is None and inv_gj is None:
        print("두 방법 모두 역행렬이 존재하지 않는다고 판정했습니다.")
        print("두 방법의 결과가 동일합니다.")
    elif matrices_equal(inv_det, inv_gj):
        print("두 방법의 결과가 동일합니다.")
    else:
        print("두 방법의 결과가 다릅니다.")
 
    # --- 추가기능 : 검증 및 성능 비교 ---
    if inv_det is not None:
        print("\n" + "-" * 50)
        print("[추가기능] A x A^-1 = I 검증")
        print("-" * 50)
        verify_inverse(matrix, inv_det)
# ===========================================================
#  메인 실행부
# ===========================================================
 
def main():
    while True:
        # [구성조건 1] 행렬 입력
        matrix = input_matrix()
 
        # [구성조건 2~4] 두 방법으로 계산하고 결과 비교
        run(matrix)
 
        # [추가기능] 가우스-조던 계산 과정 단계별 확인
        answer = input("\n가우스-조던 계산 과정을 단계별로 보시겠습니까? (y/n): ")
        if answer.strip().lower().startswith("y"):
            inverse_by_gauss_jordan(matrix, verbose=True)
 
        # 반복 실행
        answer = input("\n다른 행렬을 계산하시겠습니까? "
                       "(y: 직접 입력 / r: 랜덤 행렬 / n: 종료): ").strip().lower()
        if answer.startswith("r"):                # [추가기능] 랜덤 행렬 테스트
            try:
                n = int(input("차수 n: ").strip())
                run(random_matrix(n))
            except ValueError:
                print("[오류] 정수를 입력해주세요.")
            if not input("\n계속하시겠습니까? (y/n): ").strip().lower().startswith("y"):
                break
        elif not answer.startswith("y"):
            break
 
    print("\n프로그램을 종료합니다.")
 
 
if __name__ == "__main__":
    main()
