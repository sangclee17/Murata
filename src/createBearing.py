from hwx import simlab

import utility as util

# remove "-" from body names
util.replaceAllBodyNms("-", "_")

# get 3 faces and 2 bodies from group
face1_Ent = simlab.getEntityFromGroup("Face_Group1")
face2_Ent = simlab.getEntityFromGroup("Face_Group2")
contactFace_Ent = simlab.getEntityFromGroup("Face_Group3")

shaftEnt = simlab.getBodiesFromGroup("Body_Group4")[0]
sleeveEnt = simlab.getBodiesFromGroup("Body_Group5")[0]

plane1 = util.getPlaneDataIn3Points(face1_Ent)
plane2 = util.getPlaneDataIn3Points(face2_Ent)

regionMc_prop = "region", "{}_regionMc".format(shaftEnt), shaftEnt, plane1, plane2
util.createMeshControl(regionMc_prop)

# do sruface mesh

# Create outer Ring
destinationModel = simlab.getModelName("FEM")
height, _ = util.getDistanceBetweenTwoFaces("CAD", face1_Ent, face2_Ent)
cpt, rad = util.getCircularFeatureAssociated("CAD", contactFace_Ent)
util.createCylinderFace(cpt, rad, height, axialElems=4, circularElems=20)
util.transferBodies(sleeveEnt, "Cylindrical1", destinationModel)
util.mergeFaces(util.getFaceIdFromBody("FEM", sleeveEnt))

# Grab inner Ring within planes
innerRingEnts = util.getInnerRingFaceIdsFromFEMBody(shaftEnt, plane1, plane2)
innerRingGrp = util.getLargerRingGrp("FEM", innerRingEnts, "innerRing")
util.mergeFaces(simlab.getEntityFromGroup(innerRingGrp))
mergedFaceId = simlab.getEntityFromGroup(innerRingGrp)[0]
util.changeLayers(mergedFaceId, onAxial=4, onCircular=20)
util.createBodyFromFaces(innerRingGrp)
innerRingNm = "{}_inner".format(sleeveEnt)
util.renameBody(destinationModel, innerRingGrp, innerRingNm)
util.updateModel()

# bearing Contact Faces
outerFaceId = util.getFaceIdFromBody("FEM", sleeveEnt)
util.reverseNormal(outerFaceId)
util.changeLayers(outerFaceId, onAxial=4, onCircular=20)
innerFaceId = util.getFaceIdFromBody("FEM", innerRingNm)

util.drawEdgeFromOffset(sleeveEnt, [plane1, plane2], height/4)
outerContactFaceEntities = util.getBearingContactFaceEntities(sleeveEnt, [plane1, plane2])
# util.changeLayers(outerContactFaceEntities[0], onAxial=2, onCircular=20)

util.drawEdgeFromOffset(innerRingNm, [plane1, plane2], height/4)
innerContactFaceEntities = util.getBearingContactFaceEntities(innerRingNm, [plane1, plane2])
# util.changeLayers(innerContactFaceEntities[0], onAxial=2, onCircular=20)

# flip outer ring faces
util.flipOuterRing(sleeveEnt)

# Inner outer ring merge
util.mergeBodies(simlab.getBodiesWithSubString(simlab.getModelName("FEM"), ["{}*".format(sleeveEnt)]),"PSHELL1" )

# create Bearings with new coordinate attached and connect them in spring
_, gap = util.getDistanceBetweenTwoFaces("FEM", outerContactFaceEntities, innerContactFaceEntities)

bearingProp = innerContactFaceEntities, outerContactFaceEntities, 8, gap/2, 0, 0
coordId = 20
springStiff = 200
util.makeShellBearingWithSpring(bearingProp, coordId, springStiff)
