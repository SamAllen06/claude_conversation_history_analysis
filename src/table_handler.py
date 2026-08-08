class MultiDimTable():
    dimensions: list[Dimension] = []
    data: list = []

    def __init__(self, dimensions_dict: dict[str: list[str]]):

        self.dimensions = self._create_dimensions(dimensions_dict)
        self.data = self._initialize_data(self.dimensions, 0)


    def _create_dimensions(self, dimensions_dict: dict[str: list[str]]) -> list[Dimension]:
        dimensions = []
        for item in dimensions_dict:
            dimensions.append(Dimension(item, dimensions_dict[item]))
        return dimensions


    def _initialize_data(self, dimensions: list[Dimension], index: int) -> list:
        if index == len(dimensions)-1:
            new_row = []
            for _ in range(dimensions[index].length):
                new_row.append(None)
            return new_row
        else:
            new_row = []
            for _ in range(dimensions[index].length):
                row = self._initialize_data(dimensions, index+1)
                new_row.append(row)
            return new_row


class Dimension():
    name: str = ""
    coords: list[str] = []
    length: int = -1

    def __init__(self, name: str, coords: list[str]):
        self.name = name
        self.coords = coords
        self.length = len(coords)
