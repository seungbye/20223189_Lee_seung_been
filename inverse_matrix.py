from fractions import Fraction


# ===========================================================
# [구성조건 1] 행렬 입력 기능
# ===========================================================

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


def print_matrix(matrix, indent="    "):
    if not matrix:
        print(indent + "(빈 행렬)")
        return

    text = []
    for row in matrix:
        line = []
        for value in row:
            if value.denominator == 1:
                line.append(str(value.numerator))
            else:
                line.append(f"{value.numerator}/{value.denominator}")
        text.append(line)

    width = max(len(s) for line in text for s in line)
    for line in text:
        print(indent + "[ " + "  ".join(s.rjust(width) for s in line) + " ]")


# ===========================================================
# [구성조건 2] 행렬식을 이용한 역행렬 계산 기능
# ===========================================================

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
        return None, "행렬식이 0이므로 역행렬이 존재하지 않습니다. (det = 0)"

    adjugate = transpose(cofactor_matrix(matrix))
    n = len(matrix)
    inverse = [[adjugate[i][j] / det for j in range(n)] for i in range(n)]
    return inverse, f"det(A) = {det}"


# ===========================================================
# [구성조건 3] 가우스-조던 소거법을 이용한 역행렬 계산 기능
# ===========================================================

def inverse_by_gauss_jordan(matrix):
    n = len(matrix)

    aug = [list(matrix[i]) + [Fraction(1) if i == j else Fraction(0)
                              for j in range(n)] for i in range(n)]

    for col in range(n):
        pivot_row = max(range(col, n), key=lambda r: abs(aug[r][col]))

        if aug[pivot_row][col] == 0:
            return None, ("피벗이 0이므로 역행렬이 존재하지 않습니다. "
                          "(특이행렬 / singular matrix)")

        if pivot_row != col:
            aug[col], aug[pivot_row] = aug[pivot_row], aug[col]

        pivot = aug[col][col]
        aug[col] = [value / pivot for value in aug[col]]

        for row in range(n):
            if row != col and aug[row][col] != 0:
                factor = aug[row][col]
                aug[row] = [aug[row][k] - factor * aug[col][k]
                            for k in range(2 * n)]

    inverse = [row[n:] for row in aug]
    return inverse, "가우스-조던 소거법 완료"


# ===========================================================
# [구성조건 4] 결과 출력 및 비교 기능
# ===========================================================

def matrices_equal(A, B):
    if A is None or B is None:
        return A is B
    if len(A) != len(B):
        return False
    for i in range(len(A)):
        for j in range(len(A)):
            if A[i][j] != B[i][j]:
                return False
    return True


def multiply(A, B):
    n = len(A)
    return [[sum(A[i][k] * B[k][j] for k in range(n)) for j in range(n)]
            for i in range(n)]


def is_identity(matrix):
    n = len(matrix)
    for i in range(n):
        for j in range(n):
            expected = Fraction(1) if i == j else Fraction(0)
            if matrix[i][j] != expected:
                return False
    return True


def verify_inverse(A, A_inv):
    product = multiply(A, A_inv)
    print("    A x A^-1 =")
    print_matrix(product, indent="    ")
    if is_identity(product):
        print("    => 단위행렬 I와 일치합니다. 역행렬이 정확합니다.")
    else:
        print("    => 단위행렬이 아닙니다. 계산에 오류가 있습니다.")
    return is_identity(product)


def run(matrix):
    print()
    print("입력한 행렬 A:")
    print_matrix(matrix)

    inv_det, msg_det = inverse_by_determinant(matrix)

    print("\n행렬식으로 구한 역행렬:")
    if inv_det is None:
        print(f"    [오류] {msg_det}")
    else:
        print_matrix(inv_det)
        print(f"    ({msg_det})")

    inv_gj, msg_gj = inverse_by_gauss_jordan(matrix)

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

    if inv_det is not None:
        print("\n" + "-" * 50)
        print("[추가기능] A x A^-1 = I 검증")
        print("-" * 50)
        verify_inverse(matrix, inv_det)


def main():
    while True:
        # [구성조건 1] 행렬 입력
        matrix = input_matrix()

        # [구성조건 2~4] 두 방법으로 계산하고 결과 비교
        run(matrix)

        answer = input("\n다른 행렬을 계산하시겠습니까? (y/n): ").strip().lower()
        if not answer.startswith("y"):
            break

    print("\n프로그램을 종료합니다.")


if __name__ == "__main__":
    main()
