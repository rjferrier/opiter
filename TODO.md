- [ ] Interface
  - [x] Rename the `str` method to avoid confusion with the `str` idiom
  - [ ] Change NodeInfo method names to be more semantically correct
  - [x] Introduce an OptionsDict.get_position method so that the user
        doesn't have to touch get_node_info

- [ ] OptionsTreeElement behaviour
  - [ ] Consider reworking `collapse` as a generator
  - [ ] Separate mutating and nonmutating methods to avoid confusion.
        Consider deprecating/removing the former.
  
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