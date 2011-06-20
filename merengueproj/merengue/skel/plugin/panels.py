from django.template.loader import render_to_string

from merengue.uitools import panels


class FooPanel(panels.Panel):

    def render(self, context):
        return render_to_string('fooplugin/foo_panel.html', context)
