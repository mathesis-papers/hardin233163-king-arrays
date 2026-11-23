"""Exact finite checks for normalized eight-colour king arrays."""

from collections import Counter, defaultdict
from fractions import Fraction
from itertools import product
import hashlib
import json


def pair(colour):
    return min(colour, 7 - colour)


def polynomial_value(coefficients, value):
    total = 0
    for coefficient in coefficients:
        total = total * value + coefficient
    return total


def scan(colours, mask=0):
    for colour in colours:
        if colour in (2, 3, 4, 5, 6) and not mask & 1:
            return None
        if colour in (3, 4, 5) and not mask & 2:
            return None
        if colour == 4 and not mask & 4:
            return None
        if colour in (1, 2, 3):
            mask |= 1 << (colour - 1)
    return mask


def row_legal(row):
    return all(left != right and left + right != 7
               for left, right in zip(row, row[1:]))


def compatible(upper, lower):
    width = len(upper)
    return all(upper[column] != lower[other]
               and upper[column] + lower[other] != 7
               for column in range(width)
               for other in range(max(0, column - 1), min(width, column + 2)))


def literal_counts(width, height):
    rows = [row for row in product(range(8), repeat=width) if row_legal(row)]
    followers = {row: [other for other in rows if compatible(row, other)]
                 for row in rows}
    states = Counter({(row, scan(row)): 1 for row in rows
                      if row[0] == 0 and scan(row) is not None})
    counts = [sum(states.values())]
    for _ in range(1, height):
        following = defaultdict(int)
        for (row, mask), multiplicity in states.items():
            for other in followers[row]:
                updated = scan(other, mask)
                if updated is not None:
                    following[(other, updated)] += multiplicity
        states = following
        counts.append(sum(states.values()))
    return counts


def rectangle_formula(height, width):
    return 2 ** (height * width - 4) * (2 ** (height - 2) + 2 ** (width - 2) - 1)


def stirling(total, blocks):
    values = [0] * (blocks + 1)
    values[0] = 1
    for _ in range(total):
        values = [0] + [index * values[index] + values[index - 1]
                        for index in range(1, blocks + 1)]
    return values[blocks]


def path_formula(length):
    return sum(2 ** (length - blocks) * stirling(length - 1, blocks - 1)
               for blocks in range(1, min(4, length) + 1))


def canonical_pair_counts(height, width, canonical=True):
    colours = []
    counts = Counter()

    def extend(maximum):
        position = len(colours)
        if position == height * width:
            counts[maximum + 1] += 1
            return
        row, column = divmod(position, width)
        forbidden = set()
        if column:
            forbidden.add(colours[-1])
        if row:
            for other in range(max(0, column - 1), min(width, column + 2)):
                forbidden.add(colours[(row - 1) * width + other])
        available = range(min(3, maximum + 1) + 1) if canonical else range(4)
        for colour in available:
            if colour not in forbidden:
                colours.append(colour)
                extend(max(maximum, colour))
                colours.pop()

    extend(-1)
    return counts


def main():
    first_rows = [row for row in product(range(8), repeat=3)
                  if row[0] == 0 and row_legal(row) and scan(row) is not None]
    assert first_rows == [(0, 1, 0), (0, 1, 2), (0, 1, 7)]
    seeds = []
    seed_types = Counter()
    for upper in first_rows:
        for lower in product(range(8), repeat=3):
            if row_legal(lower) and compatible(upper, lower):
                mask = scan(lower, scan(upper))
                if mask is not None:
                    assert mask == 7
                    kind = 'ABA' if pair(lower[0]) == pair(lower[2]) else 'ABC'
                    seed_types[kind] += 1
                    seeds.append([''.join(map(str, upper)), ''.join(map(str, lower)), kind])
    assert seed_types == {'ABA': 4, 'ABC': 4}
    boundary_counts = Counter()
    for boundary in product(range(4), repeat=3):
        if boundary[0] == boundary[1] or boundary[1] == boundary[2]:
            continue
        kind = 'ABA' if boundary[0] == boundary[2] else 'ABC'
        followers = []
        for row in product(range(8), repeat=3):
            if row_legal(row) and all(boundary[column] != pair(row[other])
                    for column in range(3)
                    for other in range(max(0, column - 1), min(3, column + 2))):
                followers.append(row)
                assert ('ABA' if pair(row[0]) == pair(row[2]) else 'ABC') == kind
        assert len(followers) == (16 if kind == 'ABA' else 8)
        boundary_counts[kind] += 1
    assert boundary_counts == {'ABA': 12, 'ABC': 24}

    literal = {}
    for width in (1, 2, 3):
        counts = literal_counts(width, 12)
        for height, count in enumerate(counts, start=1):
            expected = path_formula(max(height, width)) if min(height, width) == 1 \
                else rectangle_formula(height, width)
            assert count == expected, (height, width, count, expected)
        literal[str(width)] = {
            'first_six_counts': counts[:6],
            'all_counts_sha256': hashlib.sha256(json.dumps(counts).encode()).hexdigest(),
        }

    rectangle_checks = 0
    for height in range(2, 7):
        for width in range(2, 7):
            counts = canonical_pair_counts(height, width)
            assert counts == {4: 2 ** (height - 2) + 2 ** (width - 2) - 1}
            named = canonical_pair_counts(height, width, canonical=False)
            assert named == {4: 24 * sum(counts.values())}
            assert rectangle_formula(height, width) == rectangle_formula(width, height)
            rectangle_checks += 1
    for length in range(1, 13):
        counts = canonical_pair_counts(1, length)
        assert all(counts.get(blocks, 0) == stirling(length - 1, blocks - 1)
                   for blocks in range(1, 5))
        if length >= 2:
            assert path_formula(length) == (Fraction(5 * 2 ** length, 32)
                    + Fraction(4 ** length, 64) + Fraction(6 ** length, 288))

    coefficients = [0, 3] + [rectangle_formula(height, 3) for height in range(2, 211)]
    for height in range(1, 211):
        value = coefficients[height]
        if height >= 1:
            value -= 24 * coefficients[height - 1]
        if height >= 2:
            value += 128 * coefficients[height - 2]
        assert value == {1: 3, 2: -64, 3: 288}.get(height, 0)
    for width in range(3, 8):
        for height in range(4, 31):
            assert rectangle_formula(height, width) == (
                3 * 2 ** width * rectangle_formula(height - 1, width)
                - 2 ** (2 * width + 1) * rectangle_formula(height - 2, width))
    for length in range(5, 31):
        assert path_formula(length) == (12 * path_formula(length - 1)
                - 44 * path_formula(length - 2) + 48 * path_formula(length - 3))
    path_coefficients = [0] + [path_formula(length) for length in range(1, 211)]
    for length in range(1, 211):
        coefficient = sum(multiplier * path_coefficients[length - offset]
                          for offset, multiplier in enumerate([1, -12, 44, -48])
                          if length >= offset)
        assert coefficient == {1: 1, 2: -11, 3: 35, 4: -29}.get(length, 0)
        if length >= 2:
            assert path_coefficients[length] == Fraction(
                2 ** length * (90 + 9 * 2 ** length + 2 * 3 ** length), 576)

    source_numerators = {
        3: [3, -64, 288],
        4: [11, -464, 3840],
        5: [48, -4096, 67584],
        6: [236, -41216, 1425408],
        7: [1248, -446464, 32636928],
    }
    source_closed_forms = {
        3: lambda height: 8 ** (height - 2) * (2 ** height + 4),
        4: lambda height: 4 ** (2 * height - 3) * (2 ** height + 12),
        5: lambda height: 2 ** (5 * height - 6) * (2 ** height + 28),
        6: lambda height: 64 ** (height - 1) * (2 ** height + 60),
        7: lambda height: 2 ** (7 * height - 6) * (2 ** height + 124),
    }
    for width in range(3, 8):
        coefficients = [0, path_formula(width)] + [
            rectangle_formula(height, width) for height in range(2, 211)]
        for height in range(1, 211):
            coefficient = coefficients[height] - 3 * 2 ** width * coefficients[height - 1]
            if height >= 2:
                coefficient += 2 ** (2 * width + 1) * coefficients[height - 2]
                assert coefficients[height] == source_closed_forms[width](height)
            expected = source_numerators[width][height - 1] if height <= 3 else 0
            assert coefficient == expected, (height, width, coefficient, expected)
    for width in range(2, 13):
        for height in range(2, 31):
            geometric_coefficient = (Fraction(2 ** ((width + 1) * height), 64)
                + Fraction((2 ** (width - 2) - 1) * 2 ** (width * height), 16))
            assert geometric_coefficient == rectangle_formula(height, width)
    for size in range(2, 31):
        assert rectangle_formula(size, size) == 2 ** (size * size - 4) * (2 ** (size - 1) - 1)
    for width, numerator in [(2, [24]), (3, [48, -72]), (4, [96, -168])]:
        denominator = [1, -2] if width == 2 else [1, -3, 2]
        counts = [24 * (2 ** length + 2 ** (width - 2) - 1)
                  for length in range(209)]
        for length in range(209):
            coefficient = sum(multiplier * counts[length - offset]
                              for offset, multiplier in enumerate(denominator)
                              if length >= offset)
            assert coefficient == (numerator[length] if length < len(numerator) else 0)
    assert polynomial_value([-1, 13, -68, 171, -176], 4) == -4
    assert polynomial_value([2, -33, 219, -729, 1214, -803], 4) == 5
    assert polynomial_value([1, -17, 118, -420, 770, -586], 4) == -2
    assert -polynomial_value([2, -21, 78, -113, 47], 4) == -11
    assert -polynomial_value([1, -14, 77, -204, 245, -91], 4) == 7

    report = {
        'arithmetic': 'exact integers and rational numbers; no floating point',
        'first_rows': [''.join(map(str, row)) for row in first_rows],
        'two_row_seeds': seeds,
        'seed_types': dict(seed_types),
        'proper_pair_boundaries': dict(boundary_counts),
        'boundary_rows_tested': 36 * 512,
        'literal_eight_colour_counts': {'heights': [1, 12], 'by_width': literal},
        'canonical_four_pair_rectangles': {'heights': [2, 6], 'widths': [2, 6],
                                          'rectangles': rectangle_checks},
        'canonical_pair_paths': {'lengths': [1, 12]},
        'named_four_colour_rectangles': {'heights': [2, 6], 'widths': [2, 6],
                                         'rectangles': rectangle_checks},
        'barker_series': {'widths': [3, 7], 'coefficient_degrees': [0, 210],
                          'numerators_after_one_factor_of_x': source_numerators},
        'barker_closed_forms': {'widths': [3, 7], 'heights': [2, 210]},
        'general_series_geometric_coefficients': {'widths': [2, 12], 'heights': [2, 30]},
        'square_formula': {'sizes': [2, 30]},
        'barker_path_generating_series': {'coefficient_degrees': [0, 210]},
        'barker_path_closed_form': {'lengths': [2, 210]},
        'chang_shrock_four_colour_series': {'widths': [2, 3, 4],
                                            'coefficient_degrees': [0, 208]},
        'chang_shrock_width_four_polynomials_at_four': {
            'denominator_coefficients': [1, -4, 5, -2, 0],
            'numerator_coefficients_divided_by_24': [4, -11, 7, 0]},
        'three_column_generating_series_coefficients': [0, 210],
        'rectangle_recurrences': {'widths': [3, 7], 'heights': [4, 30]},
        'path_recurrence': {'lengths': [5, 30]},
        'scope': 'The computations check finite instances. The note proves the '
                 'rectangle and path formulas for every stated size.',
        'status': 'all assertions passed',
    }
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
