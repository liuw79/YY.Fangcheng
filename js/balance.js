// 天平游戏逻辑

class BalanceGame {
    constructor(gameInstance) {
        this.game = gameInstance;
        this.currentLevel = null;
        this.draggedItem = null;
        this.leftItems = [];
        this.rightItems = [];
        this.itemWeights = {
            'apple': 1,
            'orange': 2,
            'banana': 1.5
        };
        this.isBalanced = false;
        this.userAnswer = null;
        
        this.initializeElements();
        this.setupEventListeners();
    }
    
    // 初始化DOM元素
    initializeElements() {
        this.balanceContainer = DOMUtils.getElement('.balance-container');
        this.balanceLeft = DOMUtils.getElement('#balanceLeft');
        this.balanceRight = DOMUtils.getElement('#balanceRight');
        this.leftItemsContainer = DOMUtils.getElement('#leftItems');
        this.rightItemsContainer = DOMUtils.getElement('#rightItems');
        this.itemBank = DOMUtils.getElement('#itemBank');
        this.balanceBeam = DOMUtils.getElement('.balance-beam');
    }
    
    // 设置事件监听器
    setupEventListeners() {
        // 拖拽事件
        if (this.itemBank) {
            this.itemBank.addEventListener('dragstart', this.handleDragStart.bind(this));
            this.itemBank.addEventListener('dragend', this.handleDragEnd.bind(this));
        }
        
        // 放置区域事件
        if (this.leftItemsContainer) {
            this.leftItemsContainer.addEventListener('dragover', this.handleDragOver.bind(this));
            this.leftItemsContainer.addEventListener('drop', this.handleDrop.bind(this));
        }
        
        if (this.rightItemsContainer) {
            this.rightItemsContainer.addEventListener('dragover', this.handleDragOver.bind(this));
            this.rightItemsContainer.addEventListener('drop', this.handleDrop.bind(this));
        }
    }
    
    // 加载关卡
    loadLevel(levelData) {
        this.currentLevel = levelData;
        this.leftItems = [...levelData.visual.left];
        this.rightItems = [...levelData.visual.right];
        
        this.renderBalance();
        this.renderItemBank();
        this.updateBalanceState();
        
        Debug.log('天平游戏关卡加载:', levelData);
    }
    
    // 渲染天平
    renderBalance() {
        if (!this.leftItemsContainer || !this.rightItemsContainer) return;
        
        // 清空容器
        this.leftItemsContainer.innerHTML = '';
        this.rightItemsContainer.innerHTML = '';
        
        // 渲染左边物品
        this.leftItems.forEach((item, index) => {
            const itemElement = this.createItemElement(item, `left-${index}`);
            this.leftItemsContainer.appendChild(itemElement);
        });
        
        // 渲染右边物品
        this.rightItems.forEach((item, index) => {
            const itemElement = this.createItemElement(item, `right-${index}`);
            this.rightItemsContainer.appendChild(itemElement);
        });
    }
    
    // 渲染物品银行
    renderItemBank() {
        if (!this.itemBank) return;
        
        this.itemBank.innerHTML = '';
        
        // 根据关卡类型显示不同的物品
        const availableItems = this.getAvailableItems();
        
        availableItems.forEach((item, index) => {
            const itemElement = this.createDraggableItem(item, `bank-${index}`);
            this.itemBank.appendChild(itemElement);
        });
    }
    
    // 获取可用物品
    getAvailableItems() {
        const level = this.currentLevel;
        if (!level) return [];
        
        // 根据关卡难度和类型返回不同的物品
        switch (level.difficulty) {
            case 1:
                return ['apple', 'apple', 'apple'];
            case 2:
                return ['apple', 'apple', 'orange'];
            case 3:
                return ['apple', 'apple', 'orange', 'banana'];
            default:
                return ['apple', 'orange', 'banana'];
        }
    }
    
    // 创建物品元素
    createItemElement(itemType, id) {
        const item = DOMUtils.createElement('div', `balance-item ${itemType}`);
        item.id = id;
        item.textContent = this.getItemEmoji(itemType);
        return item;
    }
    
    // 创建可拖拽物品
    createDraggableItem(itemType, id) {
        const item = DOMUtils.createElement('div', `draggable-item ${itemType}`);
        item.id = id;
        item.draggable = true;
        item.textContent = this.getItemEmoji(itemType);
        item.dataset.itemType = itemType;
        return item;
    }
    
    // 获取物品表情符号
    getItemEmoji(itemType) {
        const emojis = {
            'apple': '🍎',
            'orange': '🍊',
            'banana': '🍌'
        };
        return emojis[itemType] || '❓';
    }
    
    // 拖拽开始
    handleDragStart(event) {
        if (!event.target.classList.contains('draggable-item')) return;
        
        this.draggedItem = {
            type: event.target.dataset.itemType,
            element: event.target
        };
        
        event.target.classList.add('dragging');
        SoundManager.playClick();
        
        Debug.log('开始拖拽:', this.draggedItem.type);
    }
    
    // 拖拽结束
    handleDragEnd(event) {
        if (event.target.classList.contains('dragging')) {
            event.target.classList.remove('dragging');
        }
        this.draggedItem = null;
    }
    
    // 拖拽悬停
    handleDragOver(event) {
        event.preventDefault();
        event.currentTarget.classList.add('drop-zone-active');
    }
    
    // 放置物品
    handleDrop(event) {
        event.preventDefault();
        event.currentTarget.classList.remove('drop-zone-active');
        
        if (!this.draggedItem) return;
        
        const isLeftSide = event.currentTarget === this.leftItemsContainer;
        const itemType = this.draggedItem.type;
        
        // 添加物品到对应侧
        if (isLeftSide) {
            this.leftItems.push(itemType);
        } else {
            this.rightItems.push(itemType);
        }
        
        // 重新渲染天平
        this.renderBalance();
        this.updateBalanceState();
        
        // 播放放置音效
        SoundManager.playClick();
        
        // 检查是否完成
        this.checkCompletion();
        
        Debug.log('放置物品:', itemType, '到', isLeftSide ? '左侧' : '右侧');
    }
    
    // 更新天平状态
    updateBalanceState() {
        const leftWeight = this.calculateWeight(this.leftItems);
        const rightWeight = this.calculateWeight(this.rightItems);
        
        Debug.log('天平重量 - 左:', leftWeight, '右:', rightWeight);
        
        // 更新天平视觉状态
        this.updateBalanceVisual(leftWeight, rightWeight);
        
        // 更新平衡状态
        this.isBalanced = Math.abs(leftWeight - rightWeight) < 0.1;
    }
    
    // 计算重量
    calculateWeight(items) {
        return items.reduce((total, item) => {
            return total + (this.itemWeights[item] || 0);
        }, 0);
    }
    
    // 更新天平视觉效果
    updateBalanceVisual(leftWeight, rightWeight) {
        if (!this.balanceBeam) return;
        
        // 移除之前的动画类
        this.balanceBeam.classList.remove('balance-tilt-left', 'balance-tilt-right', 'balance-balanced');
        
        // 添加新的动画类
        setTimeout(() => {
            if (leftWeight > rightWeight) {
                this.balanceBeam.classList.add('balance-tilt-left');
            } else if (rightWeight > leftWeight) {
                this.balanceBeam.classList.add('balance-tilt-right');
            } else {
                this.balanceBeam.classList.add('balance-balanced');
            }
        }, 100);
    }
    
    // 检查完成条件
    checkCompletion() {
        const level = this.currentLevel;
        if (!level) return;
        
        let isComplete = false;
        
        switch (level.answerType) {
            case 'choice':
                // 选择题类型，需要用户选择答案
                break;
            case 'balance':
                // 平衡类型，检查天平是否平衡
                isComplete = this.isBalanced;
                break;
            default:
                // 数字类型，需要用户输入答案
                break;
        }
        
        if (isComplete) {
            this.handleLevelComplete(true);
        }
    }
    
    // 处理关卡完成
    handleLevelComplete(success) {
        if (success) {
            SoundManager.playSuccess();
            AnimationUtils.addAnimation(this.balanceContainer, 'animate-success');
            
            // 创建庆祝效果
            setTimeout(() => {
                AnimationUtils.createParticles(this.balanceContainer);
            }, 500);
        } else {
            SoundManager.playError();
            AnimationUtils.addAnimation(this.balanceContainer, 'animate-error');
        }
        
        // 通知游戏主逻辑
        if (this.game && this.game.handleAnswer) {
            setTimeout(() => {
                this.game.handleAnswer(success, this.userAnswer);
            }, 1000);
        }
    }
    
    // 检查答案
    checkAnswer(userAnswer) {
        const level = this.currentLevel;
        if (!level) return false;
        
        this.userAnswer = userAnswer;
        let isCorrect = false;
        
        switch (level.answerType) {
            case 'choice':
                isCorrect = userAnswer === level.answer;
                break;
            case 'number':
                isCorrect = MathUtils.checkAnswer(userAnswer, level.answer);
                break;
            case 'balance':
                isCorrect = this.isBalanced;
                break;
        }
        
        this.handleLevelComplete(isCorrect);
        return isCorrect;
    }
    
    // 获取提示
    getHint() {
        const level = this.currentLevel;
        if (!level) return '';
        
        SoundManager.playHint();
        return level.hint || '仔细观察天平的状态，思考等量关系。';
    }
    
    // 重置关卡
    reset() {
        if (this.currentLevel) {
            this.leftItems = [...this.currentLevel.visual.left];
            this.rightItems = [...this.currentLevel.visual.right];
            this.renderBalance();
            this.updateBalanceState();
        }
    }
    
    // 清理资源
    cleanup() {
        // 移除事件监听器
        if (this.itemBank) {
            this.itemBank.removeEventListener('dragstart', this.handleDragStart);
            this.itemBank.removeEventListener('dragend', this.handleDragEnd);
        }
        
        if (this.leftItemsContainer) {
            this.leftItemsContainer.removeEventListener('dragover', this.handleDragOver);
            this.leftItemsContainer.removeEventListener('drop', this.handleDrop);
        }
        
        if (this.rightItemsContainer) {
            this.rightItemsContainer.removeEventListener('dragover', this.handleDragOver);
            this.rightItemsContainer.removeEventListener('drop', this.handleDrop);
        }
    }
    
    // 获取当前状态
    getState() {
        return {
            leftItems: [...this.leftItems],
            rightItems: [...this.rightItems],
            isBalanced: this.isBalanced,
            leftWeight: this.calculateWeight(this.leftItems),
            rightWeight: this.calculateWeight(this.rightItems)
        };
    }
    
    // 设置状态（用于恢复游戏状态）
    setState(state) {
        if (state.leftItems) this.leftItems = [...state.leftItems];
        if (state.rightItems) this.rightItems = [...state.rightItems];
        
        this.renderBalance();
        this.updateBalanceState();
    }
    
    // 添加物品到指定侧（程序控制）
    addItem(itemType, side) {
        if (side === 'left') {
            this.leftItems.push(itemType);
        } else if (side === 'right') {
            this.rightItems.push(itemType);
        }
        
        this.renderBalance();
        this.updateBalanceState();
        this.checkCompletion();
    }
    
    // 移除物品
    removeItem(side, index) {
        if (side === 'left' && index < this.leftItems.length) {
            this.leftItems.splice(index, 1);
        } else if (side === 'right' && index < this.rightItems.length) {
            this.rightItems.splice(index, 1);
        }
        
        this.renderBalance();
        this.updateBalanceState();
    }
    
    // 获取解题步骤（用于教学）
    getSolutionSteps() {
        const level = this.currentLevel;
        if (!level) return [];
        
        const steps = [];
        const leftWeight = this.calculateWeight(this.leftItems);
        const rightWeight = this.calculateWeight(this.rightItems);
        
        steps.push(`左边重量：${leftWeight}`);
        steps.push(`右边重量：${rightWeight}`);
        
        if (leftWeight === rightWeight) {
            steps.push('天平平衡：左边 = 右边');
        } else if (leftWeight > rightWeight) {
            steps.push('天平向左倾斜：左边 > 右边');
        } else {
            steps.push('天平向右倾斜：左边 < 右边');
        }
        
        return steps;
    }
}

// 导出类
if (typeof window !== 'undefined') {
    window.BalanceGame = BalanceGame;
}

if (typeof module !== 'undefined' && module.exports) {
    module.exports = BalanceGame;
}