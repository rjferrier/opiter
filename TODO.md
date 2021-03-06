- [ ] Interface
  - [ ] Change NodeInfo method names to be more semantically correct

- [ ] OptionsTreeElement behaviour
  - [ ] Implement a recursive iterator; refactor methods accordingly.
  - [ ] Separate mutating and nonmutating methods to avoid confusion.
        Consider deprecating/removing the former.
  - [ ] Add a branch narrowing method (inverse of del)

- [ ] Tidy up
  - [ ] Review/update docstrings
  - [ ] Replace isinstance tests with try-except blocks

- [ ] Tests/Examples
  - [ ] Add a mock simulation example with convergence analysis
  - [ ] Add a parameter exploration example with contour plot
  - [ ] The Unit<...> classes that override original classes' factory methods
        to enable decoupling are unsafe when the signatures change.  Find
        a more robust alternative.
  - [ ] Extend test coverage to utilities.py.

- [ ] Misc
  - [ ] Consider changing the license
  - [ ] Check Python version compatibility
