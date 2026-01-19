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

refresh_db:
    cmd.run:
        - name: apt-get clean && apt-get update

{% for name, data in pkgs.items() %}

install_{{ name }}:
  cmd.run:
    - stateful: True
    - name: |
        finish() {
            local res=$1
            local old_v=$2
            local new_v=$3
            local msg=$(echo "$4" | tr '\n' '' | sed "s/"/\\"/g")
            local changed="false"

            if [ "$res" == "true" ] && [ "$old_v" != "$new_v" ]; then
                changed="true"
            fi

            echo ""
            cat <<EOF
{
  "result": $res,
  "changed": $changed,
  "changes": {
      "old": "$old_v",
      "new": "$new_v"
  },
  "comment": "$msg"
}
EOF
            if [ "$res" == "true" ]; then exit 0; else exit 1; fi
        }

        INSTALLED_VER=$(rpm -q --qf "%{VERSION}-%{RELEASE}" {{ name }} 2>/dev/null)
        if [ $? -ne 0 ]; then
            INSTALLED_VER="absent"
        fi

        if [ "$INSTALLED_VER" == "{{ data.version }}" ]; then
            finish true "$INSTALLED_VER" "$INSTALLED_VER" "Package {{ name }} is up-to-date"
        fi

        APT_OUT=$(apt-get install -y --force-yes -d --reinstall "{{ name }}={{ data.version }}" 2>&1)
        if [ $? -ne 0 ]; then
            finish false "$INSTALLED_VER" "{{ data.version }}" "Download failed: $APT_OUT"
        fi

        RPM_FILE=$(find /var/cache/apt/archives -name "{{ name }}-{{ data.version }}*.rpm" -o -name "{{ name }}_{{ data.version }}*.rpm" | head -n 1)

        if [ -z "$RPM_FILE" ]; then
            finish false "$INSTALLED_VER" "{{ data.version }}" "RPM file not found in cache after download"
        fi

        SIG_OUT=$(rpm -K "$RPM_FILE" 2>&1)
        if [ $? -ne 0 ]; then
             finish false "$INSTALLED_VER" "{{ data.version }}" "SECURITY ALERT: Integrity check failed for $RPM_FILE\n$SIG_OUT"
        fi

        INSTALL_OUT=$(rpm -Uvh --oldpackage --replacepkgs "$RPM_FILE" 2>&1)
        if [ $? -ne 0 ]; then
            finish false "$INSTALLED_VER" "{{ data.version }}" "Install failed: $INSTALL_OUT"
        fi

        finish true "$INSTALLED_VER" "{{ data.version }}" "Updated {{ name }}"

    - require:
      - cmd: refresh_db
      {% if data.deps %}
      {% for dep in data.deps %}
      - cmd: install_{{ dep }}
      {% endfor %}
      {% endif %}

{% endfor %}