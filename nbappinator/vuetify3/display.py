import anywidget
import traitlets

from .base import VUETIFY_LOADER_JS


class VuetifyDisplayWidget(anywidget.AnyWidget):
    """Display widget for static content.

    Types: label, pre, html, separator, image, card
    """

    widget_type = traitlets.Unicode("label").tag(sync=True)
    content = traitlets.Unicode("").tag(sync=True)
    title = traitlets.Unicode("").tag(sync=True)  # For card
    src = traitlets.Unicode("").tag(sync=True)  # For image (base64 or URL)
    width = traitlets.Unicode("auto").tag(sync=True)
    height = traitlets.Unicode("auto").tag(sync=True)

    _esm = f"""
    {VUETIFY_LOADER_JS}

    async function render({{ model, el }}) {{
        const {{ Vue }} = await loadVuetify();
        const {{ createApp, ref }} = Vue;

        const {{ vuetify, mountEl }} = initVuetify(el);

        const app = createApp({{
            setup() {{
                const widgetType = ref(model.get('widget_type'));
                const content = ref(model.get('content'));
                const title = ref(model.get('title'));
                const src = ref(model.get('src'));
                const width = ref(model.get('width'));
                const height = ref(model.get('height'));

                model.on('change:widget_type', () => widgetType.value = model.get('widget_type'));
                model.on('change:content', () => content.value = model.get('content'));
                model.on('change:title', () => title.value = model.get('title'));
                model.on('change:src', () => src.value = model.get('src'));
                model.on('change:width', () => width.value = model.get('width'));
                model.on('change:height', () => height.value = model.get('height'));

                return {{ widgetType, content, title, src, width, height }};
            }},
            template: `
                <div v-if="widgetType === 'label'" :style="{{ padding: 'var(--nbapp-spacing-xs) 0' }}">
                    {{{{ content }}}}
                </div>
                <pre v-else-if="widgetType === 'pre'" :style="{{ padding: 'var(--nbapp-spacing-md)', borderRadius: 'var(--nbapp-radius)', overflowX: 'auto', fontFamily: 'var(--nbapp-font-mono)', fontSize: '13px' }}">{{{{ content }}}}</pre>
                <div v-else-if="widgetType === 'html'" v-html="content"></div>
                <v-divider v-else-if="widgetType === 'separator'" class="my-3" />
                <v-img
                    v-else-if="widgetType === 'image'"
                    :src="src"
                    :width="width"
                    :height="height"
                    contain
                />
                <v-card v-else-if="widgetType === 'card'" variant="outlined">
                    <v-card-title v-if="title">{{{{ title }}}}</v-card-title>
                    <v-card-text v-html="content" />
                </v-card>
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
