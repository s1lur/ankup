{% set ignored = salt['pillar.get']('managed_packages_list', []) %}

hold_packages:
  pkg.held:
    - pkgs: {{ ignored | json }}

refresh_repo:
  pkg.refresh_db
  - require:
    - pkg: hold_packages

system_full_upgrade:
  pkg.uptodate:
    - refresh: False
    - dist_upgrade: True
    - require:
      - pkg: refresh_repo
