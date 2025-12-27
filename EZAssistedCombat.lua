local addonName, EZ = ...
-- 常量定义
local DEFAULT_ICON = "interface/icons/wow_token02.blp"
local BACKGROUND_TEXTURE = "Interface\\Addons\\EZAssistedCombat\\bg"

-- 获取UI缩放因子
-- @param pixelValue number 像素值
-- @return number 缩放后的值
local function GetUIScaleFactor(pixelValue)
    local screenHeight = select(2, GetPhysicalScreenSize())
    return pixelValue * (768 / screenHeight) / WorldFrame:GetEffectiveScale()
end

-- 初始化插件主框架
-- @return table MainFrame 主框架n
local function InitMainFrame()
    -- UI尺寸
    local FRAME_WIDTH = GetUIScaleFactor(64)
    local PIX_HEIGHT = GetUIScaleFactor(64)
    local ICON_HEIGHT = GetUIScaleFactor(64)
    local TITLE_HEIGHT = GetUIScaleFactor(18)

    -- 创建主框架
    local MainFrame = CreateFrame("Frame", "EZAssistedCombatFrame", WorldFrame)
    MainFrame:SetPoint("CENTER", WorldFrame, "CENTER")
    MainFrame:SetSize(FRAME_WIDTH, PIX_HEIGHT+TITLE_HEIGHT+ICON_HEIGHT)
    MainFrame:SetClampedToScreen(true)
    MainFrame:Show()

    -- 框架背景
    local MfBG = MainFrame:CreateTexture(nil, "BACKGROUND")
    MfBG:SetAllPoints()
    MfBG:SetTexture(BACKGROUND_TEXTURE)

    -- 主框架内第一个是pixelFrame
    local PixelFrame = MainFrame:CreateTexture(nil, "ARTWORK")
    PixelFrame:SetAllPoints()
    PixelFrame:SetTexture(BACKGROUND_TEXTURE)
    PixelFrame:Show()

    -- 在标题下方创建图标框架
    -- local iconFrame = CreateFrame("Frame", "EZAssistedCombatIconFrame", mainFrame)
    -- iconFrame:SetPoint("TOPLEFT", mainFrame, "BOTTOMLEFT", 0, 0)
    -- iconFrame:SetSize(FRAME_WIDTH, FRAME_WIDTH)
    -- iconFrame:Show()

    -- -- 图标背景
    -- local iconBg = iconFrame:CreateTexture(nil, "BACKGROUND")
    -- iconBg:SetAllPoints()
    -- iconBg:SetColorTexture( 29/ 255, 109 / 255, 239 / 255, 1)
    -- -- iconBg:SetTexture(BACKGROUND_TEXTURE)
    -- iconBg:Show()

    -- -- 技能图标
    -- local spellIcon = iconFrame:CreateTexture(nil, "ARTWORK")
    -- spellIcon:SetSize(ICON_SIZE, ICON_SIZE)
    -- spellIcon:SetPoint("CENTER", iconFrame, "CENTER")
    -- spellIcon:SetTexture(DEFAULT_ICON)
    -- spellIcon:Show()


    -- -- 按照逻辑关系存放框架
    -- EZ.MainFrame = {
    --     frame = MainFrame,
    --     iconFrame = iconFrame,
    --     textures = {
    --         iconBg = iconBg,
    --         spellIcon = spellIcon
    --     }
    -- }

    return MainFrame
end

InitMainFrame()

-- 事件框架
local EventFrame = CreateFrame("Frame", "EZAssistedCombatEventFrame", UIParent)

-- 更新时间计数器
local timeElapsed = 0
EventFrame:SetScript("OnUpdate", function(self, elapsed)
    timeElapsed = timeElapsed + elapsed
    if timeElapsed > 0.05 then
        timeElapsed = 0
        local spellID = C_AssistedCombat.GetNextCastSpell(false)              --- https://www.townlong-yak.com/framexml/beta/Blizzard_APIDocumentation#C_AssistedCombat.GetNextCastSpell
        if type(spellID) == "nil" then
            EZ.MainFrame.textures.spellIcon:SetTexture(DEFAULT_ICON)        --- https://www.townlong-yak.com/framexml/beta/Blizzard_APIDocumentation#SimpleTextureBaseAPI:SetTexture
        else
            local spellInfo = C_Spell.GetSpellInfo(spellID)                         --- https://www.townlong-yak.com/framexml/beta/Blizzard_APIDocumentation#C_Spell.GetSpellInfo
            if type(spellInfo) == "nil" then
                EZ.MainFrame.textures.spellIcon:SetTexture(DEFAULT_ICON)
            else
                EZ.MainFrame.textures.spellIcon:SetTexture(spellInfo.iconID)
            end
        end
    end
end)

-- 玩家登录事件处理
function EventFrame:PLAYER_LOGIN()
    SetCVar("scriptErrors", 1);
    SetCVar("doNotFlashLowHealthWarning", 1);
    SetCVar("cameraIndirectVisibility", 1);
    SetCVar("cameraIndirectOffset", 10);
    SetCVar("SpellQueueWindow", 150);
    SetCVar("targetNearestDistance", 5)
    SetCVar("cameraDistanceMaxZoomFactor", 2.6)
    SetCVar("CameraReduceUnexpectedMovement", 1)
    SetCVar("synchronizeSettings", 1)
    SetCVar("synchronizeConfig", 1)
    SetCVar("synchronizeBindings", 1)
    SetCVar("synchronizeMacros", 1)
end

EventFrame:RegisterEvent("PLAYER_LOGIN")
EventFrame:SetScript("OnEvent", function(self, event, ...)
    self[event](self, event, ...)
end)
