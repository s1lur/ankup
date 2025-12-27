include:
  - package_update

{% set services = salt['pillar.get']('services', {}) %}

{% for name, data in services.items() %}

service_{{ name }}:
  service.running:
    - name: {{ name }}
    - enable: {{ data.enabled }}

    - require:
      {% if data.parent_pkg %}
      - pkg: install_{{ data.parent_pkg }}
      {% endif %}

      {% for svc_dep in data.svc_deps %}
      - service: service_{{ svc_dep }}
      {% endfor %}

    - watch:
      {% if data.parent_pkg %}
      - pkg: install_{{ data.parent_pkg }}
      {% endif %}

      {% for conf_path in data.related_configs %}
      - file: conf_{{ conf_path }}
      {% endfor %}

{% endfor %}
