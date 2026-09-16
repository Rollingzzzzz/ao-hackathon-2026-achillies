"""AlarmStorm Correlator — S-A1 "Alarm Fırtınası" solution.

Reduces a 3,000-alarm flood over a 2-hour window into a handful of
actionable event cards, each with a root-cause hypothesis, evidence,
counter-hypotheses, affected services and a first action with owner
and lifecycle status. Every alarm is accounted for: attached to an
event or audited as noise with an explicit reason.
"""

__version__ = "1.0.0"
