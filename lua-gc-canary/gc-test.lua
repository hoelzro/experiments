local time = require 'posix.time'

local canary_mt
local gc_count = 0

local function phoenix()
  gc_count = gc_count + 1

  setmetatable({}, canary_mt)
end

local function noop(t)
end

canary_mt = {__gc = phoenix}

setmetatable({}, canary_mt)

local sleep_time = {
  tv_sec  = 0,
  tv_nsec = 100000000,
}

local mem_decr_count = 0

local prev_count
local max_count = 0

for i = 1, 10000 do
  local count = collectgarbage 'count'
  if prev_count and count < prev_count then
    mem_decr_count = mem_decr_count + 1
  end
  prev_count = count
  if count > max_count then
    max_count = count
  end

  print(i, gc_count, mem_decr_count, count)
  noop({})
  time.nanosleep(sleep_time)
end

print ''
print('Max memory usage:', max_count)
