import numbers
from typing import List


class Line:
    """
    Class for a Line object, which contains two points x1, x2.
    :param x1: The leftmost point of the line
    :param x2: The rightmost point of the line
    """

    def __init__(self, x1: numbers.Number, x2: numbers.Number):
        """
        Creates a line from point x1 to point x2.

        We make sure that x1 always contains the lowest x_val for the line. This gives us more flexibility on class
        creation, since Line(1, 5) and Line(5, 1) will be both valid, and represent the same line.
        :param x1: first point of the line
        :param x2: second point of the line
        """
        if not isinstance(x1, numbers.Number) or not isinstance(x2, numbers.Number):
            raise RuntimeError("Line created using non-numbers")

        if x1 < x2:
            self.x1 = x1
            self.x2 = x2
        elif x2 < x1:
            self.x1 = x2
            self.x2 = x1
        else:
            raise RuntimeError("Line ({}, {}) is not a line, but a point.".format(x1, x2))

    def __lt__(self, other: 'Line') -> bool:
        """
        Used to compare two lines which is the smallest. We're taking into comparison only the leftmost point of each
        line.
        :param other: other Line to compare to this one.
        :return: True if this line is smaller, False if the other line is smaller
        """
        return self.x1 < other.x1


def two_lines_overlap(line1: Line, line2: Line):
    """
    Checks whether two lines overlap, this is done in O(1) time and using O(1) space. This function is the most
    efficient for the base case of checking whether two lines overlap
    :param line1: First line to check whether they overlap or not
    :param line2: Second line to check whether they overlap or not
    :return: Whether the lines overlap or not.
    """
    left = max(line1.x1, line2.x1)
    right = min(line1.x2, line2.x2)
    return left <= right


def lines_overlap(*lines: Line) -> bool:
    """
    This functions takes care of the case when there's N Lines to check whether they overlap. This function can also be
    extended to also return the merged lines, or where they overlap, because at each step, we know whether there have
    been an overlap or not, the basic functionality for checking whether they overlap is just to return True on the
    first overlap found.

    Checks whether lines overlaps or not. Supplied parameters must be of the type Line.
    It creates a list with the lines, perform a sort, and then checks whether the end of the first line (with the
    earliest beginning) is after the start of the second line, we can assure if the lines overlap or not. Since it's
    sorted by the earliest beginning of the line, we can repeat this comparison for the other n elements of the list.

    This function takes O(n log n) time and O(n) space.
    :param lines: Lines to check whether they overlap
    :return: True if the lines overlap, False if they do not.
    """
    sorted_lines = sorted([line for line in lines])
    for i in range(len(sorted_lines)):
        try:
            if sorted_lines[i].x2 >= sorted_lines[i + 1].x1:
                return True
        except IndexError:
            return False
