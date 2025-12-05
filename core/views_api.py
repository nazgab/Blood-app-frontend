from rest_framework.views import APIView
from rest_framework.response import Response
from core.models import AdminDonation

class DonationListAPI(APIView):
    def get(self, request):
        donations = AdminDonation.objects.all()

        result = []
        for d in donations:
            result.append({
                "date": "2025-01-01",
                "center_name": f"Орталық #{d.center_id}",
                "amount_ml": 450,
                "status": "қабылданды",
                "bonus": 50,
                "comment": "",
            })

        return Response(result)
