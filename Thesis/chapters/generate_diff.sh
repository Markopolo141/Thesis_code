#!/bin/bash
for f in *; do
if [ -f "../chapters_old/old_$f" ]; then
echo "../chapters_old/old_$f";
latexdiff "../chapters_old/old_$f" $f > "../diff_chapters/$f";
fi
done

