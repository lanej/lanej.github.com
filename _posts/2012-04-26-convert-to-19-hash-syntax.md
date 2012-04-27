---
layout: post
title: "convert to 1.9 hash syntax"
description: "Tips to get used to the new 1.9 hash sytax"
category: ruby
tags: [ruby, vim]
---
{% include JB/setup %}

I am trying to get used to the new Ruby 1.9 hash syntax ([read more](http://breakthebit.org/post/8453341914/ruby-1-9-and-the-new-hash-syntax)). Here's a quick VIM replace command to convert all the 1.8 syntax to the new 1.9 syntax.

```
%s/\v\:([^\:][a-zA-Z0-9_]*)\s+\=\>/\1:/g
```

I am quickly becoming a fan of this new style simply because it's less characters to type and it looks more like JSON. 

A similiar regex could be used in conjunction with [sed](http://www.gnu.org/software/sed/manual/sed.html) to convert a whole project in one go.
