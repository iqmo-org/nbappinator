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
                    role="button"
                    tabindex="0"
                    :aria-expanded="expanded"
                    aria-label="Toggle section"
                    @click.stop.prevent="toggle"
                    @keydown.enter="toggle"
                    @keydown.space.prevent="toggle"
                    @mousedown.stop
                    @mouseup.stop
                    :style="{{
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                        padding: 'var(--nbapp-spacing-sm) var(--nbapp-spacing-md)',
                        fontSize: '13px',
                        fontWeight: '500',
                        borderRadius: 'var(--nbapp-radius)',
                        background: 'var(--nbapp-surface-variant)',
                    }}"
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
