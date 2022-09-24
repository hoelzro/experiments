#!/bin/zsh

# XXX make an amend where the changes are not tightly packed, but in the same file
# XXX make an amend where the changes are in separate files
# XXX amends removing/adding changes
# XXX adding/removing whole files

set -e -u

if [[ $# -eq 0 ]] ; then
  echo "you need to provide a target directory" >&2
  exit 1
fi

target_dir="$1"

if [[ $(ls -A "$target_dir" | wc -l) -ne 0 ]] ; then
  echo "you need to provide an empty target directory" >&2
  exit 1
fi

git init "$target_dir"

cd "$target_dir"

# make an amend where the changes are tightly packed together
git checkout -b packed-changes

perl -le 'print for 1..5' > values.txt
git add values.txt
git commit -m 'initial commit'

perl -le 'print for 1..10' > values.txt
git add values.txt
git commit -m 'add some more values'

perl -le 'print for grep { $_ != 2 && $_ != 4 && $_ != 8 } 1..10' > values.txt
git add values.txt
git commit -m 'remove a few values'

perl -le 'print for grep { $_ != 2 && $_ != 4 && $_ != 8 } 1..11' > values.txt
git add values.txt
git commit -m 'amend!'
