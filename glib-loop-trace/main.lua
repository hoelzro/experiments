local lgi = require 'lgi'
local glib = lgi.require 'GLib'

local ctx  = glib.MainContext.default()
local loop = glib.MainLoop.new(ctx)

glib.unix_signal_add(glib.PRIORITY_DEFAULT, 2, function()
  print 'got SIGINT'
  loop:quit()
end)

glib.unix_signal_add(glib.PRIORITY_DEFAULT, 15, function()
  print 'got SIGTERM'
  loop:quit()
end)

local counter = 0
glib.timeout_add(glib.PRIORITY_DEFAULT, 1000, function()
  print('ping', os.date())
  counter = counter + 1
  if counter > 10 then
    os.execute 'sleep 5'
    counter = 0
  end
  return true
end)

loop:run()
