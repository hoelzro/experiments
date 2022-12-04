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

local t = setmetatable({}, {__mode = 'k'})

local PADDING = string.rep('a', 100)
for i = 1, 1000000 do
  t[PADDING .. gen_string(i)] = 'aaaaa'
end

print(#t, count(t))

for i = 1, 5 do
  collectgarbage 'collect'
end

print(#t, count(t))
