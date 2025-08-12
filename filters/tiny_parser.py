import traceback
from typing import List, Union

import sims4
import sims4.commands

from filtered_sims import (
    BASIC_TOKENS,
    FilteredSims,
    FilterFirstName,
    FilterIsSim,
    FilterLastName,
    Logic,
    SimFilter,
    SimFilterKeyword,
    SimTransformer,
)


class TinyParser:
    def __init__(self, tokens: List[str]):
        self._tokens = [token.strip().lower() for token in tokens]

    def parse(self) -> SimFilter:
        filters: List[Union[SimFilter, SimTransformer]] = []
        for idx, token in enumerate(self._tokens):
            if token == "and":
                filt_x = filters.pop()
                filt_y = filters.pop()
                # if not isinstance(filt_x, SimFilter) or not isinstance(
                #     filt_y, SimFilter
                # ):
                #     raise ValueError(
                #         "Invalid filter expression: {}".format(self._tokens)
                #     )
                filters.append(Logic.conjunction(filt_x, filt_y))
            elif token == "or":
                filt_y = filters.pop()
                filt_x = filters.pop()
                # if not isinstance(filt_x, SimFilter) or not isinstance(
                #     filt_y, SimFilter
                # ):
                #     raise ValueError(
                #         "Invalid filter expression: {}".format(self._tokens)
                #     )
                filters.append(Logic.disjunction(filt_x, filt_y))
            elif token == "not":
                filt_x = filters.pop()
                # if not isinstance(filt_x, SimFilter):
                #     raise ValueError(
                #         "Invalid filter expression: {}".format(self._tokens)
                #     )
                filters.append(Logic.negation(filt_x))
            elif token == "compose_filter":
                filt_x = filters.pop()
                transformer = filters.pop()
                # if not isinstance(filt_x, SimFilter) or not isinstance(
                #     transformer, SimTransformer
                # ):
                #     raise ValueError(
                #         "Invalid filter expression: {} - filt_x:{}:{} - transformer:{}:{}".format(
                #             self._tokens,
                #             filt_x,
                #             isinstance(filt_x, SimFilter),
                #             transformer,
                #             isinstance(transformer, SimTransformer),
                #         )
                #     )
                filters.append(Logic.compose_filter(filt_x, transformer))
            elif token == "compose_transformer":
                transformer_x = filters.pop()
                transformer_y = filters.pop()
                # if not isinstance(transformer_x, SimTransformer) or not isinstance(
                #     transformer_y, SimTransformer
                # ):
                #     raise ValueError(
                #         "Invalid filter expression: {}".format(self._tokens)
                #     )
                filters.append(Logic.compose_transformer(transformer_x, transformer_y))
            else:
                atom = self.make_atom(token)
                filters.append(atom)
        if len(filters) != 1:
            raise ValueError("Invalid filter expression: {} - {}".format(self._tokens, filters))
        # if not isinstance(filters[0], SimFilter):
        #     raise ValueError(
        #         "Invalid filter expression: {} - {}".format(self._tokens, filters)
        #     )
        return filters[0]

    def make_atom(self, text: str) -> Union[SimFilter, SimTransformer]:
        if text in BASIC_TOKENS:
            return BASIC_TOKENS[text]
        operator_keywords = {
            "=": SimFilterKeyword.EQUALS,
            "<": SimFilterKeyword.LESS_THAN,
            ">": SimFilterKeyword.GREATER_THAN,
            ":": SimFilterKeyword.CONTAINS,
        }
        operator_filters = {
            "firstname": FilterFirstName,
            "lastname": FilterLastName,
        }
        for operator, keyword in operator_keywords.items():
            if operator in text:
                parts = text.split(operator)
                if len(parts) != 2:
                    raise ValueError(f"Invalid filter expression: {text}")
                field, value = parts
                field = field.strip()
                value = value.strip()
                if field in operator_filters:
                    return operator_filters[field](keyword, value)
                else:
                    raise ValueError(f"Unknown filter field: {field}")
        return FilterIsSim()


@sims4.commands.Command("lot51_core.sim_filter", command_type=sims4.commands.CommandType.Live)
def sim_filter(
    *args,
    _connection=None,
):
    output = sims4.commands.CheatOutput(_connection)
    try:
        output(f"Got arguments: {args}")
        parser = TinyParser(args)
        filter = parser.parse()
        fsims = FilteredSims()
        fsims.filter(filter)
        sim_infos = [sim for sim in fsims]
        for sim in sim_infos:
            output(f"Sim ID: {sim.id} Name: {sim.first_name} {sim.last_name}")
    except Exception as e:
        output(f"Error filtering Sims: {e} - {traceback.format_exc()}")
