import anywidget
import traitlets

from .base import VUETIFY_LOADER_JS


class VuetifyLayoutWidget(anywidget.AnyWidget):
    """Layout container widget.

    Types: container, row, column
    """

    widget_type = traitlets.Unicode("container").tag(sync=True)
    fluid = traitlets.Bool(True).tag(sync=True)  # For container
    cols = traitlets.Int(12).tag(sync=True)  # For column (1-12)
    justify = traitlets.Unicode("start").tag(sync=True)  # For row: start, center, end, space-between, space-around
    align = traitlets.Unicode("start").tag(sync=True)  # For row: start, center, end, stretch

    _esm = f"""
    {VUETIFY_LOADER_JS}

    async function render({{ model, el }}) {{
        const {{ Vue }} = await loadVuetify();
        const {{ createApp, ref }} = Vue;

        const {{ vuetify, mountEl }} = initVuetify(el);

        const app = createApp({{
            setup() {{
                const widgetType = ref(model.get('widget_type'));
                const fluid = ref(model.get('fluid'));
                const cols = ref(model.get('cols'));
                const justify = ref(model.get('justify'));
                const align = ref(model.get('align'));

                model.on('change:widget_type', () => widgetType.value = model.get('widget_type'));
                model.on('change:fluid', () => fluid.value = model.get('fluid'));
                model.on('change:cols', () => cols.value = model.get('cols'));
                model.on('change:justify', () => justify.value = model.get('justify'));
                model.on('change:align', () => align.value = model.get('align'));

                return {{ widgetType, fluid, cols, justify, align }};
            }},
            template: `
                <v-container v-if="widgetType === 'container'" :fluid="fluid">
                    <slot></slot>
                </v-container>
                <v-row v-else-if="widgetType === 'row'" :justify="justify" :align="align">
                    <slot></slot>
                </v-row>
                <v-col v-else-if="widgetType === 'column'" :cols="cols">
                    <slot></slot>
                </v-col>
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
