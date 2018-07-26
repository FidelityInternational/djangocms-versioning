from django.core.exceptions import ImproperlyConfigured


class Versionable:

    def __init__(self, grouper, content, grouper_field_name=None):
        self.grouper = grouper
        self.grouper_field_name = grouper_field_name
        self.content = content
        self.grouper_field = self._get_grouper_field()

    def _get_grouper_field(self):
        relations = [
            f for f in self.content._meta.get_fields() if
            f.is_relation and
            not f.auto_created and
            not f.many_to_many
        ]
        grouper_field = None
        for field in relations:
            if self.grouper_field_name and field.name != self.grouper_field_name:
                continue
            if field.rel.model != self.grouper:
                continue
            if grouper_field:
                raise ImproperlyConfigured(
                    'Found multiple relations to grouper model ({grouper}) in '
                    '{model}. Specify Versionable.grouper_field_name.'.format(
                        grouper=self.grouper,
                        model=self.content,
                    ),
                )
            grouper_field = field

        if grouper_field is None:
            raise ImproperlyConfigured(
                'No relation to grouper model ({grouper}) found in {model}.'.format(
                    grouper=self.grouper,
                    model=self.content,
                ),
            )

        return grouper_field


class VersionableList(list):

    @property
    def contents(self):
        return {versionable.content: versionable for versionable in self}
