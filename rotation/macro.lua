local addonName, EZ = ...


if not EZAssistedCombatVars.SpellDict then
    EZAssistedCombatVars.SpellDict = {}
end

if not EZ.Macros then
    EZ.Macros = {}
end

if not EZ.TitleToColor then
    EZ.TitleToColor = {}
end


function GetMacroText(spellName, classFilename, currentSpec)
    local macroText = "/cast " .. spellName

    -- 注释为例子
    -- if classFilename == "DEMONHUNTER" and currentSpec == 1 then
    --     if spellName == "献祭光环" then
    --         macroText = "/cast 献祭光环\n/cast 恶魔尖刺"
    --     elseif spellName == "灵魂裂劈" then
    --         macroText = "/cast 灵魂裂劈\n/cast 恶魔尖刺"
    --     elseif spellName == "烈焰咒符" then
    --         macroText = "/use [@player] 烈焰咒符"
    --     end
    -- end
    return macroText
end

local function InitSpellDict()
    local spellIDs = C_AssistedCombat.GetRotationSpells()
    for i = 1, #spellIDs do
        local spellID = spellIDs[i]
        local spellName = C_Spell.GetSpellName(spellID)
        local baseSpellID = C_Spell.GetBaseSpell(spellID)
        local baseSpellName = C_Spell.GetSpellName(baseSpellID)
        -- EZ.Print("SpellID:" .. spellID .. " BaseSpellID:" .. baseSpellID .. " SpellName:" .. spellName )
        EZAssistedCombatVars.SpellDict[spellID] = spellName
        EZAssistedCombatVars.SpellDict[baseSpellID] = baseSpellName
    end
end

local function InitMacro()
    local className, classFilename, classId = UnitClass("player")
    local currentSpec = GetSpecialization()
    for spellID, spellName in pairs(EZAssistedCombatVars.SpellDict) do
        -- EZ.Print("SpellID:" .. spellID .. " spellName:" .. spellName)
        local macro_text = GetMacroText(spellName, classFilename, currentSpec)
        table.insert(EZ.Macros, { ["title"] = spellName, ["macrotext"] = macro_text })
    end
    local ass_name = C_Spell.GetSpellName(C_AssistedCombat.GetActionSpell())
    local acc_macro_text = "/cast " .. ass_name
    table.insert(EZ.Macros, { ["title"] = "AssistedCombat", ["macrotext"] = acc_macro_text })
end

function RegisterMacro()
    for i = 1, #EZ.Macros do
        local macro = EZ.Macros[i]
        local title = macro["title"]
        local macrotext = macro["macrotext"]
        local key = EZ.KeyMap[i]["key"]
        local color_r = EZ.KeyMap[i]["r"]
        local color_g = EZ.KeyMap[i]["g"]
        local color_b = EZ.KeyMap[i]["b"]
        EZ.Print("RegisterMacro:" .. title .. " Text:" .. macrotext.." key:"..key.." color:"..color_r..","..color_g..","..color_b)
        EZ.TitleToColor[title] = {
            ["r"] = color_r,
            ["g"] = color_g,
            ["b"] = color_b,
        }
        local buttonName = string.format("EZButton_%s", i)
        local frame = CreateFrame("Button", buttonName, UIParent, "SecureActionButtonTemplate")
        frame:SetAttribute("type", "macro")
        frame:SetAttribute("macrotext", macrotext)
        frame:RegisterForClicks("AnyDown", "AnyUp")
        SetOverrideBindingClick(frame, true, key, buttonName)

    end
    EZ.Print("已绑定宏，数量：" .. tostring(#EZ.Macros))
end


local EventFrame = CreateFrame("Frame", "EZAssistedCombatMarco", UIParent)

function EventFrame:PLAYER_ENTERING_WORLD(isInitialLogin, isReloadingUi)
    if isInitialLogin or isReloadingUi then
        InitSpellDict()
        InitMacro()
        RegisterMacro()
    end
end

EventFrame:RegisterEvent("PLAYER_ENTERING_WORLD")
EventFrame:SetScript("OnEvent", function(self, event, ...)
    self[event](self, event, ...)
end)
