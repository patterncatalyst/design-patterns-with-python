"""Another team's module: it extends ``tariff_code`` with a kind the customs team does not own.

The registration exists once this module is imported, in every importer of ``tariff_code``,
for the rest of the process. The class is imported at run time because the annotation is
resolved when the decorator runs.
"""

from singledispatch_visitor.commodities import LithiumIonBattery
from singledispatch_visitor.tariff import tariff_code


@tariff_code.register
def _lithium_ion_battery(commodity: LithiumIonBattery) -> str:
    return "8507.60"
