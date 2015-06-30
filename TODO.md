- [ ] OptionsTreeElement behaviour
  - [ ] Consider reworking `collapse` as a generator
  - [ ] OptionsArray
    - [ ] Review behaviour of `__getitem__` in the context of tree operations.
          Should passing an index modify the returned node info?
    - [ ] Handle node keys as well as indices in `__getitem__`
  
- [ ] Syntactic sugar
  - [ ] Create `OptionsNode` from class (and integrate with `OptionsArray`)
    - [ ] Inherit attributes
  - [x] Get and set items using dot-style notation
    - [x] Warn when new names conflict with original namespace

- [ ] Tidy up
  - [ ] Review/update docstrings
  - [ ] Rename copy methods as `__deepcopy__` or remove them altogether
  - [ ] Consider deprecating/removing
    - [ ] `expand_template_file`
    - [ ] `tools.py`, `OptionsDict.array`, `OptionsDict.node`

- [ ] Tests/Examples
  - [ ] Update advanced functional tests to use tree formatting
  - [ ] More rigorously test formatter behaviour with orphaned/anonymous nodes
  - [ ] Add a mock simulation example with convergence analysis
  - [ ] Add a parameter exploration example with contour plot

- [ ] Misc
  - [ ] Check Python version compatibility