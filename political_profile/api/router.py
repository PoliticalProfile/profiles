from rest_framework import routers

from political_profile.api import viewsets

router = routers.DefaultRouter()
router.register('congressman', viewsets.CongressmanViewset)
router.register('proposition', viewsets.PropositionViewset)
router.register('discourse', viewsets.DiscourseViewset)
