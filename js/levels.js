// 关卡数据配置文件

const LEVEL_DATA = {
    // 第一阶段：天平游戏（8关）
    stage1: {
        name: "天平游戏",
        description: "通过天平理解等量关系",
        icon: "⚖️",
        totalLevels: 8,
        levels: [
            {
                id: 1,
                title: "认识天平",
                description: "观察天平的平衡状态",
                type: "balance",
                difficulty: 1,
                equation: "3 = 3",
                visual: {
                    left: ["apple", "apple", "apple"],
                    right: ["apple", "apple", "apple"]
                },
                question: "天平两边有相同数量的苹果，天平会怎样？",
                answer: "平衡",
                answerType: "choice",
                choices: ["向左倾斜", "向右倾斜", "平衡"],
                hint: "当两边重量相等时，天平会保持平衡",
                explanation: "天平两边都有3个苹果，重量相等，所以天平平衡。这就是等量关系：3 = 3"
            },
            {
                id: 2,
                title: "简单比较",
                description: "比较不同数量的物品",
                type: "balance",
                difficulty: 1,
                equation: "2 ≠ 4",
                visual: {
                    left: ["apple", "apple"],
                    right: ["apple", "apple", "apple", "apple"]
                },
                question: "左边2个苹果，右边4个苹果，天平会怎样？",
                answer: "向右倾斜",
                answerType: "choice",
                choices: ["向左倾斜", "向右倾斜", "平衡"],
                hint: "重的一边会下沉",
                explanation: "右边有4个苹果比左边的2个苹果重，所以天平向右倾斜"
            },
            {
                id: 3,
                title: "找平衡",
                description: "添加物品使天平平衡",
                type: "balance",
                difficulty: 2,
                equation: "2 + ? = 5",
                visual: {
                    left: ["apple", "apple"],
                    right: ["apple", "apple", "apple", "apple", "apple"]
                },
                question: "左边有2个苹果，右边有5个苹果。需要在左边加几个苹果才能平衡？",
                answer: 3,
                answerType: "number",
                hint: "想想：2 + ? = 5，?等于多少？",
                explanation: "左边有2个，右边有5个，需要加3个才能平衡：2 + 3 = 5"
            },
            {
                id: 4,
                title: "不同物品",
                description: "理解不同物品的等量关系",
                type: "balance",
                difficulty: 2,
                equation: "1橙子 = 2苹果",
                visual: {
                    left: ["orange"],
                    right: ["apple", "apple"]
                },
                question: "1个橙子和2个苹果平衡，那么1个橙子等于几个苹果？",
                answer: 2,
                answerType: "number",
                hint: "天平平衡说明两边重量相等",
                explanation: "天平平衡表示1个橙子的重量等于2个苹果的重量"
            },
            {
                id: 5,
                title: "混合计算",
                description: "多种物品的组合",
                type: "balance",
                difficulty: 3,
                equation: "1橙子 + 1苹果 = ?",
                visual: {
                    left: ["orange", "apple"],
                    right: []
                },
                question: "已知1个橙子=2个苹果，那么1个橙子+1个苹果等于几个苹果？",
                answer: 3,
                answerType: "number",
                hint: "先把橙子换成苹果，再计算总数",
                explanation: "1个橙子=2个苹果，所以1个橙子+1个苹果=2个苹果+1个苹果=3个苹果"
            },
            {
                id: 6,
                title: "逆向思考",
                description: "从结果推导过程",
                type: "balance",
                difficulty: 3,
                equation: "? + 2 = 7",
                visual: {
                    left: [],
                    right: ["apple", "apple", "apple", "apple", "apple", "apple", "apple"]
                },
                question: "右边有7个苹果，左边有2个苹果和一些橙子。如果1个橙子=2个苹果，左边有几个橙子？",
                answer: 2.5,
                answerType: "number",
                hint: "先算出需要多少个苹果，再换算成橙子",
                explanation: "需要7-2=5个苹果，5个苹果=2.5个橙子（但实际应该是整数，这里简化处理）"
            },
            {
                id: 7,
                title: "复杂平衡",
                description: "多步骤的平衡问题",
                type: "balance",
                difficulty: 4,
                equation: "2橙子 + 1苹果 = 1橙子 + ?苹果",
                visual: {
                    left: ["orange", "orange", "apple"],
                    right: ["orange"]
                },
                question: "左边：2个橙子+1个苹果，右边：1个橙子+?个苹果。需要几个苹果平衡？",
                answer: 3,
                answerType: "number",
                hint: "两边都减去1个橙子，看看剩下什么",
                explanation: "左边减去1个橙子剩下：1个橙子+1个苹果=2个苹果+1个苹果=3个苹果"
            },
            {
                id: 8,
                title: "天平大师",
                description: "综合运用天平知识",
                type: "balance",
                difficulty: 4,
                equation: "3橙子 = 2香蕉 + 2苹果",
                visual: {
                    left: ["orange", "orange", "orange"],
                    right: ["banana", "banana", "apple", "apple"]
                },
                question: "已知：1橙子=2苹果，1香蕉=3苹果。验证：3橙子是否等于2香蕉+2苹果？",
                answer: "是",
                answerType: "choice",
                choices: ["是", "否"],
                hint: "把所有物品都换算成苹果来比较",
                explanation: "3橙子=6苹果，2香蕉+2苹果=6苹果+2苹果=8苹果。所以不相等，答案是否"
            }
        ]
    },

    // 第二阶段：魔法盒子（10关）
    stage2: {
        name: "魔法盒子",
        description: "学习用字母表示未知数",
        icon: "📦",
        totalLevels: 10,
        levels: [
            {
                id: 1,
                title: "神秘盒子",
                description: "猜猜盒子里有什么",
                type: "magicbox",
                difficulty: 1,
                equation: "盒子 + 3 = 7",
                story: "小明有一个神秘的盒子，里面装着一些糖果。他又买了3颗糖果，现在总共有7颗糖果。",
                question: "盒子里原来有几颗糖果？",
                answer: 4,
                answerType: "number",
                hint: "7 - 3 = ?",
                explanation: "盒子里的糖果 + 3 = 7，所以盒子里原来有 7 - 3 = 4 颗糖果"
            },
            {
                id: 2,
                title: "盒子标记",
                description: "给盒子贴上标签",
                type: "magicbox",
                difficulty: 1,
                equation: "x + 5 = 12",
                story: "我们给神秘盒子贴上标签'x'，表示里面未知的数量。",
                question: "如果 x + 5 = 12，那么 x = ?",
                answer: 7,
                answerType: "number",
                hint: "x = 12 - 5",
                explanation: "这是我们的第一个方程！x + 5 = 12，所以 x = 12 - 5 = 7"
            },
            {
                id: 3,
                title: "减法盒子",
                description: "盒子里的东西被拿走了",
                type: "magicbox",
                difficulty: 2,
                equation: "x - 4 = 6",
                story: "盒子里原来有x个玩具，拿走了4个，还剩6个。",
                question: "盒子里原来有几个玩具？",
                answer: 10,
                answerType: "number",
                hint: "x = 6 + 4",
                explanation: "x - 4 = 6，所以 x = 6 + 4 = 10"
            },
            {
                id: 4,
                title: "倍数盒子",
                description: "盒子里的数量翻倍了",
                type: "magicbox",
                difficulty: 2,
                equation: "2x = 14",
                story: "魔法师把盒子里的东西变成了2倍，现在总共有14个。",
                question: "盒子里原来有几个？",
                answer: 7,
                answerType: "number",
                hint: "x = 14 ÷ 2",
                explanation: "2x = 14，所以 x = 14 ÷ 2 = 7"
            },
            {
                id: 5,
                title: "分数盒子",
                description: "盒子里只有一半",
                type: "magicbox",
                difficulty: 3,
                equation: "x/2 = 8",
                story: "盒子里的东西只剩下一半了，现在有8个。",
                question: "盒子里原来有几个？",
                answer: 16,
                answerType: "number",
                hint: "x = 8 × 2",
                explanation: "x/2 = 8，所以 x = 8 × 2 = 16"
            },
            {
                id: 6,
                title: "复合盒子",
                description: "多个步骤的变化",
                type: "magicbox",
                difficulty: 3,
                equation: "2x + 3 = 15",
                story: "盒子里的数量先翻倍，然后加3，结果是15。",
                question: "盒子里原来有几个？",
                answer: 6,
                answerType: "number",
                hint: "先算 2x = 15 - 3，再算 x",
                explanation: "2x + 3 = 15，所以 2x = 15 - 3 = 12，因此 x = 12 ÷ 2 = 6"
            },
            {
                id: 7,
                title: "两个盒子",
                description: "同样的两个盒子",
                type: "magicbox",
                difficulty: 3,
                equation: "x + x = 18",
                story: "有两个相同的盒子，里面装着同样数量的东西，总共18个。",
                question: "每个盒子里有几个？",
                answer: 9,
                answerType: "number",
                hint: "x + x = 2x = 18",
                explanation: "x + x = 2x = 18，所以 x = 18 ÷ 2 = 9"
            },
            {
                id: 8,
                title: "括号盒子",
                description: "盒子里的东西先加再乘",
                type: "magicbox",
                difficulty: 4,
                equation: "3(x + 2) = 21",
                story: "盒子里的数量加2后，再乘以3，结果是21。",
                question: "盒子里原来有几个？",
                answer: 5,
                answerType: "number",
                hint: "先算 x + 2 = 21 ÷ 3",
                explanation: "3(x + 2) = 21，所以 x + 2 = 21 ÷ 3 = 7，因此 x = 7 - 2 = 5"
            },
            {
                id: 9,
                title: "负数盒子",
                description: "盒子里的数可能是负数",
                type: "magicbox",
                difficulty: 4,
                equation: "x + 10 = 3",
                story: "盒子里的数加上10等于3。这个数可能是负数哦！",
                question: "盒子里的数是多少？",
                answer: -7,
                answerType: "number",
                hint: "x = 3 - 10",
                explanation: "x + 10 = 3，所以 x = 3 - 10 = -7。负数表示比0小的数"
            },
            {
                id: 10,
                title: "盒子大师",
                description: "最复杂的盒子问题",
                type: "magicbox",
                difficulty: 5,
                equation: "2(x - 3) + 5 = 17",
                story: "盒子里的数先减3，再乘以2，最后加5，结果是17。",
                question: "盒子里原来的数是多少？",
                answer: 9,
                answerType: "number",
                hint: "一步一步来：先算括号外的，再算括号内的",
                explanation: "2(x - 3) + 5 = 17，所以 2(x - 3) = 12，x - 3 = 6，x = 9"
            }
        ]
    },

    // 第三阶段：故事方程（12关）
    stage3: {
        name: "故事方程",
        description: "从生活故事中列方程",
        icon: "📚",
        totalLevels: 12,
        levels: [
            {
                id: 1,
                title: "买铅笔",
                description: "简单的购物问题",
                type: "story",
                difficulty: 1,
                story: "小明去文具店买铅笔。每支铅笔2元，他买了x支铅笔，总共花了10元。",
                question: "小明买了几支铅笔？",
                equation: "2x = 10",
                answer: 5,
                answerType: "number",
                hint: "每支2元，买x支，总共花了10元",
                explanation: "设买了x支铅笔，每支2元，所以2x = 10，x = 5支"
            },
            {
                id: 2,
                title: "分苹果",
                description: "平均分配问题",
                type: "story",
                difficulty: 1,
                story: "妈妈买了一些苹果，平均分给3个孩子，每个孩子分到4个苹果。",
                question: "妈妈总共买了几个苹果？",
                equation: "x ÷ 3 = 4",
                answer: 12,
                answerType: "number",
                hint: "总数除以人数等于每人分到的数量",
                explanation: "设总共有x个苹果，x ÷ 3 = 4，所以x = 4 × 3 = 12个"
            },
            {
                id: 3,
                title: "年龄问题",
                description: "简单的年龄关系",
                type: "story",
                difficulty: 2,
                story: "小红今年x岁，她比弟弟大5岁。弟弟今年8岁。",
                question: "小红今年几岁？",
                equation: "x - 5 = 8",
                answer: 13,
                answerType: "number",
                hint: "小红的年龄减去5等于弟弟的年龄",
                explanation: "设小红今年x岁，x - 5 = 8，所以x = 8 + 5 = 13岁"
            },
            {
                id: 4,
                title: "存钱罐",
                description: "储蓄问题",
                type: "story",
                difficulty: 2,
                story: "小华的存钱罐里有x元，他又存入15元，现在总共有32元。",
                question: "存钱罐里原来有多少元？",
                equation: "x + 15 = 32",
                answer: 17,
                answerType: "number",
                hint: "原来的钱加上新存的钱等于现在的总数",
                explanation: "设原来有x元，x + 15 = 32，所以x = 32 - 15 = 17元"
            },
            {
                id: 5,
                title: "跑步比赛",
                description: "速度和时间问题",
                type: "story",
                difficulty: 3,
                story: "小李以每分钟200米的速度跑了x分钟，总共跑了1000米。",
                question: "小李跑了几分钟？",
                equation: "200x = 1000",
                answer: 5,
                answerType: "number",
                hint: "速度 × 时间 = 距离",
                explanation: "设跑了x分钟，200x = 1000，所以x = 1000 ÷ 200 = 5分钟"
            },
            {
                id: 6,
                title: "班级活动",
                description: "集体活动费用",
                type: "story",
                difficulty: 3,
                story: "班级组织春游，每人交费25元。班里有x名学生，总共收到750元。",
                question: "班里有多少名学生？",
                equation: "25x = 750",
                answer: 30,
                answerType: "number",
                hint: "每人费用 × 人数 = 总费用",
                explanation: "设有x名学生，25x = 750，所以x = 750 ÷ 25 = 30名"
            },
            {
                id: 7,
                title: "图书馆借书",
                description: "借还书问题",
                type: "story",
                difficulty: 3,
                story: "图书馆原有x本书，借出120本后，还剩380本。",
                question: "图书馆原来有多少本书？",
                equation: "x - 120 = 380",
                answer: 500,
                answerType: "number",
                hint: "原有数量 - 借出数量 = 剩余数量",
                explanation: "设原有x本书，x - 120 = 380，所以x = 380 + 120 = 500本"
            },
            {
                id: 8,
                title: "水果店",
                description: "复合购买问题",
                type: "story",
                difficulty: 4,
                story: "水果店里苹果每斤3元，橙子每斤5元。小王买了2斤苹果和x斤橙子，总共花了21元。",
                question: "小王买了几斤橙子？",
                equation: "3 × 2 + 5x = 21",
                answer: 3,
                answerType: "number",
                hint: "苹果费用 + 橙子费用 = 总费用",
                explanation: "苹果费用：3 × 2 = 6元，设买了x斤橙子，6 + 5x = 21，5x = 15，x = 3斤"
            },
            {
                id: 9,
                title: "电影票",
                description: "优惠活动问题",
                type: "story",
                difficulty: 4,
                story: "电影院搞活动：买3张票送1张票。小明一共得到了x张票，其中买了9张。",
                question: "小明总共得到了几张票？",
                equation: "9 + 9 ÷ 3 = x",
                answer: 12,
                answerType: "number",
                hint: "买的票数 + 送的票数 = 总票数",
                explanation: "买了9张票，送了9 ÷ 3 = 3张票，总共x = 9 + 3 = 12张票"
            },
            {
                id: 10,
                title: "植树活动",
                description: "工作效率问题",
                type: "story",
                difficulty: 4,
                story: "学校植树活动，计划每天植x棵树，植树5天，总共植了100棵树。",
                question: "平均每天植几棵树？",
                equation: "5x = 100",
                answer: 20,
                answerType: "number",
                hint: "天数 × 每天数量 = 总数量",
                explanation: "设每天植x棵树，5x = 100，所以x = 100 ÷ 5 = 20棵"
            },
            {
                id: 11,
                title: "生日聚会",
                description: "复杂分配问题",
                type: "story",
                difficulty: 5,
                story: "小美生日聚会，买了一个大蛋糕。切成若干块后，每人分2块，还剩3块。如果每人分3块，就差5块。",
                question: "聚会有几个人？",
                equation: "2x + 3 = 3x - 5",
                answer: 8,
                answerType: "number",
                hint: "两种分法的蛋糕总数是相等的",
                explanation: "设有x个人，蛋糕总数：2x + 3 = 3x - 5，解得x = 8人"
            },
            {
                id: 12,
                title: "故事大师",
                description: "综合应用题",
                type: "story",
                difficulty: 5,
                story: "商店搞促销：买2送1。小张花了60元买笔，每支笔5元。按促销规则，他实际得到了多少支笔？",
                question: "小张实际得到了几支笔？",
                equation: "设买了x支，得到x + x÷2支，5x = 60",
                answer: 18,
                answerType: "number",
                hint: "先算买了几支，再算送了几支",
                explanation: "花60元，每支5元，买了60÷5=12支。买2送1，送了12÷2=6支。总共12+6=18支"
            }
        ]
    },

    // 第四阶段：挑战关卡（6关）
    stage4: {
        name: "挑战关卡",
        description: "综合运用所学知识",
        icon: "🏆",
        totalLevels: 6,
        levels: [
            {
                id: 1,
                title: "括号方程",
                description: "含括号的复杂方程",
                type: "challenge",
                difficulty: 4,
                equation: "3(x + 4) = 30",
                story: "工厂生产零件，每天生产(x + 4)个，生产3天，总共生产了30个零件。",
                question: "x等于多少？",
                answer: 6,
                answerType: "number",
                hint: "先算括号外的，再算括号内的",
                explanation: "3(x + 4) = 30，所以x + 4 = 10，x = 6"
            },
            {
                id: 2,
                title: "分数方程",
                description: "包含分数的方程",
                type: "challenge",
                difficulty: 4,
                equation: "x/3 + 5 = 9",
                story: "一袋糖果的三分之一加上5颗等于9颗。",
                question: "这袋糖果原来有几颗？",
                answer: 12,
                answerType: "number",
                hint: "先算x/3 = 9 - 5",
                explanation: "x/3 + 5 = 9，所以x/3 = 4，x = 12"
            },
            {
                id: 3,
                title: "比例问题",
                description: "比例关系的应用",
                type: "challenge",
                difficulty: 5,
                equation: "x : 12 = 3 : 4",
                story: "制作果汁，水和果汁浓缩液的比例是3:4。如果用了12毫升浓缩液，需要多少毫升水？",
                question: "需要多少毫升水？",
                answer: 9,
                answerType: "number",
                hint: "x/12 = 3/4",
                explanation: "根据比例：x/12 = 3/4，所以x = 12 × 3/4 = 9毫升"
            },
            {
                id: 4,
                title: "工程问题",
                description: "工作效率的综合应用",
                type: "challenge",
                difficulty: 5,
                equation: "x/20 + x/30 = 1",
                story: "甲单独完成一项工作需要20天，乙需要30天。两人合作需要几天完成？",
                question: "两人合作需要几天？",
                answer: 12,
                answerType: "number",
                hint: "甲的效率 + 乙的效率 = 合作效率",
                explanation: "设合作x天完成，x/20 + x/30 = 1，解得x = 12天"
            },
            {
                id: 5,
                title: "行程问题",
                description: "相遇和追及问题",
                type: "challenge",
                difficulty: 5,
                equation: "60x + 80x = 420",
                story: "两辆车从相距420公里的两地相向而行，甲车速度60公里/小时，乙车速度80公里/小时。",
                question: "几小时后两车相遇？",
                answer: 3,
                answerType: "number",
                hint: "相向而行，速度相加",
                explanation: "设x小时后相遇，(60 + 80)x = 420，140x = 420，x = 3小时"
            },
            {
                id: 6,
                title: "终极挑战",
                description: "最复杂的综合问题",
                type: "challenge",
                difficulty: 6,
                equation: "2(x - 5) + 3(x + 2) = 31",
                story: "商店有两种商品，A商品每个(x-5)元，买了2个；B商品每个(x+2)元，买了3个。总共花了31元。",
                question: "x等于多少？",
                answer: 7,
                answerType: "number",
                hint: "先展开括号，再合并同类项",
                explanation: "2(x-5) + 3(x+2) = 31，展开得：2x-10+3x+6 = 31，5x-4 = 31，5x = 35，x = 7"
            }
        ]
    }
};

// 获取关卡数据的工具函数
const LevelManager = {
    // 获取指定阶段的所有关卡
    getStage: function(stageNumber) {
        return LEVEL_DATA[`stage${stageNumber}`];
    },
    
    // 获取指定关卡
    getLevel: function(stageNumber, levelNumber) {
        const stage = this.getStage(stageNumber);
        return stage ? stage.levels[levelNumber - 1] : null;
    },
    
    // 获取指定阶段的所有关卡
    getLevelsByStage: function(stageNumber) {
        const stage = this.getStage(stageNumber);
        return stage ? stage.levels : [];
    },
    
    // 获取下一关卡
    getNextLevel: function(currentStage, currentLevel) {
        const stage = this.getStage(currentStage);
        if (!stage) return null;
        
        if (currentLevel < stage.totalLevels) {
            return {
                stage: currentStage,
                level: currentLevel + 1
            };
        } else if (currentStage < 4) {
            return {
                stage: currentStage + 1,
                level: 1
            };
        }
        return null; // 已完成所有关卡
    },
    
    // 检查关卡是否解锁
    isLevelUnlocked: function(stageNumber, levelNumber, progress) {
        if (stageNumber === 1 && levelNumber === 1) return true;
        
        // 检查前一关是否完成
        if (levelNumber > 1) {
            return progress[`stage${stageNumber}`] && 
                   progress[`stage${stageNumber}`][levelNumber - 1];
        } else {
            // 检查前一阶段是否完成
            const prevStage = this.getStage(stageNumber - 1);
            return prevStage && progress[`stage${stageNumber - 1}`] && 
                   progress[`stage${stageNumber - 1}`][prevStage.totalLevels];
        }
    },
    
    // 获取阶段进度
    getStageProgress: function(stageNumber, progress) {
        const stage = this.getStage(stageNumber);
        if (!stage) return { completed: 0, total: 0 };
        
        const stageProgress = progress[`stage${stageNumber}`] || {};
        let completed = 0;
        
        for (let i = 1; i <= stage.totalLevels; i++) {
            if (stageProgress[i]) completed++;
        }
        
        return {
            completed: completed,
            total: stage.totalLevels
        };
    },
    
    // 获取总体进度
    getTotalProgress: function(progress) {
        let totalCompleted = 0;
        let totalLevels = 0;
        
        for (let i = 1; i <= 4; i++) {
            const stageProgress = this.getStageProgress(i, progress);
            totalCompleted += stageProgress.completed;
            totalLevels += stageProgress.total;
        }
        
        return {
            completed: totalCompleted,
            total: totalLevels,
            percentage: Math.round((totalCompleted / totalLevels) * 100)
        };
    }
};

// 导出供其他文件使用
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { LEVEL_DATA, LevelManager };
}