include:
  - package_update

{% set services = salt['pillar.get']('services', {}) %}

{% for name, data in services.items() %}

service_{{ name }}:
  service.running:
    - name: {{ name }}
    - enable: {{ data.enabled }}

    # ПОРЯДОК ЗАПУСКА
    - require:
      {% for pkg in data.pkg_deps %}
      - pkg: install_{{ pkg }}
      {% endfor %}

      {% for svc in data.svc_deps %}
      - service: service_{{ svc }}
      {% endfor %}

    # ПЕРЕЗАПУСК (RESTART)
    - watch:
      # 1. Если обновился бинарник пакета
      {% for pkg in data.pkg_deps %}
      - pkg: install_{{ pkg }}
      {% endfor %}

      # 2. Если обновился любой конфиг этого пакета
      {% for conf in data.related_configs %}
      - file: conf_{{ conf }}
      {% endfor %}

{% endfor %}
