---
layout: post
title: "Sinatra ERB XSS escaping"
description: "Defensive ERB defaults for Sinatra with minimal changes"
category: programming
tags: [ruby, sinatra]
---

While [Rails XSS escaping by default](https://www.owasp.org/index.php/Ruby_on_Rails_Cheatsheet#Cross-site_Scripting_.28XSS.29), Sinatra requires some handholding to produce a similar protection.  The following describes two simple solutions.

## Setup

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

any user-defined input will show the unescaped value. This setup is immediately vulnerable to persistent [XSS attacks](https://en.wikipedia.org/wiki/Cross-site_scripting).  For instance, a `User` with a `name` like `<script src=http://www.example.com/malicious-code.js></script>` will appear as:

```html
<tr>
  <td>1</td>
  <td><script src=http://www.example.com/malicious-code.js></script></td>
</tr>
```

## Offensive solution

Use [`ERB::Util#h`](http://ruby-doc.org/stdlib-2.1.2/libdoc/erb/rdoc/ERB/Util.html#method-i-h) on the specific inputs that should be escaped.

* include `ERB::Util`

```ruby
# lib/app.rb
class App < Sinatra::Base
  include ERB::Util
end
```

* Explicitly escape desired inputs

```patch
-    <td><%= user.id %></td>
+    <td><%= h user.name %></td>
```

This produces the desired result of:

```html
<tr>
  <td>1</td>
  <td>&lt;script src=http://www.example.com/malicious-code.js&gt;</script></td>
</tr>
```

While this solution is very simple, if a developer forgets to escape a value the site becomes vulernable.

## Defensive solution

Assume all inputs are possible sources of attack and escape by default.

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

**Note:** There are a few cases when you absolutely do not want to render inputs as escaped. In order to get raw inputs use `==`.

* With a `yield` in a layout

```erb
# lib/views/layouts/application.erb
<body>
  <%== yield %>
</body>
```

* Partial templates

```erb
<% users.each do |user| %>
  <%== erb ':user/show', user: user %>
<% end %>
```
