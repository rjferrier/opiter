- [ ] Interface
  - [ ] Change NodeInfo method names to be more semantically correct
  - [x] Change "dynamic" entries to "dependent" entries; change `freeze`
        to `remove_links`

- [ ] OptionsTreeElement behaviour
  - [ ] Consider reworking `collapse` as a generator
  - [ ] Separate mutating and nonmutating methods to avoid confusion.
        Consider deprecating/removing the former.
  - [ ] Add a branch narrowing method (inverse of del)

- [ ] OptionsDict behaviour
  - [ ] Implement recursive iterator
  - [ ] Implement clean and check functors with "not pickleable" and
        "missing dependencies" criteria

- [ ] Tidy up
  - [ ] Review/update docstrings
  - [ ] Replace isinstance tests with try-except blocks

- [ ] Tests/Examples
  - [ ] Add a mock simulation example with convergence analysis
  - [ ] Add a parameter exploration example with contour plot
  - [ ] The Unit<...> classes that override original classes' factory methods
        to enable decoupling are unsafe when the signatures change.  Find
        a more robust alternative.

- [ ] Misc
  - [ ] Consider changing the license
  - [ ] Check Python version compatibility
  - [ ] Make expand_template_string more conservative (use substitute instead
        of safe_substitute); in utilities, warn about unexpanded placeholders