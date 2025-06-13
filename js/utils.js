// 工具函数库

// 本地存储管理
const Storage = {
    // 保存数据
    set: function(key, data) {
        try {
            localStorage.setItem(`equation_game_${key}`, JSON.stringify(data));
            return true;
        } catch (e) {
            console.error('保存数据失败:', e);
            return false;
        }
    },

    // 获取数据
    get: function(key) {
        try {
            const data = localStorage.getItem(`equation_game_${key}`);
            return data ? JSON.parse(data) : null;
        } catch (e) {
            console.error('加载数据失败:', e);
            return null;
        }
    },

    // 保存游戏进度
    saveProgress: function(progress) {
        return this.set('progress', progress);
    },
    
    // 加载游戏进度
    loadProgress: function() {
        const data = this.get('progress');
        return data || this.getDefaultProgress();
    },
    
    // 获取默认进度
    getDefaultProgress: function() {
        return {
            currentStage: 1,
            currentLevel: 1,
            totalScore: 0,
            stage1: {},
            stage2: {},
            stage3: {},
            stage4: {},
            settings: {
                soundEnabled: true,
                animationEnabled: true,
                difficulty: 'normal'
            },
            statistics: {
                totalPlayTime: 0,
                totalAttempts: 0,
                correctAnswers: 0,
                hintsUsed: 0
            }
        };
    },
    
    // 保存设置
    saveSettings: function(settings) {
        const progress = this.loadProgress();
        progress.settings = { ...progress.settings, ...settings };
        return this.saveProgress(progress);
    },
    
    // 清除所有数据
    clearAll: function() {
        try {
            // 清除所有游戏相关的localStorage项
            const keys = Object.keys(localStorage);
            keys.forEach(key => {
                if (key.startsWith('equation_game_')) {
                    localStorage.removeItem(key);
                }
            });
            return true;
        } catch (e) {
            console.error('清除数据失败:', e);
            return false;
        }
    }
};

// 动画工具
const AnimationUtils = {
    // 添加动画类
    addAnimation: function(element, animationClass, duration = 1000) {
        if (!element) return;
        
        element.classList.add(animationClass);
        
        setTimeout(() => {
            element.classList.remove(animationClass);
        }, duration);
    },
    
    // 淡入效果
    fadeIn: function(element, duration = 500) {
        if (!element) return;
        
        element.style.opacity = '0';
        element.style.display = 'block';
        
        let start = null;
        function animate(timestamp) {
            if (!start) start = timestamp;
            const progress = timestamp - start;
            
            element.style.opacity = Math.min(progress / duration, 1);
            
            if (progress < duration) {
                requestAnimationFrame(animate);
            }
        }
        
        requestAnimationFrame(animate);
    },
    
    // 淡出效果
    fadeOut: function(element, duration = 500) {
        if (!element) return;
        
        let start = null;
        function animate(timestamp) {
            if (!start) start = timestamp;
            const progress = timestamp - start;
            
            element.style.opacity = Math.max(1 - progress / duration, 0);
            
            if (progress < duration) {
                requestAnimationFrame(animate);
            } else {
                element.style.display = 'none';
            }
        }
        
        requestAnimationFrame(animate);
    },
    
    // 数字变化动画
    animateNumber: function(element, from, to, duration = 1000) {
        if (!element) return;
        
        let start = null;
        function animate(timestamp) {
            if (!start) start = timestamp;
            const progress = Math.min((timestamp - start) / duration, 1);
            
            const current = Math.floor(from + (to - from) * progress);
            element.textContent = current;
            
            if (progress < 1) {
                requestAnimationFrame(animate);
            }
        }
        
        requestAnimationFrame(animate);
    },
    
    // 创建粒子效果
    createParticles: function(container, count = 20) {
        if (!container) return;
        
        for (let i = 0; i < count; i++) {
            const particle = document.createElement('div');
            particle.className = 'particle';
            particle.style.left = Math.random() * 100 + '%';
            particle.style.animationDelay = Math.random() * 2 + 's';
            
            container.appendChild(particle);
            
            setTimeout(() => {
                if (particle.parentNode) {
                    particle.parentNode.removeChild(particle);
                }
            }, 3000);
        }
    },
    
    // 创建庆祝动画
    createCelebration: function() {
        const celebration = document.createElement('div');
        celebration.className = 'celebration';
        document.body.appendChild(celebration);
        
        // 创建彩带
        for (let i = 0; i < 50; i++) {
            const confetti = document.createElement('div');
            confetti.className = 'confetti';
            confetti.style.left = Math.random() * 100 + '%';
            confetti.style.animationDelay = Math.random() * 3 + 's';
            celebration.appendChild(confetti);
        }
        
        // 3秒后移除
        setTimeout(() => {
            if (celebration.parentNode) {
                celebration.parentNode.removeChild(celebration);
            }
        }, 3000);
    }
};

// 音效管理
const SoundManager = {
    sounds: {},
    enabled: true,
    
    // 初始化音效
    init: function() {
        // 这里可以预加载音效文件
        // 由于是演示版本，我们使用Web Audio API生成简单音效
        this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
    },
    
    // 播放成功音效
    playSuccess: function() {
        if (!this.enabled) return;
        this.playTone(523.25, 0.2); // C5
        setTimeout(() => this.playTone(659.25, 0.2), 100); // E5
        setTimeout(() => this.playTone(783.99, 0.3), 200); // G5
    },
    
    // 播放错误音效
    playError: function() {
        if (!this.enabled) return;
        this.playTone(220, 0.5); // A3
    },
    
    // 播放点击音效
    playClick: function() {
        if (!this.enabled) return;
        this.playTone(440, 0.1); // A4
    },
    
    // 播放提示音效
    playHint: function() {
        if (!this.enabled) return;
        this.playTone(659.25, 0.2); // E5
    },
    
    // 播放游戏开始音效
    playGameStart: function() {
        if (!this.enabled) return;
        const notes = [261.63, 329.63, 392, 523.25]; // C4, E4, G4, C5
        notes.forEach((note, index) => {
            setTimeout(() => this.playTone(note, 0.3), index * 150);
        });
    },
    
    // 播放故事完成音效
    playStoryComplete: function() {
        if (!this.enabled) return;
        this.playTone(523.25, 0.2); // C5
    },
    
    // 播放音调
    playTone: function(frequency, duration) {
        if (!this.audioContext) return;
        
        const oscillator = this.audioContext.createOscillator();
        const gainNode = this.audioContext.createGain();
        
        oscillator.connect(gainNode);
        gainNode.connect(this.audioContext.destination);
        
        oscillator.frequency.value = frequency;
        oscillator.type = 'sine';
        
        gainNode.gain.setValueAtTime(0.3, this.audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, this.audioContext.currentTime + duration);
        
        oscillator.start(this.audioContext.currentTime);
        oscillator.stop(this.audioContext.currentTime + duration);
    },
    
    // 播放背景音乐
    playBackgroundMusic: function() {
        if (!this.enabled) return;
        // 简单的背景音乐实现
        Debug.log('背景音乐已启动');
    },
    
    // 播放关卡完成音效
    playLevelComplete: function() {
        if (!this.enabled) return;
        this.playTone(523.25, 0.3); // C5
        setTimeout(() => this.playTone(659.25, 0.3), 150); // E5
        setTimeout(() => this.playTone(783.99, 0.3), 300); // G5
        setTimeout(() => this.playTone(1046.5, 0.5), 450); // C6
    },
    
    // 播放阶段完成音效
    playStageComplete: function() {
        if (!this.enabled) return;
        // 播放更长的庆祝音效
        const notes = [523.25, 659.25, 783.99, 1046.5, 783.99, 659.25, 523.25];
        notes.forEach((note, index) => {
            setTimeout(() => this.playTone(note, 0.3), index * 200);
        });
    },
    
    // 设置音效开关
    setEnabled: function(enabled) {
        this.enabled = enabled;
    }
};

// 数学工具
const MathUtils = {
    // 检查答案是否正确（考虑浮点数精度）
    checkAnswer: function(userAnswer, correctAnswer, tolerance = 0.001) {
        if (typeof userAnswer === 'string' && typeof correctAnswer === 'string') {
            return userAnswer.toLowerCase().trim() === correctAnswer.toLowerCase().trim();
        }
        
        const user = parseFloat(userAnswer);
        const correct = parseFloat(correctAnswer);
        
        if (isNaN(user) || isNaN(correct)) {
            return false;
        }
        
        return Math.abs(user - correct) <= tolerance;
    },
    
    // 生成随机整数
    randomInt: function(min, max) {
        return Math.floor(Math.random() * (max - min + 1)) + min;
    },
    
    // 生成随机小数
    randomFloat: function(min, max, decimals = 2) {
        const value = Math.random() * (max - min) + min;
        return parseFloat(value.toFixed(decimals));
    },
    
    // 计算百分比
    percentage: function(part, total) {
        if (total === 0) return 0;
        return Math.round((part / total) * 100);
    },
    
    // 格式化时间（秒转换为分:秒）
    formatTime: function(seconds) {
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    },
    
    // 最大公约数
    gcd: function(a, b) {
        while (b !== 0) {
            const temp = b;
            b = a % b;
            a = temp;
        }
        return a;
    },
    
    // 最小公倍数
    lcm: function(a, b) {
        return Math.abs(a * b) / this.gcd(a, b);
    },
    
    // 简化分数
    simplifyFraction: function(numerator, denominator) {
        const divisor = this.gcd(numerator, denominator);
        return {
            numerator: numerator / divisor,
            denominator: denominator / divisor
        };
    },
    
    // 检查是否为质数
    isPrime: function(n) {
        if (n < 2) return false;
        for (let i = 2; i <= Math.sqrt(n); i++) {
            if (n % i === 0) return false;
        }
        return true;
    }
};

// DOM工具
const DOMUtils = {
    // 安全获取元素
    getElement: function(selector) {
        return document.querySelector(selector);
    },
    
    // 获取所有匹配元素
    getElements: function(selector) {
        return document.querySelectorAll(selector);
    },
    
    // 创建元素
    createElement: function(tag, className = '', content = '') {
        const element = document.createElement(tag);
        if (className) element.className = className;
        if (content) element.textContent = content;
        return element;
    },
    
    // 显示元素
    show: function(element) {
        if (element) {
            element.style.display = 'block';
            element.classList.remove('hidden');
        }
    },
    
    // 隐藏元素
    hide: function(element) {
        if (element) {
            element.style.display = 'none';
            element.classList.add('hidden');
        }
    },
    
    // 切换显示状态
    toggle: function(element) {
        if (element) {
            if (element.style.display === 'none' || element.classList.contains('hidden')) {
                this.show(element);
            } else {
                this.hide(element);
            }
        }
    },
    
    // 添加事件监听器
    addEvent: function(element, event, handler) {
        if (element && typeof handler === 'function') {
            element.addEventListener(event, handler);
        }
    },
    
    // 移除事件监听器
    removeEvent: function(element, event, handler) {
        if (element && typeof handler === 'function') {
            element.removeEventListener(event, handler);
        }
    },
    
    // 设置元素内容
    setContent: function(element, content) {
        if (element) {
            element.textContent = content;
        }
    },
    
    // 设置HTML内容
    setHTML: function(element, html) {
        if (element) {
            element.innerHTML = html;
        }
    }
};

// 验证工具
const Validator = {
    // 验证数字输入
    isValidNumber: function(value) {
        return !isNaN(value) && isFinite(value);
    },
    
    // 验证整数
    isInteger: function(value) {
        return Number.isInteger(parseFloat(value));
    },
    
    // 验证正数
    isPositive: function(value) {
        return parseFloat(value) > 0;
    },
    
    // 验证范围
    inRange: function(value, min, max) {
        const num = parseFloat(value);
        return num >= min && num <= max;
    },
    
    // 验证非空
    isNotEmpty: function(value) {
        return value !== null && value !== undefined && value.toString().trim() !== '';
    }
};



// 格式化工具
const Formatter = {
    // 格式化分数
    formatFraction: function(numerator, denominator) {
        if (denominator === 1) return numerator.toString();
        return `${numerator}/${denominator}`;
    },
    
    // 格式化小数
    formatDecimal: function(value, places = 2) {
        return parseFloat(value).toFixed(places);
    },
    
    // 格式化方程
    formatEquation: function(equation) {
        return equation.replace(/\*/g, '×').replace(/\//g, '÷');
    },
    
    // 格式化大数字
    formatLargeNumber: function(num) {
        if (num >= 1000000) {
            return (num / 1000000).toFixed(1) + 'M';
        } else if (num >= 1000) {
            return (num / 1000).toFixed(1) + 'K';
        }
        return num.toString();
    }
};

// 调试工具
const Debug = {
    enabled: true,
    
    log: function(...args) {
        if (this.enabled) {
            console.log('[游戏调试]', ...args);
        }
    },
    
    error: function(...args) {
        if (this.enabled) {
            console.error('[游戏错误]', ...args);
        }
    },
    
    warn: function(...args) {
        if (this.enabled) {
            console.warn('[游戏警告]', ...args);
        }
    },
    
    enable: function() {
        this.enabled = true;
        this.log('调试模式已启用');
    },
    
    disable: function() {
        this.enabled = false;
    }
};

// 性能监控
const Performance = {
    timers: {},
    
    // 开始计时
    start: function(name) {
        this.timers[name] = performance.now();
    },
    
    // 结束计时
    end: function(name) {
        if (this.timers[name]) {
            const duration = performance.now() - this.timers[name];
            Debug.log(`${name} 耗时: ${duration.toFixed(2)}ms`);
            delete this.timers[name];
            return duration;
        }
        return 0;
    },
    
    // 测量函数执行时间
    measure: function(name, fn) {
        this.start(name);
        const result = fn();
        this.end(name);
        return result;
    }
};

// 错误处理
const ErrorHandler = {
    // 处理错误
    handle: function(error, context = '') {
        Debug.error('发生错误:', error, '上下文:', context);
        
        // 这里可以添加错误上报逻辑
        // 例如发送到服务器或显示用户友好的错误信息
    },
    
    // 安全执行函数
    safeExecute: function(fn, fallback = null) {
        try {
            return fn();
        } catch (error) {
            this.handle(error, 'safeExecute');
            return fallback;
        }
    }
};

// 导出所有工具
if (typeof window !== 'undefined') {
    window.GameUtils = {
        Storage,
        AnimationUtils,
        SoundManager,
        MathUtils,
        DOMUtils,
        Validator,
        Formatter,
        Debug,
        Performance,
        ErrorHandler
    };
}

// Node.js环境导出
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        Storage,
        AnimationUtils,
        SoundManager,
        MathUtils,
        DOMUtils,
        Validator,
        Formatter,
        Debug,
        Performance,
        ErrorHandler
    };
}