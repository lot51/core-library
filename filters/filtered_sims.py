import enum
import os
import traceback
from typing import Callable, Dict, List, Union

import services
import sims4.commands
from server_commands.argument_helpers import OptionalTargetParam
from sims4.reload import reload_file
from sims.occult.occult_enums import OccultType
from sims.sim_info import SimInfo
from sims.sim_info_manager import SimInfoManager
from sims.sim_info_types import Age, Gender, SpeciesExtended


class FilteredSims:
    """
    A class to filter SimInfo objects based on specified filters
    """

    def __init__(self):
        self._sim_info_manager: SimInfoManager = services.sim_info_manager()
        self._starter_list: list[SimInfo] = list(self._sim_info_manager.get_all())
        self._filtered_sims: filter[SimInfo] = filter(lambda x: x is not None and isinstance(x, SimInfo), self._starter_list)

    def filter(self, filter_func: Callable[[SimInfo], bool]) -> None:
        """
        Apply a filter function to the current set of filtered Sims.

        @param filter_func: A function that takes a SimInfo object and returns a boolean indicating
                            whether the object should be included in the filtered results.
        @return:            None
        @example
        from sims.sim_info_types

        def is_adult(sim: SimInfo) -> bool:
            return sim.age >= Age.YOUNGADULT

        filtered_sims = FilteredSims()
        filtered_sims.filter(is_adult)
        for sim_info in filtered_sims:
            print(sim_info.sim_id)
        """
        self._filtered_sims = filter(filter_func, self._filtered_sims)

    def __iter__(self):
        """
        Iterate over the filtered Sims.
        Once iteration has started, the filtered_sims class is now defunct and cannot be reused.
        """
        return self

    def __next__(self):
        """
        Iterate over the filtered Sims.
        Once iteration has started, the filtered_sims class is now defunct and cannot be reused.
        """
        return next(self._filtered_sims)


class SimFilterKeyword(enum.IntEnum):
    EQUALS = 1
    GREATER_THAN = 2
    LESS_THAN = 3
    CONTAINS = 4


class SimFilter:
    """
    A base class for all filters.
    """

    def __init__(self):
        return

    def __call__(self, sim: SimInfo) -> bool:
        raise NotImplementedError("Filter is an abstract base class and cannot be called directly.")


class FilterAge(SimFilter):
    def __init__(self, keyword: SimFilterKeyword, age: Age):
        super().__init__()
        self._keyword = keyword
        self._age = age

    def __call__(self, sim: SimInfo) -> bool:
        try:
            # if not hasattr(sim, "age"):
            #     return False
            # if not isinstance(sim.age, Age):
            #     return False
            if self._keyword == SimFilterKeyword.EQUALS:
                return sim.age == self._age
            elif self._keyword == SimFilterKeyword.GREATER_THAN:
                return sim.age > self._age
            elif self._keyword == SimFilterKeyword.LESS_THAN:
                return sim.age < self._age
            else:
                raise ValueError(f"Unknown keyword: {self._keyword}")
        except Exception as e:
            return False


class FilterGender(SimFilter):
    def __init__(self, gender: Gender):
        super().__init__()
        self._gender = gender

    def __call__(self, sim: SimInfo) -> bool:
        try:
            # if not hasattr(sim, "gender"):
            #     return False
            # if not isinstance(sim.gender, Gender):
            #     return False
            return sim.gender == self._gender
        except Exception as e:
            return False


class FilterFirstName(SimFilter):
    def __init__(self, keyword: SimFilterKeyword, first_name: str):
        super().__init__()
        self._keyword = keyword
        self._first_name = first_name

    def __call__(self, sim: SimInfo) -> bool:
        if not hasattr(sim, "first_name"):
            return False
        if not isinstance(sim.first_name, str):
            return False
        if self._keyword == SimFilterKeyword.EQUALS:
            return sim.first_name == self._first_name
        else:
            raise ValueError(f"Unknown keyword: {self._keyword}")


class FilterLastName(SimFilter):
    def __init__(self, keyword: SimFilterKeyword, last_name: str):
        super().__init__()
        self._keyword = keyword
        self._last_name = last_name

    def __call__(self, sim: SimInfo) -> bool:
        if not hasattr(sim, "last_name"):
            return False
        if not isinstance(sim.last_name, str):
            return False
        if self._keyword == SimFilterKeyword.EQUALS:
            return sim.last_name == self._last_name
        else:
            raise ValueError(f"Unknown keyword: {self._keyword}")


class FilterSimID(SimFilter):
    def __init__(self, sim_id: int):
        super().__init__()
        self._sim_id = sim_id

    def __call__(self, sim: SimInfo) -> bool:
        try:
            # if not hasattr(sim, "sim_id"):
            #     return False
            # if not isinstance(sim.sim_id, int):
            #     return False
            return sim.sim_id == self._sim_id
        except Exception as e:
            return False


class FilterOccult(SimFilter):
    def __init__(self, occult: OccultType):
        super().__init__()
        self._occult = occult

    def __call__(self, sim: SimInfo) -> bool:
        try:
            # if not hasattr(sim, "occult_types"):
            #     return False
            # if not isinstance(sim.occult_types, OccultType):
            #     return False
            return sim.occult_types & self._occult == self._occult
        except Exception as e:
            return False


class FilterIsSim(SimFilter):
    def __init__(self):
        super().__init__()

    def __call__(self, sim: SimInfo) -> bool:
        try:
            return isinstance(sim, SimInfo)
        except Exception as e:
            return False


class FilterPregnant(SimFilter):
    def __call__(self, sim: SimInfo) -> bool:
        try:
            # if not hasattr(sim, "is_pregnant"):
            #     return False
            # if not isinstance(sim.is_pregnant, bool):
            #     return False
            return sim.is_pregnant
        except Exception as e:
            return False


class FilterSpecies(SimFilter):
    def __init__(self, species: SpeciesExtended):
        super().__init__()
        self._species = species

    def __call__(self, sim: SimInfo) -> bool:
        try:
            if self._species == SpeciesExtended.HUMAN:
                return sim.species == SpeciesExtended.HUMAN
            return sim.extended_species == self._species
        except Exception as e:
            return False


class FilterBreed(SimFilter):
    def __init__(self, breed: str):
        super().__init__()
        self._breed = breed

    def __call__(self, sim: SimInfo) -> bool:
        try:
            if self._breed in sim.breed_name.lower():  # pyright: ignore[reportAttributeAccessIssue, reportOperatorIssue]
                return True
            return False
        except Exception as e:
            return False


class SimTransformer:
    """
    A base class for all SimInfo transformers.
    """

    def __call__(self, sim: SimInfo) -> Union[SimInfo, None]:
        raise NotImplementedError("SimTransformer is an abstract base class and cannot be called directly.")


class TransformerSpouse(SimTransformer):
    """
    Transforms a SimInfo object to its spouse SimInfo if it exists.
    """

    def __call__(self, sim: SimInfo) -> Union[SimInfo, None]:
        try:
            spouse = sim.get_spouse_sim_info()
            if not isinstance(spouse, SimInfo):
                return None
            return spouse
        except Exception as e:
            return None


class TransformerPartner(SimTransformer):
    """
    Transforms a SimInfo object to its pregnancy partner SimInfo if it exists.
    """

    def __call__(self, sim: SimInfo) -> Union[SimInfo, None]:
        try:
            if not sim.is_pregnant:
                return None
            partner = sim.pregnancy_tracker().get_partner()  # pyright: ignore[reportOptionalCall]
            if not isinstance(partner, SimInfo):
                return None
            return partner
        except Exception as e:
            return None


class Logic:
    @staticmethod
    def conjunction(*filters: SimFilter) -> SimFilter:
        class ConjunctiveFilter(SimFilter):
            def __call__(self, sim: SimInfo) -> bool:
                return all(f(sim) for f in filters)

        return ConjunctiveFilter()

    @staticmethod
    def disjunction(*filters: SimFilter) -> SimFilter:
        class DisjunctiveFilter(SimFilter):
            def __call__(self, sim: SimInfo) -> bool:
                return any(f(sim) for f in filters)

        return DisjunctiveFilter()

    @staticmethod
    def negation(filter_x: SimFilter) -> SimFilter:
        class NegationFilter(SimFilter):
            def __call__(self, sim: SimInfo) -> bool:
                return not filter_x(sim)

        return NegationFilter()

    @staticmethod
    def compose_filter(filter_x: SimFilter, transformer: SimTransformer) -> SimFilter:
        class ComposedFilter(SimFilter):
            def __call__(self, sim: SimInfo) -> bool:
                try:
                    transformed_sim = transformer(sim)
                    if transformed_sim is None:
                        return False
                    return filter_x(transformed_sim)
                except Exception as e:
                    return False

        return ComposedFilter()

    @staticmethod
    def compose_transformer(
        *transformers: SimTransformer,
    ) -> SimTransformer:
        class ComposedTransformer(SimTransformer):
            def __call__(self, sim: SimInfo) -> Union[SimInfo, None]:
                try:
                    transformed_sim = sim
                    for transformer in transformers:
                        transformed_sim = transformer(transformed_sim)
                        if transformed_sim is None:
                            return None
                    return transformed_sim
                except Exception as e:
                    return None

        return ComposedTransformer()


BASIC_TOKENS = {
    "spouse": TransformerSpouse(),
    "partner": TransformerPartner(),
    "male": FilterGender(Gender(Gender.MALE)),
    "female": FilterGender(Gender(Gender.FEMALE)),
    "elder": FilterAge(SimFilterKeyword.EQUALS, Age(Age.ELDER)),
    "adult": FilterAge(SimFilterKeyword.EQUALS, Age(Age.ADULT)),
    "youngadult": FilterAge(SimFilterKeyword.EQUALS, Age(Age.YOUNGADULT)),
    "teen": FilterAge(SimFilterKeyword.EQUALS, Age(Age.TEEN)),
    "child": FilterAge(SimFilterKeyword.EQUALS, Age(Age.CHILD)),
    "toddler": FilterAge(SimFilterKeyword.EQUALS, Age(Age.TODDLER)),
    "baby": FilterAge(SimFilterKeyword.EQUALS, Age(Age.BABY)),
    "infant": FilterAge(SimFilterKeyword.EQUALS, Age(Age.INFANT)),
    "pregnant": FilterPregnant(),
    "human": FilterSpecies(SpeciesExtended(SpeciesExtended.HUMAN)),
    "dog": FilterSpecies(SpeciesExtended(SpeciesExtended.DOG)),
    "smalldog": FilterSpecies(SpeciesExtended(SpeciesExtended.SMALLDOG)),
    "cat": FilterSpecies(SpeciesExtended(SpeciesExtended.CAT)),
    "horse": FilterSpecies(SpeciesExtended(SpeciesExtended.HORSE)),
    "fox": FilterSpecies(SpeciesExtended(SpeciesExtended.FOX)),
    "vampire": FilterOccult(OccultType(OccultType.VAMPIRE)),
    "werewolf": FilterOccult(OccultType(OccultType.WEREWOLF)),
    "witch": FilterOccult(OccultType(OccultType.WITCH)),
    "alien": FilterOccult(OccultType(OccultType.ALIEN)),
    "mermaid": FilterOccult(OccultType(OccultType.MERMAID)),
    "fairy": FilterOccult(OccultType(OccultType.FAIRY)),
    "nooccult": Logic.negation(
        Logic.conjunction(
            FilterOccult(OccultType(OccultType.VAMPIRE)),
            FilterOccult(OccultType(OccultType.WEREWOLF)),
            FilterOccult(OccultType(OccultType.WITCH)),
            FilterOccult(OccultType(OccultType.ALIEN)),
            FilterOccult(OccultType(OccultType.MERMAID)),
            FilterOccult(OccultType(OccultType.FAIRY)),
        )
    ),
}
