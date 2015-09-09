- [ ] Interface
  - [ ] Rename the `str` method to avoid confusion with the `str` idiom

- [ ] OptionsTreeElement behaviour
  - [ ] Consider reworking `collapse` as a generator
  - [x] Implement `__getitem__` and `__setitem__` for OptionsNode
        (as delegations)
  
- [ ] Tidy up
  - [ ] Review/update docstrings
  - [ ] Replace isinstance tests with try-except blocks
  - [ ] Consider deprecating/removing
    - [ ] `expand_template_file`
    - [ ] `tools.py`, `OptionsDict.array`, `OptionsDict.node`

- [ ] Tests/Examples
  - [ ] Add a mock simulation example with convergence analysis
  - [ ] Add a parameter exploration example with contour plot
  - [ ] The Unit<...> classes that override original classes' factory methods
        to enable decoupling are very unsafe when the signatures change.  Find
        a more robust alternative.

- [ ] Misc
  - [ ] Check Python version compatibility
  - [ ] Make expand_template_string more conservative (use substitute instead
        of safe_substitute); in utilities, warn about unexpanded placeholders