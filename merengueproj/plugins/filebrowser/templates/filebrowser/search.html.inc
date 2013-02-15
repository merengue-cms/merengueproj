
{% load i18n filebrowser_tags %}

<div id="search-form">
  <form class="filebrowserSearch" action="{% filebrowser_url filebrowser_search %}" method="post">
    <input name="q" type="text" />
    <input type="submit" name="{% trans "search" %}" value="{% trans "search" %}" />
  </form>
</div>
