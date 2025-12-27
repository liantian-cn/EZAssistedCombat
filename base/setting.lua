local addonName, EZ = ...

local category = Settings.RegisterVerticalLayoutCategory(addonName)
Settings.RegisterAddOnCategory(category)

if not EZAssistedCombatVars then
    EZAssistedCombatVars = {}
end

if not EZAssistedCombatVars.EzFPS then
    EZAssistedCombatVars.EzFPS = 20
end


do
    local name = "刷新率"
    local tooltip = "设置EZAssistedCombat的每秒刷新速度，是否占用过多CPU，取决于脚本内容"
    local variable = "EzFPS"
    local defaultValue = 20
    local minValue = 10
    local maxValue = 60
    local step = 5
    local function GetValue()
        return EZAssistedCombatVars.EzFPS
    end

    local function SetValue(value)
        EZAssistedCombatVars.EzFPS = value
    end

    local setting = Settings.RegisterProxySetting(category, variable, type(defaultValue), name, defaultValue, GetValue, SetValue)
    local options = Settings.CreateSliderOptions(minValue, maxValue, step)
    options:SetLabelFormatter(MinimalSliderWithSteppersMixin.Label.Right);
    Settings.CreateSlider(category, setting, options, tooltip)
end