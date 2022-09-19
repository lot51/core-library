from buffs.buff import Buff
from sims4.tuning.tunable import TunableTuple, TunableEnumEntry, TunableList, OptionalTunable, HasTunableSingletonFactory, AutoFactoryInit
from interactions.utils.loot import LootActions
from social_media import SocialMediaPostType, SocialMediaNarrative, SocialMediaPolarity
from sims4.localization import TunableLocalizedString
from social_media.social_media_tuning import SocialMediaTunables


class TunableSocialBunnyInjection(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {
        # Follows the TYPES_OF_POSTS tdesc for SocialMediaTunables
        # https://lot51.cc/tdesc/Tuning/social_media-social_media_tuning.tdesc
        "types_of_posts": TunableList(
            description='A set of the different Posts that can be made in Social Media.',
            tunable=TunableTuple(
                post_type=TunableEnumEntry(description='A SocialMediaPostType enum entry.', tunable_type=SocialMediaPostType, default=SocialMediaPostType.DEFAULT),
                narrative=TunableEnumEntry(
                    description='A SocialMediaNarrative enum entry.',
                    tunable_type=SocialMediaNarrative,
                    default=SocialMediaNarrative.FRIENDLY
                ),
                polarity=TunableEnumEntry(
                    description='A SocialMediaPolarity enum entry.',
                    tunable_type=SocialMediaPolarity,
                    default=SocialMediaPolarity.POSITIVE
                ),
                content=TunableList(
                    description='The list of strings that can be randomly used for this post.',
                    tunable=TunableLocalizedString()
                ),
                context_post=OptionalTunable(
                    description='The Buff that will allow for this contextual post to be made.',
                    tunable=Buff.TunablePackSafeReference()
                ),
                loots_on_post=TunableList(
                    description='Loots applied to the actor when the post is made.',
                    tunable=LootActions.TunableReference(description='A loot applied to the actor when the post is made.', pack_safe=True)
                ),
                target_loots_on_post=TunableList(
                    description='Loots applied to the target when the post is made.',
                    tunable=LootActions.TunableReference(description='A loot applied to the target when the post is made.', pack_safe=True)
                )
            )
        )
    }

    __slots__ = ('types_of_posts',)

    def inject(self):
        SocialMediaTunables.TYPES_OF_POSTS += self.types_of_posts
