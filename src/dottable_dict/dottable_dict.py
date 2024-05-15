from collections.abc import Mapping
from typing import Any, NewType, Sequence

FrozenState = NewType("FrozenState", tuple[tuple[Any, Any], ...])


class DottableDict:
    class _MergedValues(list):
        pass

    __data__: dict
    __autoconvert__: bool

    @staticmethod
    def __convert_sequence__(seq: Sequence):
        seq_type: type = type(seq)
        converted = []
        if "join" in dir(seq):
            return seq
        for i in seq:
            if isinstance(i, Sequence):
                converted.append(DottableDict.__convert_sequence__(i))
            else:
                try:
                    converted.append(DottableDict(i))
                except:
                    converted.append(i)
        return seq_type(converted)

    def __init__(self, data: Any = None, autoconvert_dicts: bool = True):
        self.__autoconvert__ = autoconvert_dicts
        data = {} if data is None else data
        if isinstance(data, DottableDict):
            self.__data__ = data.__data__.copy()
        else:
            try:
                data = dict(data)
            except Exception as e:
                e.args = (f"cannot convert input to dict: {data}",)
                raise (e)
            self.__data__ = {}
            for k, v in data.items():
                if self.__autoconvert__:
                    if not v:
                        val = v
                    elif isinstance(v, Sequence):
                        val = DottableDict.__convert_sequence__(v)
                    else:
                        try:
                            val = DottableDict(v)
                        except:
                            val = v
                self.__data__[k] = val

    def __getattr__(self, key: str) -> Any:
        if not (key in self.__data__ or key in dir(self)):
            return self.__data__.__getattribute__(key)
        if key.isidentifier():
            return self.__data__[key]
        else:
            return getattr(self, key)

    def __setattr__(self, key, value) -> None:
        if key.startswith("__"):
            super().__setattr__(key, value)
        else:
            self.__data__[key] = (
                DottableDict(value)
                if self.__autoconvert__ and isinstance(value, dict)
                else value
            )

    def __getitem__(self, key) -> Any:
        return self.__data__[key]

    def __setitem__(self, key, value) -> None:
        if key in dir(self) or key in dir(self.__data__):
            raise IndexError
        self.__data__[key] = (
            DottableDict(value)
            if self.__autoconvert__ and isinstance(value, dict)
            else value
        )

    def __str__(self):
        return f"<{self.__class__.__name__} {self.simple_dict}>"

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        return isinstance(other, DottableDict) and self.simple_dict == other.simple_dict

    def __len__(self):
        return len(self.__data__)

    def __iter__(self):
        return self.__data__.__iter__()

    def __add__(self, other):
        """Return a new DottableDict which is a union of this object and `other`.
        Param `other`: any item convertible to `dict`"""
        return self.merge(other)

    @property
    def simple_dict(self) -> dict:
        """Return this mapping's data as built-in `dict` objects.
        Note: due to its recursive nature, it's recommended to use this function rather than directly calling `dict()`
        """
        results = {}
        for k, v in self.__data__.items():
            results[k] = v.simple_dict if isinstance(v, DottableDict) else v
        return results

    def update(self, other):
        other_dict = other.__data__ if isinstance(other, DottableDict) else dict(other)
        self.__data__.update(other_dict)

    def copy(self):
        return DottableDict(self.__data__.copy())

    def get_by_path(self, path: str) -> Any:
        """Get a value within the mapping using the property path.
        Param `path`: dot-separated path to get"""
        parts = path.split(".")
        item = self.__data__
        for key in parts:
            item = item[key]
        return item

    def set_by_path(self, path: str, value: Any) -> None:
        """Set a value within the mapping using the property path (dot-separated).
        Param `path`:	dot-separated path to set
        Param `value`:	value to set"""
        parts = path.split(".")
        item = self
        for key in parts[:-1]:
            item = item.__data__.setdefault(key, DottableDict())
        item[parts[-1]] = value

    def get_current_state(self, frozen: bool = False) -> FrozenState | dict:
        """Get a copy of the current state of this object.
        param frozen: if True - returns a frozen (AKA immutable) copy of the current state, otherwise returns a `dict`.
        """
        if not frozen:
            return self.__data__.copy()
        results = []
        for k, v in self.__data__.items():
            v = DottableDict(v) if isinstance(v, dict) else v
            if isinstance(v, DottableDict):
                v = v.frozen_state
            results.append((k, v))
        return FrozenState(tuple(results))

    @property
    def frozen_state(self) -> FrozenState:
        """Get an immutable copy of the current state of this object"""
        return self.get_current_state(frozen=True)  # type: ignore

    def hash_current_state(self) -> int:
        """Returns the hash of the (immutable) current state"""
        return hash(self.frozen_state)

    def __hash__(self) -> None:  # type: ignore
        """Not implemeneted, as the mapping itself is inherently mutable
        Consider using `hash_current_state()` instead"""
        raise TypeError(
            f"unhashable type: '{self.__class__.__name__}'. Use hash_current_state() to hash the current state of this object."
        )

    def merge(self, other):
        """Return a new DottableDict object which includes the values in `other`.
        In case `other` contains a key which already exists in the current mapping:
                if both values are mappings - an inner merge will be executed,
            otherwise - a unified list of unique results is created"""
        ### To Do: add "for more" + link instead of inline explanation
        other = other.__data__ if isinstance(other, DottableDict) else other
        merged = self.copy()
        for k, v in other.items():
            if k not in merged:
                merged[k] = v
                continue
            current_val = merged[k]
            v = DottableDict(v) if isinstance(v, Mapping) else v
            current_val = (
                DottableDict(current_val)
                if isinstance(current_val, Mapping)
                else current_val
            )
            if v == current_val:
                continue

            if isinstance(current_val, DottableDict._MergedValues):
                merged[k] = (
                    current_val
                    if v in current_val
                    else DottableDict._MergedValues(current_val + [v])
                )
            elif isinstance(current_val, DottableDict) and isinstance(v, DottableDict):
                new_val = current_val.merge(v)
                merged[k] = new_val if self.__autoconvert__ else new_val.simple_dict
            else:
                merged[k] = DottableDict._MergedValues([current_val, v])
        return merged
