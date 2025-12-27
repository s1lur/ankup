import logging
import os
import psycopg2
from psycopg2.extras import RealDictCursor

log = logging.getLogger(__name__)


def ext_pillar(minion_id, pillar, *args, **kwargs):
    db_opts = {
        'host': kwargs.get('host', 'localhost'),
        'port': kwargs.get('port', 5432),
        'database': kwargs.get('db', 'your_db_name'),
        'user': kwargs.get('user', 'salt_user'),
        'password': kwargs.get('pass', 'salt_pass')
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
                dp.parameters as device_params,

                -- Агрегация конфигов (ConfigTemplate)
                COALESCE(
                    json_agg(json_build_object(
                        'rel_path', ct.file,
                        'dest_path', ct.dest_path,
                        'mode', ct.file_mode,
                        'tmpl_params', ct.parameters
                    )) FILTER (WHERE ct.id IS NOT NULL), 
                    '[]'::json
                ) as configs
            FROM device_package dp
            JOIN package p ON dp.package_id = p.id
            LEFT JOIN version v ON dp.version_id = v.id
            LEFT JOIN config_template ct ON p.id = ct.package_id
            WHERE dp.device_id = %s
            GROUP BY p.id, p.name, v.number, dp.parameters
        """
        cur.execute(query_pkgs, (device_id,))
        pkg_rows = cur.fetchall()

        pkg_to_configs_map = {}

        for row in pkg_rows:
            pkg_name = row['pkg_name']
            pillar_data['managed_packages_list'].append(pkg_name)

            cur.execute("""
                SELECT p_dep.name 
                FROM package_package_deps ppd
                JOIN package p_dep ON ppd.dependency_id = p_dep.id
                WHERE ppd.dependant_id = %s
            """, (row['pid'],))
            pkg_deps_names = [r['name'] for r in cur.fetchall()]

            current_pkg_paths = []

            for conf in row['configs']:
                ctx = conf['tmpl_params'] if conf['tmpl_params'] else {}
                if row['device_params']:
                    ctx.update(row['device_params'])

                full_path = os.path.join(media_root, conf['rel_path'])
                content = f"# Missing on master: {conf['rel_path']}"
                if os.path.exists(full_path):
                    with open(full_path, 'r') as f:
                        content = f.read()

                pillar_data['files'].append({
                    'path': conf['dest_path'],
                    'mode': conf['mode'],
                    'content': content,
                    'context': ctx
                })
                current_pkg_paths.append(conf['dest_path'])

            pkg_to_configs_map[pkg_name] = current_pkg_paths

            pillar_data['packages'][pkg_name] = {
                'version': row['version'],
                'deps': pkg_deps_names
            }

        query_svcs = """
            SELECT 
                s.id as sid,
                s.name as svc_name,
                ds.enabled,
                p.name as parent_pkg_name
            FROM device_service ds
            JOIN service s ON ds.service_id = s.id
            LEFT JOIN package p ON s.package_id = p.id
            WHERE ds.device_id = %s
        """
        cur.execute(query_svcs, (device_id,))
        svc_rows = cur.fetchall()

        for s_row in svc_rows:
            parent_pkg = s_row['parent_pkg_name']

            watch_configs = []
            if parent_pkg and parent_pkg in pkg_to_configs_map:
                watch_configs = pkg_to_configs_map[parent_pkg]

            cur.execute("""
                SELECT s_dep.name 
                FROM service_service_deps ssd
                JOIN service s_dep ON ssd.dependency_id = s_dep.id
                WHERE ssd.dependant_id = %s
            """, (s_row['sid'],))
            svc_svc_deps = [r['name'] for r in cur.fetchall()]

            pillar_data['services'][s_row['svc_name']] = {
                'enabled': s_row['enabled'],
                'parent_pkg': parent_pkg,
                'svc_deps': svc_svc_deps,
                'related_configs': watch_configs
            }

    except Exception as e:
        log.error(f"Pillar Error: {e}")
        return {}
    finally:
        if conn: conn.close()

    return pillar_data
