from interactions.payment.payment_dest import PaymentDestNone, PaymentDestActiveHousehold, \
    PaymentDestParticipantHousehold, PaymentDestBusiness, PaymentDestStatistic, PaymentDestRentalUnitPropertyOwners
from sims4.tuning.tunable import TunableVariant


class TunablePaymentDestinationVariant(TunableVariant):
    def __init__(self, default='disabled', **kwargs):
        super().__init__(
            default=default,
            disabled=PaymentDestNone.TunableFactory(),
            active_household=PaymentDestActiveHousehold.TunableFactory(),
            participant_household=PaymentDestParticipantHousehold.TunableFactory(),
            business=PaymentDestBusiness.TunableFactory(),
            statistic=PaymentDestStatistic.TunableFactory(),
            rental_unit_property_owner=PaymentDestRentalUnitPropertyOwners.TunableFactory(),
            **kwargs,
        )