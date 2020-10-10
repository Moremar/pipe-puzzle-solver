from point import Point

SAMPLES = {
    "4": {
        "size": 4,
        "pipes": [
            (Point(0, 0), Point(3, 1)),
            (Point(1, 1), Point(3, 0)),
            (Point(0, 3), Point(3, 2)),
        ]
    },
    "6": {
        "size": 6,
        "pipes": [
            (Point(0, 0), Point(2, 0)),
            (Point(0, 1), Point(1, 3)),
            (Point(0, 5), Point(4, 2)),
            (Point(1, 2), Point(4, 1)),
            (Point(1, 5), Point(3, 3)),
            (Point(3, 0), Point(4, 4)),
            (Point(4, 5), Point(5, 4)),
        ]
    },
    "10": {
        "size": 10,
        "pipes": [
            (Point(0, 0), Point(2, 3)),
            (Point(0, 1), Point(4, 9)),
            (Point(1, 1), Point(6, 9)),
            (Point(2, 7), Point(4, 1)),
            (Point(3, 0), Point(5, 6)),
            (Point(3, 7), Point(4, 2)),
            (Point(4, 6), Point(5, 7)),
            (Point(6, 8), Point(9, 8)),
            (Point(7, 9), Point(8, 1)),
            (Point(8, 2), Point(9, 9)),
        ]
    },
    "11": {
        "size": 11,
        "pipes": [
            (Point(0, 0), Point(8, 3)),
            (Point(0, 1), Point(3, 9)),
            (Point(0, 10), Point(2, 9)),
            (Point(1, 1), Point(8, 10)),
            (Point(1, 5), Point(6, 9)),
            (Point(1, 6), Point(7, 10)),
            (Point(1, 7), Point(1, 10)),
            (Point(3, 0), Point(9, 7)),
            (Point(3, 2), Point(9, 1)),
            (Point(4, 2), Point(9, 9)),
            (Point(9, 10), Point(10, 6)),
        ]
    },
    "12": {
        "size": 12,
        "pipes": [
            (Point(0, 10), Point(5, 1)),
            (Point(0, 11), Point(7, 10)),
            (Point(1, 1), Point(6, 10)),
            (Point(2, 1), Point(6, 4)),
            (Point(2, 9), Point(5, 3)),
            (Point(3, 4), Point(7, 0)),
            (Point(3, 8), Point(11, 11)),
            (Point(3, 9), Point(10, 11)),
            (Point(4, 0), Point(7, 4)),
            (Point(5, 4), Point(8, 6)),
            (Point(5, 5), Point(8, 3)),
            (Point(9, 0), Point(10, 9)),
            (Point(10, 0), Point(11, 9)),
        ]
    },
    "13": {
        "size": 13,
        "pipes": [
            (Point(0, 11), Point(6, 12)),
            (Point(2, 7), Point(12, 12)),
            (Point(10, 7), Point(12, 0)),
            (Point(11, 10), Point(12, 1)),
            (Point(1, 0), Point(8, 4)),
            (Point(1, 11), Point(2, 8)),
            (Point(8, 5), Point(10, 8)),
            (Point(4, 0), Point(10, 2)),
            (Point(0, 2), Point(4, 10)),
            (Point(1, 2), Point(7, 6)),
            (Point(5, 10), Point(6, 3)),
            (Point(8, 11), Point(12, 5)),
            (Point(0, 0), Point(2, 1)),
            (Point(2, 4), Point(2, 6)),
            (Point(2, 5), Point(5, 5)),
            (Point(9, 1), Point(9, 9)),
        ]
    },
    "13-2": {
        "size": 13,
        "pipes": [
            (Point(0, 6), Point(4, 0)),
            (Point(0, 7), Point(0, 12)),
            (Point(1, 8), Point(8, 12)),
            (Point(2, 2), Point(4, 1)),
            (Point(3, 1), Point(3, 10)),
            (Point(3, 4), Point(12, 3)),
            (Point(3, 5), Point(10, 7)),
            (Point(3, 9), Point(8, 11)),
            (Point(4, 6), Point(7, 8)),
            (Point(5, 2), Point(7, 2)),
            (Point(5, 3), Point(5, 10)),
            (Point(6, 3), Point(11, 1)),
            (Point(7, 7), Point(9, 12)),
            (Point(7, 9), Point(12, 4)),
            (Point(9, 5), Point(11, 4)),
            (Point(9, 11), Point(11, 11)),
        ]
    },
    "13-3": {
        "size": 13,
        "pipes": [
            (Point(0, 6), Point(5, 1)),
            (Point(0, 7), Point(2, 10)),
            (Point(0, 11), Point(1, 9)),
            (Point(0, 12), Point(5, 8)),
            (Point(1, 1), Point(1, 8)),
            (Point(2, 1), Point(7, 10)),
            (Point(2, 8), Point(4, 11)),
            (Point(4, 1), Point(6, 2)),
            (Point(4, 4), Point(10, 0)),
            (Point(4, 5), Point(8, 5)),
            (Point(6, 8), Point(12, 10)),
            (Point(7, 0), Point(8, 9)),
            (Point(7, 11), Point(12, 1)),
            (Point(8, 10), Point(10, 1)),
            (Point(10, 2), Point(10, 10)),
            (Point(11, 8), Point(12, 0)),
        ]
    },
    "14": {
        "size": 14,
        "pipes": [
            (Point(0, 0), Point(3, 1)),
            (Point(0, 3), Point(8, 0)),
            (Point(0, 13), Point(9, 10)),
            (Point(1, 0), Point(5, 0)),
            (Point(1, 3), Point(4, 3)),
            (Point(1, 5), Point(11, 11)),
            (Point(4, 7), Point(10, 6)),
            (Point(4, 8), Point(8, 5)),
            (Point(5, 6), Point(7, 9)),
            (Point(6, 2), Point(12, 11)),
            (Point(6, 4), Point(13, 4)),
            (Point(7, 7), Point(8, 2)),
            (Point(9, 3), Point(11, 4)),
            (Point(9, 4), Point(11, 2)),
            (Point(9, 6), Point(11, 9)),
            (Point(9, 8), Point(11, 7)),
        ]
    },
}


class Samples:
    @staticmethod
    def get_puzzle(name: str):
        if name in SAMPLES:
            sample = SAMPLES[name]
            return sample["size"], sample["pipes"]
        else:
            raise Exception("No puzzle called " + name)
