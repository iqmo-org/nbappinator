import anywidget
import traitlets

from .base import VUETIFY_LOADER_JS


class VuetifyFormWidget(anywidget.AnyWidget):
    """Consolidated form widget supporting multiple input types.

    Types: select, combobox, text, textarea, checkbox, radio, slider
    """

    widget_type = traitlets.Unicode("select").tag(sync=True)
    label = traitlets.Unicode("").tag(sync=True)
    items = traitlets.List([]).tag(sync=True)  # For select/combobox/radio
    value = traitlets.Any(None).tag(sync=True)
    disabled = traitlets.Bool(False).tag(sync=True)
    multiple = traitlets.Bool(False).tag(sync=True)  # For select/combobox
    min_value = traitlets.Float(0).tag(sync=True)  # For slider
    max_value = traitlets.Float(100).tag(sync=True)  # For slider
    step = traitlets.Float(1).tag(sync=True)  # For slider

    _esm = f"""
    {VUETIFY_LOADER_JS}

    async function render({{ model, el }}) {{
        const {{ Vue }} = await loadVuetify();
        const {{ createApp, ref, watch, h }} = Vue;

        const {{ vuetify, mountEl }} = initVuetify(el);

        // Create Vue app
        const app = createApp({{
            setup() {{
                const widgetType = ref(model.get('widget_type'));
                const label = ref(model.get('label'));
                const items = ref(model.get('items') || []);
                const value = ref(model.get('value'));
                const disabled = ref(model.get('disabled'));
                const multiple = ref(model.get('multiple'));
                const minValue = ref(model.get('min_value'));
                const maxValue = ref(model.get('max_value'));
                const step = ref(model.get('step'));

                // Sync from Python to JS
                model.on('change:widget_type', () => widgetType.value = model.get('widget_type'));
                model.on('change:label', () => label.value = model.get('label'));
                model.on('change:items', () => items.value = model.get('items') || []);
                model.on('change:value', () => value.value = model.get('value'));
                model.on('change:disabled', () => disabled.value = model.get('disabled'));
                model.on('change:multiple', () => multiple.value = model.get('multiple'));
                model.on('change:min_value', () => minValue.value = model.get('min_value'));
                model.on('change:max_value', () => maxValue.value = model.get('max_value'));
                model.on('change:step', () => step.value = model.get('step'));

                // Sync value from JS to Python
                watch(value, (newVal) => {{
                    model.set('value', newVal);
                    model.save_changes();
                }});

                const selectDialogOpen = ref(false);
                const comboDialogOpen = ref(false);

                const handleSelectClick = (item) => {{
                    if (multiple.value) {{
                        const arr = Array.isArray(value.value) ? [...value.value] : [];
                        const idx = arr.indexOf(item);
                        if (idx >= 0) {{
                            arr.splice(idx, 1);
                        }} else {{
                            arr.push(item);
                        }}
                        value.value = arr;
                    }} else {{
                        value.value = item;
                        selectDialogOpen.value = false;
                    }}
                }};

                return {{
                    widgetType, label, items, value, disabled, multiple,
                    minValue, maxValue, step, selectDialogOpen, comboDialogOpen,
                    handleSelectClick
                }};
            }},
            template: `
                <div v-if="widgetType === 'select'" class="vuetify-inline-select">
                    <v-text-field
                        :model-value="Array.isArray(value) ? value.join(', ') : value"
                        :label="label"
                        :disabled="disabled"
                        variant="outlined"
                        density="compact"
                        readonly
                        :append-inner-icon="selectDialogOpen ? 'mdi-chevron-up' : 'mdi-chevron-down'"
                        @click="!disabled && (selectDialogOpen = !selectDialogOpen)"
                    />
                    <v-list
                        v-if="selectDialogOpen"
                        density="compact"
                        class="vuetify-inline-select-list"
                    >
                        <v-list-item
                            v-for="item in items"
                            :key="item"
                            :active="multiple ? (value || []).includes(item) : value === item"
                            @click="handleSelectClick(item)"
                        >
                            <v-list-item-title>{{{{ item }}}}</v-list-item-title>
                        </v-list-item>
                    </v-list>
                </div>
                <div v-else-if="widgetType === 'combobox'" class="vuetify-inline-select">
                    <v-text-field
                        v-model="value"
                        :label="label"
                        :disabled="disabled"
                        variant="outlined"
                        density="compact"
                        :append-inner-icon="comboDialogOpen ? 'mdi-chevron-up' : 'mdi-chevron-down'"
                        @click:append-inner="comboDialogOpen = !comboDialogOpen"
                    />
                    <v-list
                        v-if="comboDialogOpen"
                        density="compact"
                        class="vuetify-inline-select-list"
                    >
                        <v-list-item
                            v-for="item in items"
                            :key="item"
                            :active="value === item"
                            @click="value = item; comboDialogOpen = false"
                        >
                            <v-list-item-title>{{{{ item }}}}</v-list-item-title>
                        </v-list-item>
                    </v-list>
                </div>
                <v-text-field
                    v-else-if="widgetType === 'text'"
                    v-model="value"
                    :label="label"
                    :disabled="disabled"
                    variant="outlined"
                    density="compact"
                />
                <v-textarea
                    v-else-if="widgetType === 'textarea'"
                    v-model="value"
                    :label="label"
                    :disabled="disabled"
                    variant="outlined"
                    density="compact"
                    rows="3"
                    auto-grow
                />
                <v-checkbox
                    v-else-if="widgetType === 'checkbox'"
                    v-model="value"
                    :label="label"
                    :disabled="disabled"
                    density="compact"
                />
                <v-radio-group
                    v-else-if="widgetType === 'radio'"
                    v-model="value"
                    :disabled="disabled"
                    density="compact"
                >
                    <template v-slot:label><div>{{{{ label }}}}</div></template>
                    <v-radio
                        v-for="item in items"
                        :key="item"
                        :label="String(item)"
                        :value="item"
                    />
                </v-radio-group>
                <div v-else-if="widgetType === 'slider'" :style="{{ padding: '0 var(--nbapp-spacing-md)' }}">
                    <label style="font-size: 12px; opacity: 0.7;">{{{{ label }}}}</label>
                    <v-slider
                        v-model="value"
                        :min="minValue"
                        :max="maxValue"
                        :step="step"
                        :disabled="disabled"
                        thumb-label
                        density="compact"
                    />
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
