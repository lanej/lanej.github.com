require 'rack/contrib/try_static'
require 'rack/contrib/not_found'

# enable compression
use Rack::Deflater

use Rack::TryStatic,
  :root => "_site",  # static files root dir
  :urls => %w[/],    # match all requests
  :try => ['.html', 'index.html', '/index.html'], # try these postfixes sequentially
  :gzip => true,     # enable compressed files
  :header_rules => [
    [:all, {'Cache-Control' => 'public, max-age=86400'}],
    [['css', 'js'], {'Cache-Control' => 'public, max-age=604800'}]
  ]


run Rack::NotFound.new('404.html')
