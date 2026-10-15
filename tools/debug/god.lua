-- GOD: pin the life gauge (EWRAM 0x0203315C, found by ramsearch: 116 = 6 pearls) every frame.
L.on_frame(function() emu.write(0x0203315C, 116, emu.memType.gbaMemory) end)
