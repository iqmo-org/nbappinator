class BrowserTitle:
    title: str
    icon_href: str

    def __init__(self, title: str, icon_href: str = "https://iqmo.com/iqmo-dk.svg"):
        self.title = title
        self.icon_href = icon_href

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
                    link.href = '{self.icon_href}'
                }})()
            </script>
        """
