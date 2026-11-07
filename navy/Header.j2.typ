{% set name_parts = cv.name.split(" ", 1) %}
#block(
  width: 100%,
  fill: rgb(31, 45, 77),
  outset: (left: {{ design.page.left_margin }}, right: {{ design.page.right_margin }}, top: {{ design.page.top_margin }}),
  inset: (top: 0.1cm, bottom: 0.5cm),
  below: 0.5cm,
)[
= #text(weight: 800)[{{ name_parts[0]|upper }}] #text(weight: 300)[{{ name_parts[1]|upper if name_parts|length > 1 else "" }}]

{% if cv.headline %}
  #headline([{{ cv.headline }}])

{% endif %}
  #line(length: 100%, stroke: 0.6pt + rgb(74, 90, 125))
  #v(0.1cm)
#connections(
{% for connection in cv._connections %}
  [{{ connection }}],
{% endfor %}
)
#v(0.25cm)
]
