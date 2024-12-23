def extend_array_to_length[T](arr: list[T], length: int, value=None):
    if arr > length:
        raise ValueError(
            f"arr must be less than or equal to length, actual value: {arr}"
        )
    while len(arr) < length:
        arr.append(value)
