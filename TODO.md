- [ ] Interface
  - [ ] Rename the `str` method to avoid confusion with the `str` idiom

- [ ] OptionsTreeElement behaviour
  - [ ] Consider reworking `collapse` as a generator
  - [x] Implement __delitem__
  - [ ] Separate mutating and nonmutating methods to avoid confusion.
        Consider deprecating/removing the former.
  
- [ ] Tidy up
  - [ ] Review/update docstrings
  - [ ] Replace isinstance tests with try-except blocks
  - [ ] Consider deprecating/removing
    - [ ] `expand_template_file`
    - [x] `tools.py`, `OptionsDict.array`, `OptionsDict.node`

- [ ] Tests/Examples
  - [ ] Add a mock simulation example with convergence analysis
  - [ ] Add a parameter exploration example with contour plot
  - [ ] The Unit<...> classes that override original classes' factory methods
        to enable decoupling are very unsafe when the signatures change.  Find
        a more robust alternative.

- [ ] Misc
  - [ ] Consider changing the license
  - [ ] Check Python version compatibility
  - [ ] Make expand_template_string more conservative (use substitute instead
        of safe_substitute); in utilities, warn about unexpanded placeholders