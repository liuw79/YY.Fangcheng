// 游戏主逻辑

class EquationGame {
    constructor() {
        this.currentStage = 1; // 当前阶段 (1-4)
        this.currentLevel = 1; // 当前关卡
        this.gameState = 'start'; // start, playing, paused, completed
        this.score = 0;
        this.lives = 3;
        this.hints = 3;
        this.startTime = null;
        this.gameData = null;
        
        // 游戏模块
        this.balanceGame = null;
        this.magicBoxGame = null;
        this.storyGame = null;
        
        // 用户进度
        this.userProgress = {
            unlockedStages: 1,
            unlockedLevels: { 1: 1, 2: 1, 3: 1, 4: 1 },
            completedLevels: [],
            scores: {},
            achievements: [],
            totalPlayTime: 0
        };
        
        this.initializeGame();
    }
    
    // 公共初始化方法
    init() {
        return this.initializeGame();
    }
    
    // 初始化游戏
    async initializeGame() {
        try {
            // 加载用户进度
            this.loadUserProgress();
            
            // 初始化DOM元素
            this.initializeElements();
            
            // 设置事件监听器
            this.setupEventListeners();
            
            // 初始化游戏模块
            this.initializeGameModules();
            
            // 显示开始界面
            this.showStartScreen();
            
            Debug.log('游戏初始化完成');
            
        } catch (error) {
            Debug.error('游戏初始化失败:', error);
            this.showError('游戏初始化失败，请刷新页面重试。');
        }
    }
    
    // 初始化DOM元素
    initializeElements() {
        // 主要界面元素
        this.startScreen = DOMUtils.getElement('#startScreen');
        this.gameScreen = DOMUtils.getElement('#gameScreen');
        this.resultScreen = DOMUtils.getElement('#resultScreen');
        this.helpScreen = DOMUtils.getElement('#helpScreen');
        
        // 游戏控制元素
        this.startButton = DOMUtils.getElement('#startGame');
        this.helpButton = DOMUtils.getElement('#showHelp');
        this.backButton = DOMUtils.getElement('#backToStart');
        this.pauseButton = DOMUtils.getElement('#pauseGame');
        this.hintButton = DOMUtils.getElement('#getHint');
        this.resetButton = DOMUtils.getElement('#resetLevel');
        
        // 阶段选择元素
        this.stageCards = DOMUtils.getElements('.stage-card');
        
        // 游戏信息元素
        this.scoreDisplay = DOMUtils.getElement('#scoreDisplay');
        this.livesDisplay = DOMUtils.getElement('#livesDisplay');
        this.hintsDisplay = DOMUtils.getElement('#hintsDisplay');
        this.levelDisplay = DOMUtils.getElement('#levelDisplay');
        this.progressBar = DOMUtils.getElement('#progressBar');
        
        // 答题区域
        this.answerArea = DOMUtils.getElement('#answerArea');
        this.submitButton = DOMUtils.getElement('#submitAnswer');
        this.answerInput = DOMUtils.getElement('#answerInput');
        
        // 反馈区域
        this.feedbackArea = DOMUtils.getElement('#feedbackArea');
    }
    
    // 设置事件监听器
    setupEventListeners() {
        // 开始游戏
        if (this.startButton) {
            this.startButton.addEventListener('click', this.showStageSelection.bind(this));
        }
        
        // 帮助
        if (this.helpButton) {
            this.helpButton.addEventListener('click', this.showHelp.bind(this));
        }
        
        // 返回开始界面
        if (this.backButton) {
            this.backButton.addEventListener('click', this.showStartScreen.bind(this));
        }
        
        // 游戏控制
        if (this.pauseButton) {
            this.pauseButton.addEventListener('click', this.togglePause.bind(this));
        }
        
        if (this.hintButton) {
            this.hintButton.addEventListener('click', this.showHint.bind(this));
        }
        
        if (this.resetButton) {
            this.resetButton.addEventListener('click', this.resetLevel.bind(this));
        }
        
        // 阶段选择
        this.stageCards.forEach((card, index) => {
            card.addEventListener('click', () => this.selectStage(index + 1));
        });
        
        // 答题
        if (this.submitButton) {
            this.submitButton.addEventListener('click', this.submitAnswer.bind(this));
        }
        
        if (this.answerInput) {
            this.answerInput.addEventListener('keypress', (event) => {
                if (event.key === 'Enter') {
                    this.submitAnswer();
                }
            });
        }
        
        // 键盘快捷键
        document.addEventListener('keydown', this.handleKeyPress.bind(this));
        
        // 窗口事件
        window.addEventListener('beforeunload', this.saveUserProgress.bind(this));
        window.addEventListener('visibilitychange', this.handleVisibilityChange.bind(this));
    }
    
    // 初始化游戏模块
    initializeGameModules() {
        this.balanceGame = new BalanceGame(this);
        this.magicBoxGame = new MagicBoxGame(this);
        this.storyGame = new StoryGame(this);
        
        Debug.log('游戏模块初始化完成');
    }
    
    // 加载用户进度
    loadUserProgress() {
        const savedProgress = Storage.get('userProgress');
        if (savedProgress) {
            this.userProgress = { ...this.userProgress, ...savedProgress };
        }
        Debug.log('用户进度已加载:', this.userProgress);
    }
    
    // 保存用户进度
    saveUserProgress() {
        Storage.set('userProgress', this.userProgress);
        Debug.log('用户进度已保存');
    }
    
    // 更新游戏UI
    updateGameUI() {
        // 更新得分显示
        if (this.scoreDisplay) {
            this.scoreDisplay.textContent = `得分: ${this.score}`;
        }
        
        // 更新生命显示
        if (this.livesDisplay) {
            this.livesDisplay.textContent = `生命: ${this.lives}`;
        }
        
        // 更新提示显示
        if (this.hintsDisplay) {
            this.hintsDisplay.textContent = `提示: ${this.hints}`;
        }
        
        // 更新关卡显示
        if (this.levelDisplay) {
            this.levelDisplay.textContent = `第${this.currentLevel}关`;
        }
        
        // 更新头部信息
        const currentStageSpan = DOMUtils.getElement('#currentStage');
        const currentLevelSpan = DOMUtils.getElement('#currentLevel');
        const totalScoreSpan = DOMUtils.getElement('#totalScore');
        
        if (currentStageSpan) currentStageSpan.textContent = this.currentStage;
        if (currentLevelSpan) currentLevelSpan.textContent = this.currentLevel;
        if (totalScoreSpan) totalScoreSpan.textContent = this.score;
        
        // 更新进度条
        this.updateProgressBar();
    }
    
    // 更新进度条
    updateProgressBar() {
        if (!this.progressBar) return;
        
        const stage = LevelManager.getStage(this.currentStage);
        if (stage) {
            const progress = ((this.currentLevel - 1) / stage.totalLevels) * 100;
            const progressFill = this.progressBar.querySelector('.progress-fill');
            if (progressFill) {
                progressFill.style.width = `${progress}%`;
            }
        }
    }
    
    // 隐藏所有界面
    hideAllScreens() {
        const screens = DOMUtils.getElements('.screen');
        screens.forEach(screen => {
            screen.style.display = 'none';
            screen.classList.remove('active');
        });
    }
    
    // 显示错误信息
    showError(message) {
        this.showFeedback(message, 'error');
        Debug.error('游戏错误:', message);
    }
    
    // 显示反馈信息
    showFeedback(message, type = 'info') {
        if (!this.feedbackArea) return;
        
        const feedbackContent = this.feedbackArea.querySelector('.feedback-content');
        if (feedbackContent) {
            feedbackContent.textContent = message;
            feedbackContent.className = `feedback-content feedback-${type}`;
            
            // 显示反馈区域
            this.feedbackArea.style.display = 'block';
            
            // 3秒后自动隐藏
            setTimeout(() => {
                if (this.feedbackArea) {
                    this.feedbackArea.style.display = 'none';
                }
            }, 3000);
        }
    }
    
    // 显示开始界面
    showStartScreen() {
        this.hideAllScreens();
        if (this.startScreen) {
            this.startScreen.style.display = 'block';
            this.startScreen.classList.add('active');
            AnimationUtils.addAnimation(this.startScreen, 'animate-fade-in');
        }
        
        // 隐藏加载界面
        const loadingScreen = DOMUtils.getElement('#loadingScreen');
        if (loadingScreen) {
            loadingScreen.style.display = 'none';
        }
        
        this.gameState = 'start';
        SoundManager.playBackgroundMusic();
    }
    
    // 显示阶段选择
    showStageSelection() {
        this.hideAllScreens();
        
        // 创建阶段选择界面
        this.createStageSelectionScreen();
        
        this.gameState = 'stage_selection';
        SoundManager.playClick();
    }
    
    // 创建阶段选择界面
    createStageSelectionScreen() {
        let stageSelectionScreen = DOMUtils.getElement('#stageSelectionScreen');
        if (!stageSelectionScreen) {
            stageSelectionScreen = DOMUtils.createElement('div', 'screen stage-selection-screen');
            stageSelectionScreen.id = 'stageSelectionScreen';
            document.body.appendChild(stageSelectionScreen);
        }
        
        stageSelectionScreen.innerHTML = `
            <div class="stage-selection-container">
                <h2>选择学习阶段</h2>
                <div class="stages-grid">
                    <div class="stage-card ${this.userProgress.unlockedStages >= 1 ? 'unlocked' : 'locked'}" data-stage="1">
                        <div class="stage-icon">⚖️</div>
                        <h3>天平游戏</h3>
                        <p>学习等量关系的基本概念</p>
                        <div class="stage-progress">${this.getStageProgress(1)}%</div>
                    </div>
                    <div class="stage-card ${this.userProgress.unlockedStages >= 2 ? 'unlocked' : 'locked'}" data-stage="2">
                        <div class="stage-icon">🎁</div>
                        <h3>魔法盒子</h3>
                        <p>理解函数和变换的概念</p>
                        <div class="stage-progress">${this.getStageProgress(2)}%</div>
                    </div>
                    <div class="stage-card ${this.userProgress.unlockedStages >= 3 ? 'unlocked' : 'locked'}" data-stage="3">
                        <div class="stage-icon">📚</div>
                        <h3>故事方程</h3>
                        <p>从实际问题中列出方程</p>
                        <div class="stage-progress">${this.getStageProgress(3)}%</div>
                    </div>
                    <div class="stage-card ${this.userProgress.unlockedStages >= 4 ? 'unlocked' : 'locked'}" data-stage="4">
                        <div class="stage-icon">🏆</div>
                        <h3>挑战关卡</h3>
                        <p>综合运用所学知识</p>
                        <div class="stage-progress">${this.getStageProgress(4)}%</div>
                    </div>
                </div>
                <button id="backToStart" class="back-button">返回</button>
            </div>
        `;
        
        // 重新绑定事件
        const backBtn = stageSelectionScreen.querySelector('#backToStart');
        if (backBtn) {
            backBtn.addEventListener('click', this.showStartScreen.bind(this));
        }
        
        const stageCards = stageSelectionScreen.querySelectorAll('.stage-card.unlocked');
        stageCards.forEach(card => {
            card.addEventListener('click', () => {
                const stage = parseInt(card.dataset.stage);
                this.selectStage(stage);
            });
        });
        
        stageSelectionScreen.style.display = 'flex';
        AnimationUtils.addAnimation(stageSelectionScreen, 'animate-slide-in');
    }
    
    // 获取阶段进度
    getStageProgress(stage) {
        const stageLevels = LevelManager.getLevelsByStage(stage);
        if (!stageLevels || stageLevels.length === 0) return 0;
        
        const completedCount = stageLevels.filter(level => 
            this.userProgress.completedLevels.includes(level.id)
        ).length;
        
        return Math.round((completedCount / stageLevels.length) * 100);
    }
    
    // 选择阶段
    selectStage(stage) {
        if (stage > this.userProgress.unlockedStages) {
            this.showFeedback('请先完成前面的阶段！', 'warning');
            return;
        }
        
        this.currentStage = stage;
        this.currentLevel = this.userProgress.unlockedLevels[stage] || 1;
        
        this.startGame();
        SoundManager.playClick();
    }
    
    // 开始游戏
    startGame() {
        this.hideAllScreens();
        
        if (this.gameScreen) {
            this.gameScreen.style.display = 'block';
            AnimationUtils.addAnimation(this.gameScreen, 'animate-fade-in');
        }
        
        this.gameState = 'playing';
        this.startTime = Date.now();
        
        // 加载当前关卡
        this.loadCurrentLevel();
        
        // 更新UI
        this.updateGameUI();
        
        SoundManager.playGameStart();
        Debug.log(`开始游戏 - 阶段: ${this.currentStage}, 关卡: ${this.currentLevel}`);
    }
    
    // 加载当前关卡
    loadCurrentLevel() {
        const levelData = LevelManager.getLevel(this.currentStage, this.currentLevel);
        if (!levelData) {
            this.showError('关卡数据加载失败');
            return;
        }
        
        this.gameData = levelData;
        
        // 显示对应的游戏界面
        this.showGameInterface(this.currentStage);
        
        // 加载关卡到对应的游戏模块
        switch (this.currentStage) {
            case 1:
                if (this.balanceGame) {
                    this.balanceGame.loadLevel(levelData);
                }
                break;
            case 2:
                if (this.magicBoxGame) {
                    this.magicBoxGame.loadLevel(levelData);
                }
                break;
            case 3:
                if (this.storyGame) {
                    this.storyGame.loadLevel(levelData);
                }
                break;
            case 4:
                // 挑战关卡可能包含多种类型
                this.loadChallengeLevel(levelData);
                break;
        }
        
        // 设置答题区域
        this.setupAnswerArea(levelData);
    }
    
    // 显示游戏界面
    showGameInterface(stage) {
        // 隐藏所有游戏界面
        const gameInterfaces = DOMUtils.getElements('.game-interface');
        gameInterfaces.forEach(gameInterface => {
            gameInterface.style.display = 'none';
        });
        
        // 显示对应阶段的界面
        const interfaceMap = {
            1: '.balance-game',
            2: '.magicbox-game', 
            3: '.story-game',
            4: '.challenge-game'
        };
        
        const targetInterface = DOMUtils.getElement(interfaceMap[stage]);
        if (targetInterface) {
            targetInterface.style.display = 'block';
            AnimationUtils.addAnimation(targetInterface, 'animate-slide-in');
        }
    }
    
    // 加载挑战关卡
    loadChallengeLevel(levelData) {
        // 挑战关卡根据类型加载到不同的游戏模块
        switch (levelData.type) {
            case 'balance':
                if (this.balanceGame) {
                    this.balanceGame.loadLevel(levelData);
                }
                break;
            case 'magicbox':
                if (this.magicBoxGame) {
                    this.magicBoxGame.loadLevel(levelData);
                }
                break;
            case 'story':
                if (this.storyGame) {
                    this.storyGame.loadLevel(levelData);
                }
                break;
            default:
                Debug.warn('未知的挑战关卡类型:', levelData.type);
        }
    }
    
    // 设置答题区域
    setupAnswerArea(levelData) {
        if (!this.answerArea || !levelData) return;
        
        // 根据答题类型设置不同的界面
        switch (levelData.answerType) {
            case 'choice':
                this.setupChoiceAnswer(levelData.choices);
                break;
            case 'number':
                this.setupNumberAnswer();
                break;
            case 'balance':
                this.hideAnswerArea(); // 天平游戏不需要输入答案
                break;
            default:
                this.setupNumberAnswer();
        }
    }
    
    // 设置选择题答案
    setupChoiceAnswer(choices) {
        if (!choices || !this.answerArea) return;
        
        this.answerArea.innerHTML = `
            <div class="choice-container">
                <h4>请选择正确答案：</h4>
                <div class="choices">
                    ${choices.map((choice, index) => 
                        `<button class="choice-btn" data-value="${choice}">${choice}</button>`
                    ).join('')}
                </div>
            </div>
        `;
        
        // 绑定选择事件
        const choiceBtns = this.answerArea.querySelectorAll('.choice-btn');
        choiceBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                // 移除其他按钮的选中状态
                choiceBtns.forEach(b => b.classList.remove('selected'));
                // 添加当前按钮的选中状态
                btn.classList.add('selected');
                // 启用提交按钮
                if (this.submitButton) {
                    this.submitButton.disabled = false;
                }
            });
        });
        
        this.answerArea.style.display = 'block';
    }
    
    // 设置数字答案
    setupNumberAnswer() {
        if (!this.answerArea) return;
        
        this.answerArea.innerHTML = `
            <div class="number-input-container">
                <label for="answerInput">请输入答案：</label>
                <input type="number" id="answerInput" class="answer-input" placeholder="输入数字">
                <button id="submitAnswer" class="submit-btn" disabled>提交答案</button>
            </div>
        `;
        
        // 重新获取元素引用
        this.answerInput = this.answerArea.querySelector('#answerInput');
        this.submitButton = this.answerArea.querySelector('#submitAnswer');
        
        // 绑定事件
        if (this.answerInput) {
            this.answerInput.addEventListener('input', () => {
                if (this.submitButton) {
                    this.submitButton.disabled = !this.answerInput.value.trim();
                }
            });
            
            this.answerInput.addEventListener('keypress', (event) => {
                if (event.key === 'Enter' && !this.submitButton.disabled) {
                    this.submitAnswer();
                }
            });
        }
        
        if (this.submitButton) {
            this.submitButton.addEventListener('click', this.submitAnswer.bind(this));
        }
        
        this.answerArea.style.display = 'block';
    }
    
    // 隐藏答题区域
    hideAnswerArea() {
        if (this.answerArea) {
            this.answerArea.style.display = 'none';
        }
    }
    
    // 提交答案
    submitAnswer() {
        if (!this.gameData) return;
        
        let userAnswer = null;
        
        // 获取用户答案
        if (this.gameData.answerType === 'choice') {
            const selectedChoice = this.answerArea.querySelector('.choice-btn.selected');
            if (selectedChoice) {
                userAnswer = selectedChoice.dataset.value;
            }
        } else if (this.answerInput) {
            userAnswer = this.answerInput.value.trim();
            if (this.gameData.answerType === 'number') {
                userAnswer = parseFloat(userAnswer);
            }
        }
        
        if (userAnswer === null || userAnswer === '') {
            this.showFeedback('请输入答案！', 'warning');
            return;
        }
        
        // 检查答案
        this.checkAnswer(userAnswer);
    }
    
    // 检查答案
    checkAnswer(userAnswer) {
        let isCorrect = false;
        
        // 根据当前阶段调用对应的检查方法
        switch (this.currentStage) {
            case 1:
                if (this.balanceGame) {
                    isCorrect = this.balanceGame.checkAnswer(userAnswer);
                }
                break;
            case 2:
                if (this.magicBoxGame) {
                    isCorrect = this.magicBoxGame.checkAnswer(userAnswer);
                }
                break;
            case 3:
                if (this.storyGame) {
                    isCorrect = this.storyGame.checkAnswer(userAnswer);
                }
                break;
            case 4:
                isCorrect = this.checkChallengeAnswer(userAnswer);
                break;
            default:
                isCorrect = MathUtils.checkAnswer(userAnswer, this.gameData.answer);
        }
        
        this.handleAnswer(isCorrect, userAnswer);
    }
    
    // 检查挑战关卡答案
    checkChallengeAnswer(userAnswer) {
        if (!this.gameData) return false;
        
        // 根据挑战关卡的类型调用对应的检查方法
        switch (this.gameData.type) {
            case 'balance':
                return this.balanceGame ? this.balanceGame.checkAnswer(userAnswer) : false;
            case 'magicbox':
                return this.magicBoxGame ? this.magicBoxGame.checkAnswer(userAnswer) : false;
            case 'story':
                return this.storyGame ? this.storyGame.checkAnswer(userAnswer) : false;
            default:
                return MathUtils.checkAnswer(userAnswer, this.gameData.answer);
        }
    }
    
    // 处理答案结果
    handleAnswer(isCorrect, userAnswer) {
        if (isCorrect) {
            this.handleCorrectAnswer(userAnswer);
        } else {
            this.handleIncorrectAnswer(userAnswer);
        }
    }
    
    // 处理正确答案
    handleCorrectAnswer(userAnswer) {
        // 增加分数
        const baseScore = 100;
        const timeBonus = this.calculateTimeBonus();
        const hintPenalty = (3 - this.hints) * 10;
        const levelScore = baseScore + timeBonus - hintPenalty;
        
        this.score += Math.max(levelScore, 50); // 最少50分
        
        // 记录完成的关卡
        const levelId = `${this.currentStage}-${this.currentLevel}`;
        if (!this.userProgress.completedLevels.includes(levelId)) {
            this.userProgress.completedLevels.push(levelId);
        }
        
        // 更新分数记录
        this.userProgress.scores[levelId] = Math.max(
            this.userProgress.scores[levelId] || 0,
            levelScore
        );
        
        // 显示成功反馈
        this.showFeedback(`太棒了！答案正确！\n得分：${levelScore}`, 'success');
        
        // 播放成功音效
        SoundManager.playSuccess();
        
        // 延迟进入下一关
        setTimeout(() => {
            this.nextLevel();
        }, 2000);
        
        Debug.log('答案正确:', userAnswer, '得分:', levelScore);
    }
    
    // 处理错误答案
    handleIncorrectAnswer(userAnswer) {
        this.lives--;
        
        if (this.lives <= 0) {
            this.gameOver();
        } else {
            this.showFeedback(`答案不正确，再试试看！\n剩余生命：${this.lives}`, 'error');
            SoundManager.playError();
        }
        
        this.updateGameUI();
        Debug.log('答案错误:', userAnswer, '剩余生命:', this.lives);
    }
    
    // 重置游戏状态
    resetGameState() {
        this.startTime = Date.now();
        this.hints = 3;
        this.updateGameUI();
    }
    
    // 游戏结束
    gameOver() {
        this.gameState = 'gameOver';
        
        this.showResult({
            title: '游戏结束',
            message: `很遗憾，生命值耗尽！\n\n当前得分：${this.score}\n\n不要灰心，再试一次吧！`,
            type: 'error',
            showRestart: true
        });
        
        SoundManager.playError();
        Debug.log('游戏结束 - 得分:', this.score);
    }
    
    // 显示结果界面
    showResult(options) {
        const { title, message, type = 'info', showRestart = false } = options;
        
        // 创建结果弹窗
        const resultModal = document.createElement('div');
        resultModal.className = 'result-modal';
        resultModal.innerHTML = `
            <div class="result-content">
                <h2 class="result-title">${title}</h2>
                <div class="result-message">${message}</div>
                <div class="result-actions">
                    ${showRestart ? '<button class="btn btn-primary" onclick="location.reload()">重新开始</button>' : ''}
                    <button class="btn btn-secondary" onclick="this.closest('.result-modal').remove()">确定</button>
                </div>
            </div>
        `;
        
        document.body.appendChild(resultModal);
        
        // 添加样式
        resultModal.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.8);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 10000;
        `;
        
        const content = resultModal.querySelector('.result-content');
        content.style.cssText = `
            background: white;
            padding: 30px;
            border-radius: 10px;
            text-align: center;
            max-width: 400px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        `;
    }
    
    // 计算阶段得分
    calculateStageScore() {
        const stageLevels = LevelManager.getLevelsByStage(this.currentStage);
        let totalScore = 0;
        
        stageLevels.forEach(level => {
            const levelId = `${this.currentStage}-${level.id}`;
            totalScore += this.userProgress.scores[levelId] || 0;
        });
        
        return totalScore;
    }
    
    // 计算时间奖励
    calculateTimeBonus() {
        if (!this.startTime) return 0;
        
        const elapsedTime = (Date.now() - this.startTime) / 1000; // 秒
        const targetTime = 60; // 目标时间60秒
        
        if (elapsedTime <= targetTime) {
            return Math.round((targetTime - elapsedTime) * 2); // 每秒2分
        }
        
        return 0;
    }
    
    // 下一关
    nextLevel() {
        const stageLevels = LevelManager.getLevelsByStage(this.currentStage);
        
        if (this.currentLevel < stageLevels.length) {
            // 还有下一关
            this.currentLevel++;
            this.userProgress.unlockedLevels[this.currentStage] = Math.max(
                this.userProgress.unlockedLevels[this.currentStage] || 1,
                this.currentLevel
            );
            
            this.resetGameState();
            this.loadCurrentLevel();
            this.updateGameUI();
        } else {
            // 阶段完成
            this.completeStage();
        }
    }
    
    // 完成阶段
    completeStage() {
        // 解锁下一阶段
        if (this.currentStage < 4) {
            this.userProgress.unlockedStages = Math.max(
                this.userProgress.unlockedStages,
                this.currentStage + 1
            );
            this.userProgress.unlockedLevels[this.currentStage + 1] = 1;
        }
        
        // 显示阶段完成界面
        this.showStageComplete();
        
        // 保存进度
        this.saveUserProgress();
        
        SoundManager.playStageComplete();
        Debug.log('阶段完成:', this.currentStage);
    }
    
    // 显示阶段完成界面
    showStageComplete() {
        const stageNames = {
            1: '天平游戏',
            2: '魔法盒子',
            3: '故事方程',
            4: '挑战关卡'
        };
        
        const stageName = stageNames[this.currentStage] || '未知阶段';
        const stageScore = this.calculateStageScore();
        
        this.showResult({
            title: '阶段完成！',
            message: `恭喜你完成了「${stageName}」！\n\n阶段得分：${stageScore}\n总得分：${this.score}\n\n${this.currentStage < 4 ? '下一阶段已解锁！' : '恭喜完成所有阶段！'}`,
            type: 'success',
            showRestart: false
        });
    }
}