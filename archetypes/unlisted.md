+++
title = {{ .Name | replaceRE "-" " " | title | jsonify }}
description = ""
date = {{ .Date | jsonify }}
type = "writing"
draft = false
unlisted = true
+++

