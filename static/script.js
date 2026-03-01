let sessionId = generateSessionId();
let scamDetected = false;
let turnCount = 0;
let conversationStopped = false;

function generateSessionId() {
    return 'demo-' + Date.now() + '-' + Math.random().toString(36).substr(2, 6);
}

function useExample(btn) {
    if (conversationStopped) return;
    document.getElementById('chatInput').value = btn.textContent;
    document.getElementById('chatInput').focus();
}

function resetSession() {
    sessionId = generateSessionId();
    scamDetected = false;
    turnCount = 0;
    conversationStopped = false;

    document.getElementById('chatMessages').innerHTML = `
        <div class="welcome">
            <svg class="welcome-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
            <h3>Begin Simulation</h3>
            <p>Send a scam message below to test the honeypot agent. The system will detect the threat and deploy an AI persona to engage and extract intelligence.</p>
        </div>
    `;

    const indicator = document.getElementById('statusIndicator');
    indicator.className = 'threat-status';
    document.getElementById('statusText').textContent = 'Awaiting input';
    document.getElementById('probBar').style.display = 'none';
    document.getElementById('intelBody').innerHTML = '<p class="empty-state">No data extracted yet.</p>';
    document.getElementById('turnCount').textContent = '0';
    document.getElementById('intelCount').textContent = '0';
    document.getElementById('chatInput').disabled = false;
    document.getElementById('sendBtn').disabled = false;
}

async function sendMessage() {
    const input = document.getElementById('chatInput');
    const text = input.value.trim();
    if (!text || conversationStopped) return;

    input.value = '';

    const welcome = document.querySelector('.welcome');
    if (welcome) welcome.remove();

    addMessage(text, 'scammer');

    const typing = document.getElementById('typingIndicator');
    typing.classList.add('active');
    scrollToBottom();

    input.disabled = true;
    document.getElementById('sendBtn').disabled = true;

    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                sessionId: sessionId,
                message: text
            })
        });

        const data = await response.json();
        typing.classList.remove('active');

        if (data.error) {
            addSystemMessage('Error: ' + data.error, false);
            input.disabled = false;
            document.getElementById('sendBtn').disabled = false;
            return;
        }

        if (data.scamDetected && !scamDetected) {
            scamDetected = true;
            addSystemMessage('Threat identified — agent deployed to extract intelligence.', true);
        }

        updateStatus(data.scamDetected, data.scamProbability);
        addMessage(data.reply, 'agent');

        turnCount++;
        document.getElementById('turnCount').textContent = turnCount;
        updateIntel(data.extracted);

        if (data.stopFlag) {
            conversationStopped = true;
            addSystemMessage('Session complete. Sufficient intelligence has been gathered.', false);
            input.disabled = true;
            document.getElementById('sendBtn').disabled = true;
            return;
        }

        input.disabled = false;
        document.getElementById('sendBtn').disabled = false;
        input.focus();

    } catch (err) {
        typing.classList.remove('active');
        addSystemMessage('Connection error. Please try again.', false);
        input.disabled = false;
        document.getElementById('sendBtn').disabled = false;
    }
}

function addMessage(text, type) {
    const container = document.getElementById('chatMessages');
    const label = type === 'scammer' ? 'Attacker (You)' : 'Honeypot Agent';
    const msg = document.createElement('div');
    msg.className = `message ${type}`;
    msg.innerHTML = `
        <div class="message-label">${label}</div>
        <div class="message-bubble">${escapeHtml(text)}</div>
    `;
    container.appendChild(msg);
    scrollToBottom();
}

function addSystemMessage(text, isScamAlert) {
    const container = document.getElementById('chatMessages');
    const msg = document.createElement('div');
    msg.className = 'system-message';
    msg.innerHTML = `<div class="system-bubble ${isScamAlert ? 'scam-alert' : ''}">${escapeHtml(text)}</div>`;
    container.appendChild(msg);
    scrollToBottom();
}

function updateStatus(isScam, probability) {
    const indicator = document.getElementById('statusIndicator');
    const statusText = document.getElementById('statusText');
    const probBar = document.getElementById('probBar');
    const probValue = document.getElementById('probValue');
    const probFill = document.getElementById('probFill');

    if (isScam) {
        indicator.className = 'threat-status active';
        statusText.textContent = 'Threat Detected';
        indicator.querySelector('.threat-dot').className = 'threat-dot detected';
    } else {
        indicator.className = 'threat-status';
        statusText.textContent = 'No threat detected';
        indicator.querySelector('.threat-dot').className = 'threat-dot safe';
    }

    if (probability !== undefined && probability !== null) {
        probBar.style.display = 'block';
        const pct = Math.round(probability * 100);
        probValue.textContent = pct + '%';
        probFill.style.width = pct + '%';
        if (pct > 70) probFill.style.background = 'var(--danger)';
        else if (pct > 40) probFill.style.background = 'var(--warning)';
        else probFill.style.background = 'var(--success)';
    }
}

function updateIntel(extracted) {
    if (!extracted) return;

    const body = document.getElementById('intelBody');
    let html = '';
    let totalCount = 0;

    const sections = [
        { key: 'phoneNumbers', label: 'Phone Numbers', tagClass: 'tag-phone' },
        { key: 'upiIds', label: 'UPI IDs', tagClass: 'tag-upi' },
        { key: 'phishingLinks', label: 'Phishing Links', tagClass: 'tag-link' },
        { key: 'bankAccounts', label: 'Bank Accounts', tagClass: 'tag-bank' },
        { key: 'suspiciousKeywords', label: 'Keywords', tagClass: 'tag-keyword' },
    ];

    for (const section of sections) {
        const items = extracted[section.key] || [];
        if (items.length > 0) {
            totalCount += items.length;
            html += `<div class="intel-section">
                <div class="intel-label">${section.label}</div>
                <div class="intel-items">
                    ${items.map(item => `<span class="intel-tag ${section.tagClass}">${escapeHtml(item)}</span>`).join('')}
                </div>
            </div>`;
        }
    }

    if (!html) {
        html = '<p class="empty-state">No data extracted yet.</p>';
    }

    body.innerHTML = html;
    document.getElementById('intelCount').textContent = totalCount;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function scrollToBottom() {
    const container = document.getElementById('chatMessages');
    container.scrollTop = container.scrollHeight;
}

document.getElementById('chatInput').addEventListener('keydown', function(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});
