"""Displays the next train

Requires the following library:
   * libsl (which requires pycurl)

Parameters:
   * sl.api_key : Api key (SL Departures v4.0) from https://developer.trafiklab.se/login
   * sl.site_id : Site id. Unique id for each stop which are retrieved from libsl.py. Example: "python3 station_search libsl.py <sl stop lookup v1.0 api key> Telefonplan 10"
   * sl.time_window : Get all depatures within this time window in minutes.
   * sl.line_number : Only show this line number.
   * sl.journey_direction : Can be 1,2 or 0. You need to check with departure_search in libsl what direction it refers to.

contributed by `olofsjod <https://github.com/olofsjod>`
"""

import libsl

import core.module
import core.widget

class Module(core.module.Module):
    @core.decorators.every(minutes=1, seconds=30)
    def __init__(self, config, theme):
        super().__init__(config, theme, core.widget.Widget(self.full_text))
        self.__sl_departure_v40_api_key = self.parameter("api_key", "")
        self.__siteid = self.parameter("site_id", "")
        self.__time_window = self.parameter("time_window", "15")
        self.__line_number = self.parameter("line_number", "")
        self.__journey_direction = self.parameter("journey_direction", "")

    def full_text(self, widgets):
        result = libsl.get_departures_at_site(
            self.__sl_departure_v40_api_key,
            self.__siteid,
            int(self.__time_window)
        )

        font_awesome_icons = {
            "Buses" : "",
            "Metros" : "",
            "Trains" : "",
            "Trams" : "",
            "Ships" : ""
        }

        new_result = []
        for n in ["Buses", "Metros", "Trains", "Trams", "Ships"]:
            if self.__line_number != "" and self.__journey_direction != "":
                filtered_items = list(
                    filter(
                            lambda x : (x['LineNumber'] == self.__line_number) and (x['JourneyDirection'] == int(self.__journey_direction)),
                            result[n]
                        )
                )


                for item in filtered_items:
                    item['Icon'] = font_awesome_icons[n]
                new_result.extend(
                    filtered_items
                )
            elif self.__line_number != "":
                new_result.extend(
                    list(
                        filter(
                            lambda x : (x['LineNumber'] == self.__line_number),
                            result[n]
                        )
                    )
                )
            else:
                new_result.extend(
                    result[n]
                )

        ret = ""
        for item in new_result:
            ret += f"[{item['Icon']} {item['LineNumber']} {item['Destination']} {item['DisplayTime']}]"
        return ret

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
