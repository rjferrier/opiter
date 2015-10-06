- [ ] Interface
  - [ ] Change NodeInfo method names to be more semantically correct
  - [ ] Change `rendering_strategy` to `engine`, make
        prerequisite_filenames_key optional.

- [ ] OptionsTreeElement behaviour
  - [ ] Consider reworking `collapse` as a generator
  - [ ] Separate mutating and nonmutating methods to avoid confusion.
        Consider deprecating/removing the former.
  - [x] Introduce `names` optional argument into OptionsArray constructor
  - [ ] Add a branch narrowing method (inverse of del)

- [ ] Syntax
  - [ ] Remove the necessity for `opt.` before every key in Jinja 2
        templates
  
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