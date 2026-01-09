import numpy as np


def get_max_size_along_first_or_last_dimension(
    shape: tuple[int], byte_per_dtype_instance: int, max_byte_per_chunk: int, dim: int
):
    if len(shape) > 0 and all(dim_extent > 0 for dim_extent in shape):
        prod = 1
        if dim == 0:
            for idx in range(1, len(shape)):
                prod *= shape[idx]
        elif dim == -1:
            for idx in range(0, len(shape) - 1):
                prod *= shape[idx]
        else:
            return 0
        # TODO, testing
        return max_byte_per_chunk / (prod * byte_per_dtype_instance)
    return 0


def chunk_axes_with_different_priority(
    data: np.ndarray,
    priority: tuple[int, ...],
    byte_per_item: int,
) -> tuple[int, ...] | bool:
    """Define an explicit tuple[int] how to chunk data with shape

    Parameter:
    * data, a numpy array
    * priority, a tuple[int] of axis dimension indices, sorted in ascending
    order of how conservative axis should be splitted or not.
    values in priority need to be range(0, len(shape)) but order may
    differ.

    Examples, a stack of 100,000 x 1024 x 1024 2D images 4B int, chunking
    should keep dim 1 and 2 as is, and chunk only on dim 0, if we
    know that users which to read images completely than slicing in
    other (orthogonal directions),

    Examples, reconstruction in atom probe 1,000,000 x 3 8B floats,
    users are usually more in need to getting position triplets
    for contiguous blocks of triplets rather than reading fast a
    single column, hence dim 0 should be chunked with higher
    priority than dim 1

    h5py guess_chunk e.g., https://github.com/h5py/h5py/blob/
    706755340058c8e8000ed769d4f5ad3571e4dfce/h5py/_hl/filters.py#L361
    splits alternatingly across all dims therefore shrinking
    ndarrays to roughly proportionally shrunk chunk_shape which in cases
    like above mention can easily cause that even a single 1024 x 1024
    image will be distributed across dozens of chunk_shape, mind that
    guess_chunk is a heuristic that should apply to general cases,
    it must not be understood as the solution to go with if the
    usage pattern of an array is well-known and specific more frequently
    used read-out patterns requested. Currently, guess_chunk offers
    a compromise for slicing about equally all three orthogonal
    directions

    Returns
    * tuple[int], explicit chunk sizes to use for create_dataset(chunk_shape=)
    * True, replying on h5py guess_chunk auto-chunking via chunk_shape=True."""
    if not isinstance(data, np.ndarray):  # only np.ndarray supported
        return True
    shape: tuple[int, ...] = np.shape(data)
    if any(extent == 0 for extent in shape):  # unlimited axis not supported
        return True
    if set(priority) != set(range(len(priority))):  # all dim indices need to be present
        return True
    if len(shape) == 0:
        raise ValueError("chunk_shape not allowed for scalar datasets.")
    chunk_shape: list[float] = list(float(extent) for extent in shape)
    max_byte_per_chunk: int = 4 * 1024 * 1024  # TODO, 4 MiB
    # byte_per_item: int = data.itemsize

    dim = 0
    idx = 0
    while True:
        idx += 1
        byte_per_chunk = np.prod(chunk_shape) * byte_per_item
        print(f"{idx}, {dim}, {chunk_shape}, {byte_per_chunk}")
        if byte_per_chunk < max_byte_per_chunk:
            break
        if chunk_shape[dim] % 2 == 0:
            chunk_shape[dim] = chunk_shape[dim] / 2
        else:
            chunk_shape[dim] = (chunk_shape[dim] / 2) + 1

        if dim < (len(shape) - 1):
            if chunk_shape[dim] < 2:
                dim += 1
                # seems we cannot reduce byte_per_chunk further by splitting
                # along dim, so unfortunately need to consider splitting across
                # the next, less prioritized axis
        else:
            return True
    if all(int(extent) >= 1 for extent in chunk_shape):
        return tuple(int(extent) for extent in chunk_shape)
    return True


# retval = chunk_axes_with_different_priority((100000, 2048, 2048), (0, 1, 2), 8)
# print(retval)
# retval = chunk_axes_with_different_priority((1000000, 3), (0, 1), 4)
# print(retval)
# retval = chunk_axes_with_different_priority((60, 60, 180), (2, 1, 0), 4)
# print(retval)
# retval = chunk_axes_with_different_priority((1, 1, 1), (0, 1, 2), 4)
# print(retval)
