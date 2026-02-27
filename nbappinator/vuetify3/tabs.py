import anywidget
import traitlets

from .base import VUETIFY_LOADER_JS


class VuetifyTabsWidget(anywidget.AnyWidget):
    """Tab bar widget using Vuetify 3 v-tabs."""

    tabs = traitlets.List([]).tag(sync=True)  # List of tab names
    selected = traitlets.Int(0).tag(sync=True)  # Selected tab index

    _esm = f"""
    {VUETIFY_LOADER_JS}

    async function render({{ model, el }}) {{
        const {{ Vue }} = await loadVuetify();
        const {{ createApp, ref, watch }} = Vue;

        const {{ vuetify, mountEl }} = initVuetify(el);

        const app = createApp({{
            data() {{
                return {{
                    tabs: model.get('tabs') || [],
                    selected: model.get('selected') ?? 0
                }};
            }},
            mounted() {{
                model.on('change:tabs', () => this.tabs = model.get('tabs') || []);
                model.on('change:selected', () => this.selected = model.get('selected') ?? 0);
            }},
            watch: {{
                selected(newVal) {{
                    model.set('selected', newVal);
                    model.save_changes();
                }}
            }},
            template: `
                <v-tabs
                    v-model="selected"
                    color="primary"
                    density="compact"
                    style="border-bottom: 1px solid rgba(128,128,128,0.2);"
                >
                    <v-tab v-for="(tab, i) in tabs" :key="i" :value="i">
                        {{{{ tab }}}}
                    </v-tab>
                </v-tabs>
            `
        }});

        configureApp(app);
        app.use(vuetify);
        app.mount(mountEl);
        setupThemeWatcher(vuetify, el, mountEl);

        return () => app.unmount();
    }}

    export default {{ render }}
    """
