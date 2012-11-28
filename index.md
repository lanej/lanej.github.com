---
layout: page
title: ""
tagline: ""
---
{% include JB/setup %}

<h3> Projects </h3>
<ul class="posts" style="clear:left">
  <li><a href="http://joshualane.com/zendesk2">Zendesk2</a> &raquo; <span>Zendesk V2 API Client</span></li>
  <li><a href="http://joshualane.com/cistern">Cistern</a> &raquo; <span>Generic Service Client library inspired by Fog</span></li>
</ul>
<h3> Posts </h3>
<ul class="posts" style="clear:left">
  {% for post in site.posts %}
    <li><span>{{ post.date | date_to_string }}</span> &raquo; <a href="{{ BASE_PATH }}{{ post.url }}">{{ post.title }}</a></li>
  {% endfor %}
</ul>
