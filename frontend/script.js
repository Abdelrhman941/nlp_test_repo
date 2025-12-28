// API Configuration
const API_BASE_URL = 'http://localhost:8000/api';

// State Management
let currentChatId = null;
let chats = JSON.parse(localStorage.getItem('chats')) || [];
let isWaitingForResponse = false;

// DOM Elements
const messagesContainer = document.getElementById('messages-container');
const messageInput = document.getElementById('message-input');
const sendBtn = document.getElementById('send-btn');
const chatList = document.getElementById('chat-list');
const newChatBtn = document.getElementById('new-chat-btn');
const chatTitle = document.getElementById('chat-title');
const welcomeScreen = document.getElementById('welcome-screen');
const sidebarToggle = document.getElementById('sidebar-toggle');
const sidebar = document.querySelector('.sidebar');
const scrollToBottomBtn = document.getElementById('scroll-to-bottom');

// ============================================
// Initialization
// ============================================

document.addEventListener('DOMContentLoaded', () => {
    renderChatList();
    setupEventListeners();

    // AUTO CHAT SESSION: Create default chat if no chats exist
    if (chats.length === 0) {
        createDefaultChat();
    } else {
        // Load last active chat
        const lastChat = chats[chats.length - 1];
        loadChat(lastChat.id);
    }
});

// ============================================
// Event Listeners
// ============================================

function setupEventListeners() {
    // Send button
    sendBtn.addEventListener('click', handleSendMessage);

    // Input field
    messageInput.addEventListener('input', handleInputChange);
    messageInput.addEventListener('keydown', handleInputKeydown);

    // New chat button
    newChatBtn.addEventListener('click', createNewChat);

    // Sidebar toggle
    sidebarToggle.addEventListener('click', toggleSidebar);

    // Scroll to bottom button
    scrollToBottomBtn.addEventListener('click', () => {
        messagesContainer.scrollTo({
            top: messagesContainer.scrollHeight,
            behavior: 'smooth'
        });
    });

    // Monitor scroll position for scroll-to-bottom button
    messagesContainer.addEventListener('scroll', handleScroll);

    // Example prompts
    document.querySelectorAll('.example-prompt').forEach(btn => {
        btn.addEventListener('click', () => {
            const prompt = btn.getAttribute('data-prompt');
            messageInput.value = prompt;
            handleInputChange();
            handleSendMessage();
        });
    });
}

function handleInputChange() {
    const hasText = messageInput.value.trim().length > 0;
    sendBtn.disabled = !hasText || isWaitingForResponse;

    // Auto-resize textarea
    messageInput.style.height = 'auto';
    messageInput.style.height = messageInput.scrollHeight + 'px';
}

function handleInputKeydown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        if (!sendBtn.disabled) {
            handleSendMessage();
        }
    }
}

// ============================================
// Chat Management
// ============================================

function createDefaultChat() {
    // Create a default "Untitled" chat automatically
    const chatId = 'chat_' + Date.now();
    const defaultChat = {
        id: chatId,
        title: 'Untitled',
        created: new Date().toISOString(),
        messages: []
    };

    chats.push(defaultChat);
    localStorage.setItem('chats', JSON.stringify(chats));

    currentChatId = chatId;
    renderChatList();

    // Update UI
    messagesContainer.innerHTML = '';
    messagesContainer.appendChild(welcomeScreen);
    welcomeScreen.style.display = 'block';
    chatTitle.textContent = 'Untitled';

    // Highlight the new chat in sidebar
    document.querySelectorAll('.chat-item').forEach(item => {
        item.classList.toggle('active', item.dataset.chatId === chatId);
    });
}

function createNewChat() {
    // Create a new "Untitled" chat
    const chatId = 'chat_' + Date.now();
    const newChat = {
        id: chatId,
        title: 'Untitled',
        created: new Date().toISOString(),
        messages: []
    };

    chats.push(newChat);
    localStorage.setItem('chats', JSON.stringify(chats));

    currentChatId = chatId;
    renderChatList();

    // Clear UI and restore welcome screen
    messagesContainer.innerHTML = '';
    messagesContainer.appendChild(welcomeScreen);
    welcomeScreen.style.display = 'block';
    chatTitle.textContent = 'Untitled';
    messageInput.value = '';
    messageInput.style.height = 'auto';
    handleInputChange();
    messageInput.focus();

    // Update active state
    document.querySelectorAll('.chat-item').forEach(item => {
        item.classList.toggle('active', item.dataset.chatId === chatId);
    });
}

function loadChat(chatId) {
    const chat = chats.find(c => c.id === chatId);
    if (!chat) return;

    currentChatId = chatId;
    welcomeScreen.style.display = 'none';
    chatTitle.textContent = chat.title;

    // Clear messages
    messagesContainer.innerHTML = '';

    // Render messages
    chat.messages.forEach(msg => {
        renderMessage(msg.role, msg.content, msg.sources);
    });

    // Update active state
    document.querySelectorAll('.chat-item').forEach(item => {
        item.classList.toggle('active', item.dataset.chatId === chatId);
    });

    scrollToBottom();
}

function saveChat(chatId, userMessage, assistantMessage, sources) {
    let chat = chats.find(c => c.id === chatId);

    if (!chat) {
        // This should not happen anymore, but keep as fallback
        chat = {
            id: chatId,
            title: userMessage.substring(0, 30) + (userMessage.length > 30 ? '...' : ''),
            created: new Date().toISOString(),
            messages: []
        };
        chats.push(chat);
    } else if (chat.title === 'Untitled' && chat.messages.length === 0) {
        // Update title from "Untitled" to first message
        chat.title = userMessage.substring(0, 30) + (userMessage.length > 30 ? '...' : '');
    }

    // Add messages
    chat.messages.push({
        role: 'user',
        content: userMessage,
        timestamp: new Date().toISOString()
    });

    chat.messages.push({
        role: 'assistant',
        content: assistantMessage,
        sources: sources,
        timestamp: new Date().toISOString()
    });

    // Save to localStorage
    localStorage.setItem('chats', JSON.stringify(chats));

    renderChatList();

    // Update chat title in header
    chatTitle.textContent = chat.title;
}

function deleteChat(chatId) {
    // Only delete the selected chat
    chats = chats.filter(c => c.id !== chatId);
    localStorage.setItem('chats', JSON.stringify(chats));

    if (currentChatId === chatId) {
        // If deleted chat was active, create a new default chat
        if (chats.length === 0) {
            createDefaultChat();
        } else {
            // Load the most recent chat
            const lastChat = chats[chats.length - 1];
            loadChat(lastChat.id);
        }
    }

    renderChatList();
}

// ============================================
// UI Rendering
// ============================================

function renderChatList() {
    chatList.innerHTML = '';

    // Sort chats by created date (newest first)
    const sortedChats = [...chats].sort((a, b) =>
        new Date(b.created) - new Date(a.created)
    );

    sortedChats.forEach(chat => {
        const chatItem = document.createElement('div');
        chatItem.className = 'chat-item';
        chatItem.dataset.chatId = chat.id;

        if (chat.id === currentChatId) {
            chatItem.classList.add('active');
        }

        chatItem.innerHTML = `
            <div class="chat-item-content">
                <div class="chat-item-title">${chat.title}</div>
            </div>
            <button class="chat-delete-btn" title="Delete">🗑️</button>
        `;

        // Click to load chat
        const content = chatItem.querySelector('.chat-item-content');
        content.addEventListener('click', () => {
            loadChat(chat.id);
        });

        // Delete button
        const deleteBtn = chatItem.querySelector('.chat-delete-btn');
        deleteBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            if (confirm('Delete this chat?')) {
                deleteChat(chat.id);
            }
        });

        chatList.appendChild(chatItem);
    });
}

function renderMessage(role, content, sources = null) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;

    const avatar = role === 'user' ? '👤' : '🐾';

    let sourcesHtml = '';
    if (sources && sources.length > 0) {
        sourcesHtml = `
            <div class="message-sources">
                <div class="sources-title">📚 Sources:</div>
                ${sources.map(source => `
                    <div class="source-item">
                        ${source.text}
                    </div>
                `).join('')}
            </div>
        `;
    }

    messageDiv.innerHTML = `
        <div class="message-avatar">${avatar}</div>
        <div class="message-content">
            <div class="message-text">${escapeHtml(content)}</div>
            ${sourcesHtml}
        </div>
    `;

    messagesContainer.appendChild(messageDiv);
    scrollToBottom();
}

function showLoadingIndicator() {
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'loading-indicator';
    loadingDiv.id = 'loading-indicator';

    loadingDiv.innerHTML = `
        <div class="loading-avatar">🐾</div>
        <div class="loading-content">
            <div class="loading-dots">
                <div class="loading-dot"></div>
                <div class="loading-dot"></div>
                <div class="loading-dot"></div>
            </div>
        </div>
    `;

    messagesContainer.appendChild(loadingDiv);
    scrollToBottom();
}

function hideLoadingIndicator() {
    const loadingDiv = document.getElementById('loading-indicator');
    if (loadingDiv) {
        loadingDiv.remove();
    }
}

// ============================================
// API Communication
// ============================================

async function handleSendMessage() {
    const message = messageInput.value.trim();
    if (!message || isWaitingForResponse) return;

    // Hide welcome screen
    if (welcomeScreen.style.display !== 'none') {
        welcomeScreen.style.display = 'none';
    }

    // Render user message
    renderMessage('user', message);

    // Clear input
    messageInput.value = '';
    messageInput.style.height = 'auto';
    handleInputChange();

    // Set waiting state
    isWaitingForResponse = true;
    sendBtn.disabled = true;

    // Show loading
    showLoadingIndicator();

    try {
        const response = await fetch(`${API_BASE_URL}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: message,
                chat_id: currentChatId
            })
        });

        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }

        const data = await response.json();

        // Hide loading
        hideLoadingIndicator();

        // Update chat ID
        currentChatId = data.chat_id;

        // Render assistant message
        renderMessage('assistant', data.message, data.sources);

        // Save chat
        saveChat(currentChatId, message, data.message, data.sources);

    } catch (error) {
        console.error('Error:', error);
        hideLoadingIndicator();

        renderMessage('assistant',
            '❌ Sorry, I encountered an error. Please make sure the backend server is running and try again.'
        );
    } finally {
        isWaitingForResponse = false;
        handleInputChange();
        messageInput.focus();
    }
}

// ============================================
// Utility Functions
// ============================================

function handleScroll() {
    // Check if user is near the bottom
    const threshold = 100; // pixels from bottom
    const distanceFromBottom = messagesContainer.scrollHeight - messagesContainer.scrollTop - messagesContainer.clientHeight;

    if (distanceFromBottom > threshold) {
        // User scrolled up, show button
        scrollToBottomBtn.style.display = 'flex';
    } else {
        // User is at bottom, hide button
        scrollToBottomBtn.style.display = 'none';
    }
}

function scrollToBottom() {
    setTimeout(() => {
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
        // Hide button when auto-scrolling to bottom
        scrollToBottomBtn.style.display = 'none';
    }, 100);
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function getTimeAgo(date) {
    const seconds = Math.floor((new Date() - date) / 1000);

    if (seconds < 60) return 'Just now';
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
    if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
    if (seconds < 604800) return `${Math.floor(seconds / 86400)}d ago`;

    return date.toLocaleDateString();
}

function toggleSidebar() {
    sidebar.classList.toggle('collapsed');
}
