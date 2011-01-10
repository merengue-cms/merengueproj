#!/bin/sh

./manage.py graph_models places collection base -g -o basecontent_models.png && echo "Drawn base content models in basecontent_models.png"
./manage.py graph_models section -g -o section_models.png && echo "Drawn section models in section_models.png"
./manage.py graph_models registry action block pluggable -g -o registry_models.png && echo "Drawn registry models in registry_models.png"
./manage.py graph_models multimedia -g -o multimedia_models.png && echo "Drawn multimedia models in multimedia_models.png"
./manage.py graph_models perms -g -o permission_models.png && echo "Drawn permission models in permission_models.png"
