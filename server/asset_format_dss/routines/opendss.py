from collections import namedtuple

from asset_tracker.models.assets import (
    Asset, Bus, Connection, LineType, AssetTypeCode)


TRANSFORMER = AssetTypeCode.TRANSFORMER
METER = AssetTypeCode.METER
LINE = AssetTypeCode.LINE
LINECODE = 'linecode'
GENERATOR = 'g'
STATION = 'S'
SUBSTATION = AssetTypeCode.SUBSTATION
LOAD = 'load'
BUS = 'bus'
STORAGE = 'o'
SWITCH = 'x'
POWERQUALITY = 'q'
POWERQUALITY_CAPACITOR = f'{POWERQUALITY}c'
POWERQUALITY_REGULATOR = f'{POWERQUALITY}r'


to_dss_array = lambda l:  f'[ {" ".join(l)} ]'
build_bus = lambda bus, nodes:  f'{bus}.{".".join(nodes)}' if nodes else f'{bus}'
to_str = lambda l: [str(e) for e in l if e]


def to_matrix(lists):
    rows = [' '.join(map(str, entry)) for entry in lists]
    matrix = ' | '.join(rows)
    return f'[{matrix}]'


class AssetMixin:
    @property
    def id(self):
        return self.asset.name

    @property
    def name(self):
        return self.asset.name

    def attributes(self):
        return self.asset.name


class Line(AssetMixin):
    type = LINE

    def __init__(self, asset, bus, conn, wired):
        self.asset = asset
        self.bus = bus
        self.conn = conn
        self.wired = wired

    def __str__(self):
        phases = self.asset.attributes.get('phaseCount')
        lc = self.asset.attributes.get('lineType')
        length = self.asset.attributes.get('lineLength')
        unit = self.asset.attributes.get('lengthUnit')

        line = f'New Line.{self.asset.id} '
        line += f'phases={phases} ' if phases else ''
        line += f'linecode={lc} ' if lc else ''
        line += f'length={length} ' if length else ''
        line += f'units={unit}' if unit else ''

        attr = self.wired.attributes
        bus1 = build_bus(self.bus.id, to_str(attr.get('busNodes') or []))
        bus2 = None
        if len(self.conn) > 0:
            for conn in self.conn:
                attr = conn.wired.attributes
                bus2 = build_bus(conn.bus.id, to_str(
                    attr.get('busNodes') or []))

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
        phases = self.asset.attributes.get('phaseCount')
        r1 = self.asset.attributes.get('positiveSequenceResistance')
        r0 = self.asset.attributes.get('zeroSequenceResistance')
        x1 = self.asset.attributes.get('positiveSequenceReactance')
        x0 = self.asset.attributes.get('zeroSequenceReactance')
        c1 = self.asset.attributes.get('positiveSequenceCapacitance')
        c0 = self.asset.attributes.get('zeroSequenceCapacitance')

        line = f'New Line.{self.asset.id} Switch=y phases={phases}'
        line += f' r1={r1} r0={r0} x1={x1} x0={x0} c1={c1} c0={c0}'

        attr = self.wired.attributes
        bus1 = build_bus(self.bus.id, to_str(attr.get('busNodes')))
        bus2 = None
        if len(self.conn) > 0:
            for conn in self.conn:
                attr = conn.wired.attributes
                bus2 = build_bus(conn.bus.id, to_str(attr.get('busNodes')))

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
        phases = self.asset.attributes.get('phaseCount')
        model = self.asset.attributes.get('loadModel')

        attr = self.wired.attributes
        bus1 = build_bus(self.bus.id, to_str(attr.get('busNodes') or []))

        kV = attr.get('baseVoltage')
        conn = attr.get('connectionType')
        kW = attr.get('activePower')
        kvar = attr.get('reactivePower')

        command = f'New Load.Load_{self.asset.id} '
        command += f'phases={phases} ' if phases else ''
        command += f'conn={conn} ' if conn else ''
        command += f'model={model} ' if model else ''
        command += f' Bus1={bus1} ' if bus1 else ''
        command += f'kV={kV} ' if kV else ''
        command += f'kW={kW} ' if kW else ''
        command += f'kvar={kvar}' if kV else ''

        return command


class Regulator(AssetMixin):
    type = POWERQUALITY_REGULATOR

    def __init__(self, asset, bus, conn, wired):
        self.asset = asset
        self.bus = bus
        self.conn = conn
        self.wired = wired

    def __str__(self):
        xhl = self.asset.attributes.get('percentLoadLoss')
        vreg = self.asset.attributes.get('regulatedVoltage')
        band = self.asset.attributes.get('bandwidthVoltage')
        ptratio = self.asset.attributes.get('potentialTransformerRatio')
        ctprim = self.asset.attributes.get('currentTransformerRating')
        R = self.asset.attributes.get('rSettingVoltage')
        X = self.asset.attributes.get('xSettingVoltage')
        phases = self.asset.attributes.get('phaseCount')
        winding = self.asset.attributes.get('windingCount')

        attr = self.wired.attributes
        kVs = [attr.get('baseVoltage')]
        kVAs = [attr.get('power')]
        buses = [build_bus(self.bus.id, to_str(attr.get('busNodes')))]

        for conn in self.conn:
            attr = conn.wired.attributes
            kVs.append(attr.get('baseVoltage'))
            kVAs.append(attr.get('power'))
            buses.append(build_bus(conn.bus.id, to_str(attr.get('busNodes'))))

        command = f'New Transformer.{self.asset.id} phases={phases} bank=reg1'
        command += f' buses={to_dss_array(to_str(buses))} kVs={to_dss_array(to_str(kVs))}'
        command += f' kVAs={to_dss_array(to_str(kVAs))} xhl={xhl} %LoadLoss={xhl}\n'

        command +=  f'New regcontrol.{self.asset.id} transformer={self.asset.id} '
        command += f' winding={winding} vreg={vreg} band={band} ptratio={ptratio} ctprim={ctprim}'
        command += f' R={R} X={X}'

        return command


class Capacitor(AssetMixin):
    type = POWERQUALITY_CAPACITOR

    def __init__(self, asset, bus, conn, wired):
        self.asset = asset
        self.bus = bus
        self.conn = conn
        self.wired = wired

    def __str__(self):
        phases = self.asset.attributes.get('phaseCount')

        attr = self.wired.attributes
        bus1 = build_bus(self.bus.id, to_str(attr.get('busNodes')))
        kV = attr.get('baseVoltage')
        conn = attr.get('connectionType', None)
        kvar = attr.get('reactivePower')

        command = f'new capacitor.{self.asset.id} phases={phases} bus1={bus1} kVAr={kvar} kV={kV} '

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
        command = f'// Power Quality still not supported {self.asset.id}'

        return command


class Transformer(AssetMixin):
    type = TRANSFORMER

    def __init__(self, asset, bus, conn, wired):
        self.asset = asset
        self.bus = bus
        self.conn = conn
        self.wired = wired

    def __str__(self):
        phases = self.asset.attributes.get('phaseCount')
        winding = self.asset.attributes.get('windingCount')
        xhl = self.asset.attributes.get('winding1Winding2PercentReactance', None)
        xht = self.asset.attributes.get('winding1Winding3PercentReactance', None)
        xlt = self.asset.attributes.get('winding2Winding3PercentReactance', None)
        command = f'New Transformer.{self.asset.id} Phases={phases} Windings={winding}'

        if xhl:
            command += f' xhl={xhl}'
        if xht:
            command += f' xht={xht}'
        if xlt:
            command += f' xlt={xlt}'

        attr = self.wired.attributes
        conns = [attr.get('connectionType')]
        kVs = [attr.get('baseVoltage')]
        kVAs = [attr.get('power')]
        Rs = [attr.get('powerPercentResistance')]
        buses = [self.bus.id]
        for conn in self.conn:
            attr = conn.wired.attributes
            conns.append(attr.get('connectionType'))
            kVs.append(attr.get('baseVoltage'))
            kVAs.append(attr.get('power'))
            Rs.append(attr.get('powerPercentResistance'))
            buses.append(conn.bus.id)

        command += f' buses={to_dss_array(to_str(buses))} ' \
                   f'conns={to_dss_array(to_str(conns))}'
        command += f' kVs={to_dss_array(to_str(kVs))} ' \
                   f'kvas={to_dss_array(to_str(kVAs))}'
        command += f' %Rs={to_dss_array(to_str(Rs))}'

        return command


class Generator(AssetMixin):
    type = GENERATOR

    def __init__(self, asset, bus, conn, wired):
        self.asset = asset
        self.bus = bus
        self.conn = conn
        self.wired = wired

    def __str__(self):
        command = f'New Generator.{self.asset.id}'
        return command


class Circuit(AssetMixin):
    type = ''

    def __init__(self, asset, bus, conn, wired):
        self.asset = asset
        self.bus = bus
        self.conn = conn
        self.wired = wired

    def __str__(self):
        frequency = self.asset.attributes.get('baseFrequency')
        kV = self.asset.attributes.get('baseVoltage')
        pu = self.asset.attributes.get('perUnitVoltage')
        phases = self.asset.attributes.get('phaseCount')
        angle = self.asset.attributes.get('phaseAngle')
        Isc3 = self.asset.attributes.get('shortCircuit3PhasePower')
        Isc1 = self.asset.attributes.get('shortCircuit1PhasePower')

        command = f'set defaultbasefrequency={frequency}\n'
        command += f'Edit Vsource.Source bus1={self.bus.id} BasekV={kV} pu={pu} angle={angle}'
        command += f' frequency={frequency} phases={phases} Isc3={Isc3} Isc1={Isc1}'

        return command


class LineCode(AssetMixin):
    type = LINECODE

    def __init__(self, linetype):
        self.linetype = linetype

    def __str__(self):
        rmatrix = to_matrix(self.linetype.attributes.get('resistanceMatrix'))
        xmatrix = to_matrix(self.linetype.attributes.get('reactanceMatrix'))
        frequency = self.linetype.attributes.get('baseFrequency')
        phases = self.linetype.attributes.get('phaseCount')
        unit = self.linetype.attributes.get('resistanceMatrixUnit').split('/')[1]
        return (f'New Linecode.{self.linetype.id} nphases={phases} BaseFreq={frequency} units={unit}\n' 
                f'~ rmatrix={rmatrix} \n'
                f'~ xmatrix={xmatrix}')


ASSET = (Line, Switch, Meter, Regulator, Capacitor, Transformer, Generator, PowerQuality)
Conn = namedtuple("Conn", ["bus", "element", 'asset', 'wired'])


def comment(text):
    return f'// {text}'


def generate_dss_script(db, root='voltageSource', allowed_assets=ASSET):
    buses = {}
    for conn in db.query(Connection):
        asset = None
        if conn.asset_id not in buses.keys():
            current = []
        else:
            current = buses[conn.asset_id]

        element = db.query(Asset).filter(Asset.id == conn.asset_id).one()
        print(f'===== Code:  {element.type_code}')
        bus = db.query(Bus).filter(Bus.id == conn.bus_id).one()

        if element.id == root:
            asset = Circuit
        else:
            for AssetClass in allowed_assets:
                if element.type_code == AssetClass.type:
                    asset = AssetClass

        current.append(Conn(bus, element, asset, conn))
        buses[conn.asset_id] = current

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

    ELEMENTS = (
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

    circuit = []
    circuit_head = 'clear\n'
    circuit_head += 'New Circuit.AssetTracker\n'

    circuit_tail = 'Set Voltagebases=[115, 4.16, .48]\n'
    circuit_tail += 'calcv\n'
    circuit_tail += 'solve\n'
    circuit_tail += 'Show Voltages LN Nodes\n'
    circuit_tail += 'Show Currents Elem\n'
    circuit_tail += 'Show Powers kVA Elem\n'
    circuit_tail += 'Show Losses\n'
    circuit_tail += 'Show Taps\n'

    for conn in db.query(LineType):
        lcs.append(LineCode(conn))

    for bus_id, connections in buses.items():
        print(connections)
        conns = connections[1:]
        conn = connections[0]
        asset = conn.asset(conn.element, conn.bus, conns, conn.wired)

        if conn.element.id == root:
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

    if len(stations) == 0:
        circuit.append(comment(
            'WARNING: No voltage source provided or the source id is invalid\n'
        ))

    circuit.append(circuit_head)
    for group in ELEMENTS:
        circuit.append(f'// ==== {group["title"]}\n')

        for asset in group['assets']:
            circuit.append(str(asset) + '\n')
    circuit.append(circuit_tail)

    return circuit
