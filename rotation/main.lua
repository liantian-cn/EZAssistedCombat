local addonName, EZ = ...
-- 事件框架
local EventFrame = CreateFrame("Frame", "EZAssistedCombatEventFrame", UIParent)




local function updateFrame()
    local spellID = C_AssistedCombat.GetNextCastSpell(false)
    -- EZ.Print("spellID:" .. spellID)
    if type(spellID) == "nil" then
        EZ.Reset()
    else
        local spellInfo = C_Spell.GetSpellInfo(spellID)
        if type(spellInfo) == "nil" then
            EZ.Reset()
        else
            local icon = spellInfo.iconID
            local name = spellInfo.name
            
            if EZ.TitleToColor[name] == nil then
                EZ.Print("未找到映射： SpellID:" .. spellID .. " iconID:" .. icon .. " name:" .. name)
                EZ.Print("请/reload 插件后重试。已使用带惩罚的一键施法代替。")
                EZAssistedCombatVars.SpellDict[spellID] = name
                local color = EZ.TitleToColor["AssistedCombat"]
                EZ.FrameSetMacro(icon,name,color)
            else
                local color = EZ.TitleToColor[name]
                -- EZ.Print("SpellID:" .. spellID .. " iconID:" .. icon .. " name:" .. name .. " color:" .. color.r .. "," .. color.g .. "," .. color.b)
                EZ.FrameSetMacro(icon,name,color)
            end


        end
    end
end




-- 更新时间计数器
local tickTimer = GetTime()
EventFrame:SetScript("OnUpdate", function(self, elapsed)
    local targetFps = EZAssistedCombatVars.EzFPS;
    local tickOffset = 1.0 / targetFps;
    if GetTime() > tickTimer then
        tickTimer = GetTime() + tickOffset
        updateFrame()
    end
end)