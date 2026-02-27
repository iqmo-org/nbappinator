import anywidget
import traitlets

from .base import VUETIFY_LOADER_JS


class VuetifyButtonWidget(anywidget.AnyWidget):
    """Button with optional status text and progress indicator."""

    label = traitlets.Unicode("Button").tag(sync=True)
    disabled = traitlets.Bool(False).tag(sync=True)
    color = traitlets.Unicode("primary").tag(sync=True)
    variant = traitlets.Unicode("elevated").tag(sync=True)  # elevated, flat, tonal, outlined, text, plain
    loading = traitlets.Bool(False).tag(sync=True)
    status_text = traitlets.Unicode("").tag(sync=True)
    status_color = traitlets.Unicode("").tag(sync=True)  # success, error, warning, info
    clicked = traitlets.Int(0).tag(sync=True)  # Increment to detect clicks

    _esm = f"""
    {VUETIFY_LOADER_JS}

    async function render({{ model, el }}) {{
        const {{ Vue }} = await loadVuetify();
        const {{ createApp, ref }} = Vue;

        const {{ vuetify, mountEl }} = initVuetify(el);

        const app = createApp({{
            setup() {{
                const label = ref(model.get('label'));
                const disabled = ref(model.get('disabled'));
                const color = ref(model.get('color'));
                const variant = ref(model.get('variant'));
                const loading = ref(model.get('loading'));
                const statusText = ref(model.get('status_text'));
                const statusColor = ref(model.get('status_color'));

                model.on('change:label', () => label.value = model.get('label'));
                model.on('change:disabled', () => disabled.value = model.get('disabled'));
                model.on('change:color', () => color.value = model.get('color'));
                model.on('change:variant', () => variant.value = model.get('variant'));
                model.on('change:loading', () => loading.value = model.get('loading'));
                model.on('change:status_text', () => statusText.value = model.get('status_text'));
                model.on('change:status_color', () => statusColor.value = model.get('status_color'));

                function onClick() {{
                    model.set('clicked', model.get('clicked') + 1);
                    model.save_changes();
                }}

                return {{ label, disabled, color, variant, loading, statusText, statusColor, onClick }};
            }},
            template: `
                <div style="display: flex; align-items: center; gap: 12px; flex-wrap: wrap;">
                    <v-btn
                        :color="color"
                        :variant="variant"
                        :disabled="disabled || loading"
                        :loading="loading"
                        @click="onClick"
                        density="default"
                    >
                        {{{{ label }}}}
                    </v-btn>
                    <span
                        v-if="statusText"
                        :style="{{
                            fontSize: '14px',
                            color: statusColor === 'success' ? '#4caf50' :
                                   statusColor === 'error' ? '#f44336' :
                                   statusColor === 'warning' ? '#ff9800' :
                                   statusColor === 'info' ? '#2196f3' : 'inherit'
                        }}"
                    >
                        {{{{ statusText }}}}
                    </span>
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
