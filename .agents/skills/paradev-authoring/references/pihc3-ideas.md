# PIHC3 Idea Batch

Read this reference only when creating PIHC3 `idea` modules.

Select `pihc3:idea/basic`. Its `cic` value is a decimal civilian-industry
factor, so `2%`, `5%`, `8%`, `12%`, and `16%` become `0.02`, `0.05`, `0.08`,
`0.12`, and `0.16`.

Example request rows:

```json
[
  {
    "template_id": "pihc3:idea/basic",
    "object_id": "A",
    "values": {"title": "A", "cic": 0.02}
  },
  {
    "template_id": "pihc3:idea/basic",
    "object_id": "B",
    "values": {"title": "B", "cic": 0.05}
  },
  {
    "template_id": "pihc3:idea/basic",
    "object_id": "C",
    "values": {"title": "C", "cic": 0.08}
  },
  {
    "template_id": "pihc3:idea/basic",
    "object_id": "D",
    "values": {"title": "D", "cic": 0.12}
  },
  {
    "template_id": "pihc3:idea/basic",
    "object_id": "E",
    "values": {"title": "E", "cic": 0.16}
  }
]
```

The current template plans `def.txt` and `main.loc`; it does not require
visible metadata. Always review the live rendered plan in case the Registry
template evolves.
