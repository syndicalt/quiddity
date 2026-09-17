-- Utility Belt Lua sketch.
-- Drop in Documents\Decal Plugins\UtilityBelt\scripts\quiddity\
-- Template: UB Lua APIs differ across builds.
-- Contract: write world.json Quiddity already knows how to read.

local output = os.getenv("QUIDDITY_WORLD")
    or (os.getenv("USERPROFILE") .. "\\Documents\\Decal Plugins\\UtilityBelt\\quiddity\\world.json")

local function dump()
  local snapshot = {
    source = "utilitybelt-lua",
    character = {
      name = "Unknown",
      level = 1,
      health = { current = 1, max = 1 },
      stamina = { current = 1, max = 1 },
      mana = { current = 1, max = 1 },
      position = { ns = 0, ew = 0, z = 0, landblock = nil, heading = 0, indoors = false },
      buffs = {},
      skills = {},
    },
    inventory = {},
    selected = nil,
    nearby = {},
  }

  local encoded = json.encode(snapshot)
  local f = io.open(output, "w")
  if f then
    f:write(encoded)
    f:close()
  end
end

print("[quiddity] snapshot writer loaded, path=" .. output)
dump()
