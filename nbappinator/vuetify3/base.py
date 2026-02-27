# CDN URLs - all from jsdelivr with @latest
# Using jsdelivr's ESM support (+esm suffix)
# See: https://www.jsdelivr.com/esm
VUE3_CDN = "https://cdn.jsdelivr.net/npm/vue@latest/dist/vue.esm-browser.js"
VUETIFY3_CDN = "https://cdn.jsdelivr.net/npm/vuetify@latest/dist/vuetify.esm.js"
VUETIFY3_CSS = "https://cdn.jsdelivr.net/npm/vuetify@latest/dist/vuetify.min.css"
MDI_CSS = "https://cdn.jsdelivr.net/npm/@mdi/font@latest/css/materialdesignicons.min.css"

# Shared JavaScript for loading Vue 3 + Vuetify 3
VUETIFY_LOADER_JS = f"""
// Global cache to prevent duplicate loading
const VUETIFY_CACHE = window.__VUETIFY3_CACHE__ = window.__VUETIFY3_CACHE__ || {{
    vue: null,
    vuetify: null,
    cssLoaded: false,
    importMapAdded: false,
    loading: null,
}};

// Load CSS once
function loadCSS(href, id) {{
    if (!document.getElementById(id)) {{
        const link = document.createElement('link');
        link.id = id;
        link.rel = 'stylesheet';
        link.href = href;
        document.head.appendChild(link);
    }}
}}

// Add import map for bare module specifiers
function addImportMap() {{
    if (VUETIFY_CACHE.importMapAdded) return;
    if (document.getElementById('vuetify-import-map')) {{
        VUETIFY_CACHE.importMapAdded = true;
        return;
    }}

    const importMap = document.createElement('script');
    importMap.type = 'importmap';
    importMap.id = 'vuetify-import-map';
    importMap.textContent = JSON.stringify({{
        imports: {{
            "vue": "{VUE3_CDN}"
        }}
    }});
    document.head.appendChild(importMap);
    VUETIFY_CACHE.importMapAdded = true;
}}

// Load Vue 3 and Vuetify 3 (cached)
async function loadVuetify() {{
    if (VUETIFY_CACHE.loading) {{
        return VUETIFY_CACHE.loading;
    }}

    if (VUETIFY_CACHE.vue && VUETIFY_CACHE.vuetify) {{
        return {{
            Vue: VUETIFY_CACHE.vue,
            Vuetify: VUETIFY_CACHE.vuetify,
        }};
    }}

    VUETIFY_CACHE.loading = (async () => {{
        // Load CSS
        if (!VUETIFY_CACHE.cssLoaded) {{
            loadCSS('{VUETIFY3_CSS}', 'vuetify3-css');
            loadCSS('{MDI_CSS}', 'mdi-css');
            VUETIFY_CACHE.cssLoaded = true;
        }}

        // Add import map so Vuetify can resolve "vue"
        addImportMap();

        // Load Vue 3 first
        if (!VUETIFY_CACHE.vue) {{
            const vueModule = await import('{VUE3_CDN}');
            VUETIFY_CACHE.vue = vueModule;
        }}

        // Load Vuetify 3 (will use import map to resolve "vue")
        if (!VUETIFY_CACHE.vuetify) {{
            const vuetifyModule = await import('{VUETIFY3_CDN}');
            VUETIFY_CACHE.vuetify = vuetifyModule;
        }}

        return {{
            Vue: VUETIFY_CACHE.vue,
            Vuetify: VUETIFY_CACHE.vuetify,
        }};
    }})();

    return VUETIFY_CACHE.loading;
}}

// Helper to calculate luminance from RGB
function getLuminance(r, g, b) {{
    return 0.299 * r + 0.587 * g + 0.114 * b;
}}

// Helper to parse color string to RGB (handles rgb(), rgba(), and hex)
function parseColor(colorStr) {{
    if (!colorStr) return null;
    colorStr = colorStr.trim();

    // Handle hex colors (#rgb, #rrggbb)
    if (colorStr.startsWith('#')) {{
        let hex = colorStr.slice(1);
        if (hex.length === 3) {{
            hex = hex[0] + hex[0] + hex[1] + hex[1] + hex[2] + hex[2];
        }}
        if (hex.length >= 6) {{
            return {{
                r: parseInt(hex.slice(0, 2), 16),
                g: parseInt(hex.slice(2, 4), 16),
                b: parseInt(hex.slice(4, 6), 16)
            }};
        }}
    }}

    // Handle rgb() and rgba()
    const rgbMatch = colorStr.match(/\\d+/g);
    if (rgbMatch && rgbMatch.length >= 3) {{
        return {{
            r: parseInt(rgbMatch[0]),
            g: parseInt(rgbMatch[1]),
            b: parseInt(rgbMatch[2])
        }};
    }}
    return null;
}}

function fixWidgetBackground(el, isDark) {{
    const bgColor = isDark ? '#1e1e1e' : '#ffffff';
    const existingStyle = document.getElementById('vuetify3-bg-fix');

    // Remove old style if theme changed
    if (existingStyle) {{
        existingStyle.remove();
    }}

    const style = document.createElement('style');
    style.id = 'vuetify3-bg-fix';
    style.textContent = `
        :root {{
            --nbapp-spacing-xs: 4px;
            --nbapp-spacing-sm: 8px;
            --nbapp-spacing-md: 12px;
            --nbapp-spacing-lg: 16px;
            --nbapp-radius: 4px;
            --nbapp-font-mono: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
            --nbapp-border-color: rgba(128, 128, 128, 0.3);
            --nbapp-surface-variant: rgba(128, 128, 128, 0.08);
        }}
        .cell-output-ipywidget-background,
        .cell-output-ipywidget-background > *,
        .jp-OutputArea-output,
        .jp-RenderedHTMLCommon,
        .widget-subarea,
        .widget-vbox,
        .widget-hbox {{
            background-color: ${{bgColor}} !important;
            background: ${{bgColor}} !important;
        }}
        .v-theme--dark .v-list {{
            background-color: #1e1e1e !important;
        }}
        .v-theme--light .v-list {{
            background-color: #ffffff !important;
        }}
        .vuetify-inline-select {{
            position: relative;
        }}
        .vuetify-inline-select .v-text-field {{
            cursor: pointer;
        }}
        .vuetify-inline-select .v-input {{
            margin-bottom: 0;
        }}
        .vuetify-inline-select .v-input__details {{
            display: none;
        }}
        .vuetify-inline-select-list {{
            border: 1px solid var(--nbapp-border-color);
            border-radius: var(--nbapp-radius);
            border-top-left-radius: 0;
            border-top-right-radius: 0;
            margin-top: -1px;
            max-height: 200px;
            overflow-y: auto;
        }}
        .vuetify-inline-select-list .v-list-item {{
            min-height: 32px;
        }}
        .vuetify-inline-select-list .v-list-item-title {{
            font-size: 14px !important;
        }}

        /* Normalize font sizes across all Vuetify components */
        .v-theme--dark, .v-theme--light {{
            font-size: 14px;
        }}
        .v-field__input, .v-list-item-title, .v-label {{
            font-size: 14px !important;
        }}

        /* Expansion panel content - indented under header */
        .nbapp-expansion-content {{
            padding: var(--nbapp-spacing-sm) var(--nbapp-spacing-md) !important;
            padding-left: var(--nbapp-spacing-lg) !important;
            margin-top: 0 !important;
            background: transparent !important;
        }}

        /* Hidden expansion content */
        .nbapp-expansion-content--hidden {{
            display: none !important;
        }}

        /* Tab content panel - indented under tab bar */
        .nbapp-tab-content {{
            padding: var(--nbapp-spacing-sm) var(--nbapp-spacing-md) !important;
            padding-left: var(--nbapp-spacing-lg) !important;
            margin-top: 0 !important;
            background: transparent !important;
        }}

        /* Section spacing between major sections */
        .nbapp-section-gap {{
            height: var(--nbapp-spacing-lg);
        }}
    `;
    document.head.appendChild(style);
}}

// Apply theme background color to an element
// Uses Vuetify CSS variables when available, fallback to hardcoded values
function applyThemeBackground(el, isDark) {{
    // Set initial colors (fallback values)
    el.style.backgroundColor = isDark ? '#1e1e1e' : '#ffffff';
    el.style.color = isDark ? 'rgba(255, 255, 255, 0.87)' : 'rgba(0, 0, 0, 0.87)';

    // After Vuetify mounts, use CSS variables via style attribute
    // Vuetify sets --v-theme-surface and --v-theme-on-surface as RGB triplets
    requestAnimationFrame(() => {{
        el.style.backgroundColor = 'rgb(var(--v-theme-surface, ' + (isDark ? '30, 30, 30' : '255, 255, 255') + '))';
        el.style.color = 'rgb(var(--v-theme-on-surface, ' + (isDark ? '255, 255, 255' : '0, 0, 0') + '))';
    }});
}}

// Apply only text color (no background) for transparent containers
function applyThemeTextColor(el, isDark) {{
    el.style.color = isDark ? 'rgba(255, 255, 255, 0.87)' : 'rgba(0, 0, 0, 0.87)';
    requestAnimationFrame(() => {{
        el.style.color = 'rgb(var(--v-theme-on-surface, ' + (isDark ? '255, 255, 255' : '0, 0, 0') + '))';
    }});
}}

// Set Vuetify theme using the non-deprecated API
function setVuetifyTheme(vuetify, isDark) {{
    const themeName = isDark ? 'dark' : 'light';
    vuetify.theme.global.name = themeName;
}}

// Initialize Vuetify with proper theme detection and background fix
// Returns {{ vuetify, isDark, mountEl }}
function initVuetify(el) {{
    const isDark = detectTheme(el);
    fixWidgetBackground(el, isDark);

    // Create wrapper with theme class (no background - let notebook show through)
    const mountEl = document.createElement('div');
    mountEl.className = isDark ? 'v-theme--dark' : 'v-theme--light';
    applyThemeTextColor(mountEl, isDark);
    mountEl.style.padding = '4px';
    el.appendChild(mountEl);

    const {{ createVuetify }} = window.__VUETIFY3_CACHE__.vuetify;
    const vuetify = createVuetify({{
        theme: {{
            defaultTheme: isDark ? 'dark' : 'light',
            themes: {{
                light: {{
                    colors: {{
                        primary: '#1976D2',
                        success: '#4CAF50',
                        error: '#FF5252',
                        warning: '#FB8C00',
                        info: '#2196F3',
                    }}
                }},
                dark: {{
                    colors: {{
                        primary: '#2196F3',
                        success: '#4CAF50',
                        error: '#FF5252',
                        warning: '#FFB300',
                        info: '#2196F3',
                    }}
                }}
            }}
        }},
        defaults: {{
            VBtn: {{ density: 'default' }},
            VTextField: {{ variant: 'outlined', density: 'compact' }},
            VSelect: {{ variant: 'outlined', density: 'compact' }},
            VTextarea: {{ variant: 'outlined', density: 'compact' }},
            VCheckbox: {{ density: 'compact' }},
            VRadioGroup: {{ density: 'compact' }},
            VSlider: {{ density: 'compact' }},
        }},
    }});

    return {{ vuetify, isDark, mountEl }};
}}

// Setup theme change watcher for a Vuetify instance
function setupThemeWatcher(vuetify, el, mountEl) {{
    const isDark = detectTheme(el);
    setVuetifyTheme(vuetify, isDark);
    if (mountEl) {{
        mountEl.className = isDark ? 'v-theme--dark' : 'v-theme--light';
        applyThemeTextColor(mountEl, isDark);
    }}

    onThemeChange((newIsDark) => {{
        setVuetifyTheme(vuetify, newIsDark);
        fixWidgetBackground(el, newIsDark);
        if (mountEl) {{
            mountEl.className = newIsDark ? 'v-theme--dark' : 'v-theme--light';
            applyThemeTextColor(mountEl, newIsDark);
        }}
    }}, el);
}}

// Debug theme detection - call this to see what's being detected
function debugTheme(el) {{
    const body = document.body;
    const html = document.documentElement;
    const styles = getComputedStyle(html);
    const info = [];

    info.push('=== Theme Detection Debug ===');

    // VS Code classes (checked first!)
    info.push(`[1] body.vscode-dark: ${{body.classList.contains('vscode-dark')}}`);
    info.push(`[1] body.vscode-light: ${{body.classList.contains('vscode-light')}}`);

    // VS Code attributes
    info.push(`[2] data-vscode-theme-kind: "${{body.getAttribute('data-vscode-theme-kind') || html.getAttribute('data-vscode-theme-kind') || ''}}"`);

    // VS Code CSS vars
    info.push(`[3] --vscode-editor-background: "${{styles.getPropertyValue('--vscode-editor-background')}}"`);

    // Jupyter
    info.push(`[4] data-jp-theme-light: "${{body.getAttribute('data-jp-theme-light') || ''}}"`);
    info.push(`[5] data-jp-theme-name: "${{body.getAttribute('data-jp-theme-name') || ''}}"`);

    // Element backgrounds
    if (el) {{
        let current = el;
        let depth = 0;
        while (current && current !== document && depth < 5) {{
            const bg = window.getComputedStyle(current).backgroundColor;
            info.push(`[6] Element[${{depth}}] ${{current.tagName}}: bg=${{bg}}`);
            depth++;
            current = current.parentElement;
        }}
    }}

    // Media query
    info.push(`[7] prefers-color-scheme dark: ${{window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches}}`);

    // Final result
    info.push(`\\n>>> detectTheme result: ${{detectTheme(el) ? 'DARK' : 'LIGHT'}}`);

    return info.join('\\n');
}}

// Detect current theme (dark/light)
// Pass the widget's element to detect theme from actual rendered styles
function detectTheme(el) {{
    const body = document.body;
    const html = document.documentElement;

    // Method 1: VS Code class-based (most reliable - VS Code sets this on body)
    // Check this FIRST because VS Code widget outputs have hardcoded white backgrounds
    if (body.classList.contains('vscode-dark') || html.classList.contains('vscode-dark')) {{
        return true;
    }}
    if (body.classList.contains('vscode-light') || html.classList.contains('vscode-light')) {{
        return false;
    }}

    // Method 2: VS Code attribute-based
    const vscodeTheme = body.getAttribute('data-vscode-theme-kind') ||
                        html.getAttribute('data-vscode-theme-kind');
    if (vscodeTheme) {{
        return vscodeTheme.includes('dark');
    }}

    // Method 3: VS Code CSS custom properties
    const styles = getComputedStyle(html);
    const vscodeVars = [
        '--vscode-editor-background',
        '--vscode-notebook-editorBackground'
    ];
    for (const varName of vscodeVars) {{
        const value = styles.getPropertyValue(varName);
        if (value && value.trim()) {{
            const rgb = parseColor(value.trim());
            if (rgb) {{
                return getLuminance(rgb.r, rgb.g, rgb.b) < 128;
            }}
        }}
    }}

    // Method 4: Jupyter Lab / Voila - data-jp-theme-light attribute
    if (body.hasAttribute('data-jp-theme-light')) {{
        return body.getAttribute('data-jp-theme-light') === 'false';
    }}

    // Method 5: Jupyter Lab / Voila - data-jp-theme-name attribute
    if (body.hasAttribute('data-jp-theme-name')) {{
        const themeName = body.getAttribute('data-jp-theme-name') || '';
        return themeName.toLowerCase().includes('dark');
    }}

    // Method 6: Check computed background of widget element or ancestors
    // (Skip this for VS Code since widget outputs have hardcoded backgrounds)
    if (el) {{
        let current = el;
        while (current && current !== document) {{
            const style = window.getComputedStyle(current);
            const bg = style.backgroundColor;
            if (bg && bg !== 'transparent' && bg !== 'rgba(0, 0, 0, 0)') {{
                const rgb = parseColor(bg);
                if (rgb) {{
                    return getLuminance(rgb.r, rgb.g, rgb.b) < 128;
                }}
            }}
            current = current.parentElement;
        }}
    }}

    // Method 7: CSS media query (system preference)
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {{
        return true;
    }}

    // Default to light theme
    return false;
}}

// Watch for theme changes
function onThemeChange(callback, el) {{
    let lastTheme = detectTheme(el);

    function checkTheme() {{
        const currentTheme = detectTheme(el);
        if (currentTheme !== lastTheme) {{
            lastTheme = currentTheme;
            callback(currentTheme);
        }}
    }}

    // Poll for changes (catches CSS variable changes)
    const interval = setInterval(checkTheme, 500);

    // Also observe attribute changes on body/html
    const observer = new MutationObserver(checkTheme);
    observer.observe(document.body, {{
        attributes: true,
        attributeFilter: ['class', 'data-vscode-theme-kind', 'data-jp-theme-name', 'data-jp-theme-light']
    }});
    observer.observe(document.documentElement, {{
        attributes: true,
        attributeFilter: ['class', 'data-vscode-theme-kind']
    }});

    // Listen for system preference changes
    if (window.matchMedia) {{
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', checkTheme);
    }}

    return () => {{
        clearInterval(interval);
        observer.disconnect();
        if (window.matchMedia) {{
            window.matchMedia('(prefers-color-scheme: dark)').removeEventListener('change', checkTheme);
        }}
    }};
}}

// Configure Vue app to suppress benign Vuetify warnings about hoisted vnodes
// These warnings occur when using runtime template compilation with Vuetify
// but do not affect functionality
function configureApp(app) {{
    app.config.warnHandler = (msg, vm, trace) => {{
        // Suppress "Missing ref owner context" warnings from Vuetify internals
        if (msg.includes('Missing ref owner context') ||
            msg.includes('hoisted vnodes')) {{
            return;
        }}
        // Log other warnings normally
        console.warn('[Vue warn]: ' + msg + trace);
    }};
    return app;
}}
"""
