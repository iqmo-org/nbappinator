class BrowserTitle:
    title: str
    iconHref: str

    def __init__(self, title: str, iconHref: str = "https://iqmo.com/iqmo-dk.svg"):
        self.title = title
        self.iconHref = iconHref

    def _repr_html_(self):
        return f"""
            <script>
                (()=>{{
                    document.title='{self.title}'
                    let link = document.querySelector("head link[rel~='icon']");
                    if(!link){{
                        link = document.createElement('link');
                        link.rel = 'icon';
                        document.head.appendChild(link);
                    }}
                    link.href = '{self.iconHref}'
                }})()
            </script>
        """
