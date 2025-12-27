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


function GetMacroText(spellName)
    local className, classFilename, classId = UnitClass("player")
    local currentSpec = GetSpecialization()
    local macroText = "/cast " .. spellName

    -- 注释为例子
    if classFilename == "DEATHKNIGHT" and currentSpec == 1 then
        if spellName == "枯萎凋零" then
            macroText = "/cast [@player]枯萎凋零"
        end
    end

    if classFilename == "DRUID" and currentSpec == 3 then
        if spellName == "月火" then
            macroText = "/cast 月火\n/cast 铁鬃"
        elseif spellName == "痛击" then
            macroText = "/cast 痛击\n/cast 铁鬃"
        elseif spellName == "横扫" then
            macroText = "/cast 横扫\n/cast 铁鬃"
        elseif spellName == "裂伤" then
            macroText = "/cast 裂伤\n/cast 铁鬃"
        end
    end
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

    for spellID, spellName in pairs(EZAssistedCombatVars.SpellDict) do
        -- EZ.Print("SpellID:" .. spellID .. " spellName:" .. spellName)
        local macro_text = GetMacroText(spellName)
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
