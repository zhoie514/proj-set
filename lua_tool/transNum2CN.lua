
--[[
    @desc: 数字转中文数字
    author:Bogey
    time:2019-06-17 14:41:49
    --@num: 
    @return:
]]
function string.toChineseNumber(num)
    local num = tonumber(num)
    local hzNum = {"零", "一", "二", "三", "四", "五", "六", "七", "八", "九"}
    local hzUnit = {"", "十", "百", "千"}
    local hzBigUnit = {"", "万", "亿"}

    num = string.reverse(tostring(num))

    local function getString(index, data)
        local len = #data
        local str = ""
        for i = len, 1, -1 do
            -- 两个连续的零或者末尾零，跳过
            if data[i] == "0" and (data[i - 1] == "0" or i == 1) then
            else
                --类似一十七，省略一，读十七
                if len == 2 and i == 2 and data[i] == "1" and index == 1 then
                else
                    str = str .. hzNum[tonumber(data[i]) + 1]
                end

                --单位，零没有单位
                if data[i] ~= "0" then
                    str = str .. hzUnit[i]
                end
            end
        end
        -- 大单位
        str = str .. hzBigUnit[index]
        return str
    end

    -- 拆分成4位一段
    local numTable = {}
    local len = string.len(num)
    for i = 1, len do
        local index = math.ceil(i / 4)
        if not numTable[index] then
            numTable[index] = {}
        end
        table.insert(numTable[index], string.sub(num, i, i))
    end

    -- 组合文字
    local str = ""
    for i,v in ipairs(numTable) do
        local rt = getString(i, v)
        str = rt .. str
    end
    return str
end

print(string.toChineseNumber(5110002))