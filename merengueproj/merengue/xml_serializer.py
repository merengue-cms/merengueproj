"""
XML serializer.
"""

from django.conf import settings
from django.core.serializers import base, xml_serializer
from django.db import models
from django.db.models.fields import FieldDoesNotExist

from transmeta import get_field_language


class Serializer(xml_serializer.Serializer):
    """
    Serializes a QuerySet to XML.
    """

    pass


class Deserializer(xml_serializer.Deserializer):
    """
    Deserialize XML.

    Like Django XML deserializer, with these improvements:
      * Translations fields support.
      * Option for not overwrite objects previously loaded in your site.
    """

    def next(self):
        for event, node in self.event_stream:
            if event == "START_ELEMENT" and node.nodeName == "object":
                if node.hasAttribute("overwrite") and \
                   node.getAttribute("overwrite") == 'no':
                    Model = self._get_model_from_node(node, "model")
                    pk = node.getAttribute("pk")
                    if not pk:
                        raise base.DeserializationError("<object> node is missing the 'pk' attribute")
                    if not node.hasAttribute("compare-by"):
                        filters = {'pk': Model._meta.pk.to_python(pk)}
                    else:  # comparing by custom field defined in the fixture
                        field = str(node.getAttribute("compare-by"))
                        value = node.getAttribute(field)
                        filters = {field: value}
                    if Model._base_manager.filter(**filters):
                        # if object is found we will not overwrite it
                        # because is marked as non overridable
                        continue
                self.event_stream.expandNode(node)
                return self._handle_object(node)
        raise StopIteration

    def _handle_object(self, node):
        """
        Convert an <object> node to a DeserializedObject.
        """
        # Look up the model using the model loading mechanism. If this fails,
        # bail.
        Model = self._get_model_from_node(node, "model")

        # Start building a data dictionary from the object.  If the node is
        # missing the pk attribute, fail.
        pk = node.getAttribute("pk")
        if not pk:
            raise base.DeserializationError("<object> node is missing the 'pk' attribute")

        data = {Model._meta.pk.attname: Model._meta.pk.to_python(pk)}

        # Also start building a dict of m2m data (this is saved as
        # {m2m_accessor_attribute : [list_of_related_objects]})
        m2m_data = {}

        # Deseralize each field.
        for field_node in node.getElementsByTagName("field"):
            # If the field is missing the name attribute, bail (are you
            # sensing a pattern here?)
            field_name = field_node.getAttribute("name")
            if not field_name:
                raise base.DeserializationError("<field> node is missing the 'name' attribute")

            # Get the field from the Model. This will raise a
            # FieldDoesNotExist if, well, the field doesn't exist, which will
            # be propagated correctly.
            try:
                field = Model._meta.get_field(field_name)
            except FieldDoesNotExist, e:
                try:
                    language = get_field_language(field_name)
                except:
                    raise e
                else:
                    lang_codes = [l[0] for l in settings.LANGUAGES]
                    if language not in lang_codes:
                        # fails silently because the LANGUAGES in these settings
                        # are not same as fixtures data
                        continue
                    else:
                        raise e

            # As is usually the case, relation fields get the special treatment.
            if field.rel and isinstance(field.rel, models.ManyToManyRel):
                m2m_data[field.name] = self._handle_m2m_field_node(field_node, field)
            elif field.rel and isinstance(field.rel, models.ManyToOneRel):
                data[field.attname] = self._handle_fk_field_node(field_node, field)
            else:
                if field_node.getElementsByTagName('None'):
                    value = None
                else:
                    value = field.to_python(xml_serializer.getInnerText(field_node).strip())
                data[field.name] = value

        # Return a DeserializedObject so that the m2m data has a place to live.
        return base.DeserializedObject(Model(**data), m2m_data)
