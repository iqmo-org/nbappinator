import anywidget
import traitlets

from .base import VUETIFY_LOADER_JS


class VuetifyExpansionWidget(anywidget.AnyWidget):
    """Expansion panel header that controls sibling content visibility.

    This is a header-only widget - the actual content is controlled externally
    via the `expanded` trait which toggles visibility of sibling widgets.
    """

    title = traitlets.Unicode("").tag(sync=True)
    expanded = traitlets.Bool(True).tag(sync=True)

    _esm = f"""
    {VUETIFY_LOADER_JS}

    async function render({{ model, el }}) {{
        const {{ Vue }} = await loadVuetify();
        const {{ createApp, ref, watch, computed }} = Vue;

        const {{ vuetify, mountEl }} = initVuetify(el);

        const app = createApp({{
            setup() {{
                const title = ref(model.get('title'));
                const expanded = ref(model.get('expanded'));

                model.on('change:title', () => title.value = model.get('title'));
                model.on('change:expanded', () => expanded.value = model.get('expanded'));

                const toggle = (event) => {{
                    event.stopPropagation();
                    event.preventDefault();
                    expanded.value = !expanded.value;
                    model.set('expanded', expanded.value);
                    model.save_changes();
                }};

                const icon = computed(() => expanded.value ? 'mdi-chevron-up' : 'mdi-chevron-down');

                return {{ title, expanded, toggle, icon }};
            }},
            template: `
                <div
                    @click.stop.prevent="toggle"
                    @mousedown.stop
                    @mouseup.stop
                    style="
                        cursor: pointer;
                        display: flex;
                        align-items: center;
                        justify-content: space-between;
                        padding: 8px 12px;
                        font-size: 13px;
                        font-weight: 500;
                        border: 1px solid rgba(128,128,128,0.3);
                        border-radius: 4px;
                        background: rgba(128,128,128,0.08);
                    "
                >
                    <span>{{{{ title }}}}</span>
                    <v-icon :icon="icon" size="small" />
                </div>
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
