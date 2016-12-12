namespace :lanej do
  task :precompile do
    on roles(:web), in: :parallel do
      %x( rake assets:precompile --trace )
    end
  end
end

after 'deploy:updated', 'lanej:precompile'
