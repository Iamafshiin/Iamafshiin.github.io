{% set gutter = "3.2cm" %}
{% set lines = entry.main_column.splitlines() %}
#regular-entry(
  [
    #box(width: {{ gutter }} + 0.3cm)[#text(fill: rgb(90, 100, 120))[{{ entry.date_and_location_column }}]]{{ lines[0] }}
  ],
  [],
  main-column-second-row: [
    #pad(left: {{ gutter }} + 0.3cm)[
{% for line in lines[1:] %}
      {{ line|indent(6) }}

{% endfor %}
    ]
  ],
)
