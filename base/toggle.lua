local addonName, EZ = ...

EZ.Enable = false

local function GetUIScaleFactor(pixelValue)
    local screenHeight = select(2, GetPhysicalScreenSize())
    return pixelValue * (768 / screenHeight) / WorldFrame:GetEffectiveScale()
end

local TOGGLE_WIDTH = GetUIScaleFactor(120)
local TOGGLE_HEIGHT = GetUIScaleFactor(40)
local TOGGLE_BG_COLOR = {0.1, 0.1, 0.1, 0.85}
local TOGGLE_BORDER_COLOR = {0.3, 0.3, 0.3, 1}
local ON_COLOR = {0, 1, 0}
local OFF_COLOR = {1, 0, 0}

EZ.ToggleFrame = CreateFrame("Frame", "EZToggleFrame", WorldFrame)
EZ.ToggleFrame:SetSize(TOGGLE_WIDTH, TOGGLE_HEIGHT)
EZ.ToggleFrame:SetPoint("CENTER", WorldFrame, "CENTER")
EZ.ToggleFrame:EnableMouse(true)
EZ.ToggleFrame:SetMovable(true)
EZ.ToggleFrame:RegisterForDrag("LeftButton")
EZ.ToggleFrame:SetClampedToScreen(true)
EZ.ToggleFrame:SetScript("OnDragStart", function(self) self:StartMoving() end)
EZ.ToggleFrame:SetScript("OnDragStop", function(self) self:StopMovingOrSizing() end)

local toggleBg = EZ.ToggleFrame:CreateTexture(nil, "BACKGROUND")
toggleBg:SetAllPoints()
toggleBg:SetColorTexture(unpack(TOGGLE_BG_COLOR))

local toggleBorder = EZ.ToggleFrame:CreateTexture(nil, "BORDER")
toggleBorder:SetAllPoints()
toggleBorder:SetColorTexture(unpack(TOGGLE_BORDER_COLOR))
toggleBorder:SetDrawLayer("BORDER", -1)

local labelText = EZ.ToggleFrame:CreateFontString(nil, "ARTWORK", "GameFontNormal")
local fontFile, _, _ = GameFontNormal:GetFont()
labelText:SetPoint("LEFT", EZ.ToggleFrame, "LEFT", GetUIScaleFactor(10), 0)
labelText:SetFont(fontFile, GetUIScaleFactor(16), "")
labelText:SetText("EZAC")
labelText:SetTextColor(1, 1, 1)

local toggleSwitch = CreateFrame("Frame", "EZToggleSwitch", EZ.ToggleFrame)
toggleSwitch:SetSize(GetUIScaleFactor(46), GetUIScaleFactor(26))
toggleSwitch:SetPoint("RIGHT", EZ.ToggleFrame, "RIGHT", -GetUIScaleFactor(6), 0)

local switchBg = toggleSwitch:CreateTexture(nil, "BACKGROUND")
switchBg:SetAllPoints()
switchBg:SetColorTexture(0.2, 0.2, 0.2, 1)
switchBg:SetDrawLayer("BACKGROUND", -1)

local switchIndicator = toggleSwitch:CreateTexture(nil, "ARTWORK")
switchIndicator:SetSize(GetUIScaleFactor(22), GetUIScaleFactor(22))
switchIndicator:SetPoint("CENTER", toggleSwitch, "CENTER", -GetUIScaleFactor(11), 0)
switchIndicator:SetColorTexture(1, 1, 1)
switchIndicator:SetDrawLayer("ARTWORK", 0)

local statusText = toggleSwitch:CreateFontString(nil, "ARTWORK", "GameFontNormal")
statusText:SetPoint("CENTER", toggleSwitch, "CENTER")
statusText:SetFont(fontFile, GetUIScaleFactor(12), "")
statusText:SetText("OFF")
statusText:SetTextColor(1, 0, 0)
statusText:SetDrawLayer("ARTWORK", 1)

local function UpdateToggleState(enabled)
    if enabled then
        switchIndicator:ClearAllPoints()
        switchIndicator:SetPoint("CENTER", toggleSwitch, "CENTER", GetUIScaleFactor(11), 0)
        switchIndicator:SetColorTexture(unpack(ON_COLOR))
        statusText:SetText("ON")
        statusText:SetTextColor(0, 1, 0)
    else
        switchIndicator:ClearAllPoints()
        switchIndicator:SetPoint("CENTER", toggleSwitch, "CENTER", -GetUIScaleFactor(11), 0)
        switchIndicator:SetColorTexture(unpack(OFF_COLOR))
        statusText:SetText("OFF")
        statusText:SetTextColor(1, 0, 0)
    end
end

toggleSwitch:SetScript("OnMouseDown", function()
    EZ.Enable = not EZ.Enable
    UpdateToggleState(EZ.Enable)
end)

UpdateToggleState(EZ.Enable)
