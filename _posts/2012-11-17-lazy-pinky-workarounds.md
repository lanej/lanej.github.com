---
layout: post
title: "Lazy pinky workarounds"
description: "Useful vim customizations for those who linger on the Shift key"
category: programming
tags: [vim]
---
{% include JB/setup %}

I have a tendency to keep my right pinky down on the shift key when typing ```:``` to enter vim command mode.  This causes my command to start with a capital letter, which is rarely useful.  Besides focusing more on lifting it up more quickly I have configured vim to figure out what my intentions really are.

My most commonly misspelled commands are:

* ```:Wa``` which is intended to be ```:wa``` - write all files
* ```:W``` which is intended to be ```:w``` - write current buffer
* ```:E``` which is intended to be ```:e``` - open a file

I've remapped the previous errored commands to be their intended targets by adding

<script src="https://gist.github.com/4098807.js">
</script>

to my ```~/.vimrc```

If you find this useful, [all my dotfiles are public](https://github.com/lanej/dotfiles)
