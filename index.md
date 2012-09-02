---
layout: page
title: ""
tagline: ""
---
{% include JB/setup %}

</br>

<ul class="posts" style="clear:left">
  {% for post in site.posts %}
    <li><span>{{ post.date | date_to_string }}</span> &raquo; <a href="{{ BASE_PATH }}{{ post.url }}">{{ post.title }}</a></li>
  {% endfor %}
</ul>
