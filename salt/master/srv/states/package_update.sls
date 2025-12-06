{% set files = salt['pillar.get']('files', []) %}

{% for f in files %}

conf_{{ f.path }}:
  file.managed:
    - name: {{ f.path }}
    - contents: |
        {{ f.content | indent(8) }}
    - template: jinja
    - context: {{ f.context | json }}
    - mode: {{ f.mode }}
    - makedirs: True

{% endfor %}

{% set pkgs = salt['pillar.get']('packages', {}) %}

{% for name, data in pkgs.items() %}

install_{{ name }}:
  pkg.installed:
    - name: {{ name }}
    {% if data.version %}
    - version: {{ data.version }}
    {% endif %}
    - refresh: False
    - hold: False

    {% if data.deps %}
    - require:
      {% for dep in data.deps %}
      - pkg: install_{{ dep }}
      {% endfor %}
    {% endif %}

{% endfor %}
