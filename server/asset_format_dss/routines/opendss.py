from collections import namedtuple

from asset_tracker.models.asset import AssetTypeCode
import networkx as nx

TRANSFORMER = AssetTypeCode.TRANSFORMER
METER = AssetTypeCode.METER
LINE = AssetTypeCode.LINE
LINECODE = 'linecode'
GENERATOR = AssetTypeCode.GENERATOR
STATION = AssetTypeCode.STATION
SUBSTATION = AssetTypeCode.SUBSTATION
LOAD = 'load'
BUS = 'bus'
STORAGE = AssetTypeCode.STORAGE
SWITCH = AssetTypeCode.SWITCH
POWERQUALITY = AssetTypeCode.POWERQUALITY
POWERQUALITY_CAPACITOR = AssetTypeCode.CAPACITOR
POWERQUALITY_REGULATOR = AssetTypeCode.REGULATOR


to_dss_array = lambda l:  f'[ {" ".join(l)} ]'
to_str = lambda l: [str(e) for e in l if e]
comment = lambda text: f'// {text}'


def build_bus(bus, nodes):
    group_nodes = list(filter(lambda val: val != '.', nodes))
    print(group_nodes)
    return f'{bus}.{".".join(group_nodes)}' if len(group_nodes) != 0 else f'{bus}'


def to_matrix(lists):
    rows = [' '.join(map(str, entry)) for entry in lists]
    matrix = ' | '.join(rows)
    return f'[{matrix}]'


class AssetMixin:
    @property
    def id(self):
        return self.asset['name']

    @property
    def name(self):
        return self.asset['name']

    def attributes(self):
        return {}


class Line(AssetMixin):
    type = LINE

    def __init__(self, asset, bus, conn, wired):
        self.asset = asset
        self.bus = bus
        self.conn = conn
        self.wired = wired

    def __str__(self):
        attributes = self.asset['attributes']
        line_id = self.asset['id']
        phases = attributes.get('phaseCount')
        lc = attributes.get('lineType')
        length = attributes.get('lineLength')
        unit = attributes.get('lengthUnit')

        line = f'New Line.{line_id} '
        line += f'phases={phases} ' if phases else ''
        line += f'linecode={lc} ' if lc else ''
        line += f'length={length} ' if length else ''
        line += f'units={unit}' if unit else ''

        connection_attributes = self.wired['attributes']
        bus1 = build_bus(self.bus, to_str(connection_attributes.get('busNodes') or []))
        bus2 = None
        if len(self.conn) > 0:
            for conn in self.conn:
                connection_attributes = conn.wired['attributes']
                bus2 = build_bus(conn.bus, to_str(
                    connection_attributes.get('busNodes') or []))

        if bus1:
            line += f' Bus1={bus1} '

        if bus2:
            line += f' Bus2={bus2}'

        return line


class Switch(AssetMixin):
    type = SWITCH

    def __init__(self, asset, bus, conn, wired):
        self.asset = asset
        self.bus = bus
        self.conn = conn
        self.wired = wired

    def __str__(self):
        switch_id = self.asset['id']
        attributes = self.asset['attributes']
        phases = attributes.get('phaseCount')
        r1 = attributes.get('positiveSequenceResistance')
        r0 = attributes.get('zeroSequenceResistance')
        x1 = attributes.get('positiveSequenceReactance')
        x0 = attributes.get('zeroSequenceReactance')
        c1 = attributes.get('positiveSequenceCapacitance')
        c0 = attributes.get('zeroSequenceCapacitance')

        line = f'New Line.{switch_id} Switch=y phases={phases}'
        line += f' r1={r1} r0={r0} x1={x1} x0={x0} c1={c1} c0={c0}'

        connection_attributes = self.wired['attributes']
        bus1 = build_bus(self.bus, to_str(connection_attributes.get('busNodes', [])))
        bus2 = None
        if len(self.conn) > 0:
            for conn in self.conn:
                connection_attributes = conn.wired['attributes']
                bus2 = build_bus(conn.bus, to_str(connection_attributes.get('busNodes', [])))

        if bus1:
            line += f' Bus1={bus1} '

        if bus2:
            line += f' Bus2={bus2}'

        return line


class Meter(AssetMixin):
    type = METER

    def __init__(self, asset, bus, conn, wired):
        self.asset = asset
        self.bus = bus
        self.conn = conn
        self.wired = wired

    def __str__(self):
        load_id = self.asset['id']
        attributes = self.asset['attributes']
        phases = attributes.get('phaseCount')
        model = attributes.get('loadModel')

        connection_attributes = self.wired['attributes']
        bus1 = build_bus(self.bus, to_str(connection_attributes.get('busNodes') or []))

        kv = connection_attributes.get('baseVoltage')
        conn = connection_attributes.get('connectionType')
        kw = connection_attributes.get('activePower')
        kvar = connection_attributes.get('reactivePower')

        command = f'New Load.Load_{load_id} '
        command += f'phases={phases} ' if phases else ''
        command += f'conn={conn} ' if conn else ''
        command += f'model={model} ' if model else ''
        command += f' Bus1={bus1} ' if bus1 else ''
        command += f'kV={kv} ' if kv else ''
        command += f'kW={kw} ' if kw else ''
        command += f'kvar={kvar}' if kvar else ''

        return command


class Regulator(AssetMixin):
    type = POWERQUALITY_REGULATOR

    def __init__(self, asset, bus, conn, wired):
        self.asset = asset
        self.bus = bus
        self.conn = conn
        self.wired = wired

    def __str__(self):
        regulator_id = self.asset['id']
        attributes = self.asset['attributes']
        xhl = attributes.get('percentLoadLoss')
        vreg = attributes.get('regulatedVoltage')
        band = attributes.get('bandwidthVoltage')
        ptratio = attributes.get('potentialTransformerRatio')
        ctprim = attributes.get('currentTransformerRating')
        r = attributes.get('rSettingVoltage')
        x = attributes.get('xSettingVoltage')
        phases = attributes.get('phaseCount')
        winding = attributes.get('windingCount')

        connection_attributes = self.wired['attributes']
        kvs = [connection_attributes.get('baseVoltage')]
        kvas = [connection_attributes.get('power')]
        buses = [build_bus(self.bus, to_str(connection_attributes.get('busNodes') or []))]

        for conn in self.conn:
            connection_attributes = conn.wired['attributes']
            kvs.append(connection_attributes.get('baseVoltage'))
            kvas.append(connection_attributes.get('power'))
            buses.append(build_bus(conn.bus, to_str(connection_attributes.get('busNodes') or [])))

        command = f'New Transformer.{regulator_id} phases={phases} bank=reg1'
        command += f' buses={to_dss_array(to_str(buses))} kVs={to_dss_array(to_str(kvs))}'
        command += f' kVAs={to_dss_array(to_str(kvas))} xhl={xhl} %LoadLoss={xhl}\n'

        command += f'New regcontrol.{regulator_id} transformer={regulator_id} '
        command += f' winding={winding} vreg={vreg} band={band} ptratio={ptratio} ctprim={ctprim}'
        command += f' R={r} X={x}'

        return command


class Capacitor(AssetMixin):
    type = POWERQUALITY_CAPACITOR

    def __init__(self, asset, bus, conn, wired):
        self.asset = asset
        self.bus = bus
        self.conn = conn
        self.wired = wired

    def __str__(self):
        capacitor_id = self.asset['id']
        phases = self.asset['attributes'].get('phaseCount')
        connection_attributes = self.wired['attributes']
        bus1 = build_bus(self.bus, to_str(connection_attributes.get('busNodes') or []))
        kv = connection_attributes.get('baseVoltage')
        conn = connection_attributes.get('connectionType', None)
        kvar = connection_attributes.get('reactivePower')

        command = f'new capacitor.{capacitor_id} phases={phases} bus1={bus1} kVAr={kvar} kV={kv} '

        if conn:
            command += f' conn={conn}'

        return command


class PowerQuality(AssetMixin):
    type = POWERQUALITY

    def __init__(self, asset, bus, conn, wired):
        self.asset = asset
        self.bus = bus
        self.conn = conn
        self.wired = wired

    def __str__(self):
        power_id = self.asset['id']
        command = f'// Power Quality still not supported {power_id}'

        return command


class Transformer(AssetMixin):
    type = TRANSFORMER

    def __init__(self, asset, bus, conn, wired):
        self.asset = asset
        self.bus = bus
        self.conn = conn
        self.wired = wired

    def __str__(self):
        transformer_id = self.asset['id']
        attributes = self.asset['attributes']
        phases = attributes.get('phaseCount')
        winding = attributes.get('windingCount')
        xhl = attributes.get('winding1Winding2PercentReactance', None)
        xht = attributes.get('winding1Winding3PercentReactance', None)
        xlt = attributes.get('winding2Winding3PercentReactance', None)
        command = f'New Transformer.{transformer_id} Phases={phases} Windings={winding}'

        if xhl:
            command += f' xhl={xhl}'
        if xht:
            command += f' xht={xht}'
        if xlt:
            command += f' xlt={xlt}'

        connection_attributes = self.wired['attributes']
        conns = [connection_attributes.get('connectionType')]
        kvs = [connection_attributes.get('baseVoltage')]
        kvas = [connection_attributes.get('power')]
        rs = [connection_attributes.get('powerPercentResistance')]
        buses = [self.bus]
        for conn in self.conn:
            connection_attributes = conn.wired['attributes']
            conns.append(connection_attributes.get('connectionType'))
            kvs.append(connection_attributes.get('baseVoltage'))
            kvas.append(connection_attributes.get('power'))
            rs.append(connection_attributes.get('powerPercentResistance'))
            buses.append(conn.bus)

        command += f' buses={to_dss_array(to_str(buses))} ' \
                   f'conns={to_dss_array(to_str(conns))}'
        command += f' kVs={to_dss_array(to_str(kvs))} ' \
                   f'kvas={to_dss_array(to_str(kvas))}'
        command += f' %Rs={to_dss_array(to_str(rs))}'

        return command


class Generator(AssetMixin):
    type = GENERATOR

    def __init__(self, asset, bus, conn, wired):
        self.asset = asset
        self.bus = bus
        self.conn = conn
        self.wired = wired

    def __str__(self):
        generator_id = self.asset['id']
        command = f'New Generator.{generator_id}'
        return command


class Circuit(AssetMixin):
    type = ''

    def __init__(self, asset, bus, conn, wired):
        self.asset = asset
        self.bus = bus
        self.conn = conn
        self.wired = wired

    def __str__(self):
        attributes = self.asset['attributes']
        frequency = attributes.get('baseFrequency')
        kv = attributes.get('baseVoltage')
        pu = attributes.get('perUnitVoltage')
        phases = attributes.get('phaseCount')
        angle = attributes.get('phaseAngle')
        isc3 = attributes.get('shortCircuit3PhasePower')
        isc1 = attributes.get('shortCircuit1PhasePower')

        command = f'set defaultbasefrequency={frequency}\n'
        command += f'Edit Vsource.Source bus1={self.bus} BasekV={kv} pu={pu} angle={angle}'
        command += f' frequency={frequency} phases={phases} Isc3={isc3} Isc1={isc1}'

        return command


class LineCode(AssetMixin):
    type = LINECODE

    def __init__(self, linetype):
        self.linetype = linetype

    def __str__(self):
        line_type_id = self.linetype["id"]
        attributes = self.linetype['attributes']
        rmatrix = to_matrix(attributes.get('resistanceMatrix'))
        xmatrix = to_matrix(attributes.get('reactanceMatrix'))
        frequency = attributes.get('baseFrequency')
        phases = attributes.get('phaseCount')
        unit = attributes.get('resistanceMatrixUnit').split('/')[1]
        return (f'New Linecode.{line_type_id} nphases={phases} BaseFreq={frequency} units={unit}\n' 
                f'~ rmatrix={rmatrix} \n'
                f'~ xmatrix={xmatrix}')


ASSET = (Line, Switch, Meter, Regulator, Capacitor, Transformer, Generator, PowerQuality)
Conn = namedtuple("Conn", ["bus", "element", 'asset', 'wired'])


def generate_dss_script(assets, connections, buses, line_types, root='voltageSource', allowed_assets=ASSET):
    active_buses = {}

    for conn in connections:
        if conn['asset_id'] not in active_buses.keys():
            current = []
        else:
            current = active_buses[conn['asset_id']]

        element = get_asset_by_id(conn['asset_id'], assets)
        if not element:
            continue

        bus = get_bus(conn['bus_id'], buses)
        asset_type = get_asset_type(element, allowed_assets, root)

        current.append(Conn(bus, element, asset_type, conn))
        active_buses[conn['asset_id']] = current

    assets_by_type = group_assets_by_type(active_buses, root, line_types)
    stations = assets_by_type[0]['assets']
    circuit = build_circuit(assets_by_type, get_circuit_head(), get_circuit_tail(), warning=len(stations) == 0)
    return circuit


def line_types_to_json(line_types):
    return [{
        'id': line_type.id,
        'attributes': line_type.attributes
    } for line_type in line_types]


def get_bus(bus_id, buses):
    exists_bus = list(filter(lambda current_bus: bus_id == current_bus, buses))

    if len(exists_bus):
        return exists_bus[0]


def group_assets_by_type(buses, root, line_types):
    stations = []
    # substation = []
    # linecodes = []
    lines = []
    regulators = []
    transformers = []
    capacitors = []
    loads = []
    generators = []
    lcs = []

    grouped_elements = (
        {'title': 'Station', 'assets': stations},
        {'title': 'Generators', 'assets': generators},
        {'title': 'Transformers', 'assets': transformers},
        {'title': 'Line Codes', 'assets': lcs},
        {'title': 'Lines', 'assets': lines},
        {'title': 'Loads', 'assets': loads},
        # {'title': 'Storage', 'assets': storage},
        {'title': 'Capacitor', 'assets': capacitors},
        {'title': 'Regulator', 'assets': regulators},
    )

    for line_type in line_types:
        lcs.append(LineCode(line_type))

    for bus_id, connections in buses.items():
        conns = connections[1:]
        conn = connections[0]
        if conn.asset is None:
            continue

        asset = conn.asset(conn.element, conn.bus, conns, conn.wired)

        if conn.element['id'] == root:
            stations.append(asset)
        if conn.asset == Line:
            lines.append(asset)
        if conn.asset == Switch:
            lines.append(asset)
        if conn.asset == Meter:
            loads.append(asset)
        if conn.asset == Regulator:
            regulators.append(asset)
        if conn.asset == Capacitor:
            capacitors.append(asset)
        if conn.asset == Transformer:
            transformers.append(asset)
        if conn.asset == Generator:
            generators.append(asset)

    return grouped_elements


def get_asset_type(asset, allowed_assets=list(), root=None):
    asset_type = None
    if asset.get('id') == root:
        asset_type = Circuit
    elif asset['attributes'] and asset['attributes'].get('qualityType') == 'regulator':
        asset_type = Regulator
    elif asset['attributes'] and asset['attributes'].get('qualityType') == 'capacitor':
        asset_type = Capacitor
    else:
        for AssetClass in allowed_assets:
            if asset['type_code'] == AssetClass.type:
                asset_type = AssetClass

    return asset_type


def get_circuit_head():
    circuit_head = 'clear\n'
    circuit_head += 'New Circuit.AssetTracker\n'

    return circuit_head


def get_circuit_tail():
    circuit_tail = 'Set Voltagebases=[115, 4.16, .48]\n'
    circuit_tail += 'calcv\n'
    circuit_tail += 'solve\n'
    circuit_tail += 'Show Voltages LN Nodes\n'
    circuit_tail += 'Show Currents Elem\n'
    circuit_tail += 'Show Powers kVA Elem\n'
    circuit_tail += 'Show Losses\n'
    circuit_tail += 'Show Taps\n'

    return circuit_tail


def build_circuit(assets, head='', tail='', warning=False):
    circuit = []
    if warning:
        circuit.append(
            comment('WARNING: No voltage source provided or the source id is invalid\n')
        )

    circuit.append(head)
    for group in assets:
        circuit.append(f'// ==== {group["title"]}\n')

        for asset in group['assets']:
            circuit.append(str(asset) + '\n')
    circuit.append(tail)

    return circuit


def asset_to_json(asset, index=None):
    asset_id = asset['id']
    new_asset = {
        'id': asset_id,
        'type_code': asset['type_code'],
        'name': asset['name'],
        'attributes':  asset['attributes']
    }

    if index is not None:
        new_asset['name'] = f'{asset_id}_{index}'
        new_asset['id'] = f'{asset_id}_{index}'

    return new_asset


def connection_to_json(connection, asset_id=None, vertex=None):
    new_connection = {
        'bus_id': connection['bus_id'],
        'asset_id': connection['asset_id'],
        'asset_vertex_index': connection['asset_vertex_index'],
        'attributes': connection['attributes']
    }

    if asset_id:
        new_connection['asset_id'] = asset_id
    if vertex:
        new_connection['asset_vertex_index'] = vertex

    return new_connection


def filter_connection_by_bus(bus_id, connections):
    return filter(lambda connection: connection.bus_id == bus_id, connections)


def filter_connection_by_asset(asset_id, connections):
    return filter(lambda connection: connection['asset_id'] == asset_id, connections)


def filter_connection_by_asset_obj(asset_id, connections):
    return filter(lambda connection: connection.asset_id == asset_id, connections)


def get_asset_by_id(asset_id, assets):
    for asset in filter(lambda asset: asset['id'] == asset_id, assets):
        return asset


def normalize_assets_and_connections(assets, connections):
    flat_connections = []
    flat_assets = {}

    for asset in assets:
        pool_connections = list(filter_connection_by_asset(asset['id'], connections))
        asset_id = asset['id']

        if asset['type_code'] == AssetTypeCode.LINE and len(pool_connections) > 2:
            for i in range(0, len(pool_connections) - 1):
                if not flat_assets.get(f'{asset_id}_{i}'):
                    flat_assets[f'{asset_id}_{i}'] = asset_to_json(asset, i)

                temp_connection_0 = connection_to_json(pool_connections[i], asset_id=f'{asset_id}_{i}', vertex=0)
                temp_connection_1 = connection_to_json(pool_connections[i+1], asset_id=f'{asset_id}_{i}', vertex=1)

                flat_connections.append(temp_connection_0)
                flat_connections.append(temp_connection_1)
        else:
            if not flat_assets.get(asset_id):
                flat_assets[asset_id] = asset_to_json(asset)

            for conn in pool_connections:
                flat_connections.append(connection_to_json(conn))

    return flat_assets.values(), flat_connections


def make_pairs(pool):
    groups = []
    pool_length = len(pool)

    if pool_length == 2:
        groups.append((pool[0], pool[1]))
    else:
        for index in range(0, pool_length - 1):
            groups.append((pool[index], pool[index+1]))

    return groups


def remove_temporal_line_connections(temp_assets, temp_connections):
    connections = []
    assets = []
    subgraphs = {}
    G = nx.Graph()

    for asset in temp_assets:
        pool_connections = list(filter_connection_by_asset_obj(asset.id, temp_connections))
        buses = [connection.bus_id for connection in pool_connections]
        if asset.type_code == AssetTypeCode.LINE and (not asset.attributes or asset.attributes.get('lineType', '') == ''):
            G.add_nodes_from(buses)
            for pair in make_pairs(buses):
                G.add_edge(*pair)
        else:
            assets.append({
                'id': asset.id,
                'type_code': asset.type_code,
                'name': asset.name,
                'attributes': asset.attributes
            })

    for subgraph in nx.connected_components(G):
        bus_id = '_'.join(sorted(subgraph))
        subgraphs[bus_id] = subgraph

    assets_ids = [asset['id'] for asset in assets]
    for connection in temp_connections:
        if connection.asset_id in assets_ids:
            temporal_connection = {
                'asset_id': connection.asset_id,
                'asset_vertex_index': connection.asset_vertex_index,
                'bus_id': connection.bus_id,
                'attributes': connection.attributes
            }

            for key, buses in subgraphs.items():
                if connection.bus_id in buses:
                    temporal_connection['bus_id'] = key

            connections.append(temporal_connection)

    return assets, connections
