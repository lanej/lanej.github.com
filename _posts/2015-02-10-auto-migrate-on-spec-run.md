---
layout: post
title: "Automatic database migration for happiness"
description: "Auto-migrate your database on application initialization"
category: ruby
tags: [ruby]
---

So I find this little bastard in rails 4.0.x wicked annoying.

{% highlight ruby %}
ActiveRecord::Migration.check_pending!
{% endhighlight %}

Except, I get it.  It's not up to rails to decide if you want run you migrations or not.

Sometimes you are working on tests, and you have a pending migration but you don't want it to run yet.  What I do dislike is checking out some updates, running tests and then immediately failing.  DataMapper is especially anal about this because of the relationship integrity checks.

My solution is to sprinkle this little snippet around:

{% highlight ruby %}
Rails.application.config.after_initialize do
  needs_migration = begin
                      ActiveRecord::Migrator.needs_migration?(ActiveRecord::Base.connection)
                    rescue ActiveRecord::NoDatabaseError
                      true
                    end
  # migrate database if migration file isn't run but is in version control
  pending_migration = (Dir["db/migrate/*.rb"] - `git ls-files db/migrate/*.rb`.split($\)).empty?

  if !ENV["NO_MIGRATE"] && %w[development test].include?(Rails.env) &&
      needs_migration && pending_migration
    ActiveRecord::Tasks::DatabaseTasks.create_current
    ActiveRecord::Migrator.up(ActiveRecord::Tasks::DatabaseTasks.migrations_paths)
  end
end
{% endhighlight %}

The real clutch piece here is that having a migration checked into git effectively means it's ready for party time.
