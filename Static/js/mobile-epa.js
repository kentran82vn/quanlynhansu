/*
===============================================
📱 MOBILE EPA FORM ENHANCEMENTS
===============================================
Touch-optimized EPA form with better UX
===============================================
*/

// Mobile EPA Form Manager
class MobileEPAForm {
  constructor() {
    this.currentQuestionIndex = 0;
    this.questions = [];
    this.formData = {};
    this.isSubmitting = false;
    
    this.init();
  }
  
  init() {
    console.log('📱 Initializing Mobile EPA Form...');
    
    // Check if mobile
    this.isMobile = window.innerWidth <= 768;
    
    if (this.isMobile) {
      this.enhanceForMobile();
    }
    
    // Listen for orientation changes
    window.addEventListener('orientationchange', () => {
      setTimeout(() => this.handleOrientationChange(), 100);
    });
    
    // Listen for resize
    window.addEventListener('resize', this.debounce(() => {
      this.isMobile = window.innerWidth <= 768;
      if (this.isMobile) {
        this.enhanceForMobile();
      }
    }, 300));
  }
  
  enhanceForMobile() {
    console.log('🔧 Enhancing EPA form for mobile...');
    
    // Add mobile-specific classes
    document.body.classList.add('mobile-epa-mode');
    
    // Enhance input fields
    this.enhanceInputFields();
    
    // Add touch feedback
    this.addTouchFeedback();
    
    // Improve navigation
    this.improveNavigation();
    
    // Add progress indicator
    this.addProgressIndicator();
    
    // Add auto-save
    this.enableAutoSave();
    
    // Add swipe gestures
    this.addSwipeGestures();
  }
  
  enhanceInputFields() {
    // Enhance score inputs
    const scoreInputs = document.querySelectorAll('input[type="number"]');
    scoreInputs.forEach(input => {
      // Add mobile-friendly attributes
      input.setAttribute('inputmode', 'numeric');
      input.setAttribute('pattern', '[0-9]*');
      
      // Add visual feedback
      input.addEventListener('focus', (e) => {
        e.target.parentElement.classList.add('input-focused');
      });
      
      input.addEventListener('blur', (e) => {
        e.target.parentElement.classList.remove('input-focused');
      });
      
      // Add increment/decrement buttons
      this.addStepperButtons(input);
    });
    
    // Enhance textareas
    const textareas = document.querySelectorAll('textarea');
    textareas.forEach(textarea => {
      // Auto-resize
      textarea.addEventListener('input', this.autoResize);
      
      // Character counter
      this.addCharacterCounter(textarea);
    });
  }
  
  addStepperButtons(input) {
    if (input.parentElement.querySelector('.stepper-buttons')) return;
    
    const container = document.createElement('div');
    container.className = 'stepper-buttons';
    container.innerHTML = `
      <button type="button" class="stepper-btn stepper-minus" data-action="decrement">
        <i class="fas fa-minus"></i>
      </button>
      <button type="button" class="stepper-btn stepper-plus" data-action="increment">
        <i class="fas fa-plus"></i>
      </button>
    `;
    
    input.parentElement.appendChild(container);
    
    // Add event listeners
    container.addEventListener('click', (e) => {
      const btn = e.target.closest('.stepper-btn');
      if (!btn) return;
      
      const action = btn.dataset.action;
      const currentValue = parseInt(input.value) || 0;
      const min = parseInt(input.min) || 0;
      const max = parseInt(input.max) || 100;
      
      if (action === 'increment' && currentValue < max) {
        input.value = currentValue + 1;
      } else if (action === 'decrement' && currentValue > min) {
        input.value = currentValue - 1;
      }
      
      // Trigger change event
      input.dispatchEvent(new Event('change', { bubbles: true }));
      
      // Haptic feedback
      this.vibrate(50);
    });
  }
  
  addCharacterCounter(textarea) {
    if (textarea.parentElement.querySelector('.char-counter')) return;
    
    const maxLength = textarea.maxLength || 500;
    const counter = document.createElement('div');
    counter.className = 'char-counter';
    counter.innerHTML = `<span class="current">0</span>/<span class="max">${maxLength}</span>`;
    
    textarea.parentElement.appendChild(counter);
    
    textarea.addEventListener('input', () => {
      const current = textarea.value.length;
      counter.querySelector('.current').textContent = current;
      
      // Visual feedback
      if (current > maxLength * 0.9) {
        counter.classList.add('warning');
      } else {
        counter.classList.remove('warning');
      }
    });
  }
  
  autoResize(e) {
    const textarea = e.target;
    textarea.style.height = 'auto';
    textarea.style.height = Math.min(textarea.scrollHeight, 200) + 'px';
  }
  
  addTouchFeedback() {
    // Add ripple effect to buttons
    const buttons = document.querySelectorAll('.btn');
    buttons.forEach(btn => {
      btn.addEventListener('touchstart', this.createRipple);
    });
  }
  
  createRipple(e) {
    const button = e.currentTarget;
    const rect = button.getBoundingClientRect();
    const ripple = document.createElement('span');
    
    const size = Math.max(rect.width, rect.height);
    const x = e.touches[0].clientX - rect.left - size / 2;
    const y = e.touches[0].clientY - rect.top - size / 2;
    
    ripple.style.cssText = `
      position: absolute;
      width: ${size}px;
      height: ${size}px;
      left: ${x}px;
      top: ${y}px;
      background: rgba(255, 255, 255, 0.3);
      border-radius: 50%;
      transform: scale(0);
      animation: ripple 0.6s linear;
      pointer-events: none;
    `;
    
    button.style.position = 'relative';
    button.style.overflow = 'hidden';
    button.appendChild(ripple);
    
    setTimeout(() => ripple.remove(), 600);
  }
  
  improveNavigation() {
    // Add floating action button for save
    this.addFloatingActionButton();
    
    // Add question navigation
    this.addQuestionNavigation();
  }
  
  addFloatingActionButton() {
    if (document.getElementById('mobile-save-fab')) return;
    
    const fab = document.createElement('button');
    fab.id = 'mobile-save-fab';
    fab.className = 'mobile-fab';
    fab.innerHTML = '<i class="fas fa-save"></i>';
    fab.title = 'Lưu đánh giá';
    
    fab.addEventListener('click', () => {
      this.saveForm();
      this.vibrate(100);
    });
    
    document.body.appendChild(fab);
  }
  
  addQuestionNavigation() {
    const questions = document.querySelectorAll('.question-item');
    if (questions.length <= 1) return;
    
    this.questions = Array.from(questions);
    
    // Add question indicators
    const indicators = document.createElement('div');
    indicators.className = 'question-indicators';
    indicators.innerHTML = this.questions.map((_, index) => 
      `<div class="indicator ${index === 0 ? 'active' : ''}" data-question="${index}"></div>`
    ).join('');
    
    // Add navigation controls
    const navigation = document.createElement('div');
    navigation.className = 'question-navigation';
    navigation.innerHTML = `
      <button class="nav-btn prev-btn" disabled>
        <i class="fas fa-chevron-left"></i>
        <span>Trước</span>
      </button>
      <div class="question-counter">
        <span class="current">1</span> / <span class="total">${this.questions.length}</span>
      </div>
      <button class="nav-btn next-btn">
        <span>Tiếp</span>
        <i class="fas fa-chevron-right"></i>
      </button>
    `;
    
    // Insert after first question
    this.questions[0].after(indicators);
    this.questions[this.questions.length - 1].after(navigation);
    
    // Add event listeners
    this.setupQuestionNavigation();
  }
  
  setupQuestionNavigation() {
    const prevBtn = document.querySelector('.prev-btn');
    const nextBtn = document.querySelector('.next-btn');
    const indicators = document.querySelectorAll('.indicator');
    
    prevBtn?.addEventListener('click', () => this.previousQuestion());
    nextBtn?.addEventListener('click', () => this.nextQuestion());
    
    indicators.forEach((indicator, index) => {
      indicator.addEventListener('click', () => this.goToQuestion(index));
    });
  }
  
  previousQuestion() {
    if (this.currentQuestionIndex > 0) {
      this.currentQuestionIndex--;
      this.updateQuestionView();
      this.vibrate(50);
    }
  }
  
  nextQuestion() {
    if (this.currentQuestionIndex < this.questions.length - 1) {
      this.currentQuestionIndex++;
      this.updateQuestionView();
      this.vibrate(50);
    }
  }
  
  goToQuestion(index) {
    this.currentQuestionIndex = index;
    this.updateQuestionView();
    this.vibrate(50);
  }
  
  updateQuestionView() {
    // Hide all questions
    this.questions.forEach(q => q.style.display = 'none');
    
    // Show current question
    this.questions[this.currentQuestionIndex].style.display = 'block';
    
    // Update indicators
    document.querySelectorAll('.indicator').forEach((indicator, index) => {
      indicator.classList.toggle('active', index === this.currentQuestionIndex);
    });
    
    // Update navigation buttons
    const prevBtn = document.querySelector('.prev-btn');
    const nextBtn = document.querySelector('.next-btn');
    const counter = document.querySelector('.question-counter .current');
    
    if (prevBtn) prevBtn.disabled = this.currentQuestionIndex === 0;
    if (nextBtn) nextBtn.disabled = this.currentQuestionIndex === this.questions.length - 1;
    if (counter) counter.textContent = this.currentQuestionIndex + 1;
  }
  
  addProgressIndicator() {
    const progressBar = document.createElement('div');
    progressBar.className = 'mobile-progress-bar';
    progressBar.innerHTML = '<div class="progress-fill"></div>';
    
    document.body.prepend(progressBar);
    
    // Update progress based on filled fields
    this.updateProgress();
    
    // Listen for form changes
    document.addEventListener('input', this.debounce(() => {
      this.updateProgress();
    }, 500));
  }
  
  updateProgress() {
    const inputs = document.querySelectorAll('input, textarea');
    const filled = Array.from(inputs).filter(input => input.value.trim() !== '').length;
    const progress = Math.round((filled / inputs.length) * 100);
    
    const progressFill = document.querySelector('.progress-fill');
    if (progressFill) {
      progressFill.style.width = `${progress}%`;
    }
  }
  
  enableAutoSave() {
    let saveTimeout;
    
    document.addEventListener('input', (e) => {
      if (e.target.matches('input, textarea')) {
        clearTimeout(saveTimeout);
        saveTimeout = setTimeout(() => {
          this.autoSave();
        }, 2000);
      }
    });
  }
  
  autoSave() {
    const formData = this.collectFormData();
    
    try {
      localStorage.setItem('epa_form_draft', JSON.stringify({
        data: formData,
        timestamp: Date.now()
      }));
      
      this.showToast('💾 Đã tự động lưu', 'success');
    } catch (error) {
      console.error('❌ Auto-save failed:', error);
    }
  }
  
  loadDraft() {
    try {
      const draft = localStorage.getItem('epa_form_draft');
      if (draft) {
        const { data, timestamp } = JSON.parse(draft);
        
        // Check if draft is not too old (24 hours)
        if (Date.now() - timestamp < 24 * 60 * 60 * 1000) {
          this.showRestoreDraftPrompt(data);
        }
      }
    } catch (error) {
      console.error('❌ Failed to load draft:', error);
    }
  }
  
  showRestoreDraftPrompt(data) {
    const prompt = document.createElement('div');
    prompt.className = 'draft-prompt';
    prompt.innerHTML = `
      <div class="draft-content">
        <i class="fas fa-history"></i>
        <h4>Khôi phục bản nháp?</h4>
        <p>Có bản nháp chưa hoàn thành từ lần trước</p>
        <div class="draft-actions">
          <button class="btn btn-primary" onclick="mobileEPA.restoreDraft()">Khôi phục</button>
          <button class="btn btn-secondary" onclick="mobileEPA.dismissDraft()">Bỏ qua</button>
        </div>
      </div>
    `;
    
    document.body.appendChild(prompt);
    this.draftData = data;
  }
  
  restoreDraft() {
    // Populate form with draft data
    Object.entries(this.draftData).forEach(([key, value]) => {
      const input = document.querySelector(`[name="${key}"]`);
      if (input) {
        input.value = value;
      }
    });
    
    this.dismissDraft();
    this.showToast('✅ Đã khôi phục bản nháp', 'success');
  }
  
  dismissDraft() {
    const prompt = document.querySelector('.draft-prompt');
    if (prompt) {
      prompt.remove();
    }
    localStorage.removeItem('epa_form_draft');
  }
  
  addSwipeGestures() {
    if (this.questions.length <= 1) return;
    
    let startX = 0;
    let startY = 0;
    
    document.addEventListener('touchstart', (e) => {
      startX = e.touches[0].clientX;
      startY = e.touches[0].clientY;
    });
    
    document.addEventListener('touchend', (e) => {
      if (!startX || !startY) return;
      
      const endX = e.changedTouches[0].clientX;
      const endY = e.changedTouches[0].clientY;
      
      const diffX = startX - endX;
      const diffY = startY - endY;
      
      // Check if horizontal swipe is more significant than vertical
      if (Math.abs(diffX) > Math.abs(diffY) && Math.abs(diffX) > 50) {
        if (diffX > 0) {
          // Swipe left - next question
          this.nextQuestion();
        } else {
          // Swipe right - previous question
          this.previousQuestion();
        }
      }
      
      startX = 0;
      startY = 0;
    });
  }
  
  collectFormData() {
    const formData = {};
    const inputs = document.querySelectorAll('input, textarea');
    
    inputs.forEach(input => {
      if (input.name) {
        formData[input.name] = input.value;
      }
    });
    
    return formData;
  }
  
  saveForm() {
    if (this.isSubmitting) return;
    
    this.isSubmitting = true;
    const formData = this.collectFormData();
    
    // Show loading
    this.showToast('💾 Đang lưu...', 'info');
    
    // Simulate API call (replace with actual endpoint)
    setTimeout(() => {
      this.isSubmitting = false;
      this.showToast('✅ Đã lưu thành công!', 'success');
      
      // Clear draft
      localStorage.removeItem('epa_form_draft');
      
      // Haptic feedback
      this.vibrate(200);
    }, 1500);
  }
  
  showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `mobile-toast ${type}`;
    toast.textContent = message;
    
    document.body.appendChild(toast);
    
    setTimeout(() => toast.classList.add('show'), 100);
    setTimeout(() => {
      toast.classList.remove('show');
      setTimeout(() => toast.remove(), 300);
    }, 3000);
  }
  
  vibrate(duration) {
    if ('vibrate' in navigator) {
      navigator.vibrate(duration);
    }
  }
  
  handleOrientationChange() {
    // Adjust layout for orientation change
    const isLandscape = window.orientation === 90 || window.orientation === -90;
    document.body.classList.toggle('landscape-mode', isLandscape);
  }
  
  debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  }
}

// CSS for mobile enhancements
const mobileCSS = `
  .mobile-epa-mode .question-item {
    margin-bottom: 2rem;
    padding: 1.5rem;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  }
  
  .stepper-buttons {
    display: flex;
    gap: 8px;
    margin-top: 8px;
  }
  
  .stepper-btn {
    width: 44px;
    height: 44px;
    border: 2px solid var(--primary-color);
    background: var(--bg-primary);
    color: var(--primary-color);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 16px;
    cursor: pointer;
    transition: all 0.2s ease;
  }
  
  .stepper-btn:active {
    transform: scale(0.95);
    background: var(--primary-color);
    color: white;
  }
  
  .char-counter {
    text-align: right;
    font-size: 12px;
    color: var(--text-muted);
    margin-top: 4px;
  }
  
  .char-counter.warning {
    color: var(--warning-color);
  }
  
  .mobile-fab {
    position: fixed;
    bottom: 20px;
    right: 20px;
    width: 56px;
    height: 56px;
    border-radius: 50%;
    background: var(--primary-color);
    color: white;
    border: none;
    font-size: 20px;
    box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
    z-index: 1000;
    cursor: pointer;
    transition: all 0.3s ease;
  }
  
  .mobile-fab:active {
    transform: scale(0.95);
  }
  
  .question-indicators {
    display: flex;
    justify-content: center;
    gap: 8px;
    margin: 20px 0;
  }
  
  .indicator {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    background: var(--gray-300);
    cursor: pointer;
    transition: all 0.2s ease;
  }
  
  .indicator.active {
    background: var(--primary-color);
    transform: scale(1.2);
  }
  
  .question-navigation {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin: 20px 0;
    padding: 16px;
    background: var(--bg-secondary);
    border-radius: 12px;
  }
  
  .nav-btn {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 12px 16px;
    border: none;
    background: var(--primary-color);
    color: white;
    border-radius: 8px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s ease;
  }
  
  .nav-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
  
  .question-counter {
    font-weight: 600;
    color: var(--text-primary);
  }
  
  .mobile-progress-bar {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
    background: var(--gray-200);
    z-index: 1001;
  }
  
  .progress-fill {
    height: 100%;
    background: var(--primary-color);
    transition: width 0.3s ease;
    width: 0%;
  }
  
  .mobile-toast {
    position: fixed;
    bottom: 100px;
    left: 50%;
    transform: translateX(-50%) translateY(100px);
    background: var(--gray-800);
    color: white;
    padding: 12px 20px;
    border-radius: 25px;
    font-size: 14px;
    z-index: 1002;
    transition: all 0.3s ease;
  }
  
  .mobile-toast.show {
    transform: translateX(-50%) translateY(0);
  }
  
  .mobile-toast.success {
    background: var(--success-color);
  }
  
  .mobile-toast.warning {
    background: var(--warning-color);
  }
  
  .mobile-toast.error {
    background: var(--error-color);
  }
  
  .draft-prompt {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0,0,0,0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1003;
  }
  
  .draft-content {
    background: var(--bg-primary);
    padding: 2rem;
    border-radius: 12px;
    text-align: center;
    max-width: 300px;
    margin: 1rem;
  }
  
  .draft-actions {
    display: flex;
    gap: 12px;
    margin-top: 1rem;
  }
  
  @keyframes ripple {
    to {
      transform: scale(4);
      opacity: 0;
    }
  }
  
  .input-focused {
    transform: scale(1.02);
    transition: transform 0.2s ease;
  }
  
  @media (orientation: landscape) {
    .mobile-fab {
      bottom: 10px;
      right: 10px;
    }
    
    .question-navigation {
      margin: 10px 0;
      padding: 12px;
    }
  }
`;

// Inject CSS
const styleSheet = document.createElement('style');
styleSheet.textContent = mobileCSS;
document.head.appendChild(styleSheet);

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  window.mobileEPA = new MobileEPAForm();
  
  // Load draft if available
  window.mobileEPA.loadDraft();
});

console.log('📱 Mobile EPA form enhancements loaded');