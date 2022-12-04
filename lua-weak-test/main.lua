local collectgarbage = collectgarbage

local function count(t)
  local c = 0
  for _ in pairs(t) do
    c = c + 1
  end
  return c
end

local gen_string
do
  local gen_string_chars = {}
  for i = string.byte 'A', string.byte 'Z' do
    gen_string_chars[#gen_string_chars + 1] = string.char(i)
  end
  for i = string.byte 'a', string.byte 'z' do
    gen_string_chars[#gen_string_chars + 1] = string.char(i)
  end
  for i = string.byte '0', string.byte '9' do
    gen_string_chars[#gen_string_chars + 1] = string.char(i)
  end
  gen_string_chars[#gen_string_chars + 1] = '+'
  gen_string_chars[#gen_string_chars + 1] = '/'

  -- XXX technically buggy, but ¯\_(ツ)_/¯
  --[[local]] function gen_string(n)
    assert(n > 0)

    n = n - 1

    local chars = {}
    while #chars == 0 or n ~= 0 do
      chars[#chars + 1] = gen_string_chars[(n & 63) + 1]
      n = n >> 6
    end
    return table.concat(chars)
  end
end

local gc_count = 0
local gc_count2 = 0

local canary_mt

local function gc_hook()
  gc_count = gc_count + 1
  setmetatable({}, canary_mt)
end

canary_mt = { __gc = gc_hook }

setmetatable({}, canary_mt)

for pad_size = 0, 100 do
  local t = setmetatable({}, {__mode = 'k'})
  local PADDING = string.rep('a', pad_size)

  local prev_dir = 1
  local prev_count = 0
  local start = os.time()
  for i = 1, 1000000 do
    -- XXX you want to detect change in direction, don't you?
    local count = collectgarbage 'count'
    if count ~= prev_count then
      local dir = 1
      if count < prev_count then
        dir = -1
      end

      if dir == 1 and prev_dir == -1 then
        -- count was decreasing, but now it's increasing again, which I *think*
        -- means we finished a GC cycle
        gc_count2 = gc_count2 + 1
      end

      prev_count = count
      prev_dir = dir
    end

    t[PADDING .. gen_string(i+1000000)] = 'aaaaa'
    --t[{foo=17}] = 'aaaaa'

    -- if (i % 2000) == 0 then
      -- collectgarbage 'collect'
    -- end
  end
  local finish = os.time()
  print(pad_size, 'populate', finish - start, gc_count, gc_count2, collectgarbage 'count')

  local start = os.time()
  for i = 1, 5 do
    collectgarbage 'collect'
  end
  local finish = os.time()
  print(pad_size, 'GC', finish - start)

  gc_count = 0
  gc_count2 = 0
end
