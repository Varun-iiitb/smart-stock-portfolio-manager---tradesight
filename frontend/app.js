/**
 * Tradesight - Full Stack JS Client Application
 * Premium, interactive SPA and analytics engine
 */

// ==================== STATE MANAGEMENT ====================
const state = {
    username: localStorage.getItem('tradesight_username') || null,
    activeTab: 'dashboard',
    researchTicker: null,
    researchStockName: null,
    exchangeRates: null,
};

// ==================== INITIALIZATION ====================
document.addEventListener('DOMContentLoaded', () => {
    initApp();
});

function initApp() {
    setupAuthListeners();
    setupTabListeners();
    setupDashboardListeners();
    setupPortfolioListeners();
    setupAnalysisListeners();
    setupResearchListeners();
    setupStockAutocomplete();

    // Check session
    if (state.username) {
        showMainView();
    } else {
        showAuthView();
    }
}

// ==================== AUTHENTICATION & VIEWS ====================
function showAuthView() {
    document.getElementById('main-section').classList.add('hidden');
    document.getElementById('main-section').classList.remove('active-view');
    document.getElementById('auth-section').classList.remove('hidden');
    document.getElementById('auth-section').classList.add('active-view');
    switchAuthView('login');
}

function showMainView() {
    document.getElementById('auth-section').classList.add('hidden');
    document.getElementById('auth-section').classList.remove('active-view');
    document.getElementById('main-section').classList.remove('hidden');
    document.getElementById('main-section').classList.add('active-view');
    
    // Update user display name and initials
    document.getElementById('user-display-name').textContent = state.username;
    document.getElementById('user-avatar-initial').textContent = state.username.charAt(0).toUpperCase();

    // Set default date values
    setDefaultDates();

    // Load initial tab data
    switchTab(state.activeTab);
}

function switchAuthView(view) {
    const loginForm = document.getElementById('login-form-container');
    const signupForm = document.getElementById('signup-form-container');
    
    // Clear errors/success
    document.getElementById('login-error').classList.add('hidden');
    document.getElementById('signup-error').classList.add('hidden');
    document.getElementById('signup-success').classList.add('hidden');

    if (view === 'login') {
        loginForm.classList.add('active');
        signupForm.classList.remove('active');
    } else {
        loginForm.classList.remove('active');
        signupForm.classList.add('active');
    }
}

function togglePasswordVisibility(inputId, btn) {
    const input = document.getElementById(inputId);
    if (input.type === 'password') {
        input.type = 'text';
        btn.textContent = '🙈';
    } else {
        input.type = 'password';
        btn.textContent = '👁';
    }
}

function setupAuthListeners() {
    // Login Submission
    const loginForm = document.getElementById('login-form');
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const usernameInput = document.getElementById('login-username');
        const passwordInput = document.getElementById('login-password');
        const submitBtn = document.getElementById('btn-login');
        const errorMsg = document.getElementById('login-error');
        const loader = submitBtn.querySelector('.btn-loader');

        errorMsg.classList.add('hidden');
        loader.classList.remove('hidden');
        submitBtn.disabled = true;

        try {
            const response = await fetch('/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    username: usernameInput.value.trim(),
                    password: passwordInput.value
                })
            });

            const data = await response.json();
            if (response.ok) {
                // Save user
                state.username = usernameInput.value.trim();
                localStorage.setItem('tradesight_username', state.username);
                
                // Clear form
                usernameInput.value = '';
                passwordInput.value = '';
                
                showMainView();
            } else {
                errorMsg.textContent = data.status || 'Invalid username or password';
                errorMsg.classList.remove('hidden');
            }
        } catch (error) {
            console.error('Login error:', error);
            errorMsg.textContent = 'Connection error. Please try again.';
            errorMsg.classList.remove('hidden');
        } finally {
            loader.classList.add('hidden');
            submitBtn.disabled = false;
        }
    });

    // Signup Submission
    const signupForm = document.getElementById('signup-form');
    signupForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const usernameInput = document.getElementById('signup-username');
        const emailInput = document.getElementById('signup-email');
        const passwordInput = document.getElementById('signup-password');
        const submitBtn = document.getElementById('btn-signup');
        const errorMsg = document.getElementById('signup-error');
        const successMsg = document.getElementById('signup-success');
        const loader = submitBtn.querySelector('.btn-loader');

        errorMsg.classList.add('hidden');
        successMsg.classList.add('hidden');
        loader.classList.remove('hidden');
        submitBtn.disabled = true;

        try {
            const response = await fetch('/register', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    username: usernameInput.value.trim(),
                    email: emailInput.value.trim(),
                    password: passwordInput.value
                })
            });

            if (response.status === 201) {
                successMsg.classList.remove('hidden');
                
                // Auto login after 1.5 seconds
                setTimeout(() => {
                    state.username = usernameInput.value.trim();
                    localStorage.setItem('tradesight_username', state.username);
                    
                    usernameInput.value = '';
                    emailInput.value = '';
                    passwordInput.value = '';
                    
                    showMainView();
                }, 1500);
            } else {
                const text = await response.text();
                errorMsg.textContent = text || 'Registration failed.';
                errorMsg.classList.remove('hidden');
            }
        } catch (error) {
            console.error('Signup error:', error);
            errorMsg.textContent = 'Connection error. Please try again.';
            errorMsg.classList.remove('hidden');
        } finally {
            loader.classList.add('hidden');
            submitBtn.disabled = false;
        }
    });
}

function logoutUser() {
    state.username = null;
    localStorage.removeItem('tradesight_username');
    showAuthView();
}

// ==================== NAVIGATION & TABS ====================
function setupTabListeners() {
    // Clean, standard routing handled by switchTab inline triggers in HTML
}

function switchTab(tabId) {
    state.activeTab = tabId;
    
    // Update sidebar UI active state
    const menuItems = document.querySelectorAll('.sidebar-menu .menu-item');
    menuItems.forEach(item => {
        item.classList.remove('active');
        // Simple mapping based on order: dashboard (0), portfolio (1), analysis (2), research (3)
        if (tabId === 'dashboard' && item.innerText.includes('Dashboard')) item.classList.add('active');
        if (tabId === 'portfolio' && item.innerText.includes('Portfolio')) item.classList.add('active');
        if (tabId === 'analysis' && item.innerText.includes('Analysis')) item.classList.add('active');
        if (tabId === 'research' && item.innerText.includes('Research')) item.classList.add('active');
    });

    // Toggle panels
    const panels = document.querySelectorAll('.tab-panel');
    panels.forEach(panel => {
        panel.classList.remove('active');
    });
    
    const activePanel = document.getElementById(`tab-${tabId}`);
    if (activePanel) {
        activePanel.classList.add('active');
    }

    // Trigger tab-specific loaders
    if (tabId === 'dashboard') {
        loadDashboardMetrics();
    } else if (tabId === 'portfolio') {
        loadPortfolioHoldings();
    }
}

// Set standard dynamic dates
function setDefaultDates() {
    const today = new Date().toISOString().split('T')[0];
    
    // Purchase Date input
    const addDateInput = document.getElementById('add-stock-date');
    if (addDateInput) addDateInput.value = today;

    // Analysis Date inputs
    const oneMonthAgo = new Date();
    oneMonthAgo.setMonth(oneMonthAgo.getMonth() - 1);
    const fromDateStr = oneMonthAgo.toISOString().split('T')[0];
    
    const analysisFrom = document.getElementById('analysis-daily-from');
    const analysisTo = document.getElementById('analysis-daily-to');
    
    if (analysisFrom) analysisFrom.value = fromDateStr;
    if (analysisTo) analysisTo.value = today;
}

// ==================== DASHBOARD TAB ====================
function setupDashboardListeners() {
    document.getElementById('btn-refresh-dashboard').addEventListener('click', () => {
        loadDashboardMetrics();
    });

    document.getElementById('btn-export-dashboard').addEventListener('click', () => {
        exportExcelReport('btn-export-dashboard');
    });

    // Currency Converter Interactive Hooks
    const amountInput = document.getElementById('exchange-amount');
    const baseSel = document.getElementById('exchange-base-currency');
    const targetSel = document.getElementById('exchange-target-currency');

    amountInput.addEventListener('input', calculateExchange);
    baseSel.addEventListener('change', calculateExchange);
    targetSel.addEventListener('change', calculateExchange);
}

async function loadDashboardMetrics() {
    if (!state.username) return;

    const refreshBtn = document.getElementById('btn-refresh-dashboard');
    const loader = refreshBtn.querySelector('.loader-inline');
    loader.classList.remove('hidden');
    refreshBtn.disabled = true;

    try {
        // Parallel requests for higher efficiency
        const [valRes, pnlRes, invRes] = await Promise.all([
            fetch('/portfolio_value_today', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username: state.username })
            }),
            fetch('/profit_loss_value', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username: state.username })
            }),
            fetch('/investment_value', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username: state.username })
            })
        ]);

        const totalValue = parseFloat(await valRes.text()) || 0;
        const totalPnl = parseFloat(await pnlRes.text()) || 0;
        const totalInv = parseFloat(await invRes.text()) || 0;

        // Render Values
        document.getElementById('portfolio-value-display').textContent = `₹${totalValue.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
        document.getElementById('portfolio-investment-display').textContent = `₹${totalInv.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
        
        const pnlDisplay = document.getElementById('portfolio-pnl-display');
        pnlDisplay.textContent = `${totalPnl >= 0 ? '+' : ''}₹${totalPnl.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;

        // Dynamic visual coloring & icons
        const pnlCard = document.getElementById('pnl-metric-card');
        const pnlGraphic = document.getElementById('pnl-graphic');
        
        if (totalPnl >= 0) {
            pnlDisplay.className = 'metric-value text-emerald';
            pnlCard.style.borderColor = 'rgba(6, 214, 160, 0.2)';
            pnlGraphic.className = 'metric-graphic glow-emerald';
            pnlGraphic.textContent = '📈';
        } else {
            pnlDisplay.className = 'metric-value text-rose';
            pnlCard.style.borderColor = 'rgba(255, 0, 110, 0.2)';
            pnlGraphic.className = 'metric-graphic glow-rose';
            pnlGraphic.textContent = '📉';
        }

        // Fetch currency codes if not loaded already
        if (!state.exchangeRates) {
            await loadCurrencyCodes();
        }

    } catch (error) {
        console.error('Error fetching dashboard metrics:', error);
    } finally {
        loader.classList.add('hidden');
        refreshBtn.disabled = false;
    }
}

async function loadCurrencyCodes() {
    try {
        const response = await fetch('/exchange_rate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        
        if (response.ok) {
            const data = await response.json();
            state.exchangeRates = data;

            const baseSel = document.getElementById('exchange-base-currency');
            const targetSel = document.getElementById('exchange-target-currency');

            // Clear defaults
            baseSel.innerHTML = '';
            targetSel.innerHTML = '';

            // Populate options sorted by Currency Name
            for (const [name, code] of Object.entries(data)) {
                const opt1 = document.createElement('option');
                opt1.value = code;
                opt1.textContent = `${code} - ${name}`;
                if (code === 'INR') opt1.selected = true; // Default source: INR
                baseSel.appendChild(opt1);

                const opt2 = document.createElement('option');
                opt2.value = code;
                opt2.textContent = `${code} - ${name}`;
                if (code === 'USD') opt2.selected = true; // Default target: USD
                targetSel.appendChild(opt2);
            }

            calculateExchange();
        }
    } catch (err) {
        console.error('Error listing currencies:', err);
    }
}

async function calculateExchange() {
    const amount = parseFloat(document.getElementById('exchange-amount').value) || 0;
    const base = document.getElementById('exchange-base-currency').value;
    const target = document.getElementById('exchange-target-currency').value;
    const resultInput = document.getElementById('exchange-result');

    if (amount <= 0 || !base || !target) {
        resultInput.value = '';
        return;
    }

    if (base === target) {
        resultInput.value = amount.toFixed(2);
        return;
    }

    try {
        const response = await fetch('/exchange_rate_value', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                base_currency: base,
                target_currency: target
            })
        });

        if (response.ok) {
            const rate = parseFloat(await response.text());
            if (rate) {
                const converted = amount * rate;
                resultInput.value = converted.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
            }
        }
    } catch (error) {
        console.error('Exchange calculation error:', error);
    }
}

// ==================== CONTRACT NOTE IMPORT ====================
async function importContractNotes(clearExisting = false) {
    const btn    = document.getElementById('btn-import-contract-notes');
    const loader = btn.querySelector('.loader-inline');
    const logCard = document.getElementById('import-log-card');
    const logBody = document.getElementById('import-log-body');
    const logCount = document.getElementById('import-log-count');

    btn.disabled = true;
    loader.classList.remove('hidden');
    logCard.classList.remove('hidden');
    logBody.innerHTML = '<div style="color:#3a86ff">Scanning contract notes folder…</div>';

    try {
        const resp = await fetch('/import_contract_notes', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username: state.username, clear_existing: clearExisting })
        });

        const data = await resp.json();

        if (!resp.ok) {
            logBody.innerHTML = `<div style="color:#ff006e">Error: ${data.error || 'Unknown error'}</div>`;
            return;
        }

        const total   = data.total_imported || 0;
        const results = data.results || [];

        logCount.textContent = `${results.length} file(s) processed`;

        logBody.innerHTML = results.map(line => {
            const color = line.includes('error') || line.includes('not found')
                ? '#ff006e'
                : line.includes('already imported')
                    ? '#9ca3af'
                    : '#06d6a0';
            return `<div style="color:${color}; padding:2px 0; border-bottom:1px solid rgba(255,255,255,0.04)">${line}</div>`;
        }).join('');

        logBody.innerHTML += `<div style="color:#3a86ff; margin-top:8px; font-weight:600">
            ✓ Total trades imported: ${total}
        </div>`;

        if (total > 0) {
            await loadPortfolioHoldings();
            loadDashboardMetrics();
        }
    } catch (err) {
        logBody.innerHTML = `<div style="color:#ff006e">Connection error: ${err.message}</div>`;
    } finally {
        btn.disabled = false;
        loader.classList.add('hidden');
    }
}

// ==================== PORTFOLIO TAB ====================
function setupPortfolioListeners() {
    document.getElementById('btn-import-contract-notes').addEventListener('click', () => {
        importContractNotes(false);
    });

    document.getElementById('btn-export-portfolio').addEventListener('click', () => {
        exportExcelReport('btn-export-portfolio');
    });

    // Form Submission
    const addForm = document.getElementById('add-stock-form');
    addForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const stockNameInput = document.getElementById('add-stock-name');
        const qtyInput = document.getElementById('add-stock-qty');
        const priceInput = document.getElementById('add-stock-price');
        const dateInput = document.getElementById('add-stock-date');
        const submitBtn = addForm.querySelector('button[type="submit"]');
        const errorMsg = document.getElementById('add-stock-error');
        const loader = submitBtn.querySelector('.loader-inline');

        errorMsg.classList.add('hidden');
        loader.classList.remove('hidden');
        submitBtn.disabled = true;

        try {
            const response = await fetch('/add_stock', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    username: state.username,
                    stock_name: stockNameInput.value.trim(),
                    quantity: parseInt(qtyInput.value),
                    price_per_share: parseFloat(priceInput.value),
                    date: dateInput.value
                })
            });

            if (response.status === 201) {
                // Clear fields
                stockNameInput.value = '';
                qtyInput.value = '';
                priceInput.value = '';
                setDefaultDates();
                
                // Reload holdings & update metrics
                await loadPortfolioHoldings();
                loadDashboardMetrics();
            } else {
                const data = await response.json();
                errorMsg.textContent = data.error || 'Failed to add stock position.';
                errorMsg.classList.remove('hidden');
            }
        } catch (error) {
            console.error('Error adding stock:', error);
            errorMsg.textContent = 'Connection error. Live pricing lookup may be offline.';
            errorMsg.classList.remove('hidden');
        } finally {
            loader.classList.add('hidden');
            submitBtn.disabled = false;
        }
    });
}

async function loadPortfolioHoldings() {
    if (!state.username) return;

    const tbody = document.querySelector('#holdings-table tbody');
    tbody.innerHTML = `
        <tr>
            <td colspan="8" class="text-center font-inter">
                <div class="loader-inline" style="display:inline-block; margin-right:8px;"></div> Loading asset details...
            </td>
        </tr>
    `;

    try {
        const response = await fetch('/get_stock_data', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username: state.username })
        });

        if (response.ok) {
            const stocks = await response.json();
            tbody.innerHTML = '';

            document.getElementById('positions-count').textContent = `${stocks.length} Position${stocks.length === 1 ? '' : 's'}`;

            if (stocks.length === 0) {
                tbody.innerHTML = `
                    <tr class="empty-state-row">
                        <td colspan="8" class="text-center font-inter">No stock assets in portfolio. Use the form below to add positions.</td>
                    </tr>
                `;
                return;
            }

            stocks.forEach(stock => {
                // Format: [name, qty, bprice, bdate, cprice, pnl_val, change_pct, stock_id]
                const name = stock[0];
                const qty = parseInt(stock[1]);
                const bPrice = parseFloat(stock[2]);
                const bDate = stock[3];
                const cPrice = parseFloat(stock[4]) || bPrice;
                const pnl = parseFloat(stock[5]) || 0;

                // Parse percent change string nicely
                let pctStr = stock[6] || '0.00%';
                if (pctStr.startsWith('%')) pctStr = pctStr.slice(1);
                const pctVal = parseFloat(pctStr) || 0;

                const stockId = stock[stock.length - 1];

                const row = document.createElement('tr');

                // P&L color logic
                const pnlClass = pnl >= 0 ? 'text-emerald font-semibold' : 'text-rose font-semibold';
                const pctClass = pctVal >= 0 ? 'text-emerald font-semibold' : 'text-rose font-semibold';

                row.innerHTML = `
                    <td class="font-semibold">${name}</td>
                    <td class="font-inter">${qty.toLocaleString()}</td>
                    <td class="font-inter">₹${bPrice.toFixed(2)}</td>
                    <td class="font-inter text-muted">${bDate}</td>
                    <td class="font-inter">₹${cPrice.toFixed(2)}</td>
                    <td class="${pnlClass} font-inter">${pnl >= 0 ? '+' : ''}₹${pnl.toFixed(2)}</td>
                    <td class="${pctClass} font-inter">${pctVal >= 0 ? '+' : ''}${pctVal.toFixed(2)}%</td>
                    <td>
                        <button class="btn-delete-row" title="Remove position" data-stock-id="${stockId}" data-stock-name="${name.replace(/"/g, '&quot;')}">
                            <svg viewBox="0 0 24 24" width="16" height="16" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6l-2 14a2 2 0 0 1-2 2H9a2 2 0 0 1-2-2L5 6"></path><path d="M10 11v6"></path><path d="M14 11v6"></path><path d="M9 6V4a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2v2"></path></svg>
                        </button>
                    </td>
                `;
                tbody.appendChild(row);
            });

            // Attach delete handlers
            tbody.querySelectorAll('.btn-delete-row').forEach(btn => {
                btn.addEventListener('click', () => {
                    const id = btn.getAttribute('data-stock-id');
                    const sname = btn.getAttribute('data-stock-name');
                    deleteStockPosition(id, sname);
                });
            });
        } else {
            tbody.innerHTML = `
                <tr>
                    <td colspan="8" class="text-center text-rose font-inter">Failed to retrieve positions database.</td>
                </tr>
            `;
        }
    } catch (error) {
        console.error('Error fetching holdings:', error);
        tbody.innerHTML = `
            <tr>
                <td colspan="8" class="text-center text-rose font-inter">Server connection lost.</td>
            </tr>
        `;
    }
}

async function deleteStockPosition(stockId, stockName) {
    if (!stockId) return;
    if (!confirm(`Remove "${stockName}" from your portfolio?`)) return;

    try {
        const response = await fetch('/delete_stock', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                username: state.username,
                stock_id: parseInt(stockId)
            })
        });

        if (response.ok) {
            await loadPortfolioHoldings();
            loadDashboardMetrics();
        } else {
            alert('Failed to delete position. Please try again.');
        }
    } catch (error) {
        console.error('Error deleting stock:', error);
        alert('Server connection error during deletion.');
    }
}

// ==================== ANALYSIS TAB ====================
function setupAnalysisListeners() {
    // Handle period selection radios
    const radios = document.querySelectorAll('input[name="analysis-period"]');
    radios.forEach(radio => {
        radio.addEventListener('change', (e) => {
            const mode = e.target.value;
            
            // Toggle containers
            document.getElementById('analysis-range-daily').classList.remove('active');
            document.getElementById('analysis-range-monthly').classList.remove('active');
            document.getElementById('analysis-range-yearly').classList.remove('active');
            
            document.getElementById(`analysis-range-${mode}`).classList.add('active');
        });
    });

    // Populate dropdown years
    populateDropdownYears();

    // Chart visualizer submit hook
    const analysisForm = document.getElementById('analysis-form');
    analysisForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const stockNameInput = document.getElementById('analysis-stock-name');
        const mode = document.querySelector('input[name="analysis-period"]:checked').value;
        const submitBtn = analysisForm.querySelector('button[type="submit"]');
        const loader = submitBtn.querySelector('.btn-loader');

        loader.classList.remove('hidden');
        submitBtn.disabled = true;

        // Prepare request body
        const reqData = {
            username: state.username,
            stock_name: stockNameInput.value.trim(),
            mode: mode
        };

        if (mode === 'daily') {
            reqData.start_date = document.getElementById('analysis-daily-from').value;
            reqData.end_date = document.getElementById('analysis-daily-to').value;
        } else if (mode === 'monthly') {
            reqData.month = document.getElementById('analysis-monthly-month').value;
            reqData.year = document.getElementById('analysis-monthly-year').value;
        } else if (mode === 'yearly') {
            reqData.year = document.getElementById('analysis-yearly-year').value;
        }

        // Show skeletons and clear existing iframe sources to indicate state transition
        document.getElementById('analysis-charts-section').classList.remove('hidden');
        
        const skeletons = document.querySelectorAll('.chart-loading-skeleton');
        skeletons.forEach(sk => sk.classList.remove('hidden'));
        
        document.getElementById('iframe-candlestick').src = 'about:blank';
        document.getElementById('iframe-profitloss').src = 'about:blank';
        document.getElementById('iframe-portfoliovalue').src = 'about:blank';

        try {
            const response = await fetch('/plot_all_graphs', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(reqData)
            });

            if (response.ok) {
                // Set cache-busting timestamp parameters
                const timestamp = Date.now();
                
                document.getElementById('candlestick-chart-title').textContent = `Candlestick Chart for ${stockNameInput.value.trim()}`;
                
                document.getElementById('iframe-candlestick').src = `/charts/candlestick_chart.html?t=${timestamp}`;
                document.getElementById('iframe-profitloss').src = `/charts/profit_loss.html?t=${timestamp}`;
                document.getElementById('iframe-portfoliovalue').src = `/charts/portfolio_value.html?t=${timestamp}`;
                
                // Hide loaders after a 300ms micro-buffer to let iframes load smoothly
                setTimeout(() => {
                    skeletons.forEach(sk => sk.classList.add('hidden'));
                }, 300);
            }
        } catch (error) {
            console.error('Error plotting graphs:', error);
            alert('Failed to construct visual analytics charts.');
            skeletons.forEach(sk => sk.classList.add('hidden'));
        } finally {
            loader.classList.add('hidden');
            submitBtn.disabled = false;
        }
    });
}

function populateDropdownYears() {
    const mYearSel = document.getElementById('analysis-monthly-year');
    const yYearSel = document.getElementById('analysis-yearly-year');
    const currentYear = new Date().getFullYear();

    mYearSel.innerHTML = '';
    yYearSel.innerHTML = '';

    // Reverse order: 2010 to currentYear
    for (let yr = currentYear; yr >= 2010; yr--) {
        const opt1 = document.createElement('option');
        opt1.value = yr;
        opt1.textContent = yr;
        mYearSel.appendChild(opt1);

        const opt2 = document.createElement('option');
        opt2.value = yr;
        opt2.textContent = yr;
        yYearSel.appendChild(opt2);
    }
}

// ==================== RESEARCH TAB ====================
function setupResearchListeners() {
    const researchForm = document.getElementById('research-search-form');
    researchForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const stockQuery = document.getElementById('research-stock-query');
        const submitBtn = researchForm.querySelector('button[type="submit"]');
        const loader = submitBtn.querySelector('.btn-loader');

        loader.classList.remove('hidden');
        submitBtn.disabled = true;

        const nameQuery = stockQuery.value.trim();
        state.researchStockName = nameQuery;

        try {
            // 1. Fetch detailed financial ratios and ticker information
            const res = await fetch('/detailed_stock_data', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ stock_name: nameQuery })
            });

            if (res.ok) {
                const stock = await res.json();
                state.researchTicker = stock.symbol;

                // Render metrics UI
                document.getElementById('research-company-name').textContent = stock.name || nameQuery;
                document.getElementById('research-company-symbol').textContent = stock.symbol || 'N/A';
                document.getElementById('research-company-exchange').textContent = stock.exchange || 'N/A';
                document.getElementById('research-company-industry').textContent = stock.industry || 'General Equity';
                
                const curPrice = parseFloat(stock.currentPrice) || 0;
                document.getElementById('research-live-price').textContent = `₹${curPrice.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;

                const prevClose = parseFloat(stock.previousClose) || curPrice;
                const changeAmt = curPrice - prevClose;
                const changePct = (changeAmt / prevClose) * 100;

                const priceIndicator = document.getElementById('research-price-change');
                priceIndicator.textContent = `${changeAmt >= 0 ? '+' : ''}${changeAmt.toFixed(2)} (${changeAmt >= 0 ? '+' : ''}${changePct.toFixed(2)}%)`;

                if (changeAmt >= 0) {
                    priceIndicator.className = 'price-pill-indicator positive font-inter';
                } else {
                    priceIndicator.className = 'price-pill-indicator negative font-inter';
                }

                // Financial grid parameters
                document.getElementById('ratio-prevclose').textContent = prevClose.toFixed(2);
                document.getElementById('ratio-open').textContent = (parseFloat(stock.open) || 0).toFixed(2);
                document.getElementById('ratio-high').textContent = (parseFloat(stock.high) || 0).toFixed(2);
                document.getElementById('ratio-low').textContent = (parseFloat(stock.low) || 0).toFixed(2);
                document.getElementById('ratio-52high').textContent = (parseFloat(stock['52_week_high']) || 0).toFixed(2);
                document.getElementById('ratio-52low').textContent = (parseFloat(stock['52_week_low']) || 0).toFixed(2);
                document.getElementById('ratio-pe').textContent = stock.Pe_ratio ? parseFloat(stock.Pe_ratio).toFixed(2) : 'N/A';
                document.getElementById('ratio-eps').textContent = stock.EPS ? parseFloat(stock.EPS).toFixed(2) : 'N/A';
                document.getElementById('ratio-bookvalue').textContent = stock.bookValue ? parseFloat(stock.bookValue).toFixed(2) : 'N/A';
                document.getElementById('ratio-200avg').textContent = stock['200avg'] ? parseFloat(stock['200avg']).toFixed(2) : 'N/A';

                // Display elements
                document.getElementById('research-empty-state').classList.add('hidden');
                document.getElementById('research-details-section').classList.remove('hidden');

                // 2. Load dynamic pricing chart for default 1M duration
                const activeRangeBtn = document.querySelector('.chart-range-buttons .range-btn.active');
                await updateResearchChartDuration('1M', activeRangeBtn);

                // 3. Trigger Neural predictions
                await triggerProphetForecast();
            } else {
                alert('No listings or live metrics found for security. Double check ticker name.');
            }
        } catch (error) {
            console.error('Research search error:', error);
            alert('Failed to retrieve corporate coordinates.');
        } finally {
            loader.classList.add('hidden');
            submitBtn.disabled = false;
        }
    });
}

async function updateResearchChartDuration(durationCode, btnElement) {
    if (!state.researchStockName) return;

    // Toggle active classes on range buttons
    const rangeBtns = document.querySelectorAll('.chart-range-buttons .range-btn');
    rangeBtns.forEach(btn => btn.classList.remove('active'));
    if (btnElement) btnElement.classList.add('active');

    const skeleton = document.getElementById('research-chart-skeleton');
    skeleton.classList.remove('hidden');
    document.getElementById('iframe-research-live').src = 'about:blank';

    // Compute dates
    const today = new Date();
    const fromDate = new Date();

    switch (durationCode) {
        case '1D':
            fromDate.setDate(today.getDate() - 2); // Get 2 days of buffer for yfinance
            break;
        case '5D':
            fromDate.setDate(today.getDate() - 6);
            break;
        case '1M':
            fromDate.setMonth(today.getMonth() - 1);
            break;
        case '6M':
            fromDate.setMonth(today.getMonth() - 6);
            break;
        case '1Y':
            fromDate.setFullYear(today.getFullYear() - 1);
            break;
        case '5Y':
            fromDate.setFullYear(today.getFullYear() - 5);
            break;
        default:
            fromDate.setMonth(today.getMonth() - 1);
    }

    const start_date = fromDate.toISOString().split('T')[0];
    const end_date = today.toISOString().split('T')[0];

    try {
        const response = await fetch('/plot_live_price', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                stock_name: state.researchStockName,
                start_date: start_date,
                end_date: end_date
            })
        });

        if (response.ok) {
            document.getElementById('iframe-research-live').src = `/charts/live_stock_prices.html?t=${Date.now()}`;
            setTimeout(() => {
                skeleton.classList.add('hidden');
            }, 300);
        } else {
            skeleton.classList.add('hidden');
        }
    } catch (err) {
        console.error('Error generating pricing history:', err);
        skeleton.classList.add('hidden');
    }
}

async function triggerProphetForecast() {
    if (!state.researchStockName) return;

    const skeleton = document.getElementById('prediction-chart-skeleton');
    const decisionText = document.getElementById('prediction-model-decision-text');
    
    skeleton.classList.remove('hidden');
    document.getElementById('iframe-research-predict').src = 'about:blank';
    decisionText.textContent = 'Training XGBoost classifier and fitting ARIMA trend...';

    try {
        const response = await fetch('/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ stock_name: state.researchStockName })
        });

        if (response.ok) {
            const data = await response.json();
            decisionText.textContent = data.message1 || 'Forecast complete.';

            document.getElementById('iframe-research-predict').src = `/charts/prediction.html?t=${Date.now()}`;
            setTimeout(() => {
                skeleton.classList.add('hidden');
            }, 300);
        } else {
            decisionText.textContent = 'Forecast request failed. Please try again.';
            skeleton.classList.add('hidden');
        }
    } catch (error) {
        console.error('Predict error:', error);
        decisionText.textContent = 'Machine learning fitting failed - server may be busy.';
        skeleton.classList.add('hidden');
    }
}

// ==================== EXCEL REPORT EXPORT ====================
async function exportExcelReport(triggerBtnId) {
    if (!state.username) return;

    const btn = document.getElementById(triggerBtnId);
    const loader = btn.querySelector('.loader-inline');
    loader.classList.remove('hidden');
    btn.disabled = true;

    try {
        const response = await fetch('/export', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username: state.username })
        });

        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            
            const a = document.createElement('a');
            a.href = url;
            a.download = `${state.username}_portfolio_report.xlsx`;
            document.body.appendChild(a);
            a.click();
            
            // Clean up resources
            a.remove();
            window.URL.revokeObjectURL(url);
        } else {
            alert('Failed to generate export file. Ensure charts are generated at least once.');
        }
    } catch (error) {
        console.error('Excel report generation failed:', error);
        alert('Server network error during report rendering.');
    } finally {
        loader.classList.add('hidden');
        btn.disabled = false;
    }
}

// ==================== STOCK AUTOCOMPLETE ====================
function setupStockAutocomplete() {
    const inputs = [
        { inputId: 'add-stock-name', dropdownId: 'add-stock-name-suggestions' },
        { inputId: 'analysis-stock-name', dropdownId: 'analysis-stock-name-suggestions' },
        { inputId: 'research-stock-query', dropdownId: 'research-stock-query-suggestions' }
    ];

    inputs.forEach(cfg => attachAutocomplete(cfg.inputId, cfg.dropdownId));

    // Click outside closes any open dropdown
    document.addEventListener('click', (e) => {
        document.querySelectorAll('.autocomplete-dropdown').forEach(dd => {
            if (!dd.contains(e.target) && e.target.id !== dd.id.replace('-suggestions', '')) {
                dd.classList.add('hidden');
            }
        });
    });
}

function attachAutocomplete(inputId, dropdownId) {
    const input = document.getElementById(inputId);
    const dropdown = document.getElementById(dropdownId);
    if (!input || !dropdown) return;

    let debounceTimer = null;
    let activeIndex = -1;
    let currentItems = [];

    const renderItems = (items) => {
        currentItems = items;
        activeIndex = -1;
        if (!items || items.length === 0) {
            dropdown.innerHTML = '';
            dropdown.classList.add('hidden');
            return;
        }
        dropdown.innerHTML = items.map((it, idx) => `
            <div class="autocomplete-item" data-idx="${idx}">
                <div class="autocomplete-item-main">
                    <span class="autocomplete-symbol">${escapeHtml(it.symbol)}</span>
                    <span class="autocomplete-name">${escapeHtml(it.name || '')}</span>
                </div>
                <span class="autocomplete-exchange">${escapeHtml(it.exchange || '')}</span>
            </div>
        `).join('');
        dropdown.classList.remove('hidden');

        dropdown.querySelectorAll('.autocomplete-item').forEach(el => {
            el.addEventListener('mousedown', (e) => {
                e.preventDefault(); // keep input focus
                const idx = parseInt(el.getAttribute('data-idx'));
                pick(idx);
            });
        });
    };

    const pick = (idx) => {
        const item = currentItems[idx];
        if (!item) return;
        // Use the company name (more user-friendly) but fall back to symbol
        input.value = item.name || item.symbol;
        dropdown.innerHTML = '';
        dropdown.classList.add('hidden');
        currentItems = [];
    };

    const highlight = () => {
        dropdown.querySelectorAll('.autocomplete-item').forEach((el, idx) => {
            el.classList.toggle('active', idx === activeIndex);
        });
    };

    input.addEventListener('input', () => {
        const query = input.value.trim();
        clearTimeout(debounceTimer);
        if (query.length < 2) {
            dropdown.innerHTML = '';
            dropdown.classList.add('hidden');
            return;
        }
        debounceTimer = setTimeout(async () => {
            try {
                const response = await fetch('/search_tickers', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ query })
                });
                if (response.ok) {
                    const items = await response.json();
                    renderItems(items);
                }
            } catch (err) {
                console.error('Autocomplete fetch failed:', err);
            }
        }, 220);
    });

    input.addEventListener('keydown', (e) => {
        if (dropdown.classList.contains('hidden') || currentItems.length === 0) return;
        if (e.key === 'ArrowDown') {
            e.preventDefault();
            activeIndex = (activeIndex + 1) % currentItems.length;
            highlight();
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            activeIndex = (activeIndex - 1 + currentItems.length) % currentItems.length;
            highlight();
        } else if (e.key === 'Enter' && activeIndex >= 0) {
            e.preventDefault();
            pick(activeIndex);
        } else if (e.key === 'Escape') {
            dropdown.classList.add('hidden');
        }
    });

    input.addEventListener('blur', () => {
        // Delay so click on a dropdown item can land first
        setTimeout(() => dropdown.classList.add('hidden'), 150);
    });

    input.addEventListener('focus', () => {
        if (currentItems.length > 0) dropdown.classList.remove('hidden');
    });
}

function escapeHtml(str) {
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
}
