from lot51_core.tunables.base_injection import BaseTunableInjection
from services import get_instance_manager
from sims.university.university_tuning import University
from sims4.common import Pack
from sims4.resources import Types
from sims4.tuning.tunable import TunableList, TunableReference, TunableTuple, TunableMapping


class TunableUniversityTuningInjection(BaseTunableInjection):

    FACTORY_TUNABLES = {
        'additional_majors': TunableList(
            description="Injects to ALL_DEGREES",
            tunable=TunableReference(manager=get_instance_manager(Types.UNIVERSITY_MAJOR)),
        ),
        'additional_electives': TunableList(
            description="Injects to COURSE_ELECTIVES.electives",
            tunable=TunableTuple(
                elective=TunableReference(manager=get_instance_manager(Types.UNIVERSITY_COURSE_DATA))
            )
        ),
        'skill_to_majors': TunableMapping(
            key_type=TunableReference(
                description='The skill being used to assign the major.',
                manager=get_instance_manager(Types.STATISTIC),
                class_restrictions=('Skill',),
            ),
            value_type=TunableList(
                description='The set of majors to choose from when assigning a major based on the associated skill type. If this has more than one entry then one of the majors will be chosen at random.',
                tunable=TunableReference(description='The university major to enroll the Sim in.', manager=get_instance_manager(Types.UNIVERSITY_MAJOR)),
            ),
            unique_entries=True,
        ),
    }

    __slots__ = ('additional_majors', 'additional_electives', 'skill_to_majors',)

    @property
    def required_packs(self):
        return (Pack.EP08,)

    def inject(self):

        University.ALL_DEGREES += self.additional_majors

        electives = University.COURSE_ELECTIVES.electives + self.additional_electives
        University.COURSE_ELECTIVES = University.COURSE_ELECTIVES.clone_with_overrides(electives=electives)

        for skill, majors in self.skill_to_majors:
            if skill in University.SKILL_TO_MAJOR_TUNING:
                University.SKILL_TO_MAJOR_TUNING[skill] += majors
            else:
                University.SKILL_TO_MAJOR_TUNING[skill] = majors