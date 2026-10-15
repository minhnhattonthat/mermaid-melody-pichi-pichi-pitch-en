-- Poke the top-level game state (u16 at 0x03001E00, table 0x08EB0E78) at frame AT (default 30).
-- --var STATE=9 (9 = leftover debug menu) [--var AT=30]
local at = AT or 30
L.on_frame(function(f)
  if f == at then emu.write16(0x03001E00, STATE, emu.memType.gbaMemory) ; L.log("state <- " .. STATE) end
end)
