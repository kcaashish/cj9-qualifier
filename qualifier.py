import typing
from dataclasses import dataclass


@dataclass(frozen=True)
class Request:
    scope: typing.Mapping[str, typing.Any]

    receive: typing.Callable[[], typing.Awaitable[object]]
    send: typing.Callable[[object], typing.Awaitable[None]]


class RestaurantManager:
    def __init__(self):
        """Instantiate the restaurant manager.

        This is called at the start of each day before any staff get on
        duty or any orders come in. You should do any setup necessary
        to get the system working before the day starts here; we have
        already defined a staff dictionary.
        """
        self.staff = {}

    async def __call__(self, request: Request):
        """Handle a request received.

        This is called for each request received by your application.
        In here is where most of the code for your system should go.

        :param request: request object
            Request object containing information about the sent
            request to your application.
        """
        rq_type = request.scope.get("type")

        if rq_type == "staff.onduty":
            self.staff[request.scope.get("id")] = request

        elif rq_type == "staff.offduty":
            self.staff.pop(request.scope.get("id"))
        
        elif rq_type == "order":
            rq_speciality = request.scope.get("speciality")

            special_staff = []
            for st in self.staff.values():
                st_speciality = st.scope.get("speciality")
                if rq_speciality in st_speciality:
                    special_staff.append(st)

            found = special_staff[0]
            full_order = await request.receive()
            await found.send(full_order)

            result = await found.receive()
            await request.send(result)
