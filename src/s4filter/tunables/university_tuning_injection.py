from lot51_core import logger
from lot51_core.tunables.base_injection import BaseTunableInjection
from lot51_core.utils.collections import AttributeDict
from lot51_core.utils.injection import inject_list, merge_list, inject_dict, inject_mapping_lists
from services import get_instance_manager
from sims.university.university_commands import UniversityCommandTuning
from sims.university.university_tuning import University
from sims4.common import Pack
from sims4.resources import Types
from sims4.tuning.tunable import TunableList, TunableReference, TunableTuple, TunableMapping, Tunable, OptionalTunable, \
    TunableInterval
from tunable_multiplier import TunableMultiplier


class TunableUniversityTuningInjection(BaseTunableInjection):

    FACTORY_TUNABLES = {
        'additional_majors': TunableList(
            description="Injects to ALL_DEGREES",
            tunable=TunableReference(manager=get_instance_manager(Types.UNIVERSITY_MAJOR)),
        ),
        'additional_electives': TunableList(
            description="Injects to COURSE_ELECTIVES.electives",
            tunable=TunableTuple(
                elective=TunableReference(manager=get_instance_manager(Types.UNIVERSITY_COURSE_DATA)),
                weight=TunableMultiplier.TunableFactory(
                    description='The weight of this elective relative to other electives in this list.'
                )
            )
        ),
        'additional_degree_traits': TunableList(
            description="Injects to sims.university.university_commands.UniversityCommandTuning.DEGREE_TRAITS",
            tunable=TunableTuple(
                description='A tuple of prestige and honors booleans, and the associated list of degree traits.',
                prestige=Tunable(
                    description='The prestige type (Prestige or No Prestige) of this degree list.',
                    tunable_type=bool,
                    default=False
                ),
                honors=Tunable(
                    description='The honors type (Honors or No Honors) of this degree list.',
                    tunable_type=bool,
                    default=False
                ),
                traits=TunableList(
                    description='The list of degree traits for this prestige and honors permutation.',
                    tunable=TunableReference(
                        description='The degree trait.',
                        manager=get_instance_manager(Types.TRAIT),
                        pack_safe=True
                    )
                )
            )
        ),
        'skill_to_majors': TunableMapping(
            key_type=TunableReference(
                description='The skill being used to assign the major.',
                manager=get_instance_manager(Types.STATISTIC),
                class_restrictions=('Skill',),
                pack_safe=True,
            ),
            value_type=TunableList(
                description='The set of majors to choose from when assigning a major based on the associated skill type. If this has more than one entry then one of the majors will be chosen at random.',
                tunable=TunableReference(
                    description='The university major to enroll the Sim in.',
                    manager=get_instance_manager(Types.UNIVERSITY_MAJOR)
                ),
            ),
            unique_entries=True,
        ),
        'elective_count': OptionalTunable(
            tunable=TunableInterval(
                default_lower=8,
                default_upper=10,
                minimum=1,
                maximum=100,
                tunable_type=int
            ),
        )
    }

    __slots__ = ('additional_majors', 'additional_electives', 'additional_degree_traits', 'skill_to_majors', 'elective_count',)

    @property
    def required_packs(self):
        return (Pack.EP08,)

    def inject(self):
        # Add additional_majors
        inject_list(University, 'ALL_DEGREES', self.additional_majors)

        # Add COURSE_ELECTIVES overrides
        elective_overrides = AttributeDict()
        if len(self.additional_electives):
            elective_overrides.electives = merge_list(University.COURSE_ELECTIVES.electives, self.additional_electives)
        if self.elective_count is not None:
            elective_overrides.elective_count = self.elective_count

        if len(elective_overrides):
            inject_dict(University, 'COURSE_ELECTIVES', **elective_overrides)

        # Add additional_degree_traits
        inject_list(UniversityCommandTuning, 'DEGREE_TRAITS', self.additional_degree_traits)

        # Add skill_to_major
        inject_mapping_lists(University, 'SKILL_TO_MAJOR_TUNING', self.skill_to_majors)