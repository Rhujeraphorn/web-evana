import json
import os
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Tuple, Generator, Any
from decimal import Decimal

import ijson
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

FILES: List[Tuple[str, str, str]] = [
    ('mae-hong-son', r'D:\output\routes\Maehongson_all.json', r'D:\output\routes\Maehongson_all.geojson'),
    ('chiang-mai', r'D:\output\routes\Chiangmai_routes_all.json', r'D:\output\routes\Chiangmai_routes_all.geojson'),
    ('lampang', r'D:\output\routes\Lampang_routes_all.json', r'D:\output\routes\Lampang_routes_all.geojson'),
    ('lamphun', r'D:\output\routes\Lamphun_routes.json', r'D:\output\routes\Lamphun_routes.geojson'),
]

BATCH_SIZE = 1000


def _get_engine() -> Engine:
    url = os.environ.get('DATABASE_URL')
    if not url:
        raise RuntimeError('DATABASE_URL is not set')
    return create_engine(url)


def _yield_segments(obj: Any) -> Iterator[Dict]:
    if isinstance(obj, dict):
        if 'from' in obj and 'to' in obj:
            yield obj
        if 'segments' in obj and isinstance(obj['segments'], list):
            for seg in obj['segments']:
                yield from _yield_segments(seg)
        else:
            for v in obj.values():
                yield from _yield_segments(v)
    elif isinstance(obj, list):
        for item in obj:
            yield from _yield_segments(item)


def _iter_segments(path: Path) -> Iterator[Dict]:
    if not path.exists():
        return
    try:
        with path.open('rb') as f:
            parser = ijson.items(f, 'item')
            for obj in parser:
                yield from _yield_segments(obj)
            return
    except Exception as exc:
        print('Failed to stream segments via ijson:', path, exc)
        return
    # fallback to full load
    data = json.load(path.open('r', encoding='utf-8-sig'))
    yield from _yield_segments(data)


def _iter_feature_rows(path: Path) -> Iterator[Dict]:
    if not path.exists():
        return
    try:
        with path.open('rb') as f:
            parser = ijson.items(f, 'features.item')
            for ft in parser:
                if not isinstance(ft, dict):
                    continue
                props = ft.get('properties') or {}
                geom = ft.get('geometry')
                if not geom or not isinstance(geom, dict):
                    continue
                fr = props.get('from')
                to = props.get('to')
                if not fr or not to:
                    continue
                yield {
                    'from': fr,
                    'to': to,
                    'properties': _normalize(props),
                    'geom': _normalize(geom),
                }
            return
    except Exception as exc:
        print('Failed to stream geojson via ijson:', path, exc)
        return
    data = json.load(path.open('r', encoding='utf-8'))
    if isinstance(data, dict) and data.get('type') == 'FeatureCollection':
        iterator = data.get('features') or []
    elif isinstance(data, dict) and data.get('type') == 'Feature':
        iterator = [data]
    else:
        iterator = []
    for ft in iterator:
        if not isinstance(ft, dict):
            continue
        props = ft.get('properties') or {}
        geom = ft.get('geometry')
        if not geom or not isinstance(geom, dict):
            continue
        fr = props.get('from')
        to = props.get('to')
        if not fr or not to:
            continue
        yield {
            'from': fr,
            'to': to,
            'properties': _normalize(props),
            'geom': _normalize(geom),
        }


def _chunked(iterable: Iterable[Dict], size: int = BATCH_SIZE) -> Iterator[List[Dict]]:
    chunk: List[Dict] = []
    for item in iterable:
        chunk.append(item)
        if len(chunk) >= size:
            yield chunk
            chunk = []
    if chunk:
        yield chunk


def _normalize(value: Any) -> Any:
    if isinstance(value, dict):
        return {k: _normalize(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_normalize(v) for v in value]
    if isinstance(value, Decimal):
        return float(value)
    return value


def import_segments(engine: Engine):
    stmt = text("""
        INSERT INTO route_segments
        (province, source_file, seg_id, from_name, to_name, distance_km,
         travel_time_min, energy_kwh, ev_cost_thb, attrs)
        VALUES (:province, :source_file, :seg_id, :from_name, :to_name,
                :distance_km, :travel_time_min, :energy_kwh, :ev_cost_thb,
                (:attrs)::jsonb)
    """)
    with engine.begin() as conn:
        for province, json_path, _ in FILES:
            path = Path(json_path)
            if not path.exists():
                print('Missing route segments file:', path)
                continue
            print(f'Processing segments for {province} ({path.name}) …')
            conn.execute(text('DELETE FROM route_segments WHERE province = :province'), {'province': province})
            total = 0
            for batch in _chunked(_iter_segments(path)):
                payload = [{
                    'province': province,
                    'source_file': str(path),
                    'seg_id': seg.get('id'),
                    'from_name': seg.get('from'),
                    'to_name': seg.get('to'),
                    'distance_km': seg.get('distance_km'),
                    'travel_time_min': seg.get('travel_time_min'),
                    'energy_kwh': seg.get('energy_kwh'),
                    'ev_cost_thb': seg.get('ev_cost_thb'),
                    'attrs': json.dumps(seg, ensure_ascii=False, default=str),
                } for seg in batch if seg.get('from') and seg.get('to')]
                if payload:
                    conn.execute(stmt, payload)
                    total += len(payload)
                    if total % 2000 == 0:
                        print(f'  …{total} segments inserted')
            print(f'Upserted segments for {province}: {total}')


def import_geojson(engine: Engine):
    stmt = text("""
        INSERT INTO route_geoms (province, source_file, from_name, to_name, geom, attrs)
        VALUES (:province, :source_file, :from_name, :to_name,
                ST_GeomFromGeoJSON(:geom_json), (:attrs)::jsonb)
    """)
    with engine.begin() as conn:
        for province, _, geo_path in FILES:
            path = Path(geo_path)
            if not path.exists():
                print('Missing route geojson file:', path)
                continue
            print(f'Processing geojson for {province} ({path.name}) …')
            conn.execute(text('DELETE FROM route_geoms WHERE province = :province'), {'province': province})
            total = 0
            row_iter = ({
                'province': province,
                'source_file': str(path),
                'from_name': row['from'],
                'to_name': row['to'],
                'geom_json': json.dumps(row['geom']),
                'attrs': json.dumps(row['properties'], ensure_ascii=False, default=str)
            } for row in _iter_feature_rows(path))
            for batch in _chunked(row_iter):
                conn.execute(stmt, batch)
                total += len(batch)
                if total % 2000 == 0:
                    print(f'  …{total} geo features inserted')
            print(f'Upserted geo features for {province}: {total}')


def main():
    engine = _get_engine()
    import_segments(engine)
    import_geojson(engine)
    print('Route segments + geojson imported successfully.')


if __name__ == '__main__':
    main()
