import re
import string
import warnings
from jinja2 import Environment

def _substitute(s, reps):
    # Keeping the old substitution logic for backward compatibility
    t = string.Template(s)
    i = 0
    cr = {}
    while True:
        m = re.search(r'^(.*?)\$\{(.*?)\}', s[i:], re.MULTILINE)
        if m is None:
            break
        sep = ('\n' + m.group(1)) if m.group(1).strip() == '' else '\n'
        cr[m.group(2)] = sep.join(reps[m.group(2)])
        i += m.end()
    return t.substitute(cr)

def render(template, **kwargs):
    # Add version info to kwargs
    kwargs['atcodertools'] = {
        'version': __version__,  # Make sure to import this
        'url': 'https://github.com/kyuridenamida/atcoder-tools',
    }

    # Process template indentation
    indent_template = estimate_indent(template)
    if indent_template and 'config' in kwargs:
        indent = kwargs['config'].indent(1)
        if indent_template != indent:
            def fixindent(line):
                new_indent = ''
                while line.startswith(indent_template):
                    line = line[len(indent_template):]
                    new_indent = new_indent + indent
                return new_indent + line
            template = '\n'.join(map(fixindent, template.split('\n')))

    if "${" in template:
        warnings.warn(
            "The old template engine with ${} is deprecated. Please use the Jinja2 template engine.", 
            UserWarning
        )
        return old_render(template, **kwargs)
    
    return render_by_jinja(template, **kwargs)

def old_render(template, **kwargs):
    new_args = {
        k: v if isinstance(v, list) else [v]
        for k, v in kwargs.items()
    }
    return _substitute(template, new_args)

def render_by_jinja(template, **kwargs):
    # Jinja3 compatible environment setup
    env = Environment(
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True  # Jinja3 specific option
    )
    # Remove autoescape setting as it's handled differently in Jinja3
    return env.from_string(template).render(**kwargs)

def estimate_indent(code):
    indents = re.findall(r'^([ \t]+)(?=\S)', code, re.MULTILINE)
    if not indents:
        return ''
    indents_concat = "".join(indents)
    if ' ' in indents_concat and '\t' in indents_concat:
        return ''
    lens = set(len(indent) for indent in indents)
    if not min(lens) * len(lens) == max(lens):
        return ''
    return indents[0][:min(lens)]
