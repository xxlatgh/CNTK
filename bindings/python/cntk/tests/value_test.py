# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE.md file in the project root
# for full license information.
# ==============================================================================

import pytest
import numpy as np
import scipy.sparse as sparse
import cntk as C

csr = sparse.csr_matrix

from ..core import *
from cntk.tests.test_utils import *
from cntk.ops.tests.ops_test_utils import compare_lists_of_np_arrays, cntk_device
from cntk import *
from cntk.internal import _value_as_sequence_or_array
from cntk import asarray, asvalue

test_numbers = [4., 5, 6., 7., 8.]
test_array = AA(test_numbers, dtype=np.float32)

def _dense_value_to_ndarray_test(data, num_of_dynamic_axes, expected_value_shape, expected_array_shapes):
    shape = (5,)

    if num_of_dynamic_axes == 2:
        var = sequence.input(shape)
    elif num_of_dynamic_axes == 1:
        var = input(shape)
    else:
        var = input(shape, dynamic_axes=[])

    # conversion array -> value
    val = asvalue(var, data)
    assert val.shape == expected_value_shape

    # conversion value -> array
    dense_result = _value_as_sequence_or_array(val, var)

    if isinstance(dense_result, list):
        result_shapes = [AA(v).shape for v in dense_result]
    else:
        result_shapes = dense_result.shape

    assert result_shapes == expected_array_shapes

def _sparse_value_to_csr_test(data, num_of_dynamic_axes, expected_value_shape, expected_csr_shapes):
    shape = (3,)

    if num_of_dynamic_axes == 2:
        var = sequence.input(shape, is_sparse=True)
    elif num_of_dynamic_axes == 1:
        var = input(shape, is_sparse=True)
    else:
        var = input(shape, is_sparse=True, dynamic_axes=[])

    # conversion csr array -> value
    val = asvalue(var, data)

    assert val.shape == expected_value_shape

    # conversion value -> csr array
    csr_result = val.as_sequences(var)

    csr_result_shapes = [v.shape for v in csr_result]

    assert csr_result_shapes == expected_csr_shapes

DENSE_CONFIGURATIONS = [
    # (dense data, num_of_dynamic_axes, expected_value_shape, expected_array_shapes)
    ([[test_array],
      [test_array, test_array]], 2, (2,2,5), [(1,5),(2,5)]),
    ([test_array,
      test_array], 2, (2, 1, 5), [(1,5), (1,5)]),
    ([[test_array],
      [test_array]], 2, (2, 1, 5), [(1,5), (1,5)]),
    (test_array, 2, (5,), [(), (), (), (), ()]),
    (AA([test_numbers], dtype=np.float32), 2, (1,5), [(5,)]),
    (AA([test_numbers, test_numbers], dtype=np.float32),
     2, (2, 5), [(5,), (5,)]),
    ([test_array,
      test_array], 1, (2,1,5), (2,1,5)),
    ([[test_array],
      [test_array]], 1, (2,1,5), (2,1,5)),
    (AA([test_numbers, test_numbers], dtype=np.float32), 1, (2,5), (2,5)),
    (AA([test_numbers], dtype=np.float32), 1, (1,5), (1,5)),
    ([test_array,
      test_array], 0, (2,5), (2,5)),
    (AA([test_numbers, test_numbers], dtype=np.float32), 0, (2,5), (2,5)),
    (test_array, 0, (5,), (5,)),
]

@pytest.mark.parametrize("data, num_of_dynamic_axes, expected_value_shape, expected_array_shapes", DENSE_CONFIGURATIONS)
def test_dense_value_to_ndarray(data, num_of_dynamic_axes, expected_value_shape, expected_array_shapes):
    _dense_value_to_ndarray_test(
        data, num_of_dynamic_axes, expected_value_shape, expected_array_shapes)

SPARSE_ARRAYS = [
    # (sparse data, num_of_dynamic_axes, expected_value_shape, expected_array_shapes)
    ([csr([[1.,0.,2.], [2.,3.,0.]]),
      csr([5.,0.,1.])], 2, (2, 2, 3), [(2,3),(1,3)]),
    ([csr([1,0,2]),
      csr([5,0,1])], 2, (2, 1, 3),[(1,3),(1,3)]),
    ([csr([[1,0,2],[2,3,4]])], 2, (1, 2, 3), [(2,3)]),
    ([csr([1,0,2]),
      csr([5,0,1])], 1, (2, 1, 3), [(1,3),(1,3)]),
    ([csr([[1,0,2], [2,3,0]]),
      csr([[5,0,1], [2,3,0]])], 1, (2, 2, 3), [(2,3),(2,3)]),
    ([csr([[1,0,2],[2,3,4]])], 1, (1, 2, 3), [(2,3)]),
    (csr([1,0,2]), 0, (1, 3), [(1,3)]),
]

@pytest.mark.parametrize("data, num_of_dynamic_axes, expected_value_shape, expected_csr_shapes", SPARSE_ARRAYS)
def test_sparse_value_to_csr(data, num_of_dynamic_axes, expected_value_shape, expected_csr_shapes):
    _sparse_value_to_csr_test(
        data, num_of_dynamic_axes, expected_value_shape, expected_csr_shapes)

DENSE_FAILING_CONFIGURATIONS = [
    # (dense data, num_of_dynamic_axes, expected_value_shape, expected_array_shapes)
    ([[test_array],
     [test_array, test_array]], 0, (2,2,5), [(1,5),(2,5)]),
    # TODO: enable once check is implemented
    #([[test_array],
    #  [test_array]], 0, (2, 1, 5), [(1, 5),(1, 5)]),
    #([[test_array],
    #  [test_array, test_array]], 1, (2,2,5), [(1,5),(2,5)]),
]

SPARSE_FAILING_CONFIGURATIONS = [
    # (sparse data, num_of_dynamic_axes, expected_value_shape, expected_array_shapes)
    # TODO: Following configurations are not meant to fail as expected
    #(csr([[1,0,2], [2,3,0]]), 2, (1, 3), [(1,3)]),
    #(csr([[1,0,2],[2,3,4]]), 2, (2, 1, 3), [(1,3),(1,3)]),
    #(csr([[1,0,2], [2,3,0]]), 1, (1, 3), [(1,3)]),
    ([csr([[1,0,2],[2,3,4]])], 0, (1, 2, 3), [(2,3)]),
    ([csr([[1,0,2], [2,3,0]]),
      csr([5,0,1])], 0, (2, 2, 3), [(2,3),(1,3)]),
    ([csr([1,0,2])], 0, (1, 3), [(1,3)]),
    # TODO: enable once check is implemented
    #([csr([[1,0,2], [2,3,0]]),
    #  csr([5,0,1])], 1, (2, 2, 3), [(2,3),(1,3)]),
]

@pytest.mark.parametrize("data, num_of_dynamic_axes, expected_value_shape, expected_array_shapes", DENSE_FAILING_CONFIGURATIONS)
def test_dense_failing_value_to_ndarray(data, num_of_dynamic_axes, expected_value_shape, expected_array_shapes):
    with pytest.raises(ValueError):
        _dense_value_to_ndarray_test(
            data, num_of_dynamic_axes, expected_value_shape, expected_array_shapes)

@pytest.mark.parametrize("data, num_of_dynamic_axes, expected_value_shape, expected_csr_shapes", SPARSE_FAILING_CONFIGURATIONS)
def test_sparse_failing_value_to_csr(data, num_of_dynamic_axes, expected_value_shape, expected_csr_shapes):
    with pytest.raises(ValueError):
        _sparse_value_to_csr_test(
            data, num_of_dynamic_axes, expected_value_shape, expected_csr_shapes)

def test_asarray_method():
    shape = (3,)

    var = sequence.input(shape, is_sparse=True)

    data = [csr([[1,0,2], [5,0,1]])]
    # conversion array -> value
    val = asvalue(var, data)
    as_csr = val.as_sequences(var)
    for a, d in zip(as_csr, data):
        assert (a==d).toarray().all()

    var = C.input(shape, is_sparse=True)

    data = csr([[1,0,2], [5,0,1]])
    # conversion array -> value
    val = asvalue(var, data)
    for v in [
            val, # Value
            super(Value, val), # cntk_py.Value
            val.data, # NDArrayView
            super(NDArrayView, val.data), # cntk_py.NDArrayView
            ]:
        as_csr = v.asarray()
        for a, d in zip(as_csr, data):
            assert (a==d).toarray().all()

def test_value_properties():
    ndav = NDArrayView((1, 2, 3), np.float32)
    val = Value(batch=ndav)

    dev = val.device
    assert isinstance(dev, DeviceDescriptor)
    assert str(dev) == 'CPU'

    assert val.is_read_only == False

    assert val.is_sparse == False

    assert val.dtype == np.float32


def test_ndarray_properties():
    ndav = NDArrayView((2, 3), np.float32)

    dev = ndav.device
    assert isinstance(dev, DeviceDescriptor)
    assert str(dev) == 'CPU'

    assert ndav.is_read_only == False

    assert ndav.is_sparse == False

    assert ndav.dtype == np.float32


def _to_dense(val):
    x = C.input(val.shape[1:], is_sparse=True)
    dense = C.times(x, C.constant(value=np.eye(val.shape[-1], dtype=np.float32)))
    return dense.eval({x : val}, device=val.device)

def test_ndarrayview_from_csr(device_id):
    dev = cntk_device(device_id)
    csr_data = csr(np.asarray([[0, 1, 1], [0, 1, 0], [1, 0, 0], [1, 0, 1]], dtype=np.float32))
    ndarrayview = NDArrayView.from_csr(csr_data, shape=(2, 2, 3))
    assert np.array_equal(_to_dense(ndarrayview), [[[0, 1, 1], [0, 1, 0]], [[1, 0, 0], [1, 0, 1]]])
    
    with pytest.raises(ValueError):
        ndarrayview = NDArrayView.from_csr(csr_data, shape=(3, 2, 3))

    with pytest.raises(ValueError):
        ndarrayview = NDArrayView.from_csr(csr_data, shape=(2, 2, 4))
 

def test_2d_sparse_sequences_value(device_id):
    dev = cntk_device(device_id)
    csr_seq1 = csr(np.asarray([[0, 1, 1], [0, 1, 0], [1, 0, 0], [1, 0, 1]], dtype=np.float32))
    ndarrayview1 = NDArrayView.from_csr(csr_seq1, shape=(2, 2, 3), device=cpu())
    csr_seq2 = csr(np.asarray([[0, 1, 1], [1, 1, 0]], dtype=np.float32))
    ndarrayview2 = NDArrayView.from_csr(csr_seq2, shape=(1, 2, 3), device=cpu())

    x = sequence.input((2, 3))
    sequence_value = Value.create(x, [ndarrayview1, ndarrayview2], device=dev)
    assert np.array_equal(_to_dense(sequence_value.data), [[[[0, 1, 1], [0, 1, 0]], [[1, 0, 0], [1, 0, 1]]], [[[0, 1, 1], [1, 1, 0]], [[0, 0, 0], [0, 0, 0]]]])
