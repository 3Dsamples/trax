# coding=utf-8
# Copyright 2020 The Trax Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Core class and functions for handling data abstractly as shapes/dtypes."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy as onp
import tensorflow as tf


class ShapeDtype(object):
  """A NumPy ndarray-like object abstracted as shape and dtype."""
  __slots__ = ['shape', 'dtype']

  def __init__(self, shape, dtype=onp.float32):
    """Creates a `ShapeDtype` instance, with canonicalized `shape` and `dtype`.

    Args:
      shape: A tuple or list, each element of which is an int or, less often,
          `None`.
      dtype: A `dtype` object, either from NumPy or TensorFlow.

    Returns:
      A `ShapeDtype` instance whose `shape` is a tuple and `dtype` is a NumPy
      `dtype` object.
    """
    # Canonicalize shape and dtype.
    if isinstance(shape, list):
      shape = tuple(shape)
    if not isinstance(shape, tuple):
      raise TypeError('shape must be tuple or list; got: {}'.format(shape))
    if isinstance(dtype, tf.DType):
      dtype = dtype.as_numpy_dtype

    self.shape = shape
    self.dtype = dtype

  def __eq__(self, other):
    return (isinstance(other, self.__class__)
            and self.shape == other.shape
            and self.dtype == other.dtype)

  def __ne__(self, other):
    return not self == other

  def __repr__(self):
    return 'ShapeDtype{{shape:{}, dtype:{}}}'.format(self.shape, self.dtype)

  def as_tuple(self):
    return self.shape, self.dtype


def signature(obj):
  """Returns a `ShapeDtype` signature for the given `obj`.

  A signature is either a `ShapeDtype` instance or a tuple of `ShapeDtype`
  instances. Note that this function is permissive with respect to its inputs
  (accepts lists or tuples, and underlying objects can be any type as long as
  they have shape and dtype attributes), but strict with respect to its outputs
  (only `ShapeDtype`, and only tuples).

  Args:
    obj: An object that has `shape` and `dtype` attributes, or a list/tuple
        of such objects.

  Returns:
    A single `ShapeDtype` instance if the signature has one element, else a
    tuple of `ShapeDtype` instances.
  """
  if isinstance(obj, (list, tuple)):
    output = tuple(signature(x) for x in obj)
    return output[0] if len(output) == 1 else output
  else:
    return ShapeDtype(obj.shape, obj.dtype)


def splice_signatures(*sigs):
  """Creates a new signature by splicing together any number of signatures.

  The splicing effectively flattens the top level input signatures. For
  instance, it would perform the following mapping:
    - *sigs: sd1, (sd2, sd3, sd4), (), sd5
    - return: (sd1, sd2, sd3, sd4, sd5)

  Args:
    *sigs: Any number of signatures. A signature is either a `ShapeDtype`
        instance or a tuple of `ShapeDtype` instances.

  Returns:
    A single `ShapeDtype` instance if the spliced signature has one element,
    else a tuple of `ShapeDtype` instances.
  """
  result_sigs = []
  for sig in sigs:
    if isinstance(sig, (list, tuple)):
      result_sigs.extend(sig)
    else:
      result_sigs.append(sig)
  return result_sigs[0] if len(result_sigs) == 1 else tuple(result_sigs)


def assert_shape_equals(array, shape):
  """Asserts that an array has the given shape."""
  assert array.shape == shape, (
      'Invalid shape {}; expected {}.'.format(array.shape, shape)
  )
