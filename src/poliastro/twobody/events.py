from astropy import units as u
from astropy.coordinates import (
    GCRS,
    ITRS,
    CartesianRepresentation,
    SphericalRepresentation,
)
from astropy.time import Time
from numpy.linalg import norm


class Event:
    """Base class for event functionalities.

    Parameters
    ----------
    terminal: bool
        Whether to terminate integration if this event occurs.
    direction: float
        Handle triggering of event.

    """

    def __init__(self, terminal, direction):
        self._terminal, self._direction = terminal, direction
        self._last_t = None

    @property
    def terminal(self):
        return self._terminal

    @property
    def direction(self):
        return self._direction

    @property
    def last_t(self):
        return self._last_t * u.s

    def __call__(self, t, u, k):
        raise NotImplementedError


class AltitudeCrossEvent(Event):
    """Detect if a satellite crosses a specific threshold altitude.

    Parameters
    ----------
    alt: float
        Threshold altitude (km).
    R: float
        Radius of the attractor (km).
    terminal: bool
        Whether to terminate integration if this event occurs.
    direction: float
        Handle triggering of event based on whether altitude is crossed from above
        or below, defaults to -1, i.e., event is triggered only if altitude is
        crossed from above (decreasing altitude).

    """

    def __init__(self, alt, R, terminal=True, direction=-1):
        super().__init__(terminal, direction)
        self._R = R
        self._alt = alt  # Threshold altitude from the ground.

    def __call__(self, t, u, k):
        self._last_t = t
        r_norm = norm(u[:3])

        return (
            r_norm - self._R - self._alt
        )  # If this goes from +ve to -ve, altitude is decreasing.


class LithobrakeEvent(AltitudeCrossEvent):
    """Terminal event that detects impact with the attractor surface.

    Parameters
    ----------
    R : float
        Radius of the attractor (km).
    terminal: bool
        Whether to terminate integration if this event occurs.

    """

    def __init__(self, R, terminal=True):
        super().__init__(0, R, terminal, direction=-1)


class LatitudeCrossEvent(Event):
    """Detect if a satellite crosses a specific threshold latitude.

    Parameters
    ----------
    lat: float
        Threshold latitude (km).
    R: float
        Radius of the attractor (km).
    terminal: bool
        Whether to terminate integration if this event occurs, defaults to True.
    direction: float
        Handle triggering of event based on whether latitude is crossed from above
        or below, defaults to 0, i.e., event is triggered while traversing from both directions.

    """

    def __init__(self, lat, R, terminal=True, direction=0):
        super().__init__(terminal, direction)
        self._R = R
        self._lat = lat  # Threshold latitude (in degrees).

    def __call__(self, t, u, k):
        self._last_t = t
        xyz = u[:3]

        obstime = Time(self._last_t, format="jd")
        gcrs_xyz = GCRS(
            xyz,
            obstime=obstime,
            representation_type=CartesianRepresentation,
        )
        itrs_xyz = gcrs_xyz.transform_to(ITRS(obstime=obstime))
        itrs_latlon_pos = itrs_xyz.represent_as(SphericalRepresentation)
        orbit_lat = itrs_latlon_pos.lat.value
        return self._lat - orbit_lat


class LongitudeCrossEvent(Event):
    """Detect if a satellite crosses a specific threshold latitude.

    Parameters
    ----------
    lon: float
        Threshold longitude (km).
    R: float
        Radius of the attractor (km).
    terminal: bool
        Whether to terminate integration if this event occurs, defaults to True.
    direction: float
        Handle triggering of event based on whether longitude is crossed from above
        or below, defaults to 0, i.e., event is triggered while traversing from both directions.

    """

    def __init__(self, lon, R, terminal=True, direction=0):
        super().__init__(terminal, direction)
        self._R = R
        self._lon = lon  # Threshold longitude (in degrees).

    def __call__(self, t, u, k):
        self._last_t = t
        xyz = u[:3]

        obstime = Time(self._last_t, format="jd")
        gcrs_xyz = GCRS(
            xyz,
            obstime=obstime,
            representation_type=CartesianRepresentation,
        )
        itrs_xyz = gcrs_xyz.transform_to(ITRS(obstime=obstime))
        itrs_latlon_pos = itrs_xyz.represent_as(SphericalRepresentation)
        orbit_lon = itrs_latlon_pos.lon.value

        return self._lon - orbit_lon
