import anywidget
import traitlets

from .base import VUETIFY_LOADER_JS


class ThemeDebugWidget(anywidget.AnyWidget):
    """Comprehensive debug widget that tests ALL widget types and theme detection.

    This widget creates test instances of every Vuetify component type and shows:
    1. Theme detection results for all methods
    2. Visual rendering of each widget type in both variants
    3. Computed styles and CSS classes for debugging
    4. DOM hierarchy and background colors

    Usage:
        from nbappinator.vuetify3 import ThemeDebugWidget
        debug = ThemeDebugWidget()
        display(debug)
    """

    debug_info = traitlets.Unicode("Loading...").tag(sync=True)

    _esm = f"""
    {VUETIFY_LOADER_JS}

    async function render({{ model, el }}) {{
        const {{ Vue, Vuetify }} = await loadVuetify();
        const {{ createVuetify }} = Vuetify;
        const {{ createApp, ref }} = Vue;

        // Style the container
        el.style.cssText = 'font-family: system-ui, -apple-system, sans-serif; padding: 16px;';

        // Helper to create a section
        function createSection(title) {{
            const section = document.createElement('div');
            section.style.cssText = 'margin-bottom: 20px; padding: 12px; border: 1px solid #666; border-radius: 8px;';
            const header = document.createElement('h3');
            header.textContent = title;
            header.style.cssText = 'margin: 0 0 12px 0; font-size: 14px; color: #888;';
            section.appendChild(header);
            return section;
        }}

        // Helper to get widget info
        function getWidgetInfo(container, selector = '.v-btn, .v-select, .v-checkbox, .v-tabs, .v-card') {{
            const widget = container.querySelector(selector);
            if (!widget) return 'NOT FOUND';
            const style = getComputedStyle(widget);
            return `class="${{widget.className.split(' ').filter(c => c.startsWith('v-')).join(' ')}}" bg=${{style.backgroundColor}} color=${{style.color}}`;
        }}

        // ========================================
        // SECTION 1: Theme Detection Debug Info
        // ========================================
        const infoSection = createSection('1. THEME DETECTION');
        const pre = document.createElement('pre');
        pre.style.cssText = 'font-family: monospace; font-size: 11px; padding: 10px; margin: 0; background: #1a1a1a; color: #d4d4d4; border-radius: 4px; overflow-x: auto; white-space: pre-wrap;';
        infoSection.appendChild(pre);
        el.appendChild(infoSection);

        // ========================================
        // SECTION 2: Button Variants
        // ========================================
        const btnSection = createSection('2. BUTTON VARIANTS (most important - this is what app uses)');
        const btnMount = document.createElement('div');
        btnSection.appendChild(btnMount);
        el.appendChild(btnSection);

        const {{ vuetify: vuetifyBtn, mountEl: mountElBtn }} = initVuetify(btnSection);
        const appBtn = createApp({{
            template: `
                <div style="display: flex; flex-wrap: wrap; gap: 8px; align-items: center;">
                    <div style="display: flex; flex-direction: column; gap: 4px;">
                        <v-btn color="primary" variant="elevated">elevated (default)</v-btn>
                        <span style="font-size: 10px; opacity: 0.7;">Solid bg, white text</span>
                    </div>
                    <div style="display: flex; flex-direction: column; gap: 4px;">
                        <v-btn color="primary" variant="outlined">outlined (app.py uses this)</v-btn>
                        <span style="font-size: 10px; opacity: 0.7;">Border only, primary text</span>
                    </div>
                    <div style="display: flex; flex-direction: column; gap: 4px;">
                        <v-btn color="primary" variant="flat">flat</v-btn>
                        <span style="font-size: 10px; opacity: 0.7;">Solid bg, no shadow</span>
                    </div>
                    <div style="display: flex; flex-direction: column; gap: 4px;">
                        <v-btn color="primary" variant="text">text</v-btn>
                        <span style="font-size: 10px; opacity: 0.7;">Text only</span>
                    </div>
                    <div style="display: flex; flex-direction: column; gap: 4px;">
                        <v-btn color="primary" variant="tonal">tonal</v-btn>
                        <span style="font-size: 10px; opacity: 0.7;">Subtle bg</span>
                    </div>
                </div>
            `
        }});
        configureApp(appBtn);
        appBtn.use(vuetifyBtn);
        appBtn.mount(mountElBtn);
        setupThemeWatcher(vuetifyBtn, btnSection, mountElBtn);

        // ========================================
        // SECTION 3: Form Inputs
        // ========================================
        const formSection = createSection('3. FORM INPUTS');
        el.appendChild(formSection);

        const {{ vuetify: vuetifyForm, mountEl: mountElForm }} = initVuetify(formSection);
        const appForm = createApp({{
            setup() {{
                return {{
                    selectValue: ref('Option 1'),
                    checkValue: ref(true),
                    textValue: ref('Sample text'),
                }};
            }},
            template: `
                <div style="display: flex; flex-wrap: wrap; gap: 16px; align-items: flex-start;">
                    <v-select
                        v-model="selectValue"
                        :items="['Option 1', 'Option 2', 'Option 3']"
                        label="Select"
                        variant="outlined"
                        density="compact"
                        style="min-width: 150px;"
                    />
                    <v-text-field
                        v-model="textValue"
                        label="Text Field"
                        variant="outlined"
                        density="compact"
                        style="min-width: 150px;"
                    />
                    <v-checkbox
                        v-model="checkValue"
                        label="Checkbox"
                        density="compact"
                    />
                </div>
            `
        }});
        configureApp(appForm);
        appForm.use(vuetifyForm);
        appForm.mount(mountElForm);
        setupThemeWatcher(vuetifyForm, formSection, mountElForm);

        // ========================================
        // SECTION 4: Tabs
        // ========================================
        const tabsSection = createSection('4. TABS');
        el.appendChild(tabsSection);

        const {{ vuetify: vuetifyTabs, mountEl: mountElTabs }} = initVuetify(tabsSection);
        const appTabs = createApp({{
            setup() {{
                return {{ tab: ref(0) }};
            }},
            template: `
                <v-tabs v-model="tab" color="primary" density="compact">
                    <v-tab :value="0">Tab One</v-tab>
                    <v-tab :value="1">Tab Two</v-tab>
                    <v-tab :value="2">Tab Three</v-tab>
                </v-tabs>
            `
        }});
        configureApp(appTabs);
        appTabs.use(vuetifyTabs);
        appTabs.mount(mountElTabs);
        setupThemeWatcher(vuetifyTabs, tabsSection, mountElTabs);

        // ========================================
        // SECTION 5: Expansion Panel
        // ========================================
        const expSection = createSection('5. EXPANSION PANEL');
        el.appendChild(expSection);

        const {{ vuetify: vuetifyExp, mountEl: mountElExp }} = initVuetify(expSection);
        const appExp = createApp({{
            setup() {{
                return {{ panel: ref([0]) }};
            }},
            template: `
                <v-expansion-panels v-model="panel" variant="accordion">
                    <v-expansion-panel>
                        <v-expansion-panel-title>Config Section</v-expansion-panel-title>
                        <v-expansion-panel-text>
                            This is the content inside the expansion panel.
                        </v-expansion-panel-text>
                    </v-expansion-panel>
                </v-expansion-panels>
            `
        }});
        configureApp(appExp);
        appExp.use(vuetifyExp);
        appExp.mount(mountElExp);
        setupThemeWatcher(vuetifyExp, expSection, mountElExp);

        // ========================================
        // SECTION 6: Card
        // ========================================
        const cardSection = createSection('6. CARD');
        el.appendChild(cardSection);

        const {{ vuetify: vuetifyCard, mountEl: mountElCard }} = initVuetify(cardSection);
        const appCard = createApp({{
            template: `
                <v-card variant="outlined" style="max-width: 300px;">
                    <v-card-title>Card Title</v-card-title>
                    <v-card-text>This is card content with some text.</v-card-text>
                </v-card>
            `
        }});
        configureApp(appCard);
        appCard.use(vuetifyCard);
        appCard.mount(mountElCard);
        setupThemeWatcher(vuetifyCard, cardSection, mountElCard);

        // ========================================
        // SECTION 7: AG Grid Debug
        // ========================================
        const agSection = createSection('7. AG GRID DEBUG');
        const agPre = document.createElement('pre');
        agPre.style.cssText = 'font-family: monospace; font-size: 11px; padding: 10px; margin: 0; background: #1a1a1a; color: #d4d4d4; border-radius: 4px; overflow-x: auto; white-space: pre-wrap;';
        agSection.appendChild(agPre);
        el.appendChild(agSection);

        // ========================================
        // SECTION 8: DOM Ancestry Check
        // ========================================
        const domSection = createSection('8. DOM ANCESTRY (background colors from widget to body)');
        const domPre = document.createElement('pre');
        domPre.style.cssText = 'font-family: monospace; font-size: 11px; padding: 10px; margin: 0; background: #1a1a1a; color: #d4d4d4; border-radius: 4px; overflow-x: auto; white-space: pre-wrap;';
        domSection.appendChild(domPre);
        el.appendChild(domSection);

        // ========================================
        // Gather and Display Debug Info
        // ========================================
        setTimeout(() => {{
            try {{
                const info = [];
                const body = document.body;
                const html = document.documentElement;
                const styles = getComputedStyle(html);

                // Theme detection methods
                info.push('METHOD 1 - VS Code class (checked first):');
                info.push(`  body.vscode-dark: ${{body.classList.contains('vscode-dark')}}`);
                info.push(`  body.vscode-light: ${{body.classList.contains('vscode-light')}}`);
                info.push(`  html.vscode-dark: ${{html.classList.contains('vscode-dark')}}`);

                info.push('\\nMETHOD 2 - VS Code attribute:');
                info.push(`  body data-vscode-theme-kind: "${{body.getAttribute('data-vscode-theme-kind') || '(none)' }}"`);
                info.push(`  html data-vscode-theme-kind: "${{html.getAttribute('data-vscode-theme-kind') || '(none)' }}"`);

                info.push('\\nMETHOD 3 - VS Code CSS vars:');
                info.push(`  --vscode-editor-background: "${{styles.getPropertyValue('--vscode-editor-background') || '(none)' }}"`);

                info.push('\\nMETHOD 4/5 - Jupyter:');
                info.push(`  data-jp-theme-light: "${{body.getAttribute('data-jp-theme-light') || '(none)' }}"`);
                info.push(`  data-jp-theme-name: "${{body.getAttribute('data-jp-theme-name') || '(none)' }}"`);

                info.push('\\nMETHOD 7 - Media query:');
                info.push(`  prefers-color-scheme dark: ${{window.matchMedia?.('(prefers-color-scheme: dark)')?.matches}}`);

                info.push('\\n>>> FINAL RESULT: detectTheme() = ' + (detectTheme(el) ? 'DARK' : 'LIGHT'));

                // Check Vuetify instances
                info.push('\\n--- VUETIFY INSTANCES ---');
                info.push(`Button section theme: ${{vuetifyBtn.theme.global.name}}`);
                info.push(`Form section theme: ${{vuetifyForm.theme.global.name}}`);
                info.push(`Tabs section theme: ${{vuetifyTabs.theme.global.name}}`);

                // Check mount element classes
                info.push('\\n--- MOUNT ELEMENT CLASSES ---');
                info.push(`Button mount: ${{mountElBtn.className}}`);
                info.push(`Form mount: ${{mountElForm.className}}`);
                info.push(`Tabs mount: ${{mountElTabs.className}}`);

                pre.textContent = info.join('\\n');

                // AG Grid debug
                const agInfo = [];

                // Check for AG Grid styles in DOM
                agInfo.push('--- AG GRID STYLES IN DOM ---');
                let agStyleCount = 0;
                document.querySelectorAll('style').forEach((s, i) => {{
                    const content = s.textContent || '';
                    if (content.includes('ag-theme') || content.includes('--ag-') || content.includes('.ag-root')) {{
                        agStyleCount++;
                        agInfo.push(`Style #${{i}}: ${{content.substring(0, 150).replace(/\\n/g, ' ')}}...`);
                    }}
                }});
                agInfo.push(`Total AG Grid styles found: ${{agStyleCount}}`);

                // Check for AG Grid elements
                agInfo.push('\\n--- AG GRID ELEMENTS ---');
                const agRoot = document.querySelector('.ag-root-wrapper');
                const agHeader = document.querySelector('.ag-header');
                const agBody = document.querySelector('.ag-body-viewport');
                const agRows = document.querySelectorAll('.ag-row');

                if (agRoot) {{
                    agInfo.push(`ag-root-wrapper found: class="${{agRoot.className}}"`);
                    agInfo.push(`  computed height: ${{getComputedStyle(agRoot).height}}`);
                }} else {{
                    agInfo.push('ag-root-wrapper: NOT FOUND (no grid on page?)');
                }}

                if (agHeader) {{
                    const headerStyle = getComputedStyle(agHeader);
                    agInfo.push(`ag-header found:`);
                    agInfo.push(`  height: ${{headerStyle.height}}`);
                    agInfo.push(`  position: ${{headerStyle.position}}`);
                    agInfo.push(`  top: ${{headerStyle.top}}`);
                }} else {{
                    agInfo.push('ag-header: NOT FOUND');
                }}

                if (agBody) {{
                    const bodyStyle = getComputedStyle(agBody);
                    agInfo.push(`ag-body-viewport found:`);
                    agInfo.push(`  height: ${{bodyStyle.height}}`);
                    agInfo.push(`  position: ${{bodyStyle.position}}`);
                    agInfo.push(`  top: ${{bodyStyle.top}}`);
                    agInfo.push(`  transform: ${{bodyStyle.transform}}`);
                }} else {{
                    agInfo.push('ag-body-viewport: NOT FOUND');
                }}

                agInfo.push(`\\nag-row elements found: ${{agRows.length}}`);
                if (agRows.length > 0) {{
                    const firstRow = agRows[0];
                    const rowStyle = getComputedStyle(firstRow);
                    agInfo.push(`First row:`);
                    agInfo.push(`  class: ${{firstRow.className}}`);
                    agInfo.push(`  transform: ${{rowStyle.transform}}`);
                    agInfo.push(`  top: ${{rowStyle.top}}`);
                }}

                // Check theme container
                agInfo.push('\\n--- THEME INJECTION ---');
                const bodyStyles = document.body.querySelectorAll('style');
                let themeInBody = 0;
                bodyStyles.forEach(s => {{
                    if ((s.textContent || '').includes('--ag-')) themeInBody++;
                }});
                agInfo.push(`Theme styles in body: ${{themeInBody}}`);

                const headStyles = document.head.querySelectorAll('style');
                let themeInHead = 0;
                headStyles.forEach(s => {{
                    if ((s.textContent || '').includes('--ag-')) themeInHead++;
                }});
                agInfo.push(`Theme styles in head: ${{themeInHead}}`);

                agPre.textContent = agInfo.join('\\n');

                // DOM ancestry
                const domInfo = [];
                let current = el;
                let depth = 0;
                while (current && current !== document && depth < 15) {{
                    const bg = getComputedStyle(current).backgroundColor;
                    const classes = current.className ? current.className.toString().substring(0, 60) : '';
                    domInfo.push(`[${{depth}}] ${{current.tagName}} bg=${{bg}} class="${{classes}}"`);
                    depth++;
                    current = current.parentElement;
                }}
                domPre.textContent = domInfo.join('\\n');

                // Update model
                model.set('debug_info', info.join('\\n') + '\\n\\n--- DOM ---\\n' + domInfo.join('\\n'));
                model.save_changes();
            }} catch(e) {{
                pre.textContent = 'ERROR: ' + e.message + '\\n' + e.stack;
            }}
        }}, 800);
    }}

    export default {{ render }}
    """
