import bs4


def value_in_element_attr(element, value, attr="class"):
    if not type(element) == bs4.element.Tag:
        return False
    else:
        attrs = element.attrs
        if attrs is not None and attrs != {}:
            return value in element.attrs.get(attr)
        else:
            return False


def fix_link(link):
    if link.startswith("//"):
        return "https:{}".format(link)
