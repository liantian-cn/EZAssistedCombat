local addonName, EZ = ...
-- 常量定义
local DEFAULT_ICON = "interface/icons/wow_token02.blp"
local BACKGROUND_TEXTURE = "Interface\\Addons\\EZAssistedCombat\\bg"

local function GetUIScaleFactor(pixelValue)
    local screenHeight = select(2, GetPhysicalScreenSize())
    return pixelValue * (768 / screenHeight) / WorldFrame:GetEffectiveScale()
end


-- UI尺寸
local FRAME_SIZE = GetUIScaleFactor(64+24)
local PIX_WIDTH = GetUIScaleFactor(24)
local ICON_SIZE = GetUIScaleFactor(64)



-- 创建主框架
EZ.MainFrame = CreateFrame("Frame", "EZAssistedCombatFrame", WorldFrame)
EZ.MainFrame:SetPoint("TOPLEFT", WorldFrame, "TOPLEFT")  -- 正式模式
-- EZ.MainFrame:SetPoint("CENTER", WorldFrame, "CENTER")   -- 测试模式

EZ.MainFrame:SetSize(FRAME_SIZE, FRAME_SIZE)
EZ.MainFrame:Show()

-- 框架背景
local MfBG = EZ.MainFrame:CreateTexture(nil, "BACKGROUND")
MfBG:SetAllPoints()
MfBG:SetTexture(BACKGROUND_TEXTURE)

-- 主框架内第一个是pixelFrame
local PixelFrame = CreateFrame("Frame", "EZAssistedCombatIconFrame", EZ.MainFrame)
PixelFrame:SetSize(FRAME_SIZE, FRAME_SIZE)
PixelFrame:SetPoint("TOPLEFT", EZ.MainFrame, "TOPLEFT", 0, 0)
PixelFrame:Show()

EZ.PixelTexture = PixelFrame:CreateTexture();
EZ.PixelTexture:SetAllPoints();
EZ.PixelTexture:SetColorTexture(1, 1, 1, 1)


local IconFrame = CreateFrame("Frame", "EZAssistedCombatIconFrame", EZ.MainFrame)
IconFrame:SetSize(ICON_SIZE, ICON_SIZE)
IconFrame:SetPoint("TOPRIGHT", EZ.MainFrame, "TOPRIGHT", 0, 0)
IconFrame:Show()

EZ.IconIco = IconFrame:CreateTexture(nil, "ARTWORK")
EZ.IconIco:SetSize(ICON_SIZE, ICON_SIZE)
EZ.IconIco:SetPoint("CENTER", IconFrame, "CENTER")
EZ.IconIco:SetTexture(DEFAULT_ICON)
EZ.IconIco:Show()

local TitleFrame = CreateFrame("Frame", "EZAssistedCombatTitleFrame", EZ.MainFrame)
TitleFrame:SetPoint("BOTTOMLEFT", EZ.MainFrame, "BOTTOMLEFT", 0, 0)
TitleFrame:SetSize(FRAME_SIZE, PIX_WIDTH)
TitleFrame:Show()

EZ.TitleText = TitleFrame:CreateFontString(nil, "ARTWORK", "GameFontNormal")
local fontFile, _, _ = GameFontNormal:GetFont()
EZ.TitleText:SetAllPoints()
EZ.TitleText:SetText("推荐技能")
EZ.TitleText:SetJustifyH("CENTER")
EZ.TitleText:SetJustifyV("MIDDLE")
EZ.TitleText:SetFont(fontFile, GetUIScaleFactor(20), "")
EZ.TitleText:SetTextColor(1, 1, 1)
EZ.TitleText:Show()

EZ.Reset = function()
    EZ.PixelTexture:SetColorTexture(0, 0, 0, 1)
    EZ.TitleText:SetTextColor(1, 1, 1)
    EZ.TitleText:SetText("EzAC")
    EZ.IconIco:SetTexture(DEFAULT_ICON)
end

EZ.Reset()

EZ.SetColor = function(r, g, b)
    EZ.PixelTexture:SetColorTexture(r/ 255, g / 255, b / 255, 1)
    EZ.TitleText:SetTextColor((255-r)/ 255, (255-g)/ 255, (255-b)/ 255)
end

EZ.FrameSetMacro = function(icon,name,color)
    EZ.IconIco:SetTexture(icon)
    EZ.SetColor(color.r, color.g, color.b)
    EZ.TitleText:SetText(name)
end




