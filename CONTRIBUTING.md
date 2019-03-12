## How to contribute

If you're reading this, because it means you saw something that is not right, you want to add a new feature or your manager asked you to contribute to this. In any case we are glad and it would be awesome if you can contribute.

### Testing

We have a handful of unit tests and integration tests. Unit tests are run on every push and Pull Request while integration tests run on every Pull Request.

This guide on [beacon-python testing](https://beacon-python.readthedocs.io/en/latest/testing.html) might be worth a read.

### Submitting Issues

We have templates for submitting new issues, that you can fill out. For example if you found a bug, use the following [template to report a bug](https://github.com/CSCfi/beacon-python/issues/new?template=bug_report.md).


### Submitting changes

Please send a [GitHub Pull Request to beacon-python](https://github.com/CSCfi/beacon-python/pull/new/master) with a clear list of what you've done (read more about [pull requests](https://help.github.com/en/articles/about-pull-requests)). When you send a Pull Request, we will forever be in your debt if you include unit tests. We can always use also some more integration test. 

Please follow our Git branches model and coding conventions (below) and make sure all of your commits are as atomic (preferably one feature per commit) and it is recommended a Pull Request focusses on one functionality or fixes one bug.

Always write a clear log message for your commits, and if there is an issue open reference that issue. This guide might help: [How to Write a Git Commit Message](https://chris.beams.io/posts/git-commit/).

Once submitted the Pull Request will go through a review process meaning we will judge your code :smile:.

#### Git Branches

Give your branch a short descriptive name (like the names between the `<>` below) and prefix the name with the most suitable of:

   * `feature/<feature-name>` - used when an enhancement or new feature implemented;
   * `docs/<what-the-docs>` - missing docs or making them up to date;
   * `bugfix/<caught-it>` - solved a bug;
   * `test/<thank-you>` - adding missing tests for a feature, we would prefer they would come with the `feature` but still `thank you`;
   * `refactor/<that-name-is-confusing>` - well we hope we don't mess anything and we don't use this;
   * `hotfix/<oh-no>` - for when things needed to be fixed yesterday.


### Coding conventions

Reading our code and you'll get the hang of it as we optimize for readability:

  * We follow [pep8](https://www.python.org/dev/peps/pep-0008/) and [pep257](https://www.python.org/dev/peps/pep-0257/) with some small exceptions;
  * We like to keep things simple, so when possible avoid importing any big libraries.

Thanks,
CSC Developers
