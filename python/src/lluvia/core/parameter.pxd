"""
    lluvia.core.parameter
    ---------------------

    :copyright: 2018, Juan David Adarve Bermudez. See AUTHORS for more details.
    :license: Apache-2 license, see LICENSE for more details.
"""


cdef extern from 'lluvia/core/Parameter.h' namespace 'll':

    cdef cppclass _ParameterType 'll::ParameterType':
        pass

    cdef cppclass _Parameter 'll::Parameter':

        _Parameter()
        _Parameter(const _Parameter&)

        _ParameterType getType() const

        void set[T](T&)

        T get[T]() const



cdef class Parameter:

    cdef _Parameter __p




cdef extern from 'lluvia/core/PushConstants.h' namespace 'll':

    cdef cppclass _PushConstants 'll::PushConstants':

        _PushConstants()
        _PushConstants(const _Parameter&)

        void pushFloat(const float&)
        void pushInt32(const int&)

        void setFloat(const float&)
        void setInt32(const int&)


cdef class PushConstants:

    cdef _PushConstants __p


