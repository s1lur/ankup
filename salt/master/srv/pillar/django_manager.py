import logging
import os
import psycopg2
from psycopg2.extras import RealDictCursor

log = logging.getLogger(__name__)


def ext_pillar(minion_id, pillar, *args, **kwargs):
    db_opts = {
        'host': kwargs.get('host', 'localhost'),
        'port': kwargs.get('port', 5432),
        'database': kwargs.get('db', 'postgres'),
        'user': kwargs.get('user', 'salt'),
        'password': kwargs.get('pass', 'salt')
    }
    media_root = kwargs.get('media_root', '/var/www/django_media')

    pillar_data = {
        'files': [],
        'packages': {},
        'services': {},
        'managed_packages_list': []
    }

    conn = None
    try:
        conn = psycopg2.connect(**db_opts)
        cur = conn.cursor(cursor_factory=RealDictCursor)

        cur.execute("SELECT id FROM device WHERE name = %s", (minion_id,))
        dev = cur.fetchone()
        if not dev: return {}
        device_id = dev['id']

        query_pkgs = """
            SELECT 
                p.id as pid,
                p.name as pkg_name,
                v.number as version,
                p.default_parameters,       -- Дефолты пакета
                dp.parameters as overrides, -- Переопределения устройства

                -- Агрегация конфигов
                COALESCE(
                    json_agg(json_build_object(
                        'rel_path', ct.file,
                        'dest_path', ct.dest_path,
                        'mode', ct.file_mode
                    )) FILTER (WHERE ct.id IS NOT NULL), 
                    '[]'::json
                ) as templates
            FROM device_package dp
            JOIN package p ON dp.package_id = p.id
            LEFT JOIN version v ON dp.version_id = v.id
            LEFT JOIN config_template ct ON p.id = ct.package_id
            WHERE dp.device_id = %s
            GROUP BY p.id, p.name, v.number, dp.parameters
        """
        cur.execute(query_pkgs, (device_id,))
        pkg_rows = cur.fetchall()

        pkg_configs_cache = {}

        for row in pkg_rows:
            pkg_name = row['pkg_name']
            pillar_data['managed_packages_list'].append(pkg_name)

            context = row['default_parameters'] if row['default_parameters'] else {}
            if row['overrides']:
                context.update(row['overrides'])

            current_config_paths = []
            for tmpl in row['templates']:
                full_path = os.path.join(media_root, tmpl['rel_path'])
                content = f"# Missing file: {tmpl['rel_path']}"
                if os.path.exists(full_path):
                    with open(full_path, 'r') as f:
                        content = f.read()

                pillar_data['files'].append({
                    'path': tmpl['dest_path'],
                    'mode': tmpl['mode'],
                    'content': content,
                    'context': context,
                })
                current_config_paths.append(tmpl['dest_path'])

            pkg_configs_cache[pkg_name] = current_config_paths

            cur.execute("""
                SELECT p.name FROM package_package_deps ppd
                JOIN package p ON ppd.to_package_id = p.id
                WHERE ppd.from_package_id = %s
            """, (row['pid'],))
            deps = [r['name'] for r in cur.fetchall()]

            pillar_data['packages'][pkg_name] = {
                'version': row['version'],
                'deps': deps
            }

        query_svcs = """
            SELECT s.id as sid, s.name, ds.enabled
            FROM device_service ds
            JOIN service s ON ds.service_id = s.id
            WHERE ds.device_id = %s
        """
        cur.execute(query_svcs, (device_id,))

        for row in cur.fetchall():
            cur.execute("""
                SELECT p.name FROM service_package_deps spd
                JOIN package p ON spd.package_id = p.id
                WHERE spd.service_id = %s
            """, (row['sid'],))
            svc_pkg_deps = [r['name'] for r in cur.fetchall()]

            cur.execute("""
                SELECT s.name FROM service_service_deps ssd
                JOIN service s ON ssd.to_service_id = s.id
                WHERE ssd.from_service_id = %s
            """, (row['sid'],))
            svc_svc_deps = [r['name'] for r in cur.fetchall()]

            related_configs = []
            for pkg in svc_pkg_deps:
                if pkg in pkg_configs_cache:
                    related_configs.extend(pkg_configs_cache[pkg])

            pillar_data['services'][row['name']] = {
                'enabled': row['enabled'],
                'pkg_deps': svc_pkg_deps,
                'svc_deps': svc_svc_deps,
                'related_configs': related_configs
            }

    except Exception as e:
        log.error(f"Pillar Error: {e}")
        return {}
    finally:
        if conn: conn.close()

    return pillar_data
