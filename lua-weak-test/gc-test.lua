local gc_count = 0

local canary_mt

local function gc_hook()
  gc_count = gc_count + 1
  setmetatable({}, canary_mt)
end

canary_mt = {__gc = gc_hook}

setmetatable({}, canary_mt)

for i = 1, 100 do
  collectgarbage 'collect'
end

print(gc_count)
