import io
import sys

import anywidget
import traitlets

from .base import VUETIFY_LOADER_JS


class VuetifyOutputWidget(anywidget.AnyWidget):
    """Output widget that displays captured text (stdout/stderr style).

    Supports context manager protocol for capturing stdout:
        with output_widget:
            print("This will be captured")
    """

    content = traitlets.Unicode("").tag(sync=True)
    max_height = traitlets.Unicode("300px").tag(sync=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._stdout_trap = io.StringIO()
        self._original_stdout = None

    _esm = f"""
    {VUETIFY_LOADER_JS}

    async function render({{ model, el }}) {{
        const {{ Vue }} = await loadVuetify();
        const {{ createApp, ref, watch, nextTick }} = Vue;

        const {{ vuetify, mountEl }} = initVuetify(el);

        const app = createApp({{
            setup() {{
                const content = ref(model.get('content'));
                const maxHeight = ref(model.get('max_height'));
                const preRef = ref(null);

                model.on('change:content', () => {{
                    content.value = model.get('content');
                    // Auto-scroll to bottom
                    nextTick(() => {{
                        if (preRef.value) {{
                            preRef.value.scrollTop = preRef.value.scrollHeight;
                        }}
                    }});
                }});
                model.on('change:max_height', () => maxHeight.value = model.get('max_height'));

                return {{ content, maxHeight, preRef }};
            }},
            template: `
                <pre
                    ref="preRef"
                    :style="{{
                        maxHeight: maxHeight,
                        overflow: 'auto',
                        padding: '12px',
                        margin: '0',
                        fontFamily: 'monospace',
                        fontSize: '13px',
                        whiteSpace: 'pre-wrap',
                        wordBreak: 'break-word',
                        borderRadius: '4px',
                        border: '1px solid rgba(128,128,128,0.3)',
                    }}"
                >{{{{ content }}}}</pre>
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

    def append(self, text: str) -> None:
        """Append text to output."""
        self.content += text

    def clear(self) -> None:
        """Clear output."""
        self.content = ""

    def __enter__(self):
        """Start capturing stdout."""
        self._stdout_trap = io.StringIO()
        self._original_stdout = sys.stdout
        sys.stdout = self._stdout_trap
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Stop capturing stdout and append captured content."""
        sys.stdout = self._original_stdout
        captured = self._stdout_trap.getvalue()
        if captured:
            self.append(captured)
        self._stdout_trap = io.StringIO()
        return False  # Don't suppress exceptions
