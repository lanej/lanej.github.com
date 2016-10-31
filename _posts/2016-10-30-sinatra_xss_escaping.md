---
layout: post
title: "Sinatra ERB XSS escaping"
description: "Defensive ERB defaults for Sinatra with minimal changes"
category: programming
tags: [ruby, sinatra]
---

## Problem

Given a basic Sinatra application

```ruby
# lib/app.rb
class App < Sinatra::Base
  get '/users' do
    @users = User.all

    erb :users
  end
end
```

and a corresponding ERB template

```erb
<%# lib/views/users.erb %>
<% @users.each do |user| %>
  <tr>
    <td><%= user.id %></td>
    <td><%= user.name %></td>
  </tr>
<% end %>
```

any user-defined input will show the unescaped value.

This solution is immediately vulnerable to persistent [XSS attacks](https://en.wikipedia.org/wiki/Cross-site_scripting).  For instance, a `User` with a `name` like `<script src=http://www.example.com/malicious-code.js></script>` will appear as:

```html
<tr>
  <td>1</td>
  <td><script src=http://www.example.com/malicious-code.js></script></td>
</tr>
```

## Offensive solution

Use [`ERB::Util#h`](http://ruby-doc.org/stdlib-2.1.2/libdoc/erb/rdoc/ERB/Util.html#method-i-h) for specific inputs that should be escaped.

* include `ERB::Util`

```ruby
# lib/app.rb
class App < Sinatra::Base
  include ERB::Util
end
```

* Explicitly escape desired inputs

```patch
-    <td><%= user.name %></td>
+    <td><%= h user.name %></td>
```

This produces the desired result of:

```html
<tr>
  <td>1</td>
  <td>&lt;script src=http://www.example.com/malicious-code.js&gt;</script></td>
</tr>
```

## Defensive solution

Let's assume developer are faliable and opt for inputs to be escaped by default

* Add `erubis` to your Gemfile

```ruby
gem 'erubis'
```

* Add `escape_html` ERB setting in Sinatra

```ruby
class App < Sinatra::Base
  set :erb, { escape_html: true }
end
```

This produces the desired result of:

```html
<tr>
  <td>1</td>
  <td>&lt;script src=http://www.example.com/malicious-code.js&gt;</script></td>
</tr>
```

without alterations to the ERB file.

In order to get raw inputs into ERB, you now have to add `==` before.

**Note:** This is immediately necessary for any `yield` references in layouts or partial templates (`erb :'user/show'`)
