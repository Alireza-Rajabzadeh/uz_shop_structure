from rest_framework.decorators import api_view
from commons.responses import api_response
from rest_framework.exceptions import ValidationError,PermissionDenied

@api_view(["GET"])
def test_api(request):
    return api_response(
        message="Users domain working with DRF 🚀",
        data={
            "domain": "users",
            "status": "ok"
        }
    )


@api_view(["GET"])
def crash_test(request):
      raise PermissionDenied("You are not")

