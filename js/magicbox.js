// 魔法盒子游戏逻辑

class MagicBoxGame {
    constructor(gameInstance) {
        this.game = gameInstance;
        this.currentLevel = null;
        this.userAnswer = null;
        this.inputValue = '';
        this.animationSpeed = 1000; // 动画速度（毫秒）
        
        this.initializeElements();
        this.setupEventListeners();
    }
    
    // 初始化DOM元素
    initializeElements() {
        this.magicBoxContainer = DOMUtils.getElement('.magicbox-container');
        this.inputBox = DOMUtils.getElement('#magicInput');
        this.outputBox = DOMUtils.getElement('#magicOutput');
        this.ruleDisplay = DOMUtils.getElement('#magicRule');
        this.inputValue = DOMUtils.getElement('#inputValue');
        this.outputValue = DOMUtils.getElement('#outputValue');
        this.magicProcess = DOMUtils.getElement('#magicProcess');
        this.testButton = DOMUtils.getElement('#testMagicBox');
        this.inputField = DOMUtils.getElement('#userInput');
    }
    
    // 设置事件监听器
    setupEventListeners() {
        if (this.testButton) {
            this.testButton.addEventListener('click', this.testMagicBox.bind(this));
        }
        
        if (this.inputField) {
            this.inputField.addEventListener('input', this.handleInputChange.bind(this));
            this.inputField.addEventListener('keypress', this.handleKeyPress.bind(this));
        }
        
        // 点击输入框和输出框的交互
        if (this.inputBox) {
            this.inputBox.addEventListener('click', this.highlightInput.bind(this));
        }
        
        if (this.outputBox) {
            this.outputBox.addEventListener('click', this.highlightOutput.bind(this));
        }
    }
    
    // 加载关卡
    loadLevel(levelData) {
        this.currentLevel = levelData;
        this.userAnswer = null;
        this.inputValue = '';
        
        this.renderMagicBox();
        this.showRule();
        this.setupExamples();
        
        Debug.log('魔法盒子关卡加载:', levelData);
    }
    
    // 渲染魔法盒子
    renderMagicBox() {
        if (!this.currentLevel) return;
        
        const level = this.currentLevel;
        
        // 设置魔法盒子的视觉样式
        if (this.magicBoxContainer) {
            this.magicBoxContainer.className = `magicbox-container ${level.visual.style || 'default'}`;
        }
        
        // 显示当前问题
        if (this.inputValue && level.visual.input !== undefined) {
            this.inputValue.textContent = level.visual.input;
        }
        
        // 清空输出值（等待用户操作）
        if (this.outputValue) {
            this.outputValue.textContent = '?';
        }
        
        // 重置输入框
        if (this.inputField) {
            this.inputField.value = '';
            this.inputField.placeholder = level.placeholder || '请输入你的答案';
        }
    }
    
    // 显示规则
    showRule() {
        if (!this.ruleDisplay || !this.currentLevel) return;
        
        const level = this.currentLevel;
        let ruleText = '';
        
        // 根据关卡类型显示不同的规则提示
        switch (level.type) {
            case 'addition':
                ruleText = '魔法盒子会给输入的数字加上一个神秘数字';
                break;
            case 'subtraction':
                ruleText = '魔法盒子会从输入的数字中减去一个神秘数字';
                break;
            case 'multiplication':
                ruleText = '魔法盒子会把输入的数字乘以一个神秘数字';
                break;
            case 'division':
                ruleText = '魔法盒子会把输入的数字除以一个神秘数字';
                break;
            case 'mixed':
                ruleText = '魔法盒子有一个神秘的计算规则';
                break;
            default:
                ruleText = '观察输入和输出，找出魔法盒子的规律';
        }
        
        this.ruleDisplay.textContent = ruleText;
        
        // 添加闪烁动画
        AnimationUtils.addAnimation(this.ruleDisplay, 'animate-glow');
    }
    
    // 设置示例
    setupExamples() {
        if (!this.currentLevel || !this.currentLevel.examples) return;
        
        const examples = this.currentLevel.examples;
        
        // 显示示例（如果有的话）
        if (examples.length > 0) {
            this.showExamples(examples);
        }
    }
    
    // 显示示例
    showExamples(examples) {
        // 创建示例显示区域
        let exampleContainer = DOMUtils.getElement('#exampleContainer');
        if (!exampleContainer) {
            exampleContainer = DOMUtils.createElement('div', 'example-container');
            exampleContainer.id = 'exampleContainer';
            if (this.magicBoxContainer) {
                this.magicBoxContainer.appendChild(exampleContainer);
            }
        }
        
        exampleContainer.innerHTML = '<h4>示例：</h4>';
        
        examples.forEach((example, index) => {
            const exampleDiv = DOMUtils.createElement('div', 'example-item');
            exampleDiv.innerHTML = `
                <span class="example-input">${example.input}</span>
                <span class="arrow">→</span>
                <span class="example-output">${example.output}</span>
            `;
            exampleContainer.appendChild(exampleDiv);
            
            // 添加延迟动画
            setTimeout(() => {
                AnimationUtils.addAnimation(exampleDiv, 'animate-slide-in');
            }, index * 300);
        });
    }
    
    // 测试魔法盒子
    testMagicBox() {
        if (!this.inputField || !this.currentLevel) return;
        
        const inputValue = parseFloat(this.inputField.value);
        
        if (isNaN(inputValue)) {
            this.showFeedback('请输入一个有效的数字！', 'error');
            return;
        }
        
        // 计算输出值
        const outputValue = this.calculateOutput(inputValue);
        
        // 显示计算过程动画
        this.showCalculationAnimation(inputValue, outputValue);
        
        SoundManager.playClick();
    }
    
    // 计算输出值
    calculateOutput(input) {
        const level = this.currentLevel;
        if (!level || !level.rule) return input;
        
        const rule = level.rule;
        
        switch (rule.operation) {
            case 'add':
                return input + rule.value;
            case 'subtract':
                return input - rule.value;
            case 'multiply':
                return input * rule.value;
            case 'divide':
                return input / rule.value;
            case 'mixed':
                // 复合运算
                let result = input;
                rule.steps.forEach(step => {
                    switch (step.operation) {
                        case 'add':
                            result += step.value;
                            break;
                        case 'subtract':
                            result -= step.value;
                            break;
                        case 'multiply':
                            result *= step.value;
                            break;
                        case 'divide':
                            result /= step.value;
                            break;
                    }
                });
                return result;
            default:
                return input;
        }
    }
    
    // 显示计算过程动画
    showCalculationAnimation(input, output) {
        if (!this.magicProcess) return;
        
        // 清空之前的内容
        this.magicProcess.innerHTML = '';
        
        // 创建动画步骤
        const steps = this.getCalculationSteps(input, output);
        
        let stepIndex = 0;
        const showNextStep = () => {
            if (stepIndex < steps.length) {
                const stepDiv = DOMUtils.createElement('div', 'calculation-step');
                stepDiv.textContent = steps[stepIndex];
                this.magicProcess.appendChild(stepDiv);
                
                AnimationUtils.addAnimation(stepDiv, 'animate-fade-in');
                
                stepIndex++;
                setTimeout(showNextStep, this.animationSpeed / 2);
            } else {
                // 动画完成，更新输出值
                this.updateOutput(output);
            }
        };
        
        // 开始动画
        setTimeout(showNextStep, 200);
    }
    
    // 获取计算步骤
    getCalculationSteps(input, output) {
        const level = this.currentLevel;
        if (!level || !level.rule) return [`${input} → ${output}`];
        
        const rule = level.rule;
        const steps = [];
        
        steps.push(`输入: ${input}`);
        
        switch (rule.operation) {
            case 'add':
                steps.push(`${input} + ${rule.value}`);
                steps.push(`= ${output}`);
                break;
            case 'subtract':
                steps.push(`${input} - ${rule.value}`);
                steps.push(`= ${output}`);
                break;
            case 'multiply':
                steps.push(`${input} × ${rule.value}`);
                steps.push(`= ${output}`);
                break;
            case 'divide':
                steps.push(`${input} ÷ ${rule.value}`);
                steps.push(`= ${output}`);
                break;
            case 'mixed':
                let current = input;
                rule.steps.forEach((step, index) => {
                    const prev = current;
                    switch (step.operation) {
                        case 'add':
                            current += step.value;
                            steps.push(`${prev} + ${step.value} = ${current}`);
                            break;
                        case 'subtract':
                            current -= step.value;
                            steps.push(`${prev} - ${step.value} = ${current}`);
                            break;
                        case 'multiply':
                            current *= step.value;
                            steps.push(`${prev} × ${step.value} = ${current}`);
                            break;
                        case 'divide':
                            current /= step.value;
                            steps.push(`${prev} ÷ ${step.value} = ${current}`);
                            break;
                    }
                });
                break;
        }
        
        steps.push(`输出: ${output}`);
        return steps;
    }
    
    // 更新输出值
    updateOutput(value) {
        if (this.outputValue) {
            this.outputValue.textContent = value;
            AnimationUtils.addAnimation(this.outputValue, 'animate-bounce');
        }
        
        // 播放魔法音效
        SoundManager.playMagic();
    }
    
    // 处理输入变化
    handleInputChange(event) {
        this.inputValue = event.target.value;
    }
    
    // 处理按键事件
    handleKeyPress(event) {
        if (event.key === 'Enter') {
            this.testMagicBox();
        }
    }
    
    // 高亮输入框
    highlightInput() {
        if (this.inputBox) {
            AnimationUtils.addAnimation(this.inputBox, 'animate-highlight');
        }
    }
    
    // 高亮输出框
    highlightOutput() {
        if (this.outputBox) {
            AnimationUtils.addAnimation(this.outputBox, 'animate-highlight');
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
            case 'rule':
                // 检查用户是否理解了规则
                isCorrect = this.checkRuleUnderstanding(userAnswer);
                break;
        }
        
        this.handleLevelComplete(isCorrect);
        return isCorrect;
    }
    
    // 检查规则理解
    checkRuleUnderstanding(userAnswer) {
        const level = this.currentLevel;
        if (!level || !level.visual) return false;
        
        // 计算正确答案
        const correctAnswer = this.calculateOutput(level.visual.input);
        
        return MathUtils.checkAnswer(userAnswer, correctAnswer);
    }
    
    // 处理关卡完成
    handleLevelComplete(success) {
        if (success) {
            SoundManager.playSuccess();
            AnimationUtils.addAnimation(this.magicBoxContainer, 'animate-success');
            
            // 创建魔法粒子效果
            setTimeout(() => {
                AnimationUtils.createMagicParticles(this.magicBoxContainer);
            }, 500);
            
            this.showFeedback('太棒了！你发现了魔法盒子的秘密！', 'success');
        } else {
            SoundManager.playError();
            AnimationUtils.addAnimation(this.magicBoxContainer, 'animate-error');
            this.showFeedback('再试试看，仔细观察输入和输出的关系。', 'error');
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
        let feedbackElement = DOMUtils.getElement('#magicFeedback');
        if (!feedbackElement) {
            feedbackElement = DOMUtils.createElement('div', 'feedback-message');
            feedbackElement.id = 'magicFeedback';
            if (this.magicBoxContainer) {
                this.magicBoxContainer.appendChild(feedbackElement);
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
        
        let hint = level.hint || '观察示例，找出输入和输出之间的规律。';
        
        // 根据关卡类型提供更具体的提示
        if (level.examples && level.examples.length > 0) {
            const example = level.examples[0];
            hint += ` 比如：${example.input} 变成了 ${example.output}，想想是怎么变化的？`;
        }
        
        this.showFeedback(hint, 'hint');
        return hint;
    }
    
    // 重置关卡
    reset() {
        if (this.inputField) {
            this.inputField.value = '';
        }
        
        if (this.outputValue) {
            this.outputValue.textContent = '?';
        }
        
        if (this.magicProcess) {
            this.magicProcess.innerHTML = '';
        }
        
        // 清除反馈消息
        const feedbackElement = DOMUtils.getElement('#magicFeedback');
        if (feedbackElement) {
            feedbackElement.remove();
        }
        
        this.userAnswer = null;
        this.inputValue = '';
    }
    
    // 清理资源
    cleanup() {
        if (this.testButton) {
            this.testButton.removeEventListener('click', this.testMagicBox);
        }
        
        if (this.inputField) {
            this.inputField.removeEventListener('input', this.handleInputChange);
            this.inputField.removeEventListener('keypress', this.handleKeyPress);
        }
        
        if (this.inputBox) {
            this.inputBox.removeEventListener('click', this.highlightInput);
        }
        
        if (this.outputBox) {
            this.outputBox.removeEventListener('click', this.highlightOutput);
        }
    }
    
    // 获取当前状态
    getState() {
        return {
            inputValue: this.inputValue,
            userAnswer: this.userAnswer,
            currentOutput: this.outputValue ? this.outputValue.textContent : '?'
        };
    }
    
    // 设置状态
    setState(state) {
        if (state.inputValue && this.inputField) {
            this.inputField.value = state.inputValue;
            this.inputValue = state.inputValue;
        }
        
        if (state.userAnswer) {
            this.userAnswer = state.userAnswer;
        }
        
        if (state.currentOutput && this.outputValue) {
            this.outputValue.textContent = state.currentOutput;
        }
    }
    
    // 演示魔法盒子工作过程
    demonstrateRule() {
        const level = this.currentLevel;
        if (!level || !level.examples || level.examples.length === 0) return;
        
        const example = level.examples[0];
        
        // 设置输入值
        if (this.inputField) {
            this.inputField.value = example.input;
        }
        
        // 延迟执行测试
        setTimeout(() => {
            this.testMagicBox();
        }, 500);
    }
    
    // 获取解题步骤
    getSolutionSteps() {
        const level = this.currentLevel;
        if (!level) return [];
        
        const steps = [];
        
        if (level.examples && level.examples.length > 0) {
            steps.push('观察示例：');
            level.examples.forEach(example => {
                steps.push(`${example.input} → ${example.output}`);
            });
        }
        
        if (level.rule) {
            const rule = level.rule;
            switch (rule.operation) {
                case 'add':
                    steps.push(`规律：输入 + ${rule.value} = 输出`);
                    break;
                case 'subtract':
                    steps.push(`规律：输入 - ${rule.value} = 输出`);
                    break;
                case 'multiply':
                    steps.push(`规律：输入 × ${rule.value} = 输出`);
                    break;
                case 'divide':
                    steps.push(`规律：输入 ÷ ${rule.value} = 输出`);
                    break;
            }
        }
        
        if (level.visual && level.visual.input !== undefined) {
            const correctAnswer = this.calculateOutput(level.visual.input);
            steps.push(`所以：${level.visual.input} → ${correctAnswer}`);
        }
        
        return steps;
    }
}

// 导出类
if (typeof window !== 'undefined') {
    window.MagicBoxGame = MagicBoxGame;
}

if (typeof module !== 'undefined' && module.exports) {
    module.exports = MagicBoxGame;
}