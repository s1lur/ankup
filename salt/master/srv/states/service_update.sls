include:
  - package_update

{% set services = salt['pillar.get']('services', {}) %}

{% for name, data in services.items() %}

service_{{ name }}:
  service.running:
    - name: {{ name }}
    - enable: {{ data.enabled }}

    - require:
      {% for pkg in data.pkg_deps %}
      - pkg: install_{{ pkg }}
      {% endfor %}

      {% for svc in data.svc_deps %}
      - service: service_{{ svc }}
      {% endfor %}

    - watch:
      {% for pkg in data.pkg_deps %}
      - pkg: install_{{ pkg }}
      {% endfor %}

      {% for conf in data.related_configs %}
      - file: conf_{{ conf }}
      {% endfor %}

{% endfor %}
