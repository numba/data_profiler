from __future__ import absolute_import

import sys
from os.path import dirname, join
from jinja2 import Template
from IPython.display import display, IFrame, HTML

def _open2(file, mode, encoding):
    # Provide our own 'open' for backward compatibility.
    import codecs
    return codecs.open(filename=file, mode=mode, encoding=encoding)

if sys.version_info[0] < 3:
    open = _open2

def _plot_in_notebook(profiler):
    """Generate interactive (notebook) visualization of the current profile statistics
    in `profiler`."""
    
    from .pstats import Stats
    import snakeviz
    import snakeviz.stats

    stats = Stats(profiler)
    table_rows=snakeviz.stats.table_rows(stats)
    callees=snakeviz.stats.json_stats(stats)
    base = join(dirname(__file__), 'snakeviz')
    template = join(base, 'template.jinja')
    resources={}
    resources['style_css'] = join(base, 'style.css')
    base = join(dirname(snakeviz.__file__), 'static')
    resources['snakeviz_js'] = join(base, 'snakeviz.js')
    resources['drawsvg_js'] = join(base, 'drawsvg.js')
    resources['datatables_css'] = join(base, 'vendor/jquery.dataTables.min.css')
    resources['jquery_min_js'] = join(base, 'vendor/jquery-1.11.1.min.js')
    resources['d3_min_js'] = join(base, 'vendor/d3.min.js')
    resources['jquery_dt_js'] = join(base, 'vendor/jquery.dataTables.min.js')
    resources['lodash_js'] = join(base, 'vendor/lodash.compat.min.js')
    resources['immutable_js'] = join(base, 'vendor/immutable.min.js')
    for r in resources:
        with open(resources[r], 'r', encoding='utf-8') as f:
            resources[r] = f.read()

    with open(template, 'r', encoding='utf-8') as f:
        template = Template(f.read())
    html = template.render(table_rows=table_rows, callees=callees, **resources)
    # We can't embed the snakeviz html because its js isn't (yet) compatible
    # with the notebook's use of RequireJS, so we fall back to using an iframe
    # until that's fixed.
    with open("snakeviz.html", 'w', encoding='utf-8') as f:
        f.write(html)
    return HTML(data="""<div class="resizable" style="height:500px;">
<iframe src="./snakeviz.html" width="100%" height="100%"/>
</div>
<script type="text/javascript">
$(function() {
  $('.resizable').resizable({
      handles: 'n,s',
      start: function(event, ui) {
        $('iframe').css('pointer-events','none');
         },
      stop: function(event, ui) {
        $('iframe').css('pointer-events','auto');
      }
  });
});
</script>
""")


def plot(profiler):
    """Generate visualization of the current profile statistics
    in `profiler`. Right now this is only supported for interactive notebooks"""
    try:
        # If it detects any IPython frontend
        # (qtconsole, interpreter or notebook)
        config = get_ipython().config
        return _plot_in_notebook(profiler)
    except:
        raise RuntimeError("This function is presently only implemented to be used inside notebooks.")

