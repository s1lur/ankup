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

{% set pkg_names = pkgs.keys() | list %}

{% if pkg_names %}
prefetch_packages:
  cmd.run:
    - name: apt-get install -y -d {{ pkg_names | join(' ') }}
{% endif %}

{% for name, data in pkgs.items() %}

verify_signature_{{ name }}:
  cmd.run:
    - name: |
        RPM_FILE=$(find /var/cache/apt/archives -name "{{ name }}-{{ data.version }}*.rpm" | head -n 1)
        if [ -z "$RPM_FILE" ]; then
            echo "File not found for {{ name }}, skipping check (maybe already installed?)"
            exit 0
        fi

        echo "Verifying $RPM_FILE..."
        rpm -K "$RPM_FILE" | grep -q "OK"
        if [ $? -ne 0 ]; then
            echo "SECURITY ALERT: Signature verification failed for $RPM_FILE"
            exit 1
        fi
        exit 0
    - require:
      - cmd: prefetch_packages

install_{{ name }}:
  pkg.installed:
    - name: {{ name }}
    {% if data.version %}
    - version: {{ data.version }}
    {% endif %}
    - refresh: False
    - hold: False

    - require:
      - cmd: verify_signature_{{ name }}
      {% if data.deps %}
      {% for dep in data.deps %}
      - pkg: install_{{ dep }}
      {% endfor %}
      {% endif %}

{% endfor %}