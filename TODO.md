- [ ] OptionsTreeElement behaviour
  - [ ] Consider reworking `collapse` as a generator
  - [ ] OptionsArray
    - [ ] `__getitem__` by index, as by slice, should not modify node info
    - [ ] Instead, `popitem` should be implemented and modify node info 
  
- [ ] Syntactic sugar
  - [ ] Create `OptionsNode` from class (and integrate with `OptionsArray`)
  - [ ] Update `OptionsDict` entries by variable list
  - [ ] Get and set items using dot-style notation
    - [ ] Warn when new names conflict with original namespace

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