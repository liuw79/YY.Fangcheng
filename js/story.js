// 故事方程游戏逻辑

class StoryGame {
    constructor(gameInstance) {
        this.game = gameInstance;
        this.currentLevel = null;
        this.userAnswer = null;
        this.storyProgress = 0;
        this.storySteps = [];
        this.currentStep = 0;
        this.isAnimating = false;
        
        this.initializeElements();
        this.setupEventListeners();
    }
    
    // 初始化DOM元素
    initializeElements() {
        this.storyContainer = DOMUtils.getElement('.story-container');
        this.storyText = DOMUtils.getElement('#storyText');
        this.storyImage = DOMUtils.getElement('#storyImage');
        this.questionArea = DOMUtils.getElement('#questionArea');
        this.equationBuilder = DOMUtils.getElement('#equationBuilder');
        this.nextStoryButton = DOMUtils.getElement('#nextStory');
        this.prevStoryButton = DOMUtils.getElement('#prevStory');
        this.storyProgress = DOMUtils.getElement('#storyProgress');
        this.characterContainer = DOMUtils.getElement('#characterContainer');
    }
    
    // 设置事件监听器
    setupEventListeners() {
        if (this.nextStoryButton) {
            this.nextStoryButton.addEventListener('click', this.nextStoryStep.bind(this));
        }
        
        if (this.prevStoryButton) {
            this.prevStoryButton.addEventListener('click', this.prevStoryStep.bind(this));
        }
        
        // 方程构建器事件
        if (this.equationBuilder) {
            this.equationBuilder.addEventListener('click', this.handleEquationClick.bind(this));
        }
    }
    
    // 加载关卡
    loadLevel(levelData) {
        this.currentLevel = levelData;
        this.userAnswer = null;
        this.currentStep = 0;
        this.storySteps = levelData.story ? levelData.story.steps : [];
        
        this.renderStory();
        this.setupEquationBuilder();
        this.updateProgress();
        
        Debug.log('故事方程关卡加载:', levelData);
    }
    
    // 渲染故事
    renderStory() {
        if (!this.currentLevel || !this.storySteps.length) return;
        
        const currentStoryStep = this.storySteps[this.currentStep];
        
        // 更新故事文本
        this.updateStoryText(currentStoryStep.text);
        
        // 更新故事图片
        this.updateStoryImage(currentStoryStep.image);
        
        // 更新角色
        this.updateCharacters(currentStoryStep.characters);
        
        // 更新问题区域
        this.updateQuestionArea(currentStoryStep);
        
        // 更新导航按钮状态
        this.updateNavigationButtons();
    }
    
    // 更新故事文本
    updateStoryText(text) {
        if (!this.storyText || !text) return;
        
        // 清空当前文本
        this.storyText.innerHTML = '';
        
        // 打字机效果
        this.typewriterEffect(this.storyText, text, 50);
    }
    
    // 打字机效果
    typewriterEffect(element, text, speed = 50) {
        if (this.isAnimating) return;
        
        this.isAnimating = true;
        let index = 0;
        
        const typeChar = () => {
            if (index < text.length) {
                element.textContent += text.charAt(index);
                index++;
                setTimeout(typeChar, speed);
            } else {
                this.isAnimating = false;
                // 文本完成后播放音效
                SoundManager.playStoryComplete();
            }
        };
        
        typeChar();
    }
    
    // 更新故事图片
    updateStoryImage(imagePath) {
        if (!this.storyImage) return;
        
        if (imagePath) {
            this.storyImage.src = imagePath;
            this.storyImage.style.display = 'block';
            AnimationUtils.addAnimation(this.storyImage, 'animate-fade-in');
        } else {
            this.storyImage.style.display = 'none';
        }
    }
    
    // 更新角色
    updateCharacters(characters) {
        if (!this.characterContainer || !characters) return;
        
        this.characterContainer.innerHTML = '';
        
        characters.forEach((character, index) => {
            const characterDiv = DOMUtils.createElement('div', `character ${character.name}`);
            characterDiv.innerHTML = `
                <div class="character-avatar">${character.avatar}</div>
                <div class="character-name">${character.name}</div>
                ${character.speech ? `<div class="character-speech">${character.speech}</div>` : ''}
            `;
            
            this.characterContainer.appendChild(characterDiv);
            
            // 添加延迟动画
            setTimeout(() => {
                AnimationUtils.addAnimation(characterDiv, 'animate-slide-in');
            }, index * 200);
        });
    }
    
    // 更新问题区域
    updateQuestionArea(storyStep) {
        if (!this.questionArea) return;
        
        if (storyStep.question) {
            this.questionArea.innerHTML = `
                <div class="question-text">${storyStep.question}</div>
                <div class="question-hint">${storyStep.hint || ''}</div>
            `;
            this.questionArea.style.display = 'block';
            AnimationUtils.addAnimation(this.questionArea, 'animate-slide-up');
        } else {
            this.questionArea.style.display = 'none';
        }
    }
    
    // 设置方程构建器
    setupEquationBuilder() {
        if (!this.equationBuilder || !this.currentLevel) return;
        
        const level = this.currentLevel;
        
        // 清空构建器
        this.equationBuilder.innerHTML = '';
        
        // 创建方程构建区域
        const builderArea = DOMUtils.createElement('div', 'equation-builder-area');
        
        // 左侧表达式
        const leftSide = DOMUtils.createElement('div', 'equation-side left-side');
        leftSide.innerHTML = '<span class="side-label">左边：</span><div class="equation-parts" data-side="left"></div>';
        
        // 等号
        const equalSign = DOMUtils.createElement('div', 'equal-sign');
        equalSign.textContent = '=';
        
        // 右侧表达式
        const rightSide = DOMUtils.createElement('div', 'equation-side right-side');
        rightSide.innerHTML = '<span class="side-label">右边：</span><div class="equation-parts" data-side="right"></div>';
        
        builderArea.appendChild(leftSide);
        builderArea.appendChild(equalSign);
        builderArea.appendChild(rightSide);
        
        // 组件库
        const componentLibrary = this.createComponentLibrary();
        
        this.equationBuilder.appendChild(builderArea);
        this.equationBuilder.appendChild(componentLibrary);
        
        // 设置拖拽功能
        this.setupDragAndDrop();
    }
    
    // 创建组件库
    createComponentLibrary() {
        const library = DOMUtils.createElement('div', 'component-library');
        library.innerHTML = '<h4>拖拽下面的组件来构建方程：</h4>';
        
        const componentsContainer = DOMUtils.createElement('div', 'components-container');
        
        // 基础组件
        const components = [
            { type: 'number', value: '1', label: '数字1' },
            { type: 'number', value: '2', label: '数字2' },
            { type: 'number', value: '3', label: '数字3' },
            { type: 'number', value: '5', label: '数字5' },
            { type: 'number', value: '10', label: '数字10' },
            { type: 'variable', value: 'x', label: '未知数x' },
            { type: 'operator', value: '+', label: '加号' },
            { type: 'operator', value: '-', label: '减号' },
            { type: 'operator', value: '×', label: '乘号' },
            { type: 'operator', value: '÷', label: '除号' }
        ];
        
        // 根据关卡难度调整可用组件
        const availableComponents = this.getAvailableComponents(components);
        
        availableComponents.forEach(component => {
            const componentDiv = DOMUtils.createElement('div', `component ${component.type}`);
            componentDiv.draggable = true;
            componentDiv.dataset.type = component.type;
            componentDiv.dataset.value = component.value;
            componentDiv.textContent = component.value;
            componentDiv.title = component.label;
            
            componentsContainer.appendChild(componentDiv);
        });
        
        library.appendChild(componentsContainer);
        return library;
    }
    
    // 获取可用组件
    getAvailableComponents(allComponents) {
        const level = this.currentLevel;
        if (!level) return allComponents;
        
        // 根据关卡难度过滤组件
        switch (level.difficulty) {
            case 1:
                // 简单：只有基础数字和加减
                return allComponents.filter(c => 
                    (c.type === 'number' && parseInt(c.value) <= 5) ||
                    c.type === 'variable' ||
                    (c.type === 'operator' && ['+', '-'].includes(c.value))
                );
            case 2:
                // 中等：添加更多数字和乘除
                return allComponents.filter(c => 
                    (c.type === 'number' && parseInt(c.value) <= 10) ||
                    c.type === 'variable' ||
                    c.type === 'operator'
                );
            default:
                // 困难：所有组件
                return allComponents;
        }
    }
    
    // 设置拖拽功能
    setupDragAndDrop() {
        const components = this.equationBuilder.querySelectorAll('.component');
        const dropZones = this.equationBuilder.querySelectorAll('.equation-parts');
        
        // 组件拖拽事件
        components.forEach(component => {
            component.addEventListener('dragstart', this.handleDragStart.bind(this));
            component.addEventListener('dragend', this.handleDragEnd.bind(this));
        });
        
        // 放置区域事件
        dropZones.forEach(zone => {
            zone.addEventListener('dragover', this.handleDragOver.bind(this));
            zone.addEventListener('drop', this.handleDrop.bind(this));
        });
    }
    
    // 拖拽开始
    handleDragStart(event) {
        if (!event.target.classList.contains('component')) return;
        
        event.dataTransfer.setData('text/plain', JSON.stringify({
            type: event.target.dataset.type,
            value: event.target.dataset.value
        }));
        
        event.target.classList.add('dragging');
        SoundManager.playClick();
    }
    
    // 拖拽结束
    handleDragEnd(event) {
        event.target.classList.remove('dragging');
    }
    
    // 拖拽悬停
    handleDragOver(event) {
        event.preventDefault();
        event.currentTarget.classList.add('drop-zone-active');
    }
    
    // 放置组件
    handleDrop(event) {
        event.preventDefault();
        event.currentTarget.classList.remove('drop-zone-active');
        
        try {
            const componentData = JSON.parse(event.dataTransfer.getData('text/plain'));
            
            // 创建新的方程部分
            const equationPart = DOMUtils.createElement('span', `equation-part ${componentData.type}`);
            equationPart.textContent = componentData.value;
            equationPart.dataset.type = componentData.type;
            equationPart.dataset.value = componentData.value;
            
            // 添加删除功能
            equationPart.addEventListener('click', this.removeEquationPart.bind(this));
            
            event.currentTarget.appendChild(equationPart);
            
            AnimationUtils.addAnimation(equationPart, 'animate-bounce');
            SoundManager.playSuccess();
            
            // 检查方程是否完整
            this.checkEquationCompletion();
            
        } catch (error) {
            Debug.error('放置组件失败:', error);
        }
    }
    
    // 移除方程部分
    removeEquationPart(event) {
        const part = event.target;
        AnimationUtils.addAnimation(part, 'animate-fade-out');
        
        setTimeout(() => {
            part.remove();
            this.checkEquationCompletion();
        }, 300);
        
        SoundManager.playClick();
    }
    
    // 检查方程完整性
    checkEquationCompletion() {
        const leftParts = this.equationBuilder.querySelectorAll('[data-side="left"] .equation-part');
        const rightParts = this.equationBuilder.querySelectorAll('[data-side="right"] .equation-part');
        
        // 检查是否两边都有内容
        if (leftParts.length > 0 && rightParts.length > 0) {
            // 显示检查按钮
            this.showCheckButton();
        } else {
            // 隐藏检查按钮
            this.hideCheckButton();
        }
    }
    
    // 显示检查按钮
    showCheckButton() {
        let checkButton = DOMUtils.getElement('#checkEquation');
        if (!checkButton) {
            checkButton = DOMUtils.createElement('button', 'check-equation-btn');
            checkButton.id = 'checkEquation';
            checkButton.textContent = '检查方程';
            checkButton.addEventListener('click', this.checkEquation.bind(this));
            
            if (this.equationBuilder) {
                this.equationBuilder.appendChild(checkButton);
            }
        }
        
        checkButton.style.display = 'block';
        AnimationUtils.addAnimation(checkButton, 'animate-slide-up');
    }
    
    // 隐藏检查按钮
    hideCheckButton() {
        const checkButton = DOMUtils.getElement('#checkEquation');
        if (checkButton) {
            checkButton.style.display = 'none';
        }
    }
    
    // 检查方程
    checkEquation() {
        const userEquation = this.getUserEquation();
        const isCorrect = this.validateEquation(userEquation);
        
        this.userAnswer = userEquation;
        this.handleLevelComplete(isCorrect);
    }
    
    // 获取用户构建的方程
    getUserEquation() {
        const leftParts = Array.from(this.equationBuilder.querySelectorAll('[data-side="left"] .equation-part'));
        const rightParts = Array.from(this.equationBuilder.querySelectorAll('[data-side="right"] .equation-part'));
        
        const leftExpression = leftParts.map(part => part.dataset.value).join(' ');
        const rightExpression = rightParts.map(part => part.dataset.value).join(' ');
        
        return {
            left: leftExpression,
            right: rightExpression,
            full: `${leftExpression} = ${rightExpression}`
        };
    }
    
    // 验证方程
    validateEquation(userEquation) {
        const level = this.currentLevel;
        if (!level || !level.equation) return false;
        
        // 简单的字符串匹配（可以扩展为更复杂的数学验证）
        const correctEquation = level.equation;
        
        // 检查是否包含必要的元素
        const hasVariable = userEquation.full.includes('x');
        const hasNumbers = /\d/.test(userEquation.full);
        const hasOperators = /[+\-×÷]/.test(userEquation.full);
        
        // 基础验证
        if (!hasVariable || !hasNumbers) {
            return false;
        }
        
        // 更详细的验证可以在这里添加
        // 例如：解方程并检查答案是否正确
        
        return this.checkEquationMeaning(userEquation, correctEquation);
    }
    
    // 检查方程含义
    checkEquationMeaning(userEquation, correctEquation) {
        // 这里可以实现更复杂的方程语义检查
        // 暂时使用简单的模式匹配
        
        const userPattern = this.extractEquationPattern(userEquation.full);
        const correctPattern = this.extractEquationPattern(correctEquation);
        
        return userPattern === correctPattern;
    }
    
    // 提取方程模式
    extractEquationPattern(equation) {
        // 简化方程为模式，例如 "x + 3 = 8" -> "x+n=n"
        return equation
            .replace(/\d+/g, 'n')  // 数字替换为n
            .replace(/\s+/g, '')   // 移除空格
            .toLowerCase();
    }
    
    // 下一个故事步骤
    nextStoryStep() {
        if (this.currentStep < this.storySteps.length - 1) {
            this.currentStep++;
            this.renderStory();
            this.updateProgress();
            SoundManager.playClick();
        }
    }
    
    // 上一个故事步骤
    prevStoryStep() {
        if (this.currentStep > 0) {
            this.currentStep--;
            this.renderStory();
            this.updateProgress();
            SoundManager.playClick();
        }
    }
    
    // 更新进度
    updateProgress() {
        if (!this.storyProgress) return;
        
        const progress = ((this.currentStep + 1) / this.storySteps.length) * 100;
        this.storyProgress.style.width = `${progress}%`;
        
        // 更新进度文本
        const progressText = DOMUtils.getElement('#progressText');
        if (progressText) {
            progressText.textContent = `${this.currentStep + 1} / ${this.storySteps.length}`;
        }
    }
    
    // 更新导航按钮
    updateNavigationButtons() {
        if (this.prevStoryButton) {
            this.prevStoryButton.disabled = this.currentStep === 0;
        }
        
        if (this.nextStoryButton) {
            this.nextStoryButton.disabled = this.currentStep === this.storySteps.length - 1;
        }
    }
    
    // 处理方程点击
    handleEquationClick(event) {
        // 处理方程构建器中的点击事件
        if (event.target.classList.contains('equation-part')) {
            AnimationUtils.addAnimation(event.target, 'animate-highlight');
        }
    }
    
    // 处理关卡完成
    handleLevelComplete(success) {
        if (success) {
            SoundManager.playSuccess();
            AnimationUtils.addAnimation(this.storyContainer, 'animate-success');
            
            // 创建庆祝效果
            setTimeout(() => {
                AnimationUtils.createParticles(this.storyContainer);
            }, 500);
            
            this.showFeedback('太棒了！你成功列出了正确的方程！', 'success');
        } else {
            SoundManager.playError();
            AnimationUtils.addAnimation(this.storyContainer, 'animate-error');
            this.showFeedback('方程还不太对，再想想故事中的数量关系。', 'error');
        }
        
        // 通知游戏主逻辑
        if (this.game && this.game.handleAnswer) {
            setTimeout(() => {
                this.game.handleAnswer(success, this.userAnswer);
            }, 1000);
        }
    }
    
    // 显示反馈
    showFeedback(message, type) {
        let feedbackElement = DOMUtils.getElement('#storyFeedback');
        if (!feedbackElement) {
            feedbackElement = DOMUtils.createElement('div', 'feedback-message');
            feedbackElement.id = 'storyFeedback';
            if (this.storyContainer) {
                this.storyContainer.appendChild(feedbackElement);
            }
        }
        
        feedbackElement.textContent = message;
        feedbackElement.className = `feedback-message ${type}`;
        
        AnimationUtils.addAnimation(feedbackElement, 'animate-slide-in');
        
        // 3秒后自动隐藏
        setTimeout(() => {
            AnimationUtils.addAnimation(feedbackElement, 'animate-fade-out');
        }, 3000);
    }
    
    // 获取提示
    getHint() {
        const level = this.currentLevel;
        if (!level) return '';
        
        SoundManager.playHint();
        
        const currentStoryStep = this.storySteps[this.currentStep];
        let hint = level.hint || '仔细阅读故事，找出数量之间的关系。';
        
        if (currentStoryStep && currentStoryStep.hint) {
            hint = currentStoryStep.hint;
        }
        
        this.showFeedback(hint, 'hint');
        return hint;
    }
    
    // 重置关卡
    reset() {
        this.currentStep = 0;
        this.userAnswer = null;
        
        // 清空方程构建器
        const equationParts = this.equationBuilder.querySelectorAll('.equation-part');
        equationParts.forEach(part => part.remove());
        
        // 隐藏检查按钮
        this.hideCheckButton();
        
        // 重新渲染故事
        this.renderStory();
        this.updateProgress();
        
        // 清除反馈消息
        const feedbackElement = DOMUtils.getElement('#storyFeedback');
        if (feedbackElement) {
            feedbackElement.remove();
        }
    }
    
    // 清理资源
    cleanup() {
        if (this.nextStoryButton) {
            this.nextStoryButton.removeEventListener('click', this.nextStoryStep);
        }
        
        if (this.prevStoryButton) {
            this.prevStoryButton.removeEventListener('click', this.prevStoryStep);
        }
        
        if (this.equationBuilder) {
            this.equationBuilder.removeEventListener('click', this.handleEquationClick);
        }
    }
    
    // 获取当前状态
    getState() {
        return {
            currentStep: this.currentStep,
            userAnswer: this.userAnswer,
            userEquation: this.getUserEquation()
        };
    }
    
    // 设置状态
    setState(state) {
        if (state.currentStep !== undefined) {
            this.currentStep = state.currentStep;
            this.renderStory();
            this.updateProgress();
        }
        
        if (state.userAnswer) {
            this.userAnswer = state.userAnswer;
        }
    }
    
    // 获取解题步骤
    getSolutionSteps() {
        const level = this.currentLevel;
        if (!level) return [];
        
        const steps = [];
        
        if (level.story && level.story.steps) {
            steps.push('故事分析：');
            level.story.steps.forEach((step, index) => {
                if (step.analysis) {
                    steps.push(`${index + 1}. ${step.analysis}`);
                }
            });
        }
        
        if (level.equation) {
            steps.push(`正确方程：${level.equation}`);
        }
        
        if (level.explanation) {
            steps.push(`解释：${level.explanation}`);
        }
        
        return steps;
    }
}

// 导出类
if (typeof window !== 'undefined') {
    window.StoryGame = StoryGame;
}

if (typeof module !== 'undefined' && module.exports) {
    module.exports = StoryGame;
}