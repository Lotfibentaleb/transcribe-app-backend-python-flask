
def getForgotPassworHtml(new_password):
    html = '<html>' \
                '<body>' \
                    '<div style="width: 100%; height: 30px; text-align: center; color: red; font-size: 18px;">' \
                    + new_password +\
                    '</div>' \
                '</body>' \
           '</html>'
    return html