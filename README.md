# Dottable Dictionary
Your everyday dictionary, with the special ability to be accessed using dot-notation.

Use dottable dictionaries to turn this: \
`d["somekey"]["some_inner_key"]["some_internal_key"]`\
to this:\
`d.somekey.some_inner_key.some_internal_key`.

## Background
The basic idea behind this package was to migrate JavaScript's dot-notation access to Python dictionaries.
In many (maybe most) cases, dictionaries are used with keys which can serve as identifiers (for more on those take a look [here](https://docs.python.org/3/library/stdtypes.html#str.isidentifier)).\
By taking advantage of this, dictionary access can be as intuitive as accessing properties within an object (rather than being constrained to using strings).

Importantly - dottable dictionaries are first and foremost **dictionaries**.
Therefore, they implement the same basic functionalities as native `dict` objects, and are generally designed to interact with them as seamlessly as possible, such that using dottable dictionaries should be compatible with existing code and/or any external module/package.

## Functionality
### Dictionary functionality
Some basic native `dict` functionalities which are implemented in dottable dictionaries:
- `copy()`
- `update()`
- `keys()`, `values()`, `items()`
- `in` operator (`__contains__()`)
- Iterability (`__iter__`)
- TBD: `setdefault`


### Extra functionality
Some extra functionality (extending native `dict` functionality):
- Adding & merging: merging mappings to get a unified view of all values (also availble using the `+` operator)
- Access by complex string paths - set/get properties using a dot-separated path (e.g., `["a"]["b"]["c"]` <-> `"a.b.c"`). This can be useful for dynamically accessing properties in objects with complex data schemas.
- Immutable copies - generating an immutable copy of the current state of the mapping. This is also used to allow a pseudo-hash of the mapping (i.e., hash of the current state)

### Conversions
Dottable dictionaries can be directly (recursively) converted to native `dict` objects by using the `simple_dict` property.
