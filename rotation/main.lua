local addonName, EZ = ...
-- 事件框架
local EventFrame = CreateFrame("Frame", "EZAssistedCombatEventFrame", UIParent)

local IDLE_ICON = "interface/icons/inv_corgi2.blp"

local function updateFrame()

    if not EZ.Enable then
         return EZ.FrameSetMacro(IDLE_ICON,"未启动",{r=0,g=0,b=0})
    end

    if UnitIsDeadOrGhost("player") then
        return EZ.FrameSetMacro(IDLE_ICON,"挂了",{r=0,g=0,b=0})
    end

    if not UnitAffectingCombat("player") then
        return EZ.FrameSetMacro(IDLE_ICON,"未在战斗",{r=0,g=0,b=0})
    end

    if UnitInVehicle("player") then
        return EZ.FrameSetMacro(IDLE_ICON,"坐骑中",{r=0,g=0,b=0})
    end

    if UnitIsUnit("player", "target") then
        return EZ.FrameSetMacro(IDLE_ICON,"目标是玩家",{r=0,g=0,b=0})
    end

    if not UnitExists("target") then
        return EZ.FrameSetMacro(IDLE_ICON,"目标不存在",{r=0,g=0,b=0})
    end

    local  _, _, _, _, _, _, _, _, isEmpowered, _ = UnitChannelInfo("player")
    if isEmpowered then
        return EZ.FrameSetMacro(IDLE_ICON,"蓄力",{r=0,g=0,b=0})
    end



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